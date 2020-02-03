from datetime import date
from os import path
#import hpfeeds
import json
import configparser

"""
Holds the logs from the honeypot
"""


class DataLog:
    def __init__(self):
        self.logs = []

    """
    Returns:
        a list of log objects
    """

    def getLogs(self):
        return self.logs

    """
    Writes all of the current logs to a file
    """

    def writeLogs(self, filename):
        #d = str(date.today())
        #f = open('../logs/' + d + '.txt', 'a+')
        f = open(filename, 'a+')
        for log in self.logs:
            f.write(str(log.timestamp) + ' ' + str(log.sourceIPAddress) + ' ' +
                    str(log.sourcePortNumber) + ' ' + str(log.destIPAddress) + ' ' +
                    str(log.destPortNumber) + '\n')
        self.logs.clear()
        f.close()

    """
    Report logs to MHN using hpfeeds (Work in Progress)

    def reportLogs(self):
        # Get config info for hpfeeds client
        config = configparser.RawConfigParser()
        configFilePath = r'../config/properties.cfg'
        config.read(configFilePath)
        host = config.get('hpfeeds', 'host')
        port = config.get('hpfeeds', 'port')
        ident = config.get('hpfeeds', 'ident')
        secret = config.get('hpfeeds', 'secret')

        # Create a client object
        hpclient = hpfeeds.new(host, port, ident, secret)

        # Publish each event in the DataLog object
        for log in logs:
            # Normalize log to MHN session
            session = {
	            'timestamp': log.timestamp,
                'source_ip': log.sourceIPAddress,
                'source_port': int(log.sourcePortNumber),
                'destination_ip': 0,
                'destination_port': 0,
                'honeypot': 'prodhoneypot',
                'protocol': 'unknown'
            }
            hpclient.publish('prodhoneypot.events', json.dumps(session))
        hpclient.close()
    """
