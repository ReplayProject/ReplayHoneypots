import json
from datetime import datetime

"""
Stores information to be propagated to the management system
"""


class Notification:
    """
    Initializes the notification with basic info
    variant - "admin", "meta", "alert"
    message - String giving more detail
    timestamp - epoch time of notification
    references - a list of related Traffic IDs, if applicable
    """
    __name__ = "Notification"

    def __init__(self, variant, message="", references=None, db_url=None):
        self.variant = variant
        self.message = message
        self.timestamp = int(datetime.now().timestamp())
        self.references = references
        self.db_url=None

    def json(self):
        return json.dumps({
            "variant": self.variant,
            "message": self.message,
            "timestamp": self.timestamp,
            "references": self.references
        })

    def post(self, payload):
        header = {"content-type": "application/json"}
        try:
            r = post(url=self.db_url, data=payload.json(),
                     headers=header, verify=False)
            log_id = r.json()["id"]
            #differentiates between different object types
            print("Notification created: %s" % log_id)
        except Exception:
            print("DB-Inactive: ", payload.json())