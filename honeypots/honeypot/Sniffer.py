"""
Uses Scapy library to examine all incoming traffic
"""

from scapy.all import sniff
from threading import Thread

class Sniffer(Thread):
    def __init__(self, config = "base"):
        #list of saved packets
        self.RECORD = []

        #Filtered lists of saved packets (TODO: make saving more comprehensive later)
        self.ICMP_RECORD = dict()
        self.TCP_RECORD = dict()
        self.UDP_RECORD = dict()

        print("Sniffing")
        if (config == "testing"):
            #this ignores the ssh spam you get when sending packets between two ssh terminals
            sniff(filter="ip and not (src port ssh or dst port ssh)", prn = self.save_packet)
        elif (config == "base"):
            sniff(filter="ip", prn = self.save_packet)

    def save_packet(self, packet):
        self.RECORD.append(packet)

        #TODO: make this work with layer 2, for now just skip filtering those packets
        if (packet.haslayer("IP") == False):
            return

        ipLayer = packet.getlayer("IP")

        #IP where this came from
        srcIP = ipLayer.src

        if (ipLayer.haslayer("ICMP")):
            if srcIP in self.ICMP_RECORD:
                self.ICMP_RECORD[srcIP].append(packet)
            else:
                self.ICMP_RECORD[srcIP] = [packet]
            return

        destPort = ipLayer.dport
        pair = (srcIP, destPort)

        if (ipLayer.haslayer("UDP")):
            if pair in self.UDP_RECORD:
                self.UDP_RECORD[pair].append(packet)
            else:
                self.UDP_RECORD[pair] = [packet]
        elif (ipLayer.haslayer("TCP")):
            if pair in self.TCP_RECORD:
                self.TCP_RECORD[pair].append(packet)
            else:
                self.TCP_RECORD[pair] = [packet]
