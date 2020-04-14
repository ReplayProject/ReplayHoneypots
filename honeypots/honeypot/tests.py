import unittest
from unittest.mock import MagicMock
import json
from Port import Port
from NmapParser import NmapParser
from PortThreadManager import PortThreadManager
from LogEntry import LogEntry
from ConfigTunnel import ConfigTunnel
from Databaser import Databaser
from Sniffer import Sniffer
from CronInstaller import CronInstaller
from CronUninstaller import CronUninstaller
from scapy.all import send, UDP, Raw, IP, TCP
import os
import time
from threading import Thread
import socket
import subprocess
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
        parser = NmapParser("../../logs/nmap/default.nmap")
        self.assertTrue(5040 in parser.getPorts())


class TestLogs(unittest.TestCase):
    """
    Test the logging functionality
    """
    def test_entry(self):
        entry = LogEntry("80", "192.1.1.1", "00-11-22-33-44-55", "81",
                         "192.1.1.2", "AA-BB-CC-DD-EE-FF", "TCP", True, "test_logs")
        self.assertEqual("80", entry.sourcePortNumber)
        self.assertTrue(type(entry.timestamp) is int)


# DB_URL = 'http://admin:couchdb@152.14.85.156:5984'
DB_URL = 'http://admin:couchdb@127.0.0.1:5984'


class TestDatabaser(unittest.TestCase):
    def tearDown(self):
        """
        Clear out testing db (BE CAREFUL)
        """
        os.environ["DB_URL"] = DB_URL
        try:
            db = Databaser()
            db.deleteDB()  # assuming admin
        except Exception:
            self.fail("Databaser raised an exception during teardown!")

        return super().tearDown()

    def test_init(self):
        """
        Test that the database successfully sets itself up
        """
        # Env Variables
        os.environ["DB_URL"] = DB_URL
        # Successful run (assuming couch is running)
        try:
            db = Databaser()
            print("Databases: ", db.listDbs())
        except Exception:
            self.fail("Databaser raised an exception unexpectedly!")

    def test_fail(self):
        try:
            os.environ["DB_URL"] = DB_URL + "9"
            db = Databaser()
        except ConnectionRefusedError:
            self.assertRaises(Exception)

    def test_fail_2(self):
        try:
            os.environ["DB_URL"] = "http://localhost:1020"
            db = Databaser()
        except ConnectionRefusedError:
            self.assertRaises(Exception)

        try:
            os.environ["TARGET_ADDR"] = ""
            db = Databaser()
        except Exception:
            self.assertRaises(Exception)


