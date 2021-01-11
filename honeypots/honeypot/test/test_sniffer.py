"""
If testing inside of an alpine container, will need to run
 apk add curl bind-tools
honeypot_tests.sh script automatically does this
"""
import os

import pytest
import trio
from scapy.all import ICMP
from scapy.all import IP
from scapy.all import send
from Sniffer import Sniffer

WAIT_TIME = 0.1

class TestConfig:
        def __init__(self, open_ports, whitelist_ports, portscan_window, whitelist_addrs):
            self.open_ports = open_ports
            self.whitelist_ports = whitelist_ports
            self.portscan_window = portscan_window
            self.whitelist_addrs = whitelist_addrs

testConfig = TestConfig([], [], 300, [])
testConfig2 = TestConfig([80,443], [777,888,999], 300, ["8.8.8.8","9.9.9.9"])

class TestSniffer:
    """
    Testing for the async sniffer
    """

    async def test_init(self, nursery):
        """
        Test that the sniffer successfully sets itself up
        """
        #  Start the sniffer
        s = Sniffer(
            config=testConfig,
            databaser=None,
        )
        s.start()

        # Google IP; we'll be using this later
        IPPipe = os.popen("dig +short www.google.com")
        responseIPs = IPPipe.read()[:-1].split("\n")
        IPPipe.close()

        # Making sure we catch it
        os.system("curl -s www.google.com -o /dev/null")

        # Let the logger handle whats up
        await trio.sleep(WAIT_TIME)

        # Dig sometimes gives us multiple IPs, not all of which are used.
        #  If one is used, that's a successful read.
        for ip in responseIPs:
            assert ip in s.RECORD.keys()
            assert s.RECORD[ip][0].sourceIPAddress == ip
            assert s.RECORD[ip][0].sourcePortNumber == 80
            assert s.RECORD[ip][0].trafficType == "TCP"
            assert s.RECORD[ip][0].length != 0

        s.stop()

    async def test_icmp(self, nursery):
        """
        Test that the sniffer successfully sets itself up
        """
        #  Start the sniffer
        s = Sniffer(
            config=testConfig,
            databaser=None,
        )
        s.start()

        # Do an ICMP request to a DNS resolver
        targets = ["9.9.9.9", "8.8.8.8", "1.1.1.1"]

        for ip in targets:
            send(IP(dst=ip) / ICMP())

        # Let the logger handle whats up
        await trio.sleep(WAIT_TIME * 4)

        for ip in targets:
            assert ip in s.RECORD.keys()
            assert s.RECORD[ip][0].sourceIPAddress == ip
            assert s.RECORD[ip][0].trafficType == "ICMP"
            assert s.RECORD[ip][0].length == 28
            print("check for {}".format(ip))

        s.stop()

    async def testConfigUpdate(self):
        """
        Checks if updated options work
        """
        host_ip = "192.168.42.51"
        # Start the sniffer
        s = Sniffer(
            config=testConfig,
            databaser=None,
        )
        s.start()

        assert len(s.config.open_ports) == 0
        assert len(s.config.whitelist_addrs) == 0
        assert len(s.config.whitelist_ports) == 0

        s.configUpdate(testConfig2)
        # used to flush the Sniffer
        os.system("curl -s www.google.com -o /dev/null")
        assert len(s.config.open_ports) == 2
        assert len(s.config.whitelist_addrs) == 2
        assert len(s.config.whitelist_ports) == 3

        s.stop()