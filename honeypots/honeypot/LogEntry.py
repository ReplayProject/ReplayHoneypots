"""
Holds logging information for local logs and Modern Honey Network
"""


class LogEntry:
    """
    Initializes the log entry with the basic info
    """

    def __init__(self, sourcePortNumber, sourceIPAddress, destPortNumber, destIPAddress, timestamp):
        self.sourcePortNumber = sourcePortNumber
        self.sourceIPAddress = sourceIPAddress
        self.destPortNumber = destPortNumber
        self.destIPAddress = destIPAddress
        self.timestamp = timestamp
