"""
Handles the modules and logic to run the honeypot
  Usage: python3 -u ./PortThreadManager.py
"""
import argparse
import configparser
import json
import os
import signal
from functools import partial

import trio
from Alert import Alert
from ConfigTunnel import ConfigTunnel
from Databaser import Databaser
from NmapParser import NmapParser
from requests import get
from Sniffer import Sniffer
from TCPPortListener import TCPPortListener
from UDPPortListener import UDPPortListener


class PortThreadManager:
    """
    Initialize the response data and port list

    Args:
        portList: a list of int port numbers
    """

    def __init__(self):
        self.portList = []
        # self.ip = str(get("https://api.ipify.org").text)
        self.processList = dict()
        # where the async sniffer will be located
        self.sniffer = None
        # delay specified by config file
        self.response_delay = None
        # whitelist of ports
        self.portWhitelist = None
        # whitelist of IPs
        self.whitelist = None
        # used to tell it to quit
        # self.keepRunning = True
        # port for ConfigTunnel
        self.confport = None
        # certfile for ConfigTunnel
        self.confcert = None
        # list containing socket responses
        self.responseData = None
        # database interface object
        self.db = Databaser()

    def getConfigTunnelData(self):
        conf = self.db.getConfig()

        # Configtunnel config options
        self.confport = conf["configtunnel"]["port"]
        self.confcert = conf["configtunnel"]["cert_file"]

    """
    Gets config information; ran when PortThreadManager configuration changes
    """

    def getConfigData(self):
        conf = self.db.getConfig()

        # A bunch of config options
        self.HONEY_IP = conf["ip_addresses"]["honeypotIP"]
        self.MGMT_IPs = conf["ip_addresses"]["managementIPs"]
        self.response_delay = float(conf["attributes"]["response_delay"])
        self.port_scan_window = int(conf["attributes"]["port_scan_window"])
        self.port_scan_sensitivity = int(conf["attributes"]["port_scan_sensitivity"])

        self.whitelist = conf["allowlist"]["addresses"]
        self.portWhitelist = conf["allowlist"]["ports"]
        self.responseData = conf["response_config"]

    """
    Start a thread that does the following
    - for each port in the config file
    - connects to the database
    - runs sniffer class

    Returns: 0 if no changes
             1 if only Sniffer changed
             2 if only sockets changed
             3 if both changed
    """

    async def activate(
        self,
        updateSniffer=False,
        updateOpenPorts=False,
        user="",
        task_status=trio.TASK_STATUS_IGNORED,
    ):
        # Gets the info from config file initially
        self.getConfigData()

        # Return code
        retCode = 0
        # Convience reference
        replayPorts = self.responseData.keys()

        with trio.CancelScope() as scope:
            # --- Start Async Sniffer ---#
            if self.sniffer is None:
                # TODO: Switch config="testing" to "base" when in production
                self.sniffer = Sniffer(
                    config="base",
                    openPorts=list(replayPorts),
                    whitelist=self.whitelist,
                    portWhitelist=self.portWhitelist,
                    honeypotIP=self.HONEY_IP,
                    managementIPs=self.MGMT_IPs,
                    port_scan_window=self.port_scan_window,
                    port_scan_sensitivity=self.port_scan_sensitivity,
                    databaser=self.db,
                )
                self.sniffer.start()
            elif updateSniffer:
                oldHash = self.sniffer.currentHash
                self.sniffer.configUpdate(
                    openPorts=list(replayPorts),
                    whitelist=self.whitelist,
                    portWhitelist=self.portWhitelist,
                    honeypotIP=self.HONEY_IP,
                    managementIPs=self.MGMT_IPs,
                    port_scan_window=self.port_scan_window,
                    port_scan_sensitivity=self.port_scan_sensitivity,
                )
                if not self.sniffer.currentHash == oldHash:
                    retCode = 1
            # Mark trio task as started
            task_status.started(scope)

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
                        port,
                        self.responseData[port][config_path],
                        self.response_delay,
                        nursery,
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

            # return the code here;
            # 0 means no changes,
            # 1 means only sniffer changed,
            # 2 means only TCP ports were changed,
            # 3 means both were changed
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
    # manager.getConfigTunnelData()
    # tunnel = ConfigTunnel(
    #     "server",
    #     manager.confport,
    #     cafile=None if manager.confcert == "" else manager.confcert,
    # )
    # tunnel.setHandler(
    #     "reconfigure", tunnel.relaytochannel
    # )  # TODO: change when we have other tunnel actions to worry about

    async def main():
        async with trio.open_nursery() as nursery:
            # Get our CTRL-C handler, tunnel, and trio channels running
            nursery.start_soon(control_c_handler, nursery)

            send_channel, receive_channel = trio.open_memory_channel(0)
            async with send_channel, receive_channel:
                # Start the configtunnel listener
                # nursery.start_soon(tunnel.listen, send_channel.clone())
                # Start the database listener
                nursery.start_soon(manager.db.watchConfig, send_channel.clone())

                everything_else = await nursery.start(
                    partial(manager.activate, user="system")
                )
                # Respond to incoming updates
                async for command in receive_channel:
                    print("config command '{!r}' received".format(command))

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

    manager.db.couch.disconnect()
