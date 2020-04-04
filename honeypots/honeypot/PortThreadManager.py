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
from PortListener import PortListener
from ConfigTunnel import ConfigTunnel

# default location that PortThreadManager will look for config options
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

        with open(dataFile, "r") as responseDataFile:
            self.responseData = json.load(responseDataFile)

        self.delay = config.get('Attributes', 'delay')
        self.whitelist = json.loads(config.get("Whitelist", "addresses"))

    """
    Start a thread for each port in the config file, connects to the database, runs sniffer class

    Returns: 0 if no changes
             1 if only Sniffer changed
             2 if only sockets changed
             3 if both changed
    """

    def activate(self,
                 propertiesFile=CONFIG_FILE_PATH,
                 updateSniffer=False,
                 updateOpenPorts=False):
        self.configFilePath = propertiesFile

        # Gets the info from config file initially
        self.getConfigData()

        #Return code
        retCode = 0

        #--- Sniffer Thread ---#
        if (self.snifferThread == None):
            # TODO: Switch config="testing" to "base" when in production
            self.snifferThread = Sniffer(config="testing",
                                         openPorts=list(
                                             self.responseData.keys()),
                                         whitelist=self.whitelist,
                                         honeypotIP=self.HONEY_IP,
                                         managementIPs=self.MGMT_IPs)
            self.snifferThread.daemon = True
            self.snifferThread.start()
        elif (updateSniffer == True):
            oldHash = self.snifferThread.currentHash

            self.snifferThread.configUpdate(openPorts=list(
                self.responseData.keys()),
                                            whitelist=self.whitelist,
                                            honeypotIP=self.HONEY_IP,
                                            managementIPs=self.MGMT_IPs)
            if (not self.snifferThread.currentHash == oldHash):
                retCode = 1

        #--- Open Sockets ---#
        # On initial run
        if (len(self.processList) == 0):
            for port in self.responseData.keys():
                portThread = PortListener(port, self.responseData[port],
                                          self.delay)
                portThread.daemon = True
                portThread.start()
                self.processList[port] = portThread


        # Updating to new set of ports
        elif (updateOpenPorts == True):
            #this value keeps track of if we've made changes
            portsAltered = False

            updatedPorts = list(self.responseData.keys())
            updatedPorts.sort()
            currentPorts = list(self.processList.keys())
            currentPorts.sort()

            #we'll change things if these don't match
            if (not updatedPorts == currentPorts):
                portsAltered = True
                print("yikes")

            for p in currentPorts:
                if (not p in updatedPorts):
                    self.processList[p].isRunning = False
                    del self.processList[p]
                elif (not self.processList[p].response == self.responseData[p]):
                    #check if we need to alter response -- just change everything, might not matter
                    self.processList[p].response = self.responseData[p]
                    portsAltered = True
                    
            for p in updatedPorts:
                if (not p in currentPorts):
                    portThread = PortListener(p, self.responseData[p],
                                              self.delay)
                    portThread.daemon = True
                    portThread.start()
                    self.processList[p] = portThread

            if (portsAltered):
                retCode += 2

        #return the code here; 0 means no changes, 1 means only sniffer changed, 2 means only TCP ports were changed, 3 means both were changed
        return retCode

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Deploy the honeypot')
    parser.add_argument('-n', '--nmap', help='nmap file')
    args = parser.parse_args()

    portList = []
    if args.nmap:
        parser = NmapParser(args.nmap)
        portList = parser.getPorts()

    manager = PortThreadManager()
    manager.activate()

    def reconfigure(args):
        manager.activate(updateSniffer='sniff' in args,
                         updateOpenPorts='ports' in args)
        print("Reconfiguring Replay Manager: ", args)

    # Lets get cracking
    stunnel = ConfigTunnel('server')
    stunnel.setHandler("reconfigure", reconfigure)
    stunnel.start()

    print("Listening")

    # keep main thread alive
    while True:
        time.sleep(5)
