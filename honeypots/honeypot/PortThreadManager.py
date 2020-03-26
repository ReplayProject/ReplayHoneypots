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
from ConfigTunnel import ConfigTunnel

#default location that PortThreadManager will look for config options
CONFIG_FILE_PATH = r'../config/properties.cfg'

"""
Handles the port threads to run the honeypot
"""


class PortThreadManager:
    """
    Initialize the response data and port list

    Args:
        portList: a list of int port numbers
    """

    def __init__(self):
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
        self.configFilePath = None

    """
    Gets config information; ran when PortThreadManager configuration changes
    """
    def getConfigData(self):
        config = configparser.RawConfigParser()

        config.read(self.configFilePath)
        dataFile = config.get('Attributes', 'pcap_data_file')

        self.HONEY_IP = config.get('IPs', 'honeypotIP')
        self.MGMT_IPs = json.loads(config.get("IPs", "managementIPs"))

        self.DATABASE_OPTIONS = [
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

    def deploy(self, propertiesFile = CONFIG_FILE_PATH, updateSniffer = False, updateOpenPorts = False):
        self.configFilePath = propertiesFile

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
            self.snifferThread = Sniffer(config="testing", openPorts=list(self.responseData.keys()), whitelist=self.whitelist,
                                         db_url=self.databaserThread.db_url, honeypotIP=self.HONEY_IP, managementIPs=self.MGMT_IPs)
            self.snifferThread.daemon = True
            self.snifferThread.start()
        elif (updateSniffer == True):
            self.snifferThread.configUpdate(openPorts=list(self.responseData.keys()), whitelist=self.whitelist, db_url=self.databaserThread.db_url, honeypotIP=self.HONEY_IP, managementIPs=self.MGMT_IPs)

        #--- Open Sockets ---#
        #On initial run
        if (len(self.processList) == 0):
            for port in self.responseData.keys():
                portThread = PortListener(port, self.responseData[port], self.delay)
                portThread.daemon = True
                portThread.start()
                self.processList[port] = portThread
            # for thread in self.processList.values():
            #     thread.join()

        #Updating to new set of ports
        elif (updateOpenPorts == True):
            updatedPorts = list(self.responseData.keys())
            currentPorts = list(self.processList.keys())

            for p in currentPorts:
                if (not p in updatedPorts):
                    self.processList[p].isRunning = False
            for p in updatedPorts:
                if (not p in currentPorts):
                    portThread = PortListener(p, self.responseData[p], self.delay)
                    portThread.daemon = True
                    portThread.start()
                    self.processList[p] = portThread


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

    manager = PortThreadManager()
    # manager.deploy()
    def handle_test(args):
      print("YONK WE GOT A POKE SONNY: ", args)

    # Lets get cracking
    stunnel = ConfigTunnel('server')
    stunnel.setHandler("test", handle_test)
    stunnel.start()

    print("Listening")
    #keep main thread alive
    while True:
        time.sleep(5)
        # print("READY: ", stunnel.ready)
        print("redeploying")
        manager.deploy()
        