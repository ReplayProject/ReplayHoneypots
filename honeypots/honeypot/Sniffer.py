from LogEntry import LogEntry
from scapy.all import sniff
from threading import Thread
from Databaser import Databaser
from datetime import datetime
import requests
requests.adapters.DEFAULT_RETRIES = 0
"""
Uses Scapy library to examine all incoming traffic
"""


class Sniffer(Thread):
    """
    Constructor; takes a config keyword to see what mode to run it in
    'testing' ignores ssh spam you get
    """
    def __init__(self,
                 config="base",
                 openPorts=[],
                 whitelist=[],
                 portWhitelist=[],
                 honeypotIP=None,
                 managementIPs=None,
                 databaser=None):
        Thread.__init__(self)

        self.config = config
        self.openPorts = openPorts
        self.whitelist = whitelist
        self.honeypotIP = honeypotIP
        self.portWhitelist = portWhitelist
        self.managementIPs = managementIPs
        self.db = databaser

        self.running = True
        #This number doesn't matter, this is used to stop the thread if a reset is necessary
        self.count = 1
        self.portScanTimeout = None

        #set used for testing convenience
        self.RECORD = dict()
        self.currentHash = hash(self.config)
        self.currentHash += hash(tuple(self.openPorts))
        self.currentHash += hash(tuple(self.whitelist))
        self.currentHash += hash(honeypotIP)
        self.currentHash += hash(tuple(managementIPs))

    """
    Runs the thread, begins sniffing
    """

    def run(self):
        print("Sniffing")

        #This loop, along with self.count allow us to effectively update values on the fly
        while self.running:
            #building the base filter
            fltr = "not src host {} ".format(self.honeypotIP)
            #adding a variable number of management ips
            for ip in self.managementIPs:
                fltr += "and not host {} ".format(ip)
            for port in self.portWhitelist:
                fltr += "and not dst port {} ".format(port)

            if (self.config == "testing"):
                fltr = fltr + " and not (src port ssh or dst port ssh)"
                # this ignores the ssh spam you get when sending packets between two ssh terminals
                sniff(filter=fltr, prn=self.save_packet, count=self.count)
            elif (self.config == "base"):
                sniff(filter=fltr, prn=self.save_packet, count=self.count)
            elif (self.config == "onlyUDP"):
                fltr = "udp"
                sniff(filter=fltr,
                      prn=self.save_packet,
                      count=self.count,
                      iface="lo")

    """
    Updates configuration options during runtime
    """

    def configUpdate(self,
                     openPorts=[],
                     whitelist=[],
                     portWhitelist = [],
                     honeypotIP=None,
                     managementIPs=None):
        self.openPorts = openPorts
        self.whitelist = whitelist
        self.portWhitelist = portWhitelist
        self.honeypotIP = honeypotIP
        self.managementIPs = managementIPs

        self.currentHash = hash(self.config)
        self.currentHash += hash(tuple(self.openPorts))
        self.currentHash += hash(tuple(self.whitelist))
        self.currentHash += hash(honeypotIP)
        self.currentHash += hash(tuple(managementIPs))
    """
    Function for recording a packet during sniff runtime
    packet = the packet passed through the sniff function
    """

    def save_packet(self, packet):
        # TODO: make this work with layer 2, for now just skip filtering those packets
        if (packet.haslayer("IP") == False):
            return

        currentTime = int(datetime.now().timestamp())
        if (self.portScanTimeout is None):
            self.portScanTimeout = int(datetime.now().timestamp())

        #how to tell if we need to reset our port scan record
        if (currentTime > self.portScanTimeout + 60):
            self.portScanTimeout = currentTime
            self.RECORD = dict()


        sourceMAC = packet.src
        destMAC = packet.dst

        ipLayer = packet.getlayer("IP")

        # IP where this came from
        srcIP = ipLayer.src
        dstIP = ipLayer.dst

        #TODO: add other types of packets
        if (not ipLayer.haslayer("TCP") and not ipLayer.haslayer("UDP")):
            return

        destPort = ipLayer.dport
        srcPort = ipLayer.sport
        pair = (srcIP, destPort)

        if srcIP not in self.whitelist:
            trafficType = "TCP" if ipLayer.haslayer("TCP") else "UDP"
            log = LogEntry(srcPort, srcIP, sourceMAC, destPort, dstIP, destMAC,
                           trafficType, destPort in self.openPorts, self.db.hostname)

            self.db.save(log.json())

            #storing mini-logs for testing
            if (self.config == "testing"):
                if (not srcIP in self.RECORD.keys()):
                    self.RECORD[srcIP] = [log]
                else:
                    self.RECORD[srcIP].append(log)
