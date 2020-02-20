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
    def __init__(self, config="base",  count=0, openPorts=[], whitelist=[], db_url=None, honeypotIP=None, managementIPs=None):
        Thread.__init__(self)
        # list of saved packets
        self.RECORD = []
        self.config = config
        self.count = count
        self.openPorts = openPorts
        self.whitelist = whitelist
        self.db_url = db_url
        self.honeypotIP = honeypotIP
        self.managementIPs = managementIPs

        # Filtered lists of saved packets (TODO: make saving more comprehensive later)
        self.ICMP_RECORD = dict()
        self.TCP_RECORD = dict()
        self.UDP_RECORD = dict()
    """
    Runs the thread, begins sniffing
    """

    def run(self):
        print("Sniffing")
        fltr = "not src host {0} and not host {1} and not host {2}".format(self.honeypotIP, self.managementIPs[1], self.managementIPs[0])
        if (self.config == "testing"):
            fltr = fltr + " and not (src port ssh or dst port ssh)"
            # this ignores the ssh spam you get when sending packets between two ssh terminals
            sniff(filter=fltr, prn=self.save_packet, count=self.count)
        elif (self.config == "base"):
            sniff(filter=fltr, prn=self.save_packet, count=self.count)

    """
    Function for recording a packet during sniff runtime
    packet = the packet passed through the sniff function
    """

    def save_packet(self, packet):
        self.RECORD.append(packet)

        # TODO: make this work with layer 2, for now just skip filtering those packets
        if (packet.haslayer("IP") == False):
            return

        ipLayer = packet.getlayer("IP")

        # IP where this came from
        srcIP = ipLayer.src
        dstIP = ipLayer.dst

        if (ipLayer.haslayer("ICMP")):
            # print("ICMP packet sent from IP {0}".format(srcIP))
            if srcIP in self.ICMP_RECORD:
                self.ICMP_RECORD[srcIP].append(packet)
            else:
                self.ICMP_RECORD[srcIP] = [packet]
            return

        destPort = ipLayer.dport
        srcPort = ipLayer.sport
        pair = (srcIP, destPort)

        if (ipLayer.haslayer("UDP")):
            # print("UDP packet sent from IP {0} to port {1}".format(srcIP, destPort))
            if pair in self.UDP_RECORD:
                self.UDP_RECORD[pair].append(packet)
            else:
                self.UDP_RECORD[pair] = [packet]
        elif (ipLayer.haslayer("TCP")):
            # print("TCP packet sent from IP {0} to port {1}".format(srcIP, destPort))
            if pair in self.TCP_RECORD:
                self.TCP_RECORD[pair].append(packet)
            else:
                self.TCP_RECORD[pair] = [packet]

        if srcIP not in self.whitelist:
            # TODO: make this more sensible
            trafficType = "TCP" if ipLayer.haslayer("TCP") else "UDP"
            # TODO: IS PORT OPEN NOT WORKING
            log = LogEntry(srcPort, srcIP, destPort, dstIP,
                           trafficType, destPort in self.openPorts)
            self.post(log)

    def post(self, payload):
        header = {"content-type": "application/json"}
        try:
            r = post(url=self.db_url, data=payload.json(),
                     headers=header, verify=False)
            log_id = r.json()["id"]
            print("Log created: %s" % log_id)
        except Exception:
            print("DB-Failed: ", payload.json())
