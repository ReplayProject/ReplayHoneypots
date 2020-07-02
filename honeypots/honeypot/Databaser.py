import json
import os
import socket

from cloudant.client import CouchDB

# from cloudant.replicator import Replicator

# Cloudant library Docs
# https://python-cloudant.readthedocs.io/en/stable/


class Databaser:
    """
    Use pouch db to run the database for logging
           Uses env Variables:
    DB_URL, and TARGET_ADDR
    """

    def __init__(self):
        """
        Initialize
        """
        self.hostname = socket.gethostname()
        self.db_name = "aggregate" + "_logs"
        self.alerts_name = "alerts"
        # Connect
        db_url = os.getenv("DB_URL")
        if db_url and db_url.strip() != "":
            creds = db_url.split("//")[1].split("@")[0].split(":")
            self.couch = CouchDB(creds[0], creds[1], url=db_url, connect=True)
            self.createDB()  # create the logging db for this device's logs
            # Decide if we should be replicating
            target = os.getenv("TARGET_ADDR")
            if target and target.strip() != "":
                print("Replication Disabled")  # self.startReplicate(target)

            print(
                "CouchDB Is connected to {} as {}".format(self.db_name, self.hostname)
            )
        else:
            print("No DB_URL provided, logging to stdout only")

    def startReplicate(self, target):
        """
        Attempt to setup replication
        """
        self.couch.replicate(
            self.db_name,
            target + "/" + self.db_name,
            options={"continuous": True, "create_target": True},
        )

        print("Replicating to:", target + self.db_name)

    def listDbs(self):
        """
        Get list of dbs
        """
        return [dbname for dbname in self.couch]

    def deleteDB(self):
        """
        Delete the database this host is bound to
        """
        # TODO: decide if this is needed (remove testing logs from db)
        print("Deletion like this disabled due to aggregate databases")
        # del self.couch[self.db_name]

    def createDB(self):
        """
        Create this device's log database
        """
        # Attempt Traffic DB creation
        self.couch[
            self.db_name
        ] if self.db_name in self.couch else self.couch.create_database(self.db_name)
        # Attempt Alerting DB Creation
        self.couch[
            self.alerts_name
        ] if self.alerts_name in self.couch else self.couch.create_database(
            self.alerts_name
        )

    def save(self, json_raw):
        """
        Save a json document
        """
        # Logic for live mode vs testing mode
        try:
            # TODO: should put extra test here
            db = self.couch[self.db_name]
            doc = db.create_document(json.loads(json_raw))
            print("Log created: %s" % doc["_id"])
            return doc["_id"]
        except Exception:
            print("DB Save Error:", json_raw)
            return None
        except AttributeError:
            print("Attr Warning:", json_raw)
            return None

    def alert(self, json_raw):
        """
        Save a json document (that is an alert)
        """
        # Logic for live mode vs testing mode
        try:
            db = self.couch[self.alerts_name]
            doc = db.create_document(json.loads(json_raw))
            print("Alert created: %s" % doc["_id"])
            return doc["_id"]
        except Exception:
            print("Alert DB Save Error:", json_raw)
            return None
        except AttributeError:
            print("Alert Attr Warning:", json_raw)
            return None
