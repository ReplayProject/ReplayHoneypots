from LogEntry import LogEntry
from requests import post
from scapy.all import sniff
from threading import Thread
from datetime import datetime
from Notification import Notification
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

    def __init__(self, config="base",  count=0, openPorts=[], whitelist=[], db_url=None, honeypotIP=None, managementIPs=None):
        Thread.__init__(self)

        self.config = config
        self.count = count
        self.openPorts = openPorts
        self.whitelist = whitelist
        self.db_url = db_url
        self.honeypotIP = honeypotIP
        self.managementIPs = managementIPs

        #Used to keep track of potential port scans
        self.RECORD = None
        #used to tell save_packet when to clear RECORD
        self.portScanTimeout = None
    """
    Runs the thread, begins sniffing
    """

    def run(self):
        print("Sniffing")

        #building the base filter
        fltr = "not src host {} ".format(self.honeypotIP)
        #adding a variable number of management ips
        for ip in self.managementIPs:
            fltr += "and not host {} ".format(ip)

        if (self.config == "testing"):
            fltr = fltr + " and not (src port ssh or dst port ssh)"
            # this ignores the ssh spam you get when sending packets between two ssh terminals
            sniff(filter=fltr, prn=self.save_packet, count=self.count)
        elif (self.config == "base"):
            sniff(filter=fltr, prn=self.save_packet, count=self.count)
        elif (self.config == "onlyUDP"):
            fltr = "udp and host {}".format(self.honeypotIP)
            sniff(filter=fltr, prn=self.save_packet, count=self.count)

    """
    Function for recording a packet during sniff runtime
    packet = the packet passed through the sniff function
    """

    def save_packet(self, packet):
        # TODO: make this work with layer 2, for now just skip filtering those packets
        if (packet.haslayer("IP") == False):
            return
        
        currentTime = int(datetime.now().timestamp())
        if (self.RECORD == None and self.portScanTimeout == None):
            self.RECORD = dict()
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
            # TODO: make this more sensible
            trafficType = "TCP" if ipLayer.haslayer("TCP") else "UDP"
            # TODO: IS PORT OPEN NOT WORKING
            log = LogEntry(srcPort, srcIP, sourceMAC, destPort, dstIP, destMAC,
                           trafficType, destPort in self.openPorts)
            self.post(log)
            
            #Port scan detection
            if (trafficType == "TCP"):
                if (srcIP in self.RECORD.keys()):
                    if (len(self.RECORD[srcIP]) > 10000):
                        msg = "Port scan detected from {}".format(srcIP)
                        self.post(Notification(variant = "alert", message = msg))
                    
                    if (destPort not in self.RECORD[srcIP]):
                        self.RECORD[srcIP].append(destPort)
                else:
                    self.RECORD[srcIP] = [destPort]

    def post(self, payload):
        header = {"content-type": "application/json"}
        try:
            r = post(url=self.db_url, data=payload.json(),
                     headers=header, verify=False)
            log_id = r.json()["id"]
            #differentiates between different object types
            if (payload.__name__ == "LogEntry"):
                print("Log created: %s" % log_id)
            elif (payload.__name__ == "Notification"):
                print("Notification created: %s" % log_id)
        except Exception:
            print("DB-Inactive: ", payload.json())
