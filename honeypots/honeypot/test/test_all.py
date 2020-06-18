"""
This file contains test cases for the honeypot code
"""
import os
import subprocess
import time
import unittest
from unittest.mock import MagicMock

from CronInstaller import CronInstaller
from CronUninstaller import CronUninstaller
from Databaser import Databaser
from LogEntry import LogEntry
from NmapParser import NmapParser
from Port import Port


def run_nmap():
    time.sleep(5)
    os.system("nmap localhost")


class TestPort(unittest.TestCase):
    """
    Test the Port object
    """

    def test_response(self):
        port = Port(455, 0x11FF)
        self.assertEqual(0x11FF, port.response())

    def test_get_json(self):
        port = Port(455, 0x11FF)
        self.assertEqual(port.get_json(), {"port": 455, "defaultData": 4607})

    def test_str(self):
        port = Port(455, 0x11FF)
        self.assertEqual(str(port), "Port: 455")


class TestNmapParser(unittest.TestCase):
    """
    Test the NmapParser class
    """

    def test_invalid_filename(self):
        with self.assertRaises(FileNotFoundError):
            NmapParser("wrongfilename")

    def test_ports(self):
        parser = NmapParser("../../logs/nmap/default.nmap")
        self.assertTrue(5040 in parser.getPorts())


class TestLogs(unittest.TestCase):
    """
    Test the logging functionality
    """

    def test_entry(self):
        entry = LogEntry(
            "80",
            "192.1.1.1",
            "00-11-22-33-44-55",
            "81",
            "192.1.1.2",
            "AA-BB-CC-DD-EE-FF",
            "TCP",
            True,
            "test_logs",
        )
        self.assertEqual("80", entry.sourcePortNumber)
        self.assertTrue(type(entry.timestamp) is int)


