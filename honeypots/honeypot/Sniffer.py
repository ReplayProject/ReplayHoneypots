from LogEntry import LogEntry
from requests import post
from scapy.all import sniff
from threading import Thread
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

    def __init__(self, config="base", openPorts=[], whitelist=[], db_url=None, honeypotIP=None, managementIPs=None):
        Thread.__init__(self)

        self.config = config
        self.openPorts = openPorts
        self.whitelist = whitelist
        self.db_url = db_url
        self.honeypotIP = honeypotIP
        self.managementIPs = managementIPs

        self.running = True
        #This number doesn't matter, this is used to stop the thread if a reset is necessary
        self.count = 1

        #set used for testing convenience
        self.RECORD = dict()
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

            if (self.config == "testing"):
                fltr = fltr + " and not (src port ssh or dst port ssh)"
                # this ignores the ssh spam you get when sending packets between two ssh terminals
                sniff(filter=fltr, prn=self.save_packet, count=self.count)
            elif (self.config == "base"):
                sniff(filter=fltr, prn=self.save_packet, count=self.count)
            elif (self.config == "onlyUDP"):
                fltr = "udp"
                sniff(filter=fltr, prn=self.save_packet, count=self.count, iface="lo")

    """
    Updates configuration options during runtime
    """
    def configUpdate(self, openPorts=[], whitelist=[], db_url=None, honeypotIP=None, managementIPs=None):
        self.openPorts = openPorts
        self.whitelist = whitelist
        self.db_url = db_url
        self.honeypotIP = honeypotIP
        self.managementIPs = managementIPs

    """
    Function for recording a packet during sniff runtime
    packet = the packet passed through the sniff function
    """

    def save_packet(self, packet):
        print(packet.summary())

        # TODO: make this work with layer 2, for now just skip filtering those packets
        if (packet.haslayer("IP") == False):
            return

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

            #storing UDP mini-logs for testing
            if (self.config == "testing"):
                if (not srcIP in self.RECORD.keys()):
                    self.RECORD[srcIP] = [log]
                else:
                    self.RECORD[srcIP].append(log)

    def post(self, payload):
        header = {"content-type": "application/json"}
        try:
            r = post(url=self.db_url, data=payload.json(),
                     headers=header, verify=False)
            log_id = r.json()["id"]
            print("Log created: %s" % log_id)
        except Exception:
            print("DB-Inactive: ", payload.json())
