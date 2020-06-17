"""
Opens one UDP port through a trio socket
"""


import trio


class UDPPortListener:
    """
    Constructor - makes a new socket
    """

    def __init__(self, port, response, delay, nursery):
        self.port = port
        self.response = response
        self.delay = delay
        self.nursery = nursery

        # Defaults
        self.ip = ""
        self.isRunning = False

    """
    Send a response on a port

    Args:
      addr: where to send the payload to
    """

    async def portResponse(self, sock, addr):
        byteData = bytes.fromhex(self.response)
        await trio.sleep(float(self.delay))
        await sock.sendto(byteData, addr)

    """
    Listen and respond on this listener's port
    """

    async def handler(self):
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
