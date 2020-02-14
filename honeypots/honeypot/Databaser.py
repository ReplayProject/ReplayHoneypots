import os
from threading import Thread

"""
Use pouch db to run the database for loggins
"""


class Databaser(Thread):
    """
    Constructor; takes a config keyword to see what mode to run it in
    'testing' ignores ssh spam you get
    """

    def __init__(self):
        Thread.__init__(self)

    """
    Runs the thread, begins sniffing
    """

    def run(self):
        print("Handling DB: http://127.0.0.1:1437/_utils")
        PORT = 1437
        conf = "../config/dbconfig.json"
        dbfolder = "../database"
        bindaddress = "127.0.0.1"
        # toggle --in-memory to save data
        template = "pouchdb-server --in-memory -n --dir {} --port {} --host {} --config {}"
        cmd = template.format(dbfolder, PORT, bindaddress, conf)
        os.system(cmd)
