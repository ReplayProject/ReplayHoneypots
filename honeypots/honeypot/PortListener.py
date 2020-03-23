from threading import Thread
import socket
import time

"""
Opens one TCP port through a python socket
"""

class PortListener(Thread):
    """
    Constructor - makes a new socket
    """
    def __init__(self, port, response, delay):
        Thread.__init__(self)

        self.port = port
        self.response = response
        self.delay = delay
        self.isRunning = True

    """
    Listen and respond on the given port

    Args:
      portObj: port object with communication info
    """
    def portListener(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("", self.port))
        sock.listen(1)
        while self.isRunning:
            print("Listening on port " + str(self.port))
            conn, addr = sock.accept()
            print(conn)
            print(addr)
            responseThread = Thread(target=self.portResponse, args=[conn])
            responseThread.daemon = True
            responseThread.start()
        conn.close()

    """
    Send a response on a port

    Args:
      portObj: port object with communication info
      conn: connection object to communicate on
    """

    def portResponse(self, conn):
        byteData = bytes.fromhex(self.response)
        time.sleep(float(self.delay))
        try:
            conn.send(byteData)
        except:
            print("Connection reset on port " + str(self.port))