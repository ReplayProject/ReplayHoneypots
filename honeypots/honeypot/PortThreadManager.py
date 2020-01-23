# python3 PortThreadManager.py
import json
import sys
from threading import Thread
import socket
from datetime import date
from requests import get
from Port import Port
import configparser
import time
import datetime
from DataLog import DataLog
from LogEntry import LogEntry
import argparse
from NmapParser import NmapParser

config = configparser.RawConfigParser()
configFilePath = r'../config/properties.cfg'
config.read(configFilePath)
dataFile = config.get('Attributes', 'pcap_data_file')

"""
Handles the port threads to run the honeypot
"""
class PortThreadManager:
    """
    Initialize the response data and port list
    
    Args:
        portList: a list of int port numbers
    """
    def __init__(self, portList):
        with open(dataFile,"r") as responseDataFile:
            responseData = json.load(responseDataFile)
        self.portList = []
        for port in portList:
            try:
                portData = responseData[str(port)]
            except:
                print("Couldn't find data for port " + str(port))
                continue
            self.portList.append(Port(port, portData))
        self.ip = str(get('https://api.ipify.org').text)
        self.processList = []
        self.datalog = DataLog()
        self.delay = config.get('Attributes', 'delay')
        self.whitelist = json.loads(config.get("Whitelist", "addresses"))
        self.keepRunning = True
        
    """
    Send a response on a port
    
    Args:
      portObj: port object with communication info
      conn: connection object to communicate on
    """
    def portResponse(self, portObj, conn):
        byteData = bytes.fromhex(portObj.response())
        time.sleep(float(self.delay))
        try:
            conn.send(byteData)
        except:
            print("Connection reset on port " + str(portObj.port))

    """
    Listen and respond on the given port
    
    Args:
      portObj: port object with communication info
    """
    def portListener(self, portObj):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("", portObj.port))
        sock.listen(1)
        while True:
            print("Listening on port " + str(portObj.port))
            conn, addr = sock.accept()
            print(conn)
            print(addr)
            responseThread = Thread(target=self.portResponse, args=[portObj, conn])
            responseThread.daemon = True
            responseThread.start()
            if addr[0] not in self.whitelist:
              log = LogEntry(addr[1],addr[0], portObj.port, socket.gethostbyname(socket.gethostname()), datetime.datetime.now())
              self.datalog.logs.append(log)
              self.datalog.writeLogs('../logs/' + str(date.today()).replace('-', '') + '.txt')

            if not self.keepRunning:
                break
        conn.close()
    
    """
    Start a thread for each port in the config file
    """
    def deploy(self):
        for port in self.portList:
            portThread = Thread(target=self.portListener, args=[port])
            portThread.daemon = True
            portThread.start()
            self.processList.append(portThread)

        for thread in self.processList:
            thread.join()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deploy the honeypot')
    parser.add_argument('-c', '--config', help='config file')
    parser.add_argument('-n', '--nmap', help='nmap file')
    args = parser.parse_args()

    portList = []
    if args.config:
        with open(args.config,"r") as configFile:
            portList = json.load(configFile)
    elif args.nmap:
        parser = NmapParser(args.nmap)
        portList = parser.getPorts()
    else:
        print("Need to pass in an nmap file or a config file. Use -h for help.")
        exit()

    manager = PortThreadManager(portList)
    manager.deploy()
