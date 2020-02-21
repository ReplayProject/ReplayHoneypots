import unittest
from unittest.mock import MagicMock
import json
from requests import get
from Port import Port
from NmapParser import NmapParser
from PortThreadManager import PortThreadManager
from LogEntry import LogEntry
from ConfigTunnel import ConfigTunnel
from Databaser import Databaser
from Sniffer import Sniffer
from scapy.all import send, UDP, Raw, IP
import os
import time
from threading import Thread
import socket

"""
This file contains test cases for the honeypot code
"""


def run_nmap():
    time.sleep(5)
    os.system("nmap localhost")


class TestPort(unittest.TestCase):
    """
    Test the Port object
    """

    def test_response(self):
        port = Port(455, 0x11ff)
        self.assertEqual(0x11ff, port.response())

    def test_get_json(self):
        port = Port(455, 0x11ff)
        self.assertEqual(port.get_json(), {"port": 455, "defaultData": 4607})

    def test_str(self):
        port = Port(455, 0x11ff)
        self.assertEqual(str(port), "Port: 455")


class TestNmapParser(unittest.TestCase):
    """
    Test the NmapParser class
    """

    def test_invalid_filename(self):
        with self.assertRaises(FileNotFoundError):
            parser = NmapParser("wrongfilename")

    def test_ports(self):
        parser = NmapParser("../nmap/default.nmap")
        self.assertTrue(5040 in parser.getPorts())


class TestLogs(unittest.TestCase):
    """
    Test the logging functionality
    """

    def test_entry(self):
        entry = LogEntry("80", "192.1.1.1", "81", "192.1.1.2",
                         "Www Mmm dd hh:mm:ss yyyy", True)
        self.assertEqual("80", entry.sourcePortNumber)
        self.assertTrue(type(entry.timestamp) is int)


class TestDatabaser(unittest.TestCase):
    def test_init(self):
        """
        Test that the database successfully sets itself up
        """
        db = Databaser()
        db.daemon = True
        db.start()

        # Wait for the DB to be ready
        time.sleep(7)

        self.assertTrue(db.ready)

        db.stop()
        db.join()


class TestSniffer(unittest.TestCase):
    def test_init(self):
        """
        Test that the sniffer successfully sets itself up
        """
        # Get my IP
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        # Start the sniffer
        sniff = Sniffer(
            count=10,
            config="onlyUDP",
            openPorts=[],
            whitelist=[],
            db_url="fakeURL",
            honeypotIP=host_ip,
            managementIPs=("52.87.97.77", "54.80.228.0")
        )
        sniff.daemon = True
        sniff.start()

        # Make some UDP traffic
        send(IP(dst=host_ip)/UDP(dport=1337)/Raw(load="whatever"), count=10)

        # Let the logger handle whats up
        time.sleep(2)

        print(list(sniff.UDP_RECORD.keys()))

        localhost_in_udp_record = any(
            host_ip in i for i in list(sniff.UDP_RECORD.keys()))
        self.assertTrue(localhost_in_udp_record)

        sniff.join()

# TODO: track down the unclosed socket
class TestConfigTunnel(unittest.TestCase):
    """
    Handles testing for the ConfigTunnel module
    """

    def setUp(self):
        """
        Setup both ends of the tunnel with a connection to localhost
        """
        self.stunnel = ConfigTunnel('server')
        self.ctunnel = ConfigTunnel('client', "localhost")

    def tearDown(self):
        """
        Get ready for the next test
        """
        self.ctunnel.stop()
        self.stunnel.stop()
        time.sleep(2)
        self.ctunnel.join()
        self.stunnel.join()

    def test_init(self):
        """
        Test that server/client start and connect to eachother
        """
        # Server & Client Start
        self.stunnel.start()
        self.ctunnel.start()
        time.sleep(1)

        self.assertTrue(self.stunnel.ready)
        self.assertTrue(self.ctunnel.ready)

    def test_basic_handlers(self):
        """
        Test that we can use the tunnel with a one way handler
        """
        # Helper Variables & Functions
        handle_test = MagicMock(return_value=None)
        # Server Handler Setup
        self.stunnel.setHandler("test", handle_test)
        # Server & Client Start
        self.stunnel.start()
        self.ctunnel.start()
        # Wait and send a "command"
        time.sleep(2)
        self.ctunnel.send("test")
        # Final checks
        time.sleep(1)
        self.assertTrue(handle_test.called)

    def test_advanced_handlers(self):
        """
        More complex usage of handlers and passing simple data
        """
        # Helper Variables & Functions
        handle_server_echo = MagicMock(return_value="echo value")
        handle_client_done = MagicMock(return_value=None)
        # Server & Client Setup
        self.stunnel.setHandler("test", handle_server_echo)
        self.stunnel.start()
        self.ctunnel.setHandler("done", handle_client_done)
        self.ctunnel.start()
        # Wait and send a "command"
        time.sleep(2)
        self.ctunnel.send("test with a somewhat longer message")
        # Final checks
        time.sleep(1)
        # Server received command
        self.assertTrue(handle_server_echo.called)
        server_expected = ['with', 'a', 'somewhat', 'longer', 'message']
        handle_server_echo.assert_called_once_with(server_expected)
        # Client received response and payload
        self.assertTrue(handle_client_done.called)
        handle_client_done.assert_called_once_with(["echo", "value"])


if __name__ == '__main__':
    unittest.main()
