import os
import couchdb
import socket
import json


# Couchdb Tutorial
# https://gist.github.com/marians/8e41fc817f04de7c4a70
# Actual Docs
# https://couchdb-python.readthedocs.io/en/latest/
class Databaser():
    """
    Use pouch db to run the database for logging
    Uses env Variables:
    DB_URL, and TARGET_ADDR
    """
    def __init__(self):
        """
        Initialize
        """
        self.db_name = socket.gethostname() + "_logs"
        # Connect
        db_url = os.getenv('DB_URL')
        if (db_url and db_url.strip() != ""):
            self.couch = couchdb.Server(db_url)
            self.createDB()  # create the logging db for this device's logs

            # Decide if we should be replicating
            target = os.getenv("TARGET_ADDR")
            if (target and target.strip() != ""):
                self.startReplicate(target)

            print("CouchDB Is connected with version ", self.couch.version())
        else:
            print("No DB_URL provided, logging to stdout only")

    def startReplicate(self, target):
        """
        Attempt to setup replication
        """
        self.couch.replicate(self.db_name,
                             target + "/" + self.db_name,
                             options={
                                 "continuous": True,
                                 "create_target": True
                             })

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
        del self.couch[self.db_name]

    def createDB(self):
        """
        Create this device's log database
        """
        # Attempt DB creation
        if self.db_name in self.couch:
            db = self.couch[self.db_name]
        else:
            db = self.couch.create(self.db_name)

    def save(self, json_raw):
        """
        Save a json document
        """
        # Logic for live mode vs testing mode
        try:
            # TODO: should put extra test here
            db = self.couch[self.db_name]
            doc_id, doc_rev = db.save(json.loads(json_raw))
            print("Log created: %s" % doc_id)
            return doc_id
        except Exception as e:
            # print(str(e))
            print("DB Save Error:", json_raw)
            return None
        except AttributeError:
            print("Attr Warning:", json_raw)
            return None
