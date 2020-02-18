import os
import subprocess
import socket
import time
from threading import Thread
from requests import put


class Databaser(Thread):
    """
    Use pouch db to run the database for logging
    """

    def __init__(self):
        """
        Constructor; takes a config keyword to see what mode to run it in
        'testing' ignores ssh spam you get
        """
        Thread.__init__(self)
        self.process = None
        # Config Cariables
        self.port = "1437"
        self.conf = "../config/dbconfig.json"
        self.dbfolder = "../database"
        self.bindaddress = "192.168.23.51"
        self.url = 'http://{}:{}/'.format(self.bindaddress, self.port)
        self.db_name = socket.gethostname() + "_logs"
        self.db_url = self.url + self.db_name

        self.ready = False

    def createDatabase(self):
        """
        Create this device's log daatbase
        """
        # TODO: automatically setup the replication settings
        header = {"content-type": "application/json"}
        r = put(url=self.url + self.db_name,
                headers=header, verify=False, timeout=2)
        if (r.status_code != 201):
            Exception("Database could not be created")
        return r

    def run(self):
        """
        Runs the thread, begins sniffing
        """
        # toggle --in-memory to save data
        cmd = ["pouchdb-server", "--in-memory", "--dir", self.dbfolder,
               "--port", self.port, "--host", self.bindaddress, "--config", self.conf]
        self.process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.dbfolder)

        time.sleep(.5)

        status = self.createDatabase()
        print("Handling DB: " + self.url + "_utils")
        print("Logging DB is: %s" % status.json())

        self.ready = True

        while True:
            output = self.process.stdout.readline()
            if output == '' and self.process.poll() is not None:
                break
            if output:
                print(output.decode("utf-8"))
        rc = self.process.poll()
        return rc
