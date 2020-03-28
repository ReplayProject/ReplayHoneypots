import os
import subprocess
import socket
import time
import json
from threading import Thread
from requests import put, post
from pathlib import Path

# TODO: make starting replication something that can be triggered async
class Databaser(Thread):
    """
    Use pouch db to run the database for logging
    """

    def __init__(self, replication=False, options=[]):
        """
        Constructor; takes a config keyword to see what mode to run it in
        'testing' ignores ssh spam you get
        """
        Thread.__init__(self)
        self.process = None
        self.running = True
        # Config Cariables
        self.port = options[0]
        self.conf = options[1]
        self.dbfolder = options[2]
        self.bindaddress = options[3]
        self.targetaddress = options[4]
        self.url = 'http://{}:{}/'.format(self.bindaddress, self.port)
        self.db_name = socket.gethostname() + "_logs"
        self.db_url = self.url + self.db_name
        self.replication = replication

        self.ready = False

    def createDatabase(self):
        """
        Create this device's log database
        """
        header = {"content-type": "application/json"}
        r = put(url=self.url + self.db_name,
                headers=header, verify=False, timeout=3)
        if (r.status_code != 201):
            Exception("Database could not be created")

        # Optional step for continuous
        header = {"content-type": "application/json"}

        payload = {
            "continuous": True,
            "create_target": True,
            "source": self.db_name,
            "target": self.targetaddress + self.db_name
        }

        if self.replication:
            res = post(url=self.url + '_replicate',
                       data=json.dumps(payload), headers=header, verify=False)
            print("Replication Status: \n%s" % res.json())

        return r

    def run(self):
        """
        Runs the thread, begins sniffing
        """
        # Setup files needed to run db
        # Path(self.dbfolder + '/log.txt').touch(mode=0o777, exist_ok=True)
        Path(self.dbfolder + '/log.txt').touch(mode=0o777, exist_ok=True)
        os.chmod(self.dbfolder + '/log.txt', 0o777)

        # toggle --in-memory to save data
        cmd = ["pouchdb-server", "--in-memory", "-n", "--dir", self.dbfolder,
               "--port", self.port, "--host", self.bindaddress, "--config", self.conf]
        self.process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=self.dbfolder)

        print("Waiting 5 seconds for DB to start")
        time.sleep(5)

        status = self.createDatabase()
        print("Handling DB: " + self.url + "_utils")
        print("Logging DB is: %s" % status.json())

        self.ready = True

        while self.running:
            output = self.process.stdout.readline()
            if output == '' and self.process.poll() is not None:
                break
            if output:
                print(output.decode("utf-8"))
        rc = self.process.poll()
        return rc

    def stop(self):
        """
        Toggles the running flag on the main loop
        """
        self.running = False
        self.process.kill()
