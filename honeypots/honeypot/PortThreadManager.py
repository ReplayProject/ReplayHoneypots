# python3 PortThreadManager.py
import json
import os

import trio
from functools import partial
import signal

from requests import get
import configparser
import argparse
from NmapParser import NmapParser
from Sniffer import Sniffer
from TCPPortListener import TCPPortListener
from UDPPortListener import UDPPortListener
from ConfigTunnel import ConfigTunnel
from Databaser import Databaser
from Alert import Alert

# default location that PortThreadManager will look for config options

configpath = os.getenv("HONEY_CFG")  # will usually be '/properties.cfg'
CONFIG_FILE_PATH = (
    configpath
    if (configpath and configpath.strip() != "")
    else r"../../config/honeypot.cfg"
)
"""
Handles the port threads to run the honeypot
"""


class PortThreadManager:
    """
    Initialize the response data and port list

    Args:
        portList: a list of int port numbers
    """

    def __init__(self):
        self.portList = []
        self.ip = str(get("https://api.ipify.org").text)
        self.processList = dict()
        # where the async sniffer will be located
        self.sniffer = None
        # delay specified by config file
        self.delay = None
        # whitelist of ports
        self.portWhitelist = None
        # whitelist of IPs
        self.whitelist = None
        # used to tell it to quit
        self.keepRunning = True
        # port for ConfigTunnel
        self.confport = None
        # certfile for ConfigTunnel
        self.confcert = None
        # list containing socket responses
        self.responseData = None
        self.configFilePath = None
        # database interface object
        self.db = Databaser()

    def getConfigTunnelData(self):
        config = configparser.RawConfigParser()
        config.read(CONFIG_FILE_PATH)
        # Configtunnel config options
        self.confport = config.get("ConfigTunnel", "port")
        self.confcert = config.get("ConfigTunnel", "cert_file")

    """
    Gets config information; ran when PortThreadManager configuration changes
    """

    def getConfigData(self):
        config = configparser.RawConfigParser()

        config.read(self.configFilePath)

        # A bunch of config options
        self.HONEY_IP = config.get("IPs", "honeypotIP")
        self.MGMT_IPs = json.loads(config.get("IPs", "managementIPs"))

        self.delay = config.get("Attributes", "delay")
        self.whitelist = json.loads(config.get("Whitelist", "addresses"))
        self.portWhitelist = json.loads(config.get("Whitelist", "whitelistedPorts"))

        # Gets a separate file
        dataFile = config.get("Attributes", "pcap_data_file")
        # Separate file contains socket response data
        with open(dataFile, "r") as responseDataFile:
            self.responseData = json.load(responseDataFile)

    """
    Start a thread for each port in the config file, connects to the database, runs sniffer class

    Returns: 0 if no changes
             1 if only Sniffer changed
             2 if only sockets changed
             3 if both changed
    """

    async def activate(
        self,
        propertiesFile=CONFIG_FILE_PATH,
        updateSniffer=False,
        updateOpenPorts=False,
        user="",
        task_status=trio.TASK_STATUS_IGNORED,
    ):
        self.configFilePath = propertiesFile

        # Gets the info from config file initially
        self.getConfigData()

        # Return code
        retCode = 0
        # Convience reference
        replayPorts = self.responseData.keys()

        with trio.CancelScope() as scope:
            # --- Start Async Sniffer ---#
            if self.sniffer == None:
                # TODO: Switch config="testing" to "base" when in production
                self.sniffer = Sniffer(
                    config="base",
                    openPorts=list(replayPorts),
                    whitelist=self.whitelist,
                    portWhitelist=self.portWhitelist,
                    honeypotIP=self.HONEY_IP,
                    managementIPs=self.MGMT_IPs,
                    databaser=self.db,
                )
                self.sniffer.start()
            elif updateSniffer == True:
                oldHash = self.sniffer.currentHash
                self.sniffer.configUpdate(
                    openPorts=list(replayPorts),
                    whitelist=self.whitelist,
                    portWhitelist=self.portWhitelist,
                    honeypotIP=self.HONEY_IP,
                    managementIPs=self.MGMT_IPs,
                )
                if not self.sniffer.currentHash == oldHash:
                    retCode = 1
            # Mark trio task as started
            task_status.started(scope)

            # --- Open Sockets - Disabled due to new TRIO API---#
            # On initial run
            # if (len(self.processList) == 0):
            #     for port in replayPorts:
            #         portThread = TCPPortListener(port, self.responseData[port]["TCP"],
            #                                   self.delay)
            #         portThread.daemon = True
            #         portThread.start()
            #         self.processList[port] = portThread

            # # Updating to new set of ports
            # elif (updateOpenPorts == True):
            #     #this value keeps track of if we've made changes
            #     portsAltered = False

            #     updatedPorts = list(tcp_sockets)
            #     updatedPorts.sort()
            #     currentPorts = list(self.processList.keys())
            #     currentPorts.sort()

            #     #we'll change things if these don't match
            #     if (not updatedPorts == currentPorts):
            #         portsAltered = True

            #     for p in currentPorts:
            #         if (not p in updatedPorts):
            #             self.processList[p].isRunning = False
            #             del self.processList[p]
            #         elif (not self.processList[p].response == self.responseData[p]["TCP"]
            #               ):
            #             #check if we need to alter response -- just change everything, might not matter
            #             self.processList[p].response = self.responseData[p]["TCP"]
            #             portsAltered = True

            #     for p in updatedPorts:
            #         if (not p in currentPorts):
            #             portThread = TCPPortListener(p, self.responseData[p]["TCP"],
            #                                       self.delay)
            #             portThread.daemon = True
            #             portThread.start()
            #             self.processList[p] = portThread

            #     if (portsAltered):
            #         retCode += 2

            # --- Open async UDP & TCP Sockets ---#
            udp_sockets = list(
                filter(lambda x: "UDP" in self.responseData[x].keys(), replayPorts)
            )
            tcp_sockets = list(
                filter(lambda x: "TCP" in self.responseData[x].keys(), replayPorts)
            )

            async def replay_server(listener_class, sockets, config_path, nursery):
                for port in sockets:
                    self.processList[port] = listener_class(
                        port, self.responseData[port][config_path], self.delay, nursery
                    )
                    nursery.start_soon(self.processList[port].handler)

            try:
                # --- Actually Start up listeners ---#
                async with trio.open_nursery() as nursery:
                    nursery.start_soon(
                        replay_server, UDPPortListener, udp_sockets, "UDP", nursery
                    )
                    nursery.start_soon(
                        replay_server, TCPPortListener, tcp_sockets, "TCP", nursery
                    )
            except Exception as ex:
                print("listener nursery exception: ", str(ex))
            finally:
                print("Listeners have been killed")

            # return the code here; 0 means no changes, 1 means only sniffer changed, 2 means only TCP ports were changed, 3 means both were changed
            if retCode == 1:
                self.db.alert(
                    Alert(
                        variant="admin",
                        message="Sniffer updated during runtime by " + user,
                        hostname=self.db.hostname,
                    ).json()
                )
            elif retCode == 2:
                self.db.alert(
                    Alert(
                        variant="admin",
                        message="TCP sockets updated during runtime by " + user,
                        hostname=self.db.hostname,
                    ).json()
                )
            elif retCode == 3:
                self.db.alert(
                    Alert(
                        variant="admin",
                        message="TCP sockets and Sniffer updated during runtime by "
                        + user,
                        hostname=self.db.hostname,
                    ).json()
                )
            elif retCode == 0:
                self.db.alert(
                    Alert(
                        variant="admin",
                        message="Attempted configuration change during runtime by "
                        + user,
                        hostname=self.db.hostname,
                    ).json()
                )
            return retCode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy the honeypot")
    parser.add_argument("-n", "--nmap", help="nmap file")
    args = parser.parse_args()

    portList = []
    if args.nmap:
        parser = NmapParser(args.nmap)
        portList = parser.getPorts()

    async def control_c_handler(nursery):
        with trio.open_signal_receiver(signal.SIGINT) as batched_signal_aiter:
            async for _ in batched_signal_aiter:
                print("\nAttempting graceful honeypot shutdown")
                nursery.cancel_scope.cancel()
                # We exit the loop, restoring the normal behavior of
                # control-C. This way hitting control-C once will try to
                # do a polite shutdown, but if that gets stuck the user
                # can hit control-C again to raise KeyboardInterrupt and
                # force things to exit.
                break

    manager = PortThreadManager()
    # initial creation alert
    manager.db.alert(
        Alert(
            variant="meta",
            message="Honeypot startup.",
            references=[],
            hostname=manager.db.hostname,
        ).json()
    )

    # --- ConfigTunnel - connection allows for live configuration options ---#
    manager.getConfigTunnelData()
    tunnel = ConfigTunnel("server", manager.confport, cafile=manager.confcert)
    tunnel.setHandler(
        "reconfigure", tunnel.relaytochannel
    )  # TODO: change when we have other tunnel actions to worry about

    async def main():
        async with trio.open_nursery() as nursery:
            # Get our CTRL-C handler, tunnel, and trio channels running
            nursery.start_soon(control_c_handler, nursery)

            send_channel, receive_channel = trio.open_memory_channel(0)
            nursery.start_soon(tunnel.listen, send_channel)
            everything_else = await nursery.start(
                partial(manager.activate, user="system")
            )
            # Respond to updates coming from tunnel
            async for command in receive_channel:
                print("config command {!r} received".format(command))

                everything_else.cancel()  # clean tasks
                manager.processList = dict()  # clean listener objects

                print("Reconfiguring Replay Manager: ", command)
                everything_else = await nursery.start(
                    partial(
                        manager.activate,
                        updateSniffer="sniff" in command,
                        updateOpenPorts="ports" in command,
                        user=command[-1] if "user" in command else "system",
                    )
                )

    trio.run(main)
