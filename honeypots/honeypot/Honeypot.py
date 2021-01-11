"""
Stores information to be propagated to the system database
"""
import json


class Honeypot:
    """
    Initializes the honeypot record with basic info
    hostname - String hostname
    ipAddress - IP address of the honeypot
    uuid - uuid of the honeypot
    auth_group_id - the auth group assigned to the honeypot
        - defaults to "authGroupDefault"
    config_id - the config record assigned to the honeypot
        - defaults to "configdefault"
    """

    __name__ = "Honeypot"

    def __init__(
        self, uuid, ipAddress, authGroupID="Default-Aydindril", configID="configDefault",
    ):
        self._id = uuid
        self.ip_addr = ipAddress
        self.auth_group_id = authGroupID
        self.config_id = configID
        self.tags = []
        self.deleted = False

    def json(self):
        return json.dumps(self.__dict__)
