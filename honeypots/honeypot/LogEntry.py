import json
from datetime import datetime

"""
Holds logging information for local logs and Modern Honey Network
"""


class LogEntry:
    """
    Initializes the log entry with the basic info
    """

    def __init__(self, sourcePortNumber, sourceIPAddress, destPortNumber, destIPAddress, trafficType, isPortOpen):
        self.sourcePortNumber = sourcePortNumber
        self.sourceIPAddress = sourceIPAddress
        self.destPortNumber = destPortNumber
        self.destIPAddress = destIPAddress
        self.timestamp = int(datetime.now().timestamp())
        self.trafficType = trafficType
        self.isPortOpen = isPortOpen

    def json(self):
        return json.dumps(self.__dict__)
