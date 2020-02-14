import json
from datetime import datetime

"""
Stores information to be propagated to the management system
"""
class Notification:
    """
    Initializes the notification with basic info
    variant - "admin", "meta", "alert"
    alertType - (optional) "portScan", "nmapScan",
    adminType - (optional) "configChange", "portChange",
    metaType - (optional) "crash",
    message - String giving more detail
    timestamp - epoch time of notification
    references - a list of related Traffic IDs, if applicable
    """
    def __init__(self, variant, alertType = None, adminType = None, metaType = None, message = "", references = None):
        self.variant = variant
        self.alertType = alertType
        self.adminType = adminType
        self.metaType = metaType
        self.message = message
        self.timestamp = int(datetime.now().timestamp())
        self.references = references

    def json(self):
      return json.dumps(self.__dict__)
