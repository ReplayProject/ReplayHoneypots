import unittest
import json
from requests import get
from Port import Port
from NmapParser import NmapParser
from PortThreadManager import PortThreadManager
from LogEntry import LogEntry
from DataLog import DataLog
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
        self.assertEqual(port.get_json(), {"port":455,"defaultData":4607})
        
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
        entry = LogEntry("80", "192.1.1.1", "81", "192.1.1.2", "Www Mmm dd hh:mm:ss yyyy")
        self.assertEqual("80", entry.sourcePortNumber)
        self.assertEqual("Www Mmm dd hh:mm:ss yyyy", entry.timestamp)

    def test_data_log(self):
        # remove test file if it exists
        try:
          os.remove('../logs/test.txt')
        except:
          pass
        datalog = DataLog()
        entry1 = LogEntry("1", "1.1.1.1", "81", "192.1.1.2", "Www Mmm dd hh:mm:ss yyyy")
        entry2 = LogEntry("2", "2.2.2.2", "81", "192.1.1.2", "Www Mmm dd hh:mm:ss yyyy")
        datalog.logs.append(entry1)
        datalog.logs.append(entry2)
        datalog.writeLogs('../logs/test.txt')
        f = open('../logs/test.txt', 'r')
        self.assertEqual(f.readline(), "Www Mmm dd hh:mm:ss yyyy 1.1.1.1 1 192.1.1.2 81\n")
        self.assertEqual(f.readline(), "Www Mmm dd hh:mm:ss yyyy 2.2.2.2 2 192.1.1.2 81\n")
        os.remove('../logs/test.txt')
        f.close()
        

if __name__ == '__main__':
    unittest.main()
