"""
Module to support remote/live configuration over a discrete connection

Adapted from CSC 474 Homework Assignments
Author: Seth Parrish
"""
from threading import Thread
import configparser

# Crypto Imports
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.Hash import HMAC
from Crypto import Random

# Refular imports
import select
import socket
import sys
import os
import io

dhg = 2
dhp = 0x00cc81ea8157352a9e9a318aac4e33ffba80fc8da3373fb44895109e4c3ff6cedcc55c02228fccbd551a504feb4346d2aef47053311ceaba95f6c540b967b9409e9f0502e598cfc71327c5a455e2e807bede1e0b7d23fbea054b951ca964eaecae7ba842ba1fc6818c453bf19eb9c5c86e723e69a210d4b72561cab97b3fb3060b


def fast_power(base, power):
    """
    Returns the result of a^b i.e. a**b
    We assume that a >= 1 and b >= 0

    Remember two things!
    - Divide power by 2 and multiply base to itself (if the power is even)
    - Decrement power by 1 to make it even and then follow the first step
    """
    result = 1
    while power > 0:
        # If power is even
        if power % 2 == 0:
            # Divide the power by 2
            power = power // 2
            # Multiply base to itself
            base = base * base
        else:
            # Decrement the power by 1 and make it even
            power = power - 1
            # Take care of the extra value that we took out
            # We will store it directly in result
            result = result * base
            # Now power is even, so we can follow our previous procedure
            power = power // 2
            base = base * base
    return result


