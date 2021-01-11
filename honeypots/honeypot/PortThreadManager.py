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
from pprint import pprint

import trio
from Alert import Alert
from Databaser import Databaser
from requests import get
from Sniffer import Sniffer
from Listener import Listener
from Config import Config
from DeviceMetrics import DeviceMetrics

ONE_MINUTE_IN_SECONDS = 60
METRICS_INTERVAL = 15

class PortThreadManager:
    """
    Initialize and control the sniffer, modules, database connection
    """

    def __init__(self):
        self.portList = []
        # self.ip = str(get("https://api.ipify.org").text)
        self.processList = dict()
        # where the async sniffer will be kept
        self.sniffer = None
        # delay specified by config file
        self.response_delay = None
        # whitelist of ports
        self.portWhitelist = None
        # whitelist of IPs
        self.whitelist = None
        # used to tell it to quit
        # self.keepRunning = True
        # list containing socket responses
        # self.responseData = None
        self.config = None
        # database interface object
        self.db = Databaser()

    def getConfigData(self):
        """
        Gets config information
        ran when PortThreadManager configuration changes
        """
        tempConfigObject = self.db.getConfig()
        self.config = Config(tempConfigObject)
        return self.config

    async def activate(
        self,
        updateSniffer=False,
        updateOpenPorts=False,
        user="",
        task_status=trio.TASK_STATUS_IGNORED,
        send_channel=None,
        receive_channel=None
    ):
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
        # Gets the info from config file initially
        conf = self.getConfigData()

        # Return code
        retCode = 0
        # Setup way to cancel these tasks
        with trio.CancelScope() as scope:
            # --- Start Async Sniffer ---#
            if self.sniffer is None:
                # TODO: Switch config="testing" to "base" when in production
                self.sniffer = Sniffer(config=conf, mode="base", databaser=self.db, send_channel=send_channel)
                self.sniffer.start()
            elif updateSniffer:
                oldHash = self.sniffer.currentHash
                self.sniffer.configUpdate(conf)
                if not self.sniffer.currentHash == oldHash:
                    retCode = 1
            # Mark trio task as started (and pass cancel scope back to nursery)
            task_status.started(scope)

            udp_services = self.config.udp_services
            tcp_services = self.config.tcp_services

            # Convience method to help with setting up TCP & UDP modules
            async def replay_server(sockets, protocol, nursery):
                print("Testing", protocol)
                print(str(sockets))
                try:
                    for service in sockets:
                        port = service.port
                        print("Port", port)
                        self.processList[port] = Listener(
                            port,
                            service,
                            protocol,        
                            self.config.response_delay,
                            nursery,
                        )
                        nursery.start_soon(self.processList[port].handler)
                except Exception as ex:
                    print("Replay_server exception", str(ex))

            print("UDP", udp_services)
            print("TCP", tcp_services)

            # --- Actually Start up listeners --- #
            try:
                async with trio.open_nursery() as nursery:
                    nursery.start_soon(
                        replay_server, udp_services, "UDP", nursery
                    )
                    nursery.start_soon(
                        replay_server, tcp_services, "TCP", nursery
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
                self.db.saveAlertObject(
                    Alert(
                        variant="admin",
                        message="Sniffer updated during runtime by " + user,
                    )
                )
            elif retCode == 2:
                self.db.saveAlertObject(
                    Alert(
                        variant="admin",
                        message="TCP sockets updated during runtime by " + user,
                    )
                )
            elif retCode == 3:
                self.db.saveAlertObject(
                    Alert(
                        variant="admin",
                        message="TCP sockets and Sniffer updated during runtime by "
                        + user,
                    )
                )
            elif retCode == 0:
                self.db.saveAlertObject(
                    Alert(
                        variant="admin",
                        message="Attempted configuration change during runtime by "
                        + user,
                    )
                )
            return retCode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy the honeypot")
    args = parser.parse_args()

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
    manager.db.saveAlertObject(
        Alert(variant="meta", message="Honeypot startup.", references=[])
    )

    async def metricsReporter():
        while True:
            # create metrics for honeypot and save them in database
            manager.db.saveMetricsObject()

            if manager.config == None or manager.config.metrics_interval == None or not isinstance(manager.config.metrics_interval, int):
                # send metrics per every 15 minutes
                await trio.sleep(ONE_MINUTE_IN_SECONDS * METRICS_INTERVAL)
            else:
                # send metrics per every 15 minutes
                await trio.sleep(ONE_MINUTE_IN_SECONDS * manager.config.metrics_interval)
    
    async def main():
        async with trio.open_nursery() as nursery:
            # Get our CTRL-C handler, tunnel, and trio channels running
            nursery.start_soon(control_c_handler, nursery)

            send_channel, receive_channel = trio.open_memory_channel(0)
            async with send_channel, receive_channel:

                # Start the database listener
                nursery.start_soon(manager.db.watchConfig, send_channel.clone())

                # Start report metrics
                nursery.start_soon(metricsReporter)

                everything_else = await nursery.start(
                    partial(
                        manager.activate, 
                        user="system", 
                        send_channel=send_channel,
                        receive_channel=receive_channel
                    )
                )
                # Respond to incoming updates
                async for command in receive_channel:
                    if "reconfigure" in command:
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
                                send_channel=send_channel,
                                receive_channel=receive_channel
                            )
                        )

    trio.run(main)

    manager.db.couch.disconnect()
