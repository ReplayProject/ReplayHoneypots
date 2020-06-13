import trio
import sys


class ConfigTunnel:
    """
    Handles the creation/usage of the configuration tunnel, which is a module to support remote/live configuration over a discrete connection
    """

    def __init__(self, mode, host=""):
        """
        Setup variables for the config tunnel to operate
        Input: mode [server|client], host (optional ssh tunnel host)
        """
        self.mode = mode
        self.connectHost = host
        self.serverPort = 9998
        self.handlers = {}
        self.client_stream = None

    def setHandler(self, trigger, handler):
        """
        Sets a handler for a trigger keyword (triggered over socket)
        """
        if trigger in self.handlers.keys():
            raise Exception("Handler for " + trigger + " already defined")
        self.handlers[trigger] = handler

    def triggerHandler(self, input):
        """
        Triggers a handler given an input, also deals with the return values
        """
        text = input.decode("utf-8").rstrip()
        cmds = text.split(" ")

        # Trigger handler on first word and pass the test
        if cmds[0] not in self.handlers.keys():
            print("Handler for ", cmds[0], " not found")
            return

        resp = self.handlers[cmds[0]](cmds[1:])
        if resp is not None:
            return "done " + str(resp) + "\n"

    async def readstream(self, stream):
        """
        Logic for listening on a stream and triggering handlers
        """
        print(self.mode + " receiver started!")

        async with stream:
            # try:
            async for data in stream:
                print(self.mode + " receiver got: {!r}".format(data))
                resp = self.triggerHandler(data)
                if resp is not None:
                    await stream.send_all(resp.encode("utf8"))
        print(self.mode + "receiver: connection closed")
        # except Exception as exc:
        #     print(self.mode +" readstream crashed: {!r}".format(exc))

    async def listen(self):
        """
        Start the config server as a host
        """
        await trio.serve_tcp(self.readstream, self.serverPort)

    async def connect(self):
        """
        Start the config server client (and tunnel in)
        """
        print("connecting to {}:{}".format(self.connectHost, self.serverPort))

        self.client_stream = await trio.open_tcp_stream(
            self.connectHost, self.serverPort
        )

        async with trio.open_nursery() as nursery:
            nursery.start_soon(self.readstream, self.client_stream)

    async def send(self, given_line):
        """
        Encrypt and send stdin over socket connection
        """
        if not self.client_stream:
            raise Exception("no stream on client tunnel")

        print("client sending: ", given_line)
        await self.client_stream.send_all(given_line.encode("utf8"))

    def destroy(self):
        """
        Closes stream resources
        """
        if self.client_stream:
            self.client_stream.aclose()
