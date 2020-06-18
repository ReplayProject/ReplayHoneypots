"""
This object contains information about a port
"""
import json


class Port:
    """
    This object contains information about each
    open port

    Args:
        portNumber : port number 1-65535
        service : service identifier string
    """

    def __init__(self, port, defaultData):
        self.port = port
        self.defaultData = defaultData

    """
    Sends back a repsonse to a query on the port
    #TODO: In the future this function could be changed to add more dynamic responses

    Returns:
        a data string
    """

    def response(self):
        return self.defaultData

    """
    Return the object in json format

    Returns:
        json format of port object
    """

    def get_json(self):
        return {"port": self.port, "defaultData": self.defaultData}

    def __str__(self):
        return "Port: " + str(self.port)
