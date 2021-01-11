import trio
from difflib import SequenceMatcher
from pprint import pprint
import errno
from strsimpy.normalized_levenshtein import NormalizedLevenshtein

DISTANCE_PROPORTION_THRESHOLD = 0.85

class Listener:
    """
    Opens one TCP port through a python socket
    """
    def __init__(self, port, service_obj, protocol, delay, nursery):
        """
        Constructor - makes a new socket
        """
        self.port = port
        self.service_obj = service_obj
        self.protocol = protocol
        self.delay = delay
        self.nursery = nursery

        self.index_map = {}

        # Defaults
        self.ip = ""
        self.isRunning = False

    

    async def handleConnection(self, sock, conn, addr):
        try:
            # Send first responses if first request is empty
            if len(self.service_obj.response_model) > 1 and self.service_obj.response_model[0]["request"] is None:
                responses = self.service_obj.response_model[0]["responses"]
                for response in responses:
                    payload = response["payload"]
                    print("Sending first response", payload)
                    byteData = bytes.fromhex(payload)
                    await conn.send(byteData)

            while True:
                data = await conn.recv(1024)
                if not data:
                    print("Connection closed")
                    conn.shutdown(2)
                    conn.close()
                    self.index_map[addr] = 0
                    return

                data = data.hex()
            
                await self.portResponse(sock, conn, addr, data)
        except:
            print("Connection reset by peer. Exiting Connection Logic.")
            return


    async def portResponse(self, sock, conn, addr, data):
        """
        Send a response on a port

        Args:
          addr: where to send the payload to
        """
        response_idx = self.getResponseIdx(addr, data)
        if response_idx != -1:
            responses = self.service_obj.response_model[response_idx]["responses"]
            for response in responses:
                payload = response["payload"]
                byteData = bytes.fromhex(payload)
                await trio.sleep(self.delay)
                if self.protocol == "TCP":
                    await conn.send(byteData)
                else:
                    print("Sending UDP data", data)
                    await sock.sendto(byteData, addr)

    def getResponseIdx(self, addr, data):
        index = 0
        print("Getting response idx for addr: ", addr)
        try:
            index = self.index_map[addr]
        except:
            pass


        i = index
        # Start at index i and loop back around from the beginning
        while True:
            if self.service_obj.response_model[i]["request"] is not None:
                request = self.service_obj.response_model[i]["request"]["payload"]
                if self.requestMatches(data, request):
                    self.index_map[addr] = i
                    print("MATCH")
                    try:
                        print("Request: ", bytes.fromhex(request).decode('utf-8'))
                    except:
                        print("Request: ", request)
                    return i
            
            if i == len(self.service_obj.response_model) - 1:
                print("Looping back, length: ", len(self.service_obj.response_model))
                i = 0
            else:
                i += 1

            if i == index:
                break
        
        return -1

    def requestMatches(self, data, request):

        if data == None or request == None:
            return data == None and request == None

        requestLength = len(request)
        dataLength = len(data)

        if (requestLength > 25 or dataLength > 25): # do not perform distance ignorance if payload is short - a five byte payload may match even with a 20% length difference
            if (requestLength < (0.9 * dataLength)): # if request is much shorter than data
                return False
            if (dataLength < (0.9 * requestLength)): # if data is much shorter than request            
                return False

        matcher = NormalizedLevenshtein()
        score = matcher.similarity(data, request)
        print(request)
        print(data)
        print(score)

        return score > 0.8

    async def handler(self):
        """
        Listen and respond on the given port
        """
        print(self.protocol)
        conn = None
        addr = None
        sock_type = trio.socket.SOCK_STREAM
        if self.protocol == "UDP":
            sock_type = trio.socket.SOCK_DGRAM
        with trio.socket.socket(trio.socket.AF_INET, sock_type) as sock:
            if self.protocol == "TCP":
                sock.setsockopt(trio.socket.SOL_SOCKET, trio.socket.SO_REUSEADDR, 1)
            print("A")
            try:
                await sock.bind((self.ip, int(self.port)))
                if self.protocol == "TCP":
                    sock.listen(1)
            except Exception as e:
                print(str(e))

            print(self.protocol + " Listening on port " + str(self.port))
            self.isRunning = True

            if self.protocol == "TCP":
                while self.isRunning:
                    conn, addr = await sock.accept()
                    print("Accepting connection from ", addr)
                    self.nursery.start_soon(self.handleConnection, sock, conn, addr)
            else:
                while True:
                    data, addr = await sock.recvfrom(1024)  # buffer size is 1024 bytes
                    data = data.hex()
                    await self.portResponse(sock, conn, addr, data)