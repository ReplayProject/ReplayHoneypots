import trio


class UDPPortListener:
    """
    Opens one UDP port through a trio socket
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

    async def portResponse(self, sock, addr):
        """
        Send a response on a port

        Args:
          addr: where to send the payload to
        """
        byteData = bytes.fromhex(self.response)
        await trio.sleep(self.delay)
        await sock.sendto(byteData, addr)

    async def handler(self):
        """
        Listen and respond on this listener's port
        """
        with trio.socket.socket(trio.socket.AF_INET, trio.socket.SOCK_DGRAM) as sock:

            await sock.bind((self.ip, int(self.port)))
            print("UDP Listening on port " + str(self.port))
            self.isRunning = True

            while self.isRunning:
                data, addr = await sock.recvfrom(1024)  # buffer size is 1024 bytes
                print("UDP from:", addr)
                # Print out incoming data
                # print("received message:", data)
                self.nursery.start_soon(self.portResponse, sock, addr)
