# python3 PortThreadManager.py
import json
import sys
import os

import trio
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
from UDPPortListener import UDPPortListener
from ConfigTunnel import ConfigTunnel
from Databaser import Databaser
from Alert import Alert

# default location that PortThreadManager will look for config options

configpath = os.getenv('HONEY_CFG')  # will usually be '/properties.cfg'
CONFIG_FILE_PATH = configpath if (
    configpath and configpath.strip() != "") else r'../../config/honeypot.cfg'
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
        #delay specified by config file
        self.delay = None
        #whitelist of ports
        self.portWhitelist = None
        #whitelist of IPs
        self.whitelist = None
        #used to tell it to quit
        self.keepRunning = True
        #list containing socket responses
        self.responseData = None
        self.configFilePath = None
        #database interface object
        self.db = Databaser()

    """
    Gets config information; ran when PortThreadManager configuration changes
    """

    def getConfigData(self):
        config = configparser.RawConfigParser()

        config.read(self.configFilePath)

        #A bunch of config options
        self.HONEY_IP = config.get('IPs', 'honeypotIP')
        self.MGMT_IPs = json.loads(config.get("IPs", "managementIPs"))

        self.delay = config.get('Attributes', 'delay')
        self.whitelist = json.loads(config.get("Whitelist", "addresses"))
        self.portWhitelist = json.loads(
            config.get("Whitelist", "whitelistedPorts"))

        #Gets a separate file
        dataFile = config.get('Attributes', 'pcap_data_file')
        #Separate file contains socket response data
        with open(dataFile, "r") as responseDataFile:
            self.responseData = json.load(responseDataFile)

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
                 updateOpenPorts=False,
                 user=""):
        self.configFilePath = propertiesFile

        # Gets the info from config file initially
        self.getConfigData()

        #Return code
        retCode = 0
        # Convience reference
        replayPorts = self.responseData.keys()

        #--- Start Sniffer Thread ---#
        if (self.snifferThread == None):
            # TODO: Switch config="testing" to "base" when in production
            self.snifferThread = Sniffer(config="base",
                                         openPorts=list(replayPorts),
                                         whitelist=self.whitelist,
                                         portWhitelist=self.portWhitelist,
                                         honeypotIP=self.HONEY_IP,
                                         managementIPs=self.MGMT_IPs,
                                         databaser=self.db)
            self.snifferThread.daemon = True
            self.snifferThread.start()
        elif (updateSniffer == True):
            oldHash = self.snifferThread.currentHash

            self.snifferThread.configUpdate(openPorts=list(replayPorts),
                                            whitelist=self.whitelist,
                                            portWhitelist=self.portWhitelist,
                                            honeypotIP=self.HONEY_IP,
                                            managementIPs=self.MGMT_IPs)
            if (not self.snifferThread.currentHash == oldHash):
                retCode = 1

        #--- Open Sockets - Disabled due to new TRIO API---#
        # On initial run
        # if (len(self.processList) == 0):
        #     for port in replayPorts:
        #         portThread = PortListener(port, self.responseData[port]["TCP"],
        #                                   self.delay)
        #         portThread.daemon = True
        #         portThread.start()
        #         self.processList[port] = portThread

        # # Updating to new set of ports
        # elif (updateOpenPorts == True):
        #     #this value keeps track of if we've made changes
        #     portsAltered = False

        #     updatedPorts = list(tcp_sockets)
        #     updatedPorts.sort()
        #     currentPorts = list(self.processList.keys())
        #     currentPorts.sort()

        #     #we'll change things if these don't match
        #     if (not updatedPorts == currentPorts):
        #         portsAltered = True

        #     for p in currentPorts:
        #         if (not p in updatedPorts):
        #             self.processList[p].isRunning = False
        #             del self.processList[p]
        #         elif (not self.processList[p].response == self.responseData[p]["TCP"]
        #               ):
        #             #check if we need to alter response -- just change everything, might not matter
        #             self.processList[p].response = self.responseData[p]["TCP"]
        #             portsAltered = True

        #     for p in updatedPorts:
        #         if (not p in currentPorts):
        #             portThread = PortListener(p, self.responseData[p]["TCP"],
        #                                       self.delay)
        #             portThread.daemon = True
        #             portThread.start()
        #             self.processList[p] = portThread

        #     if (portsAltered):
        #         retCode += 2

        #--- Open async UDP & TCP Sockets ---#
        udp_sockets =  list(filter(lambda x: "UDP" in self.responseData[x].keys(), replayPorts))
        tcp_sockets =  list(filter(lambda x: "TCP" in self.responseData[x].keys(), replayPorts))

        async def replay_server(listener_class, sockets, config_path):
          async with trio.open_nursery() as nursery:
            for port in sockets:
              listener = listener_class(port, self.responseData[port][config_path], self.delay, nursery)
              nursery.start_soon(listener.handler)

        async def nursery_bag():
          async with trio.open_nursery() as nursery:
              nursery.start_soon(replay_server, UDPPortListener, udp_sockets, "UDP")
              nursery.start_soon(replay_server, PortListener, tcp_sockets, "TCP")

        trio.run(nursery_bag)

        #return the code here; 0 means no changes, 1 means only sniffer changed, 2 means only TCP ports were changed, 3 means both were changed
        if (retCode == 1):
            self.db.alert(
                Alert(variant="admin",
                      message="Sniffer updated during runtime by " + user,
                      hostname=self.db.hostname).json())
        elif (retCode == 2):
            self.db.alert(
                Alert(variant="admin",
                      message="TCP sockets updated during runtime by " + user,
                      hostname=self.db.hostname).json())
        elif (retCode == 3):
            self.db.alert(
                Alert(
                    variant="admin",
                    message="TCP sockets and Sniffer updated during runtime by "
                    + user,
                    hostname=self.db.hostname).json())
        elif (retCode == 0):
            self.db.alert(
                Alert(
                    variant="admin",
                    message="Attempted configuration change during runtime by "
                    + user,
                    hostname=self.db.hostname).json())
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
    #initial creation alert
    manager.db.alert(
        Alert(variant="meta",
              message="Honeypot startup.",
              references=[],
              hostname=manager.db.hostname).json())

    def reconfigure(args):
        manager.activate(updateSniffer='sniff' in args,
                         updateOpenPorts='ports' in args,
                         user=args[-1] if 'user' in args else 'blank_user')
        print("Reconfiguring Replay Manager: ", args)

    # ConfigTunnel connection allows for live configuration options
    stunnel = ConfigTunnel('server')
    stunnel.setHandler("reconfigure", reconfigure)
    stunnel.daemon = True
    stunnel.start()

    manager.activate(user="system")

    # Old keep main thread alive
    # while True:
    #     time.sleep(5)
