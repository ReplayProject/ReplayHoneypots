import json
from datetime import datetime

"""
Holds logging information for local logs and Modern Honey Network
"""


class LogEntry:
    """
    Initializes the log entry with the basic info
    """

    __name__ = "LogEntry"

    def __init__(self, sourcePortNumber, sourceIPAddress, sourceMAC, destPortNumber, destIPAddress, destMAC, trafficType, isPortOpen):
        self.sourcePortNumber = sourcePortNumber
        self.sourceIPAddress = sourceIPAddress
        self.sourceMAC = sourceMAC
        self.destPortNumber = destPortNumber
        self.destIPAddress = destIPAddress
        self.destMAC = destMAC
        self.timestamp = int(datetime.now().timestamp())
        self.trafficType = trafficType
        self.isPortOpen = isPortOpen

    def json(self):
        return json.dumps(self.__dict__)
