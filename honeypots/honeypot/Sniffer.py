"""
Uses Scapy library to examine all incoming traffic
"""

from scapy.all import sniff

#list of saved packets
RECORD = []

#Filtered lists of saved packets (TODO: make saving more comprehensive later)
ICMP_RECORD = dict()
TCP_RECORD = dict()
UDP_RECORD = dict()

def save_packet(packet):
    RECORD.append(packet)

    #TODO: make this work with layer 2, for now just skip filtering those packets
    if (packet.haslayer("IP") == False):
        return

    ipLayer = packet.getlayer("IP")

    #IP where this came from
    srcIP = ipLayer.src

    if (ipLayer.haslayer("ICMP")):
        if srcIP in ICMP_RECORD:
            ICMP_RECORD[srcIP].append(packet)
        else:
            ICMP_RECORD[srcIP] = [packet]
        return

    destPort = ipLayer.dport
    pair = (srcIP, destPort)

    if (ipLayer.haslayer("UDP")):
        if pair in UDP_RECORD:
            UDP_RECORD[pair].append(packet)
        else:
            UDP_RECORD[pair] = [packet]
    elif (ipLayer.haslayer("TCP")):
        if pair in TCP_RECORD:
            TCP_RECORD[pair].append(packet)
        else:
            TCP_RECORD[pair] = [packet]

sniff(filter="ip", prn = save_packet)