class TestSniffer(unittest.TestCase):
    def test_init(self):
        """
        Test that the sniffer successfully sets itself up
        """

        # Start the sniffer
        s = Sniffer(config="testing",
                    openPorts=[],
                    whitelist=[],
                    honeypotIP="localhost",
                    managementIPs=("52.87.97.77", "54.80.228.0"),
                    databaser=None)
        s.daemon = True
        s.start()

        #Google IP; we'll be using this later
        IPPipe = os.popen('dig +short www.google.com')
        responseIP = IPPipe.read()[:-1]
        IPPipe.close()

        #Making sure we catch it
        os.system("curl www.google.com 2>&1 >> /dev/null")
        os.system("curl www.google.com 2>&1 >> /dev/null")
        os.system("curl www.google.com 2>&1 >> /dev/null")

        # Let the logger handle whats up
        time.sleep(2)

        self.assertTrue(responseIP in s.RECORD.keys())
        self.assertTrue(s.RECORD[responseIP][0].sourceIPAddress == responseIP)
        self.assertTrue(s.RECORD[responseIP][0].sourcePortNumber == 80)
        self.assertTrue(s.RECORD[responseIP][0].trafficType == "TCP")

        s.running = False

    def testConfigUpdate(self):
        """
        Checks if updated options work
        """
        host_ip = "192.168.42.51"
        # Start the sniffer
        s = Sniffer(config="onlyUDP",
                    openPorts=[],
                    whitelist=[],
                    portWhitelist=[],
                    honeypotIP=host_ip,
                    managementIPs=("52.87.97.77", "54.80.228.0"))
        s.daemon = True
        s.start()

        self.assertTrue(len(s.openPorts) == 0)
        self.assertTrue(len(s.whitelist) == 0)
        self.assertTrue(len(s.portWhitelist) == 0)
        self.assertTrue(s.config == "onlyUDP")
        self.assertTrue(len(s.managementIPs) == 2)
        self.assertTrue(s.honeypotIP == "192.168.42.51")

        s.configUpdate(openPorts=[80, 443],
                       whitelist=["8.8.8.8", "9.9.9.9"],
                       portWhitelist=[777, 888, 999],
                       honeypotIP="192.168.42.42",
                       managementIPs="54.80.228.0")
        self.assertTrue(len(s.openPorts) == 2)
        self.assertTrue(len(s.whitelist) == 2)
        self.assertTrue(len(s.portWhitelist) == 3)
        self.assertTrue(s.managementIPs == "54.80.228.0")
        self.assertTrue(s.honeypotIP == "192.168.42.42")

        s.running = False


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

    def test_fulltest(self):
        # Server & Client Start
        self.stunnel.start()
        self.ctunnel.start()
        time.sleep(1)
        self.assertTrue(True)

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


