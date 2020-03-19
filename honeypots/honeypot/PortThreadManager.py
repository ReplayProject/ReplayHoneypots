# python3 PortThreadManager.py
import json
import sys
import os
from threading import Thread
import socket
from datetime import date
from requests import get
from Port import Port
import configparser
import time
import datetime
import argparse
from NmapParser import NmapParser
from Sniffer import Sniffer
from Databaser import Databaser

config = configparser.RawConfigParser()
configFilePath = r'../config/properties.cfg'
HONEY_IP = None
MGMT_IPs = None
DATABASE_OPTIONS = None

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
        self.portList = []
        self.ip = str(get('https://api.ipify.org').text)
        self.processList = []
        # where the db thread will be located
        self.databaserThread = None
        # where the sniffer thread will be located
        self.snifferThread = None
        self.delay = None
        self.whitelist = None
        self.keepRunning = True

        #Gets the info from config file initially
        self.getConfigData()

    """
    Gets config information; ran when PortThreadManager configuration changes      
    """
    def getConfigData(self):
        global config
        global HONEY_IP
        global MGMT_IPs
        global DATABASE_OPTIONS

        config.read(configFilePath)
        dataFile = config.get('Attributes', 'pcap_data_file')

        HONEY_IP = config.get('IPs', 'honeypotIP')
        MGMT_IPs = json.loads(config.get("IPs", "managementIPs"))

        DATABASE_OPTIONS = [
            config.get("Databaser", "port"),
            config.get("Databaser", "dbconf"),
            config.get("Databaser", "dbfolder"),
            config.get("Databaser", "bindaddress"),
            config.get("Databaser", "targetaddress")
        ]

        with open(dataFile, "r") as responseDataFile:
            responseData = json.load(responseDataFile)
        for port in portList:
            try:
                portData = responseData[str(port)]
            except:
                print("Couldn't find data for port " + str(port))
                continue
            self.portList.append(Port(port, portData))

        self.delay = config.get('Attributes', 'delay')
        self.whitelist = json.loads(config.get("Whitelist", "addresses"))

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
            responseThread = Thread(
                target=self.portResponse, args=[portObj, conn])
            responseThread.daemon = True
            responseThread.start()
            if not self.keepRunning:
                break
        conn.close()

    """
    Start a thread for each port in the config file
    """

    def deploy(self):
        #--- Databaser Thread ---#
        #If this is a refresh deploy, clear out old threads
        if (not self.databaserThread == None):
            self.databaserThread.stop()
        # Setup the DB
        self.databaserThread = Databaser(options=DATABASE_OPTIONS)
        self.databaserThread.daemon = True
        self.databaserThread.start()

        # Wait for the DB to be ready
        while not self.databaserThread.ready:
          pass

        #--- Sniffer Thread ---#
        if (self.databaserThread == None):
            #TODO: Switch config="testing" to "base" when in production
            self.snifferThread = Sniffer(config="testing", openPorts=self.portList, whitelist=self.whitelist,
                                         db_url=self.databaserThread.db_url, honeypotIP=HONEY_IP, managementIPs=MGMT_IPs)
            self.snifferThread.daemon = True
            self.snifferThread.start()
        else:
            self.snifferThread.configUpdate(openPorts=self.portList, whitelist=self.whitelist, db_url=self.databaserThread.db_url, honeypotIP=HONEY_IP, managementIPs=MGMT_IPs)

        #--- Open Sockets ---#
        #TODO: adjust sockets to respond to dybamic configuration
        for port in self.portList:
            portThread = Thread(target=self.portListener, args=[port])
            portThread.daemon = True
            portThread.start()
            self.processList.append(portThread)

        for thread in self.processList:
            thread.join()

        self.snifferThread.join()
        self.databaserThread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deploy the honeypot')
    parser.add_argument('-c', '--config', help='config file')
    parser.add_argument('-n', '--nmap', help='nmap file')
    args = parser.parse_args()

    portList = []
    if args.config:
        with open(args.config, "r") as configFile:
            portList = json.load(configFile)
    elif args.nmap:
        parser = NmapParser(args.nmap) 
        portList = parser.getPorts()
    else:
        print("Need to pass in an nmap file or a config file. Use -h for help.")
        exit()

    manager = PortThreadManager(portList)
    manager.deploy()

    #keep main thread alive
    while True:
        time.sleep(0.5)
