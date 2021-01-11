"""
Uses Scapy library to examine all incoming traffic
"""
import socket
import binascii
from netifaces import interfaces, ifaddresses, AF_INET
from datetime import datetime

import requests
from Alert import Alert
from LogEntry import LogEntry
from scapy.all import AsyncSniffer, TCP, IP, send, NoPayload, Raw, raw, bytes_hex
from scapy.error import Scapy_Exception
from difflib import SequenceMatcher

requests.adapters.DEFAULT_RETRIES = 0
SIMILARITY_SCORE_THRESHOLD = 0.9

class Sniffer:
    """
    Constructs the sniffer object; notably takes a config
    keyword to control what mode to run in
    'testing' ignores ssh traffic
    """

    def __init__(
        self, config, mode="base", databaser=None, send_channel=None
    ):

        self.config = config
        self.mode = mode
        self.db = databaser
        self.channel = send_channel
        # used to detect port scans
        self.portScanTimeout = None
        # also used to detect port scans
        self.PS_RECORD = dict()
        # set used for testing convenience
        self.RECORD = dict()
        # Hash used to tell if we properly updated Sniffer class;
        # there is probably a better way of making this hash
        self.currentHash = hash(self.config)
        self.index_map = {}
        for port in self.config.open_ports:
            self.index_map[port] = {}

    def start(self):
        """
        Runs the thread, begins sniffing with given config
        """
        print("Starting async sniffer")
        localIPList = []
        fltr = ""
        # Get a list of all IP addresses assigned to local NICs
        # and ensure that this packet is not from any of them
        for interface in interfaces():
            for link in ifaddresses(interface).get(AF_INET, ()):
                if fltr != "":
                    fltr += "and "
                localIPList.append(link["addr"])
                fltr += "not src host {} ".format(link["addr"])

        # Not to or from the database IP
        if self.db is not None:
            if fltr != "":
                fltr += "and "
            fltr += "not src host {} and not dst host {} ".format(socket.gethostbyname(self.db.db_ip), socket.gethostbyname(self.db.db_ip))

        # Honor the port whitelist for incoming packets
        for port in self.config.whitelist_ports:
            if fltr != "":
                fltr += "and "
            fltr += "not dst port {} ".format(port)
        # Honor the ip whitelist for both direction
        for ip in self.config.whitelist_addrs:
            if ip not in localIPList: # avoid blocking all incoming packets in the case that our own IP is entered into whitelist
                if fltr != "":
                    fltr += "and "
                fltr += "not src host {} and not dst host {} ".format(ip, ip)

        print("Filter", fltr)

        # here's where the packet detection starts

        if self.mode == "testing":
            # this ignores the ssh spam you get when sending
            # packets between two ssh terminals
            if fltr != "":
                fltr += "and "
            fltr = fltr + "not (src port ssh or dst port ssh)"
        elif self.mode == "base":
            # this above filter ignores the ssh spam you get when sending packets
            #  between two ssh terminals - TODO: TAKE THIS OUT IN PROD
            if fltr != "":
                fltr += "and "
            fltr = fltr + "not (src port ssh or dst port ssh)"
        elif self.mode == "onlyUDP":
            # this last config option is used in testing
            fltr = "udp"

        self.sniffer = AsyncSniffer(filter=fltr, prn=self.save_packet, store=False)
        if not self.sniffer:
            raise Exception("Async sniffer not initialized")

        self.sniffer.start()

    def stop(self):
        """
        Attempts to stop the async sniffer
        """
        if not self.sniffer or not self.sniffer.running:
            raise Exception("Async sniffer not initialized")
        self.sniffer.stop()

    def configUpdate(self, conf):
        """
        Updates configuration options during runtime
        """
        print("Async sniffer updated")
        self.running = False
        self.config = conf
        # updates hash
        self.currentHash = hash(self.config)

        # restart's Sniffer
        try:
            self.stop()
        except Scapy_Exception as ex:
            print("Sniffer did not finish setting up before teardown: ", str(ex))
        self.start()

    async def send_msg(self, destPort):
        await self.channel.send("{ port: " + str(destPort) + ", packet: {} }")

    def save_packet(self, packet):
        """
        Function for recording a packet during sniff runtime
        packet = the packet passed through the sniff function
        """
        # TODO: make this work with layer 2, for now just skip filtering those packets
        if not packet.haslayer("IP"):
            return

        # timestamp used for port scan detection
        currentTime = int(datetime.now().timestamp())
        if self.portScanTimeout is None:
            self.portScanTimeout = currentTime

        # how to tell if we need to reset our port scan record
        if currentTime > self.portScanTimeout + self.config.portscan_window:
            print("resetting timeout time")
            self.portScanTimeout = currentTime
            self.PS_RECORD = dict()

        # A bunch of packet data, collected to be stored
        sourceMAC = packet.src
        destMAC = packet.dst
        ipLayer = packet.getlayer("IP")
        # IP where this came from
        srcIP = ipLayer.src
        dstIP = ipLayer.dst
        destPort = ipLayer.dport if hasattr(ipLayer, "dport") else None
        srcPort = ipLayer.sport if hasattr(ipLayer, "sport") else None

        if (
            not ipLayer.haslayer("TCP")
            and not ipLayer.haslayer("UDP")
            and not ipLayer.haslayer("ICMP")
        ):
            return

        # Testing config - does not utilize a database
        # isTest = self.config == "onlyUDP" or self.config == "testing"

        trafficType = (
            "TCP"
            if ipLayer.haslayer("TCP")
            else "UDP"
            if ipLayer.haslayer("UDP")
            else "ICMP"
            if ipLayer.haslayer("ICMP")
            else "Other"
        )

        # Log Entry object we're saving
        log = LogEntry(
            srcPort,
            srcIP,
            sourceMAC,
            destPort,
            dstIP,
            destMAC,
            trafficType,
            ipLayer.len,
            destPort in self.config.open_ports,
        )

        # self.RECORD is where we save logs for easy testing
        if srcIP in self.RECORD.keys():
            self.RECORD[srcIP].append(log)
        else:
            self.RECORD[srcIP] = [log]

        # saving the database ID in case of port scan detection
        if self.mode == "base" and self.db is not None:
            dbID = self.db.saveLogObject(log)
        else:
            return

        # self.PS_RECORD is a separate dictionary used for port scan detection
        if srcIP not in self.PS_RECORD.keys():
            self.PS_RECORD[srcIP] = dict()
            self.PS_RECORD[srcIP][log.destPortNumber] = dbID
        else:
            self.PS_RECORD[srcIP][log.destPortNumber] = dbID

            # Sending out the port scan alert
            if len(self.PS_RECORD[srcIP]) > self.config.portscan_threshold:
                if self.db is not None:
                    self.db.saveAlertObject(
                        Alert(
                            variant="alert",
                            message="Port scan detected from IP {}".format(srcIP),
                            references=list(self.PS_RECORD[srcIP].values()),
                        )
                    )
                self.PS_RECORD[srcIP] = dict()