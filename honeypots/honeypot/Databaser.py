import atexit
import json
import os
import socket
import sys
import time
import uuid
import psutil
from pprint import pprint

import trio
from cloudant.client import CouchDB
from cloudant.document import Document
from Honeypot import Honeypot
from DeviceMetrics import DeviceMetrics

# from cloudant.replicator import Replicator

# Cloudant library Docs
# https://python-cloudant.readthedocs.io/en/stable/

DEFAULT_CONFIG_DEFAULT_ID = "configDefault"
# The number of seconds between each time the honeypot checks for a config assignment or config data change
DEFAULT_WAIT_TIME_BETWEEN_UPDATE_CHECKS = 1
# The number of times the honeypot should check for updates between each database tie check. Can be relatively high given an appropriate update check interval
DEFAULT_UPDATE_CHECKS_BETWEEN_DATABASE_TIE_CHECKS = 5
# The amount of time that context manager gets will wait on a failure loop
DEFAULT_CONTEXT_MANAGER_RETRY_WAIT = 5

ONE_MINUTE_IN_SECONDS = 60

class Databaser:
    """
    Use cloudant to interface with the database for logging and configuration
    Uses env Variables: DB_URL, TARGET_ADDR, and AM_I_IN_A_DOCKER_CONTAINER
    """

    def __init__(self, test=False):
        """
        Initialize variables and setup device "identity"
        """
        # Status indicator for the database connection as a whole
        self.down = True

        self.uuid = self.claimUUID()
        self.hostname = socket.gethostname()
        self.logs_db = "aggregate" + "_logs"
        self.alerts_db = "alerts"
        self.config_db = "configs"
        self.honeypot_db = "honeypots"
        self.metrics_db = "metrics"
        self.config_doc = None

        # If in test mode, dont touch the real databases
        self.test = test
        # if self.test:
        #     self.logs_db += "_test"
        #     self.alerts_db += "_test"
        #     self.config_db += "_test"
        #     self.honeypot_db += "_test"
        #     self.metrics_db += "_test"
            
        # Connect to the database
        db_url = os.getenv("DB_URL")
        if db_url and db_url.strip() != "":
            host = db_url.split("@")[1].split(":")[0]
            self.db_ip = socket.gethostbyname(host)
            print("Database IP:", self.db_ip)
        else:
            raise Exception("DB_URL not provided.")

        # Get fresh context manager
        self.couch = self.getContextManager(True)
        atexit.register(self.shutdownDB)
        self.createDB()
        self.tieToDatabase()
        # TODO: Decide if we should be replicating, and what policy we should use
        target = os.getenv("TARGET_ADDR")
        if target and target.strip() != "":
            print("Replication Disabled")
            # self.startReplicate(target)

        print("CouchDB Is connected to {} as {}".format(self.logs_db, self.hostname))

    ########## --------------------------------------------------- ##########
    ########## ------ DB System Management Functions / Code ------ ##########
    ########## --------------------------------------------------- ##########

    def getContextManager(self, isOnBoot=False):
        db_url = os.getenv("DB_URL")
        if db_url and db_url.strip() != "":
            creds = db_url.split("//")[1].split("@")[0].split(":")
            while self.down:
                try:
                    db = CouchDB(
                        creds[0],
                        creds[1],
                        url=db_url,
                        connect=True,
                        auto_renew=True,
                        timeout=20,
                    )
                    print("DATABASE UP: Database connection recovered.")
                    self.down = False
                    return db
                except Exception as e:

                    if self.test:
                        raise e

                    if isOnBoot:
                        print(e)
                        print("Database is not available on boot. Entering dead spin. No services online.")
                        time.sleep(DEFAULT_CONTEXT_MANAGER_RETRY_WAIT)
                        self.down = True
                    else:
                        time.sleep(DEFAULT_CONTEXT_MANAGER_RETRY_WAIT)
        else:
            raise Exception("DB_URL not provided.")

    def shutdownDB(self):
        print("Shutting down Database connection")
        self.couch.disconnect()

    # def merge(self, source, destination):
    #     """
    #     Recursive deepmerge
    #     """
    #     for key, value in source.items():
    #         if isinstance(value, dict):
    #             node = destination.setdefault(key, {})
    #             self.merge(value, node)
    #         else:
    #             destination[key] = value
    #     return destination

    # def startReplicate(self, target):
    #     """
    #     Attempt to setup replication
    #     TODO: test replication
    #     """
    #     raise Exception("Replication not Implemented/Tested")
    #     self.couch.replicate(
    #         self.logs_db,
    #         target + "/" + self.logs_db,
    #         options={"continuous": True, "create_target": True},
    #     )

    #     print("Replicating to:", target + self.logs_db)

    def listDbs(self):
        """
        Get list of dbs
        """
        return [dbname for dbname in self.couch]

    def deleteDB(self):
        """
        Delete the databases this host is depending on
        """
        if not self.test:
            print("DB Deletion disabled due to use of aggregate databases")
            return
        # Attempt deletion of each required DB
        for db in [self.logs_db, self.alerts_db, self.config_db]:
            self.couch.delete_database(db)

    def createDB(self):
        """
        Create the databases this host is depending on
        """
        # Attempt creation of each required DB
        for db in [self.logs_db, self.alerts_db, self.config_db, self.honeypot_db]:
            self.couch[db] if db in self.couch else self.couch.create_database(db)

    ########## ---------------------------------------------------- ##########
    ########## ------ Object Lifecycle Mgmt Functions / Code ------ ##########
    ########## ---------------------------------------------------- ##########

    def save_document(self, document, db_url, doc_type):
        """
        General function to save alerts and logs
        """
        # If database connection is down, skip
        if self.down:
            print("Database connection is down. Skipping document save.")
            return None

        # Add the hostname and uuid into the log
        document.hostname = self.hostname
        document.uuid = self.uuid

        # Logic for live mode vs testing mode (stdout)
        try:
            db = self.couch[db_url]
            doc = db.create_document(json.loads(document.json()))
            # print(doc_type, "created: %s" % doc["_id"])
            # pprint(vars(document))
            return doc["_id"]
        except AttributeError:
            print("Attr Warning:", document.json())
            return None
        except Exception:
            print("DB Save Error:", document.json())
            print("Setting database to down state due to error.")
            self.down = True
            return None

    def saveLogObject(self, json):
        """
        Save a JSON document to the logs DB
        """
        return self.save_document(json, self.logs_db, 'Log')

    def saveAlertObject(self, json):
        """
        Save a JSON document to the alerts DB
        """
        return self.save_document(json, self.alerts_db, 'Alert')

    def saveMetricsObject(self):
        """
        Save a JSON document to the metrics DB
        """
        # toal cpu usage of the device(percentage)
        cpu_usage = psutil.cpu_percent(interval=1)
        # virtual memery usage of the device(percentage)
        ram = psutil.virtual_memory().percent
        # disk storage available of the device(GiB)
        raw_storage = psutil.disk_usage('/').free // (2**30)
        # set the decimal place to 2
        Gib_storage = float("{:.2f}".format(raw_storage))

        # check input
        if self.hostname and 0 <= cpu_usage <= 100 and 0 <= ram <= 100 and 0 <= Gib_storage and uuid.UUID(self.uuid):
            metrics = DeviceMetrics(self.uuid, self.hostname,cpu_usage,ram,Gib_storage)
            return self.save_document(metrics, self.metrics_db, 'Metric')
        else:
            raise Exception("Validation error: invalid input for device metrics. CPU:", cpu_usage, "RAM:", ram, "Storage:", Gib_storage, "UUID:", self.uuid)

    ########## -------------------------------------------------- ##########
    ########## ------ Honeypot Management Functions / Code ------ ##########
    ########## -------------------------------------------------- ##########

    def claimUUID(self):
        """
        Check if this device has been marked with a UUID,
        and if not, will generate and mark by creating an
        ID file in the appropriate location
        """
        device_uuid = None
        # ENV variable & volume set in replay-honeypot Dockerfile
        is_docker = os.environ.get("AM_I_IN_A_DOCKER_CONTAINER", False)
        tagpath = ("/storage/" if is_docker else "./") + "RPHP-UUID"

        exists = os.path.exists(tagpath)
        mode = "r" if exists else "w"
        # Either read or generate UUID file
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

    def tieToDatabase(self):
        """
        Check if this device record (based on UUID) exists in the database.
        If not, create a new DB record for the honeypot.
        """
        thrownToPreventSave = False
        database = self.couch[self.honeypot_db]
        try:
            with Document(database, self.uuid) as honeypotObj:
                changed = False
                if honeypotObj.exists():
                    if honeypotObj["hostname"] != self.hostname:
                        honeypotObj["hostname"] = self.hostname
                        print("Honeypot record updated due to hostname change.")
                        changed = True
                    if honeypotObj["deleted"]:
                        honeypotObj["deleted"] = False
                        print("Honeypot record updated due to rewake of a deleted HP.")
                        changed = True
                    ipAddress = socket.gethostbyname(self.hostname)
                    if honeypotObj["ip_addr"] != ipAddress:
                        honeypotObj["ip_addr"] = ipAddress
                        print("Honeypot record updated due to IP change.")
                        changed = True
                    if not changed:
                        thrownToPreventSave = True
                        raise Exception(
                            "No changes made in context manager - no need to save to DB"
                        )
                else:
                    # Honeypot not in system - create new record
                    hpRecord = Honeypot(self.uuid, socket.gethostbyname(self.hostname))
                    hpRecord.hostname = self.hostname

                    try:
                        honeypotObj["ip_addr"] = hpRecord.ip_addr
                        honeypotObj["auth_group_id"] = hpRecord.auth_group_id
                        honeypotObj["config_id"] = hpRecord.config_id
                        honeypotObj["tags"] = [hpRecord.config_id]
                        honeypotObj["deleted"] = False
                        honeypotObj["hostname"] = hpRecord.hostname
                        print("Honeypot record created for: %s" % self.uuid)
                    except AttributeError as aE:
                        print("HP Attr Warning:", aE, hpRecord.json())
                        sys.exit(1)
                    except Exception as e:
                        print(
                            "HP DB Save Error:", hpRecord.json(), "Exception:", str(e)
                        )
                        sys.exit(1)
        except Exception as e:
            if not thrownToPreventSave:
                pprint(e)
                self.down = True

    def updateTags(self, removeTag, addTag):
        """
        Remove the removeTag from the list of tags on this device, and
        add the new addTag. Handles boundary cases for things being missing
        when expected or present when not expected.
        """
        thrownToPreventSave = False
        database = self.couch[self.honeypot_db]
        try:
            with Document(database, self.uuid) as honeypotObj:
                changed = False
                if honeypotObj.exists():
                    if removeTag != None and removeTag in honeypotObj["tags"]:
                        # Remove the tag from the list
                        honeypotObj["tags"].remove(removeTag)
                        print("Tag " + removeTag + " removed from honeypot " + self.uuid)
                        changed = True
                    if addTag != None and not addTag in honeypotObj["tags"]:
                        # Add the new tag to the list
                        honeypotObj["tags"].append(addTag)
                        print("Tag " + removeTag + " added to honeypot " + self.uuid)
                        changed = True
                    if not changed:
                        thrownToPreventSave = True
                        raise Exception(
                            "No changes made in context manager - no need to save to DB"
                        )
                else:
                    # TODO: Handle more
                    print("Honeypot found to not exist when updating tags. Exiting.")
                    sys.exit(1)
        except Exception as e:
            if not thrownToPreventSave:
                pprint(e)
                self.down = True

    async def waitBasedOnConfiguration(self, default, configFieldName):
        """
        Waits for a set amount of time.
        If the config does not contain the given field,
        the wait is done with the default time
        """
        configValue = self.couch[self.honeypot_db][self.uuid][configFieldName]
        if not configValue == None and isinstance(configValue, int):
            await trio.sleep(configValue)
        else:
            await trio.sleep(default)

    ########## --------------------------------------------- ##########
    ########## ------ Config Related Functions / Code ------ ##########
    ########## --------------------------------------------- ##########

    def getConfig(self):
        thrownToPreventSave = False
        configNotFound = False
        returnConfig = None
        hpDatabase = self.couch[self.honeypot_db]
        conDatabase = self.couch[self.config_db]
        try:
            with Document(hpDatabase, self.uuid) as honeypotObj:
                if honeypotObj.exists():
                    try:
                        with Document(
                            conDatabase, honeypotObj["config_id"]
                        ) as configObj:
                            if configObj.exists():
                                returnConfig = configObj
                                thrownToPreventSave = True
                                raise Exception("Config exists, but will receive a update if we do not throw this")
                            else:
                                thrownToPreventSave = True
                                configNotFound = True
                                raise Exception("No config exists in context manage - do not create it")
                    except Exception as iE:
                        if not thrownToPreventSave:
                            # print(iE)
                            raise iE
                        elif configNotFound:
                            print("ERROR: Could not fetch configuration. (", honeypotObj["config_id"], ") Setting to default.")
                            self.setConfig(DEFAULT_CONFIG_DEFAULT_ID)
                            returnConfig = self.getConfig()
                            thrownToPreventSave = True
                            raise Exception("Preventing honeypot save")
                        else:
                            # Error is the normal flow, where we only have
                            # to raise an exception to avoid save
                            raise iE
                else:
                    print("ERROR: Could not fetch honeypot.")
                    sys.exit(1)
        except Exception as oE:
            if not thrownToPreventSave:
                # print(oE)
                raise oE
            else:
                # Normal flow that simply protects against unneeded save
                return returnConfig

    def setConfig(self, newConfigID):
        thrownToPreventSave = False
        updateHP = False
        try:
            with Document(self.couch[self.honeypot_db], self.uuid) as honeypotObj:
                if honeypotObj.exists():
                    try:
                        with Document(
                            self.couch[self.config_db], newConfigID
                        ) as configObj:
                            if configObj.exists():
                                honeypotObj["config_id"] = newConfigID
                                updateHP = True
                                thrownToPreventSave = True
                                raise Exception("Preventing config object save")
                            else:
                                thrownToPreventSave = True
                                raise Exception(
                                    "No config exists in context manager "
                                    + "- do not create it"
                                )
                    except Exception as iE:
                        if not thrownToPreventSave:
                            # print(iE)
                            raise iE
                        elif not updateHP:
                            print("ERROR: Could not fetch configuration. (", honeypotObj["config_id"], ") Setting to default.")
                            time.sleep(5) # Sleep here to throttle the constant repolling in a case where default config got deleted, etc.
                            self.setConfig(DEFAULT_CONFIG_DEFAULT_ID)
                            raise Exception("Preventing honeypot save")
                else:
                    print("ERROR: Could not fetch honeypot.")
                    sys.exit(1)
        except Exception as oE:
            if not thrownToPreventSave:
                # print(oE)
                raise oE
            else:
                # Normal flow that simply protects against unneeded save
                pass

    async def watchConfig(self, channel):
        """
        Read from DB changes and trigger a reconfiguration on the PTM
        using TRIO channels for communication
        """
        config_db = self.couch[self.config_db]
        honeypot_db = self.couch[self.honeypot_db]

        loopIndex = 0
        async with channel:
            sinceFrame1 = 0
            sinceFrame2 = 0
            while True:
                if not self.down:
                    # Check to see if the database contains an entry tied to this honeypot
                    if loopIndex > 0 and loopIndex % DEFAULT_UPDATE_CHECKS_BETWEEN_DATABASE_TIE_CHECKS == 0:
                        self.tieToDatabase()

                    # Main change detection loop
                    try:
                        updatedAssignment = False
                        honeypot_changes = honeypot_db.changes(
                            since=sinceFrame1,
                            style="main_only",
                            include_docs=True,
                            filter="_doc_ids",
                            doc_ids=[self.uuid],
                        )
                        await trio.sleep(0)  # provide a cancellation checkpoint
                        # Handle any changes
                        for honeypotChange in honeypot_changes:
                            sinceFrame1 = honeypotChange["seq"]
                            newConfigID = honeypotChange["doc"]["config_id"]
                            oldConfigID = self.couch[self.honeypot_db][self.uuid]["config_id"]
                            if newConfigID != oldConfigID:
                                print("Detected Change in Honeypot Config assignment. Sending Reconfig.")
                                # Change the local assignments
                                # and pull the new config
                                self.couch[self.honeypot_db][self.uuid] = honeypotChange["doc"]
                                self.setConfig(newConfigID)
                                # this is using the same syntax as the CLI
                                # but PTM does not care
                                await channel.send("reconfigure sniff ports user CouchDB")
                                self.updateTags(oldConfigID, newConfigID)
                                updatedAssignment = True
                            await trio.sleep(0)  # provide a cancellation checkpoint
                        # Do not process a config update
                        # immediately if just reset assignment
                        if not updatedAssignment:
                            # Watch for changes to the configuration object itself
                            config_changes = config_db.changes(
                                since=sinceFrame2,
                                style="main_only",
                                include_docs=True,
                                filter="_doc_ids",
                                doc_ids=[
                                    self.couch[self.honeypot_db][self.uuid]["config_id"]
                                ],
                            )
                            await trio.sleep(0)  # provide a cancellation checkpoint
                            # Handle any changes
                            for configChange in config_changes:
                                sinceFrame2 = configChange["seq"]
                                configID = self.couch[self.honeypot_db][self.uuid]["config_id"]
                                if self.couch[self.config_db][configID]["_rev"] != configChange["doc"]["_rev"]:
                                    self.couch[self.config_db][configID] = configChange["doc"]
                                    print("Detected Change in Config Settings. Sending Reconfig.")
                                    # this is using the same syntax as the CLI
                                    # but PTM does not care
                                    await channel.send("reconfigure sniff ports user CouchDB")
                                await trio.sleep(0)  # provide a cancellation checkpoint
                    except Exception as e:
                        print("DATABASE DOWN: Setting database to down state. ERR:", e)
                        self.down = True
                else:
                    self.couch = self.getContextManager()
                    self.tieToDatabase()
                loopIndex += 1
                configID = self.couch[self.honeypot_db][self.uuid]["config_id"]
                configWaitValue = self.couch[self.config_db][configID]["update_interval"]
                if configWaitValue != None:
                    await trio.sleep(int(configWaitValue) * ONE_MINUTE_IN_SECONDS)
                else:
                    await trio.sleep(DEFAULT_WAIT_TIME_BETWEEN_UPDATE_CHECKS * ONE_MINUTE_IN_SECONDS)