class ConfigTunnel(Thread):
    """
    Handles the creation/usage of the configuration tunnel
    """
    def __init__(self, mode, host=""):
        """
        Setup variables for the config tunnel to operate
        Input: mode [server|client], host (optional ssh tunnel host)
        """
        Thread.__init__(self)
        self.mode = mode
        self.connectHost = host
        self.needsTunnel = host not in ["localhost", "127.0.0.1"]
        self.keyMaterial = ""

        self.running = True
        self.serverPort = 9998
        self.ready = False
        self.handlers = {}

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
        cmds = text.split(' ')

        # Trigger handler on first word and pass the test
        if cmds[0] not in self.handlers.keys():
            print("Handler for ", cmds[0], " not found")
            return 1

        resp = self.handlers[cmds[0]](cmds[1:])
        if resp is not None:
            self.send("done " + str(resp) + '\n')

    def mainloop(self, s):
        """
        Runs the loop for listening and parsing input
        """
        self.input = [s]
        is_server = self.mode == "server"
        input_size = (1 if is_server else 0)

        while self.running:
            # Run select with a 2 second timeout
            readables, writeables, exceptions = select.select(
                self.input, [], [], 2)
            for x in readables:
                # New Client For Server
                if is_server and x == s:
                    soc = s.accept()[0]
                    try:
                        self.input.append(soc)
                        self.keyMaterial = self.DiffieHellam(soc)
                        self.ready = True
                    except Exception as e:
                        self.input.remove(soc)
                        print("Error during CT connection", e)
                # Stdin Message
                elif x == sys.stdin and len(self.input) > input_size:
                    self.send()  # self.running =
                # Socket Message
                elif len(self.input) > input_size:
                    self.readFromSocket(x)  # self.running =

    def listen(self):
        """
        Start the config server as a host
        """
        with socket.socket() as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setblocking(False)
            s.bind(('', self.serverPort))
            s.listen(5)
            self.mainloop(s)

    def connect(self):
        """
        Start the config server client (and tunnel in)
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            host = self.connectHost
            port = self.serverPort

            s.connect((socket.gethostbyname(host), port))

            try:
                self.keyMaterial = self.DiffieHellam(s)
                self.ready = True
            except TypeError:
                print("Something went wrong in client tunnel connection")
                sys.exit()
            self.mainloop(s)

    def run(self):
        """
        Decide on how to start the tunnel
        """
        print('Starting ', self.mode, ' ConfigTunnel')

        if self.mode == "server":
            self.listen()
        elif self.mode == "client":
            self.connect()

    def stop(self):
        """
        Toggles the running flag on the main loop
        """
        self.running = 0

    # Socket Logic
    def readFromSocket(self, x):
        """
        Read section of data from socket, and then decrypt it
        """
        datalen = 80
        buffer = bytes()
        while '\n' not in buffer.decode('utf-8'):
            data = x.recv(datalen)
            if (len(data) > 80):
                sys.stdout.buffer.write(data)
            if ((data is not None) and (len(data) > 0) and data != b''):
                buffer += self.de(data)
                if '\n' not in buffer.decode('utf-8'):
                    continue
                self.triggerHandler(buffer)
                # sys.stdout.buffer.write(self.de(data))
                # sys.stdout.flush()
                return True
            self.input.remove(x)
            x.close()
            return False

    def send(self, given_line=""):
        """
        Encrypt and send stdin over socket connection
        """
        if given_line == "":
            line = sys.stdin.buffer.readline(1024)
        else:
            line = io.StringIO(given_line + '\n').readline(1024)

        if (len(line) <= AES.block_size):
            if ((line is not None) and (len(line) > 0) and line != b''):
                self.input[-1].sendall(self.en(line))
                return True
        else:
            i = 0
            while (i < len(line)):
                i += 16
                self.input[-1].sendall(self.en(line[i - 16:i]))
            return True
        return False

    # CRYPTO STUFF

    def sha256(self, s):
        h = SHA256.new()
        h.update(s.encode())
        return h.hexdigest()

    def en(self, cleartext):
        pt1k1 = self.keyMaterial[:AES.block_size]
        pt1k2 = self.keyMaterial[AES.block_size:]
        # AES ENCRYPT MESSAGE
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(pt1k1.encode("utf8"), AES.MODE_CBC, iv)
        # Pad It
        x = bytes(cleartext.encode("ascii"))
        length = 32 - (len(x) % 32)
        x += bytes([length]) * length
        # Encrypt It
        ciphertext = cipher.encrypt(x)
        # Add Verification
        h = HMAC.new(pt1k2.encode('utf-8'), digestmod=SHA256)
        h.update(ciphertext)
        mac = h.digest()
        # print(" ", len(iv + mac + ciphertext), "  -  " ,len(ciphertext))
        # Package: IV + HMAC + MSG
        return iv + mac + ciphertext

    def de(self, package):
        pt1k1 = self.keyMaterial[:AES.block_size]
        pt1k2 = self.keyMaterial[AES.block_size:]
        iv = package[0:16]
        mac = package[16:48]
        ciphertext = package[48:len(package)]
        # print(" ", len(package), "  -  " ,len(ciphertext))
        h = HMAC.new(pt1k2.encode('utf-8'), digestmod=SHA256)
        h.update(ciphertext)
        # Authenticity Check
        if mac != h.digest():
            sys.exit("THE MESSAGE OR AUTHKEY IS WRONG (non-authentic)")
        decipher = AES.new(pt1k1.encode('utf8'), AES.MODE_CBC, iv)
        cleartext = decipher.decrypt(ciphertext)
        padding = cleartext[len(cleartext) - 1]
        # Should work most of the time
        if padding > 32:
            return cleartext
        else:
            return cleartext[:-padding]

    def DiffieHellam(self, s):
        """
        Perform a dh exchange to arrive at compatible keys
        """
        my_secret = int.from_bytes(os.urandom(1), byteorder='little')
        is_server = self.mode == "server"
        x = None

        def recvit():
            data = s.recv(100)
            if ((data is not None) and (len(data) > 0) and data != b''):
                return data
            return None

        is_server = self.mode == "server"
        if is_server:
            # Server sends A = g^a mod p to client
            s.sendall(str((fast_power(dhg, my_secret)) % dhp).encode('utf-8'))
            x = recvit()
        else:
            x = recvit()
            # Client sends B = g^b mod p
            s.sendall(str((fast_power(dhg, my_secret)) % dhp).encode('utf-8'))
        # Get the Shared Secret
        return self.sha256(str((fast_power(int(x), my_secret)) % dhp))
