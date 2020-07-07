import json
import os
import socket
import uuid

import trio
from cloudant.client import CouchDB
from cloudant.document import Document

# from cloudant.replicator import Replicator

# Cloudant library Docs
# https://python-cloudant.readthedocs.io/en/stable/


class Databaser:
    """
    Use pouch db to run the database for logging
           Uses env Variables:
    DB_URL, and TARGET_ADDR
    """

    def __init__(self, test=False):
        """
        Initialize
        """
        self.uuid = self.claimUUID()
        self.hostname = socket.gethostname()
        self.logs_db = "aggregate" + "_logs"
        self.alerts_db = "alerts"
        self.config_db = "configs"
        self.config_doc = None

        self.test = test
        if self.test:
            self.logs_db += "_test"
            self.alerts_db += "_test"
            self.config_db += "_test"

        # Connect to the database
        db_url = os.getenv("DB_URL")
        if db_url and db_url.strip() != "":
            creds = db_url.split("//")[1].split("@")[0].split(":")
            self.couch = CouchDB(
                creds[0], creds[1], url=db_url, connect=True, auto_renew=True
            )
            self.createDB()
            # Decide if we should be replicating
            target = os.getenv("TARGET_ADDR")
            if target and target.strip() != "":
                print("Replication Disabled")  # self.startReplicate(target)

            print(
                "CouchDB Is connected to {} as {}".format(self.logs_db, self.hostname)
            )
        else:
            print("No DB_URL provided, logging to stdout only")

    def merge(self, source, destination):
        for key, value in source.items():
            if isinstance(value, dict):
                # get node or create one
                node = destination.setdefault(key, {})
                self.merge(value, node)
            else:
                destination[key] = value
        return destination

    def startReplicate(self, target):
        """
        Attempt to setup replication
        TODO: test this explicitly
        """
        self.couch.replicate(
            self.logs_db,
            target + "/" + self.logs_db,
            options={"continuous": True, "create_target": True},
        )

        print("Replicating to:", target + self.logs_db)

    def listDbs(self):
        """
        Get list of dbs
        """
        return [dbname for dbname in self.couch]

    def deleteDB(self):
        """
        Delete the database this host is bound to
        """
        if not self.test:
            print("Deletion like this disabled due to aggregate databases")
            return
        # Attempt deletion of each required DB
        for db in [self.logs_db, self.alerts_db, self.config_db]:
            self.couch.delete_database(db)

    def createDB(self):
        """
        Create this device's log database
        """
        # Attempt creation of each required DB
        for db in [self.logs_db, self.alerts_db, self.config_db]:
            self.couch[db] if db in self.couch else self.couch.create_database(db)

    def save(self, json_raw):
        """
        Save a json document
        """
        # Logic for live mode vs testing mode
        try:
            # TODO: should put extra test here
            db = self.couch[self.logs_db]
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
            db = self.couch[self.alerts_db]
            doc = db.create_document(json.loads(json_raw))
            print("Alert created: %s" % doc["_id"])
            return doc["_id"]
        except Exception:
            print("Alert DB Save Error:", json_raw)
            return None
        except AttributeError:
            print("Alert Attr Warning:", json_raw)
            return None

    def claimUUID(self):
        """
        this function will check if this honeypot has been marked with a UUID,
        and if not, will generate and mark by creating an ID file
        """
        device_uuid = None
        tagpath = "RPHP-UUID"

        exists = os.path.exists(tagpath)
        mode = "r" if exists else "w"
        with open(tagpath, mode) as f:
            if exists:
                device_uuid = f.readline()
                print("Honeypot tagged as:", device_uuid)
            else:
                device_uuid = uuid.uuid4().hex
                print("Honeypot UUID generated:", device_uuid)
                f.write(device_uuid)

        if device_uuid is None:
            raise Exception("Honeypot UUID could not be generated or claimed")

        return device_uuid

    def getConfig(self):
        """
        Get configuration from the database, and store in self
        """
        db = self.couch[self.config_db]
        conf_id = "HP-" + self.uuid
        default_conf_id = "HP-default"

        # Check if this honeypot's unique config exists
        if conf_id in db:
            db[conf_id].fetch()
            self.config_doc = db[conf_id]
            # do validity checks on the configuration
            # TODO: decide if this should be on couchdb's side

            c = self.config_doc

            if not (
                "attributes" in c
                and "allowlist" in c
                and "ip_addresses" in c
                and "configtunnel" in c
                and "response_delay" in c["attributes"]
                and "port_scan_window" in c["attributes"]
                and "port_scan_sensitivity" in c["attributes"]
            ):
                raise Exception("Invalid configuration received")

            print("Honeypot config loaded")
            return self.config_doc
        else:
            # Create initial/default config
            # But check if DB default exists first
            if default_conf_id not in db:
                with open("../../config/defaults.json") as f:
                    with Document(db, default_conf_id) as document:
                        self.merge(json.load(f), document)

            default = db[default_conf_id]
            default["_id"] = conf_id
            del default["_rev"]

            self.config_doc = db.create_document(default)

            if self.config_doc.exists():
                print("Honeypot config created from defaults")
            else:
                raise Exception("Honeypot config, was unable to be generated.")

            return self.config_doc

    async def watchConfig(self, channel):
        """
        Read from DB changed and trigger a reconfiguration on the PTM
        (use TRIO channels for communication)
        """
        db = self.couch[self.config_db]
        conf_id = "HP-" + self.uuid

        print("Listening for configuration changes on:", conf_id)
        async with channel:
            while True:
                # TODO: may want to refactor if fixing the CTRL-C delay is a priority
                changes = db.infinite_changes(
                    heartbeat=3000,
                    since="now",
                    include_docs=True,
                    filter="_doc_ids",
                    doc_ids=[conf_id],
                )
                await trio.sleep(0)  # provide a cancellation checkpoint
                for change in changes:
                    if change:
                        self.config_doc = change["doc"]
                        # this is using the same syntax as the CLI
                        # but PTM does not care
                        print("Honeypot config changed from couchdb:", change)
                        await channel.send("reconfigure sniff ports user CouchDB")
                        continue
                    await trio.sleep(1)  # provide a cancellation checkpoint
                changes.stop()
