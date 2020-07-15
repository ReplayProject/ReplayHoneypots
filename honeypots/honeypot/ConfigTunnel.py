import inspect
import ssl
import sys

import trio


class ConfigTunnel:
    """
    Handles the creation/usage of the configuration tunnel,
    which is a module to support remote/live configuration over
    TCP or SSL connections
    """

    def __init__(self, mode, port, host="", cafile=None):
        """
        Setup variables for the config tunnel to operate
        Input: mode [server|client], host [IP], cafile [PATH]
        """
        self.mode = mode
        self.connectHost = host
        self.serverPort = int(port)
        self.handlers = {}
        self.certfile = cafile
        self.client_stream = None
        self.channel = None

    def setHandler(self, trigger, handler):
        """
        Sets a handler for a trigger keyword (triggered via incoming message)
        """
        if trigger in self.handlers.keys():
            raise Exception("Handler for " + trigger + " already defined")
        self.handlers[trigger] = handler

    async def triggerHandler(self, input):
        """
        Triggers a handler given an input, also deals with the return values
        """
        text = input.decode("utf-8").rstrip()
        cmds = text.split(" ")

        # Trigger handler on first word and pass the test
        if cmds[0] not in self.handlers.keys():
            print("Handler for ", cmds[0], " not found")
            return

        func = self.handlers[cmds[0]]

        # Check if we are dealing with an async function or not
        if inspect.iscoroutinefunction(func):
            resp = await func(cmds[1:])
        else:
            resp = func(cmds[1:])

        if resp is not None:
            return "done " + str(resp) + "\n"

    async def readstream(self, stream):
        """
        Logic for listening on a stream and triggering handlers
        """
        async with stream:
            async for data in stream:
                print(self.mode + " conftunnel got: {!r}".format(data))
                resp = await self.triggerHandler(data)
                if resp is not None:
                    await stream.send_all(resp.encode("utf8"))
            print(self.mode + "conftunnel: connection closed")

    async def listen(self, channel=None):
        """
        Start the config server as a host
        """
        # Decide if we are encrypting or not.
        print(self.mode + " conftunnel starting")
        # Optional trio channel for communicating commands
        if channel:
            self.channel = channel
        # Optional certfile to use for a SSL connection
        if self.certfile:
            sslctx = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
            sslctx.load_cert_chain(certfile=self.certfile, keyfile=self.certfile)
            await trio.serve_ssl_over_tcp(self.readstream, self.serverPort, sslctx)
        else:
            await trio.serve_tcp(self.readstream, self.serverPort)

    async def connect(self, task_status=trio.TASK_STATUS_IGNORED):
        """
        Start the config server client
        """
        print(
            "conftunnel connecting to {}:{}".format(self.connectHost, self.serverPort)
        )

        # Decide if we are encrypting or not.
        if self.certfile:
            sslctx = ssl.create_default_context(cafile=self.certfile)
            sslctx.check_hostname = False

            self.client_stream = await trio.open_ssl_over_tcp_stream(
                self.connectHost, self.serverPort, ssl_context=sslctx
            )
        else:
            self.client_stream = await trio.open_tcp_stream(
                self.connectHost, self.serverPort
            )

        # Mark task as started for parent nursery
        task_status.started()

        async with trio.open_nursery() as nursery:
            nursery.start_soon(self.readstream, self.client_stream)

    async def send(self, given_line):
        """
        Encrypt and send messages over connection
        """
        if not self.client_stream:
            raise Exception("no stream on client conftunnel")

        print("client sending: ", given_line)
        await self.client_stream.send_all(given_line.encode("utf8"))

    async def relaytochannel(self, x):
        """
        Relay the incoming commands to PTM
        """
        await self.channel.send(x)
        return

    async def destroy(self, cancel_scope):
        """
        Closes stream and channel resources
        """
        if self.client_stream:
            await self.client_stream.aclose()
        if self.channel:
            await self.channel.aclose()
        if cancel_scope:
            cancel_scope.cancel()
