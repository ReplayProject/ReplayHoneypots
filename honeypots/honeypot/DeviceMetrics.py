import json
import psutil
import os
import socket
import http.client
import uuid
from datetime import datetime


class DeviceMetrics:
    def __init__(self, uuid=None, hostname='', cpu=0, ram=0, storage=0):
        self.uuid = uuid
        self.hostname = hostname
        self.timestamp = int(datetime.now().timestamp())
        self.cpu = cpu
        self.ram = ram
        self.storage = storage

    def json(self):
        return json.dumps(self.__dict__)

    def validate(self):
        if not self.hostname or 0 > self.cpu or self.cpu > 100 or 0 > self.ram or self.ram > 100 or 0 > self.storage or not uuid.UUID(self.uuid):
            raise Exception("Invalid input for device metrics(e.g. negative usage, null hostname")
        else:
            return True
