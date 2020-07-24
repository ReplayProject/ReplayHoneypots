"""
Stores information to be propagated to the management system
"""
import json
from datetime import datetime


class Alert:
    """
    Initializes the alert with basic info
    variant - "admin", "meta", "alert"
    message - String giving more detail
    timestamp - epoch time of alert
    references - a list of related Traffic IDs, if applicable
    hostname - which honeypot this came from
    UUID - what unique honeypot this alert originated from
    """

    __name__ = "Alert"

    def __init__(
        self, variant, message="", references=None,
    ):
        self.variant = variant
        self.message = message
        self.timestamp = int(datetime.now().timestamp())
        self.references = [] if references is None else references

    def json(self):
        return json.dumps(self.__dict__)
