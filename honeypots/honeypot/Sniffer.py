from LogEntry import LogEntry
from scapy.all import sniff
from threading import Thread
from Databaser import Databaser
from datetime import datetime
from Alert import Alert
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

        #Used to tell if we should continue running sniffer
        self.running = True
        #Semaphore that tells us when we can restart the run method with new config details
        self.ready = True

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

    def run(self):
        print("Sniffing")

        #This acts as a semaphore
        self.ready = False

        #building the base filter
        fltr = "not src host {} ".format(self.honeypotIP)
        #adding a variable number of management ips
        for ip in self.managementIPs:
            fltr += "and not host {} ".format(ip)
        #adding things from the port list
        for port in self.portWhitelist:
            fltr += "and not dst port {} ".format(port)

        #here's where the packet detection starts
        if (self.config == "testing"):
            fltr = fltr + " and not (src port ssh or dst port ssh)"
            # this ignores the ssh spam you get when sending packets between two ssh terminals
            sniff(filter=fltr,
                  prn=self.save_packet,
                  stop_filter=lambda p: not self.running)
        elif (self.config == "base"):
            fltr = fltr + " and not (src port ssh or dst port ssh)"
            # this above filter ignores the ssh spam you get when sending packets between two ssh terminals - TAKE THIS OUT IN PROD
            sniff(filter=fltr,
                  prn=self.save_packet,
                  stop_filter=lambda p: not self.running)
        #this last config option is used in testing
        elif (self.config == "onlyUDP"):
            fltr = "udp"
            sniff(filter=fltr,
                  prn=self.save_packet,
                  stop_filter=lambda p: not self.running)

        self.ready = True

    """
    Updates configuration options during runtime
    """

    def configUpdate(self,
                     openPorts=[],
                     whitelist=[],
                     portWhitelist=[],
                     honeypotIP=None,
                     managementIPs=None):
        print("Sniffer updated")
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

        #preps Sniffer
        if (self.ready):
            self.running = True
            self.run()

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
            #ICMP layer check first
            if (ipLayer.haslayer("ICMP")):
                trafficType = "ICMP"
                log = LogEntry(None, srcIP, sourceMAC, None, dstIP, destMAC, trafficType, None, dbHostname)
                self.db.save(log.json())
                return            

            #TCP/UDP section now
            
            #Testing config - does not utilize a database
            if (self.config == "onlyUDP" or self.config == "testing"):
                dbHostname = "N/A"
            else:
                dbHostname = self.db.hostname

            #Log Entry object we're saving
            log = LogEntry(srcPort, srcIP, sourceMAC, destPort, dstIP, destMAC,
                           trafficType, destPort in self.openPorts, dbHostname)

            #saving the database ID in case of port scan detection
            if (self.config == "base"):
                dbID = self.db.save(log.json())

            #self.RECORD is where we save logs for easy testing
            if (not srcIP in self.RECORD.keys()):
                self.RECORD[srcIP] = [log]
            else:
                self.RECORD[srcIP].append(log)

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