# TODO: DB conenction string for testing
# Default 'http://admin:couchdb@127.0.0.1:5984'
DB_URL = "http://admin:couchdb@10.11.12.125:5984"


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
            Databaser()
        except ConnectionRefusedError:
            self.assertRaises(Exception)

    def test_fail_2(self):
        try:
            os.environ["DB_URL"] = "http://localhost:1020"
            Databaser()
        except ConnectionRefusedError:
            self.assertRaises(Exception)
        except OSError:
            self.assertRaises(Exception)

        try:
            os.environ["TARGET_ADDR"] = ""
            Databaser()
        except Exception:
            self.assertRaises(Exception)


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
        process = subprocess.Popen(
            ["crontab", "-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        # If there are previous Cron jobs, save them before clearing out Cron
        previous = False
        if stdout:
            previous = True
            crontab_file = open("previous", "w")
            crontab_file.write(stdout.decode())
            crontab_file.close()
            process = subprocess.Popen(
                ["crontab", "-r"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
        """
        Test CronInstaller's argparser
        """

        with self.assertRaises(SystemExit):
            CronInstaller.main([])
        with self.assertRaises(FileNotFoundError):
            CronInstaller.main(["-p", "badfilepath"])
        with self.assertRaises(FileNotFoundError):
            CronInstaller.main(["-p", "PortThreadManager.py", "-n", "badfilepath"])
        CronInstaller.main(["-p", "PortThreadManager.py"])
        CronUninstaller.uninstall()
        CronInstaller.main(
            ["-p", "PortThreadManager.py", "-n", "../../logs/nmap/default.nmap"]
        )
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

        CronInstaller.install(
            "PortThreadManager.py", "-n", "../../logs/nmap/default.nmap"
        )
        self.assertTrue(os.path.exists("restart.sh"))
        restart_script = open("restart.sh", "r")
        script_file = os.path.abspath("PortThreadManager.py")
        config_file = os.path.abspath("../../logs/nmap/default.nmap")
        self.assertEqual(
            restart_script.read(),
            "#!/bin/bash\n\n"
            + "var=$(pgrep -af PortThreadManager.py | wc -l)\n\n"
            + "if [ $var -le 0 ]\n"
            + "then\n"
            + "\tcd "
            + os.path.dirname(os.path.dirname(script_file))
            + " && pip3 install -r requirements.txt\n"
            + "\techo $(date) 'Running: sudo python3 "
            + script_file
            + " -n "
            + config_file
            + ".' >> "
            + os.path.dirname(os.path.dirname(os.path.dirname(script_file)))
            + "/logs/logs/cron.txt\n"
            + "\tcd "
            + os.path.dirname(script_file)
            + " && sudo python3 "
            + script_file
            + " -n "
            + config_file
            + "\n"
            + "fi\n",
        )
        restart_script.close()
        process = subprocess.Popen(
            ["crontab", "-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        self.assertEqual(
            stdout.decode(),
            "* * * * * /bin/bash "
            + os.path.dirname(os.path.abspath(__file__))
            + "/restart.sh >> "
            + os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            + "/logs/logs/restart.txt 2>&1\n",
        )
        CronUninstaller.uninstall()
        process = subprocess.Popen(
            ["crontab", "-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        self.assertEqual(stderr.decode(), "no crontab for root\n")
        """
        Install Cron when there is already an existing Cron file, and
        that file contains our job. We expect the installer to identify
        our job and not duplicate the Cron job.
        """

        CronInstaller.install(
            "PortThreadManager.py", "-n", "../../logs/nmap/default.nmap"
        )
        CronInstaller.install(
            "PortThreadManager.py", "-n", "../../logs/nmap/default.nmap"
        )
        process = subprocess.Popen(
            ["crontab", "-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        self.assertEqual(
            stdout.decode(),
            "* * * * * /bin/bash "
            + os.path.dirname(os.path.abspath(__file__))
            + "/restart.sh >> "
            + os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            + "/logs/logs/restart.txt 2>&1\n",
        )
        CronUninstaller.uninstall()
        """
        Install Cron when there is already an existing Cron file, and that
         file does not contain our job.
        We expect the installer to:
        - Preserve the previous contents of the Cron file
        - Add our job to the Cron file

        Uninstall Cron when there are other jobs besides our own.
        We expect the uninstaller to:
        - Preserve the previous contents of the Cron file
        - Remove our job from the Cron file
        """

        crontab_file = open("not_honeypot", "w")
        crontab_file.write("* * * * * Hello World!\n")
        crontab_file.close()
        process = subprocess.Popen(
            ["crontab", "not_honeypot"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        os.remove("not_honeypot")
        CronInstaller.install(
            "PortThreadManager.py", "-n", "../../logs/nmap/default.nmap"
        )
        process = subprocess.Popen(
            ["crontab", "-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        self.assertEqual(
            stdout.decode(),
            "* * * * * Hello World!\n* * * * * /bin/bash "
            + os.path.dirname(os.path.abspath(__file__))
            + "/restart.sh >> "
            + os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            + "/logs/logs/restart.txt 2>&1\n",
        )
        CronUninstaller.uninstall()
        process = subprocess.Popen(
            ["crontab", "-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        self.assertEqual(stdout.decode(), "* * * * * Hello World!\n\n")
        process = subprocess.Popen(
            ["crontab", "-r"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
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
        crontab_file = open("not_honeypot", "w")
        crontab_file.write("* * * * * Hello World!\n")
        crontab_file.close()
        process = subprocess.Popen(
            ["crontab", "not_honeypot"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        os.remove("not_honeypot")
        with self.assertRaises(LookupError):
            CronUninstaller.uninstall()
        process = subprocess.Popen(
            ["crontab", "-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        self.assertEqual(stdout.decode(), "* * * * * Hello World!\n")
        process = subprocess.Popen(
            ["crontab", "-r"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        """
        Teardown
        """
        if previous:  # If there were previous Cron jobs:
            # Restore them
            process = subprocess.Popen(
                ["crontab", "previous"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()

            # Remove generated files
            os.remove("previous")


if __name__ == "__main__":
    unittest.main()
