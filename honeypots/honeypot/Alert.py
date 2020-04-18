import json
from datetime import datetime

"""
Stores information to be propagated to the management system
"""


class Alert:
    """
    Initializes the alert with basic info
    variant - "admin", "meta", "alert"
    message - String giving more detail
    timestamp - epoch time of alert
    references - a list of related Traffic IDs, if applicable
    hostname - which honeypot this came from
    """
    __name__ = "Alert"

    def __init__(self, variant, message="", references=[], hostname="DefaultHostname"):
        self.variant = variant
        self.message = message
        self.timestamp = int(datetime.now().timestamp())
        self.references = references
        self.hostname = hostname

    def json(self):
        return json.dumps({
            "variant": self.variant,
            "message": self.message,
            "timestamp": self.timestamp,
            "references": self.references,
            "hostname": self.hostname
        })
