import trio


class TCPPortListener:
    """
    Opens one TCP port through a python socket
    """

    def __init__(self, port, response, delay, nursery):
        """
        Constructor - makes a new socket
        """
        self.port = port
        self.response = response
        self.delay = delay
        self.nursery = nursery

        # Defaults
        self.ip = ""
        self.isRunning = False

    async def portResponse(self, conn):
        """
        Send a response on a port

        Args:
          addr: where to send the payload to
        """
        byteData = bytes.fromhex(self.response)
        await trio.sleep(self.delay)
        await conn.send(byteData)
        # TODO: check if desired behaivor to disconnect immediately
        conn.shutdown(trio.socket.SHUT_RDWR)
        conn.close()

    async def handler(self):
        """
        Listen and respond on the given port
        """
        with trio.socket.socket(trio.socket.AF_INET, trio.socket.SOCK_STREAM) as sock:

            sock.setsockopt(trio.socket.SOL_SOCKET, trio.socket.SO_REUSEADDR, 1)
            await sock.bind((self.ip, int(self.port)))
            sock.listen(1)
            print("TCP Listening on port " + str(self.port))
            self.isRunning = True

            while True:
                conn, addr = await sock.accept()
                print("TCP from:", addr)
                # Print out incoming data
                # data = await conn.recv(1024)
                # print("received message:", data)
                self.nursery.start_soon(self.portResponse, conn)
