import unittest
from unittest.mock import MagicMock
import json
from requests import get
from Port import Port
from NmapParser import NmapParser
from PortThreadManager import PortThreadManager
from LogEntry import LogEntry
from DataLog import DataLog
from ConfigTunnel import ConfigTunnel
import os
import time
from threading import Thread

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
                         "Www Mmm dd hh:mm:ss yyyy")
        self.assertEqual("80", entry.sourcePortNumber)
        self.assertEqual("Www Mmm dd hh:mm:ss yyyy", entry.timestamp)

    def test_data_log(self):
        # remove test file if it exists
        try:
            os.remove('../logs/test.txt')
        except:
            pass
        datalog = DataLog()
        entry1 = LogEntry("1", "1.1.1.1", "81", "192.1.1.2",
                          "Www Mmm dd hh:mm:ss yyyy")
        entry2 = LogEntry("2", "2.2.2.2", "81", "192.1.1.2",
                          "Www Mmm dd hh:mm:ss yyyy")
        datalog.logs.append(entry1)
        datalog.logs.append(entry2)
        datalog.writeLogs('../logs/test.txt')
        f = open('../logs/test.txt', 'r')
        self.assertEqual(
            f.readline(), "Www Mmm dd hh:mm:ss yyyy 1.1.1.1 1 192.1.1.2 81\n")
        self.assertEqual(
            f.readline(), "Www Mmm dd hh:mm:ss yyyy 2.2.2.2 2 192.1.1.2 81\n")
        os.remove('../logs/test.txt')
        f.close()


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
