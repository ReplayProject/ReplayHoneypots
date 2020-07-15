"""
Uses Scapy library to examine all incoming traffic
"""
from datetime import datetime

import requests
from Alert import Alert
from LogEntry import LogEntry
from scapy.all import AsyncSniffer
from scapy.error import Scapy_Exception

requests.adapters.DEFAULT_RETRIES = 0


class Sniffer:
    """
    Constructs the sniffer object; notably takes a config
    keyword to control what mode to run in
    'testing' ignores ssh traffic
    """

    def __init__(
        self,
        config="base",
        openPorts=None,
        whitelist=None,
        portWhitelist=None,
        honeypotIP=None,
        managementIPs=None,
        port_scan_window=None,
        port_scan_sensitivity=None,
        databaser=None,
    ):

        self.config = config
        self.openPorts = [] if openPorts is None else openPorts
        self.whitelist = [] if whitelist is None else whitelist
        self.honeypotIP = honeypotIP
        self.portWhitelist = [] if portWhitelist is None else portWhitelist
        self.managementIPs = managementIPs
        self.scan_window = port_scan_window
        self.scan_sensitivity = port_scan_sensitivity
        self.db = databaser
        # used to detect port scans
        self.portScanTimeout = None
        # also used to detect port scans
        self.PS_RECORD = dict()
        # set used for testing convenience
        self.RECORD = dict()
        # Hash used to tell if we properly updated Sniffer class;
        # there is probably a better way of making this hash
        self.currentHash = hash(self.config)
        self.currentHash += hash(tuple(self.openPorts))
        self.currentHash += hash(tuple(self.whitelist))
        self.currentHash += hash(honeypotIP)
        self.currentHash += hash(tuple(managementIPs))

    def start(self):
        """
        Runs the thread, begins sniffing with given config
        """
        print("Starting async sniffer")
        # building the base filter
        fltr = "not src host {} ".format(self.honeypotIP)
        # adding a variable number of management ips
        for ip in self.managementIPs:
            fltr += "and not host {} ".format(ip)
        # adding things from the port list
        for port in self.portWhitelist:
            fltr += "and not dst port {} ".format(port)

        # here's where the packet detection starts

        if self.config == "testing":
            # this ignores the ssh spam you get when sending
            # packets between two ssh terminals
            fltr = fltr + " and not (src port ssh or dst port ssh)"
        elif self.config == "base":
            # this above filter ignores the ssh spam you get when sending packets
            #  between two ssh terminals - TODO: TAKE THIS OUT IN PROD
            fltr = fltr + " and not (src port ssh or dst port ssh)"
        elif self.config == "onlyUDP":
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

    def configUpdate(
        self,
        openPorts=None,
        whitelist=None,
        portWhitelist=None,
        honeypotIP=None,
        managementIPs=None,
        port_scan_window=None,
        port_scan_sensitivity=None,
    ):
        """
        Updates configuration options during runtime
        """
        print("Async sniffer updated")
        self.running = False
        self.openPorts = [] if openPorts is None else openPorts
        self.whitelist = [] if whitelist is None else whitelist
        self.portWhitelist = [] if portWhitelist is None else portWhitelist
        self.honeypotIP = honeypotIP
        self.managementIPs = managementIPs
        self.scan_window = port_scan_window
        self.scan_sensitivity = port_scan_sensitivity

        # updates hash
        self.currentHash = hash(self.config)
        self.currentHash += hash(tuple(self.openPorts))
        self.currentHash += hash(tuple(self.whitelist))
        self.currentHash += hash(honeypotIP)
        self.currentHash += hash(tuple(managementIPs))
        self.currentHash += hash(tuple([self.scan_window, self.scan_sensitivity]))

        # restart's Sniffer
        try:
            self.stop()
        except Scapy_Exception as ex:
            print("Sniffer did not finish setting up before teardown: ", str(ex))
        self.start()

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
        if currentTime > self.portScanTimeout + self.scan_window:
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

        # Whitelist check
        if srcIP not in self.whitelist:
            # Testing config - does not utilize a database
            isTest = self.config == "onlyUDP" or self.config == "testing"
            dbHostname = self.db.hostname if not isTest else "N/A"

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
                destPort in self.openPorts,
                dbHostname,
                self.db.uuid if self.db else "",
            )

            # self.RECORD is where we save logs for easy testing
            if srcIP in self.RECORD.keys():
                self.RECORD[srcIP].append(log)
            else:
                self.RECORD[srcIP] = [log]

            # saving the database ID in case of port scan detection
            if self.config == "base":
                dbID = self.db.save(log.json())
            else:
                return

            # self.PS_RECORD is a separate dictionary used for port scan detection
            if srcIP not in self.PS_RECORD.keys():
                self.PS_RECORD[srcIP] = dict()
                self.PS_RECORD[srcIP][log.destPortNumber] = dbID
            else:
                self.PS_RECORD[srcIP][log.destPortNumber] = dbID

                # Sending out the port scan alert
                if len(self.PS_RECORD[srcIP]) > self.scan_sensitivity:
                    self.db.alert(
                        Alert(
                            variant="alert",
                            message="Port scan detected from IP {}".format(srcIP),
                            references=list(self.PS_RECORD[srcIP].values()),
                            hostname=self.db.hostname,
                            uuid=self.db.uuid if self.db else "",
                        ).json()
                    )
                    self.PS_RECORD[srcIP] = dict()
