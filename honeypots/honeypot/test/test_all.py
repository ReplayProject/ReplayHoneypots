"""
This file contains test cases for some the honeypot modules
"""
import os
import subprocess
import time
import unittest
from unittest.mock import MagicMock

from Databaser import Databaser
from LogEntry import LogEntry
from requests.exceptions import ConnectionError


def run_nmap():
    time.sleep(5)
    os.system("nmap localhost")

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
            "20",
            True,
        )
        self.assertEqual("80", entry.sourcePortNumber)
        self.assertTrue(type(entry.timestamp) is int)


# TODO: DB conenction string for testing
# make sure this url resolves correctly
# Default 'http://admin:couchdb@127.0.0.1:5984'
DB_URL = "http://admin:couchdb@host.docker.internal:5984"  # Docker compose mode


class TestDatabaser(unittest.TestCase):
    """
    Tests that check how the Databaser starts and runs
    (required an instance of couchDB to be running and accessible)
    """

    def tearDown(self):
        """
        Clear out the testing DBs
        Note that inside of databaser there is logic to create test databases
        """
        os.environ["DB_URL"] = DB_URL
        try:
            db = Databaser(test=True)
            # db.deleteDB()  # assuming admin
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
            db = Databaser(test=True)
            print("Databases: ", db.listDbs())
        except Exception:
            self.fail("Databaser raised an exception unexpectedly!")

    def test_claim_uuid(self):
        """
        Test that the honeypot can claim a UUID
        """
        # Env Variables
        os.environ["DB_URL"] = DB_URL
        # Successful run (assuming couch is running)
        try:
            db = Databaser(test=True)
            uuid = db.claimUUID()
            self.assertIsNotNone(uuid)
        except Exception:
            self.fail("Databaser raised an exception unexpectedly!")

    def test_get_config(self):
        """
        Test that the honeypot can claim a UUID
        """
        # Env Variables
        os.environ["DB_URL"] = DB_URL
        # Successful run (assuming couch is running)
        try:
            db = Databaser(test=True)
            config = db.getConfig()
            self.assertIsNotNone(config)
            self.assertIsNotNone(config["id"])
            self.assertIsNotNone(uuid)
        except Exception:
            self.fail("Databaser raised an exception unexpectedly!")

    def test_fail(self):
        """
        Test that connecting to a strange url responds with error
        """
        try:
            os.environ["DB_URL"] = DB_URL + "9"
            Databaser(test=True)
        except ConnectionError:
            self.assertRaises(Exception)

    def test_fail_2(self):
        """
        Test that connecting to a strange url responds with error
        """
        try:
            os.environ["DB_URL"] = "http://localhost:1020"
            Databaser(test=True)
        except:
            self.assertRaises(Exception)

        try:
            os.environ["TARGET_ADDR"] = ""
            Databaser(test=True)
        except Exception:
            self.assertRaises(Exception)

if __name__ == "__main__":
    unittest.main()