class TestCron(unittest.TestCase):
    """
    Tests CronInstaller and CronUninstaller
    """
    def test_cron(self):
        """
        Setup
        """

        # Confirm that the user has root access
        self.assertEqual(os.geteuid(), 0)

        # Before installing/uninstalling Cron, check for any existing Cron jobs
        process = subprocess.Popen(['crontab', '-l'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        # If there are previous Cron jobs, save them before clearing out Cron
        previous = False
        if stdout:
            previous = True
            crontab_file = open("previous", 'w')
            crontab_file.write(stdout.decode())
            crontab_file.close()
            process = subprocess.Popen(['crontab', '-r'],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
        """
        Test CronInstaller's argparser
        """

        with self.assertRaises(SystemExit):
            CronInstaller.main([])
        with self.assertRaises(FileNotFoundError):
            CronInstaller.main(['-p', 'badfilepath'])
        with self.assertRaises(FileNotFoundError):
            CronInstaller.main(
                ['-p', 'PortThreadManager.py', '-n', 'badfilepath'])
        CronInstaller.main(
            ['-p', 'PortThreadManager.py'])
        CronUninstaller.uninstall()
        CronInstaller.main(
            ['-p', 'PortThreadManager.py', '-n', '../../logs/nmap/default.nmap'])
        CronUninstaller.uninstall()
        """
        Install Cron when there is no existing Cron file.
        We expect the installer to:
        - Create/edit the restart script
        - Create a Cron file for the user
        - Use the correct absolute paths for both files

        Uninstall Cron when there is only our job.
        We expect the uninstaller to simply delete the Cron file.
        """

        CronInstaller.install("PortThreadManager.py", "-n",
                              "../../logs/nmap/default.nmap")
        self.assertTrue(os.path.exists("restart.sh"))
        restart_script = open("restart.sh", 'r')
        script_file = os.path.abspath("PortThreadManager.py")
        config_file = os.path.abspath("../../logs/nmap/default.nmap")
        self.assertEqual(
            restart_script.read(), "#!/bin/bash\n\n" +
            "var=$(pgrep -af PortThreadManager.py | wc -l)\n\n" +
            "if [ $var -le 0 ]\n" + "then\n" + "\tcd " +
            os.path.dirname(os.path.dirname(script_file)) +
            " && pip3 install -r requirements.txt\n" +
            "\techo $(date) 'Running: sudo python3 " + script_file + " -n " +
            config_file + ".' >> " +
            os.path.dirname(os.path.dirname(os.path.dirname(script_file))) +
            "/logs/logs/cron.txt\n" +  "\tcd " +
            os.path.dirname(script_file) + " && sudo python3 " + script_file +
            " -n " + config_file + "\n" + "fi\n")
        restart_script.close()
        process = subprocess.Popen(['crontab', '-l'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        self.assertEqual(
            stdout.decode(), "* * * * * /bin/bash " +
            os.path.dirname(os.path.abspath(__file__)) + "/restart.sh >> " +
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) +
            "/logs/logs/restart.txt 2>&1\n")
        CronUninstaller.uninstall()
        process = subprocess.Popen(['crontab', '-l'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        self.assertEqual(stderr.decode(), "no crontab for root\n")
        """
        Install Cron when there is already an existing Cron file, and that file contains our job.
        We expect the installer to identify our job and not duplicate the Cron job.
        """

        CronInstaller.install("PortThreadManager.py", "-n",
                              "../../logs/nmap/default.nmap")
        CronInstaller.install("PortThreadManager.py", "-n",
                              "../../logs/nmap/default.nmap")
        process = subprocess.Popen(['crontab', '-l'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        self.assertEqual(
            stdout.decode(), "* * * * * /bin/bash " +
            os.path.dirname(os.path.abspath(__file__)) + "/restart.sh >> " +
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) +
            "/logs/logs/restart.txt 2>&1\n")
        CronUninstaller.uninstall()
        """
        Install Cron when there is already an existing Cron file, and that file does not contain our job.
        We expect the installer to:
        - Preserve the previous contents of the Cron file
        - Add our job to the Cron file

        Uninstall Cron when there are other jobs besides our own.
        We expect the uninstaller to:
        - Preserve the previous contents of the Cron file
        - Remove our job from the Cron file
        """

        crontab_file = open("not_honeypot", 'w')
        crontab_file.write("* * * * * Hello World!\n")
        crontab_file.close()
        process = subprocess.Popen(['crontab', 'not_honeypot'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        os.remove("not_honeypot")
        CronInstaller.install("PortThreadManager.py", "-n",
                              "../../logs/nmap/default.nmap")
        process = subprocess.Popen(['crontab', '-l'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        self.assertEqual(
            stdout.decode(), "* * * * * Hello World!\n* * * * * /bin/bash " +
            os.path.dirname(os.path.abspath(__file__)) + "/restart.sh >> " +
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) +
            "/logs/logs/restart.txt 2>&1\n")
        CronUninstaller.uninstall()
        process = subprocess.Popen(['crontab', '-l'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        self.assertEqual(stdout.decode(), "* * * * * Hello World!\n\n")
        process = subprocess.Popen(['crontab', '-r'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        """
        Uninstall Cron when there is no Cron file.
        We expect the uninstaller to throw an error.
        """
        with self.assertRaises(FileNotFoundError):
            CronUninstaller.uninstall()
        """
        Uninstall Cron when there are is a Cron file, but it does not contain our job.
        We expect the uninstaller to:
        - Preserve the previous contents of the Cron file
        - Throw an error
        """
        crontab_file = open("not_honeypot", 'w')
        crontab_file.write("* * * * * Hello World!\n")
        crontab_file.close()
        process = subprocess.Popen(['crontab', 'not_honeypot'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        os.remove("not_honeypot")
        with self.assertRaises(LookupError):
            CronUninstaller.uninstall()
        process = subprocess.Popen(['crontab', '-l'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        self.assertEqual(stdout.decode(), "* * * * * Hello World!\n")
        process = subprocess.Popen(['crontab', '-r'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        """
        Teardown
        """
        if previous:  # If there were previous Cron jobs:
            # Restore them
            process = subprocess.Popen(['crontab', 'previous'],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            # Remove generated files
            os.remove("previous")


if __name__ == '__main__':
    unittest.main()
