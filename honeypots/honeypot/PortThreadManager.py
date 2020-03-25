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
from PortListener import PortListener

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
        self.processList = dict()
        # where the db thread will be located
        self.databaserThread = None
        # where the sniffer thread will be located
        self.snifferThread = None
        self.delay = None
        self.whitelist = None
        self.keepRunning = True
        self.responseData = None

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
            self.responseData = json.load(responseDataFile)

        self.delay = config.get('Attributes', 'delay')
        self.whitelist = json.loads(config.get("Whitelist", "addresses"))

    """
    Start a thread for each port in the config file, connects to the database, runs sniffer class
    """

    def deploy(self, updateSniffer = False, updateOpenPorts = False):
        #TODO: add three optional parameters to tell which part is getting updated

        #Gets the info from config file initially
        self.getConfigData()

        #--- Databaser Thread (does not get updated on dynamic config change)---#
        # Setup the DB
        if (self.databaserThread == None):
            self.databaserThread = Databaser(options=DATABASE_OPTIONS, replication=True)
            self.databaserThread.daemon = True
            self.databaserThread.start()

        # Wait for the DB to be ready
        while not self.databaserThread.ready:
          pass

        #--- Sniffer Thread ---#
        if (self.snifferThread == None):
            #TODO: Switch config="testing" to "base" when in production
            self.snifferThread = Sniffer(config="testing", openPorts=self.portList, whitelist=self.whitelist,
                                         db_url=self.databaserThread.db_url, honeypotIP=HONEY_IP, managementIPs=MGMT_IPs)
            self.snifferThread.daemon = True
            self.snifferThread.start()
        elif (updateSniffer == True):
            self.snifferThread.configUpdate(openPorts=self.portList, whitelist=self.whitelist, db_url=self.databaserThread.db_url, honeypotIP=HONEY_IP, managementIPs=MGMT_IPs)

        #--- Open Sockets ---#
        #On initial run
        if (len(portList) == 0):
            for port in self.responseData.keys():
                portThread = PortListener(port, self.responseData[port], self.delay)
                portThread.daemon = True
                portThread.start()
                self.processList[port] = portThread
            # for thread in self.processList.values():
            #     thread.join()
        #Updating to new set of ports
        elif (updateOpenPorts == True):
            updatedPorts = self.responseData.keys()
            currentPorts = map(lambda x: x.port(), self.processList.keys())

            for p in currentPorts:
                if (not p in updatedPorts):
                    self.processList[p].isRunning = False
            for p in updatedPorts:
                if (not p in currentPorts):
                    portThread = PortListener(port, self.responseData[port], self.delay)
                    portThread.daemon = True
                    portThread.start()
                    self.processList[port] = portThread


        # self.snifferThread.join()
        # self.databaserThread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deploy the honeypot')
    parser.add_argument('-n', '--nmap', help='nmap file')
    args = parser.parse_args()

    portList = []
    if args.nmap:
        parser = NmapParser(args.nmap)
        portList = parser.getPorts()

    manager = PortThreadManager(portList)
    manager.deploy()

    #keep main thread alive
    while True:
        time.sleep(0.5)
