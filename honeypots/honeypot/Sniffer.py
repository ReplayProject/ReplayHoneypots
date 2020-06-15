from LogEntry import LogEntry
from scapy.all import AsyncSniffer
from scapy.error import Scapy_Exception
from Databaser import Databaser
from datetime import datetime
from Alert import Alert
import requests
requests.adapters.DEFAULT_RETRIES = 0

"""
Uses Scapy library to examine all incoming traffic
"""


class Sniffer():
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

        self.config = config
        self.openPorts = openPorts
        self.whitelist = whitelist
        self.honeypotIP = honeypotIP
        self.portWhitelist = portWhitelist
        self.managementIPs = managementIPs
        self.db = databaser
        #used to detect port scans
        self.portScanTimeout = None
        #also used to detect port scans
        self.PS_RECORD = dict()
        #set used for testing convenience
        self.RECORD = dict()
        #Hash used to tell if we properly updated Sniffer class; probably a better way of making this hash
        self.currentHash = hash(self.config)
        self.currentHash += hash(tuple(self.openPorts))
        self.currentHash += hash(tuple(self.whitelist))
        self.currentHash += hash(honeypotIP)
        self.currentHash += hash(tuple(managementIPs))

    """
    Runs the thread, begins sniffing
    """

    def start(self):
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
            # this ignores the ssh spam you get when sending packets between two ssh terminals
            fltr = fltr + " and not (src port ssh or dst port ssh)"
        elif self.config == "base":
            # this above filter ignores the ssh spam you get when sending packets between two ssh terminals - TAKE THIS OUT IN PROD
            fltr = fltr + " and not (src port ssh or dst port ssh)"
        elif self.config == "onlyUDP":
            # this last config option is used in testing
            fltr = "udp"

        self.sniffer = AsyncSniffer(
            filter=fltr, prn=self.save_packet, store=False
        )

        if not self.sniffer:
          raise Exception("Async sniffer not initialized")

        self.sniffer.start()

    """
    Attempts to stop the async sniffer
    """

    def stop(self):
      if not self.sniffer or not self.sniffer.running:
          raise Exception("Async sniffer not initialized")
      self.sniffer.stop()

    """
    Updates configuration options during runtime
    """

    def configUpdate(self,
                     openPorts=[],
                     whitelist=[],
                     portWhitelist=[],
                     honeypotIP=None,
                     managementIPs=None):
        print("Async sniffer updated")
        self.running = False
        self.openPorts = openPorts
        self.whitelist = whitelist
        self.portWhitelist = portWhitelist
        self.honeypotIP = honeypotIP
        self.managementIPs = managementIPs

        #updates hash
        self.currentHash = hash(self.config)
        self.currentHash += hash(tuple(self.openPorts))
        self.currentHash += hash(tuple(self.whitelist))
        self.currentHash += hash(honeypotIP)
        self.currentHash += hash(tuple(managementIPs))

        #restart's Sniffer
        try:
          self.stop()
        except Scapy_Exception as ex:
          print("Sniffer did not finish setting up before teardown: ", str(ex))
        self.start()

    """
    Function for recording a packet during sniff runtime
    packet = the packet passed through the sniff function
    """

    def save_packet(self, packet):
        # TODO: make this work with layer 2, for now just skip filtering those packets
        if (packet.haslayer("IP") == False):
            return

        #timestamp used for port scan detection
        currentTime = int(datetime.now().timestamp())
        if (self.portScanTimeout is None):
            self.portScanTimeout = int(datetime.now().timestamp())

        #how to tell if we need to reset our port scan record
        if (currentTime > self.portScanTimeout + 60):
            self.portScanTimeout = currentTime
            self.PS_RECORD = dict()

        #A bunch of packet data, collected to be stored
        sourceMAC = packet.src
        destMAC = packet.dst
        ipLayer = packet.getlayer("IP")
        # IP where this came from
        srcIP = ipLayer.src
        dstIP = ipLayer.dst
        destPort = ipLayer.dport
        srcPort = ipLayer.sport
        pair = (srcIP, destPort)

        if (not ipLayer.haslayer("TCP") and not ipLayer.haslayer("UDP") and not ipLayer.haslayer("ICMP")):
            return

        #Whitelist check
        if srcIP not in self.whitelist:
            #Testing config - does not utilize a database
            if (self.config == "onlyUDP" or self.config == "testing"):
                dbHostname = "N/A"
            else:
                dbHostname = self.db.hostname

            #ICMP layer check first
            if (ipLayer.haslayer("ICMP")):
                trafficType = "ICMP"
                log = LogEntry(None, srcIP, sourceMAC, None, dstIP, destMAC, trafficType, None, dbHostname)
                self.db.save(log.json())
                return

            #TCP/UDP section now


            if (ipLayer.haslayer("TCP")):
                trafficType = "TCP"
            elif (ipLayer.haslayer("UDP")):
                trafficType = "UDP"
            else:
                trafficType = "Other"

            #Log Entry object we're saving
            log = LogEntry(srcPort, srcIP, sourceMAC, destPort, dstIP, destMAC,
                           trafficType, destPort in self.openPorts, dbHostname)


            #self.RECORD is where we save logs for easy testing
            if (not srcIP in self.RECORD.keys()):
                self.RECORD[srcIP] = [log]
            else:
                self.RECORD[srcIP].append(log)

            #saving the database ID in case of port scan detection
            if (self.config == "base"):
                dbID = self.db.save(log.json())
            else:
                return

            #self.PS_RECORD is a separate dictionary used for port scan detection
            if (not srcIP in self.PS_RECORD.keys()):
                self.PS_RECORD[srcIP] = dict()
                self.PS_RECORD[srcIP][log.destPortNumber] = dbID
            else:
                self.PS_RECORD[srcIP][log.destPortNumber] = dbID

                #Sending out the port scan alert
                if (len(self.PS_RECORD[srcIP]) > 100):
                    self.db.alert(
                        Alert(variant="alert",
                              message="Port scan detected from IP {}".format(
                                  srcIP),
                              references=list(self.PS_RECORD[srcIP].values()),
                              hostname=self.db.hostname).json())
                    self.PS_RECORD[srcIP] = dict()
