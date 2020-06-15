from Sniffer import Sniffer

import trio
import pytest
import os

WAIT_TIME = 2

"""
If testing in alpine container, may need to run
apk add curl bind-tools
"""


class TestConfigTunnel:
    """
    Testing for the async sniffer
    """

    async def test_init(self, nursery):
        """
        Test that the sniffer successfully sets itself up
        """
        #  Start the sniffer
        s = Sniffer(
            config="testing",
            openPorts=[],
            whitelist=[],
            honeypotIP="localhost",
            managementIPs=(),
            databaser=None,
        )
        s.start()

        # Google IP; we'll be using this later
        IPPipe = os.popen("dig +short www.google.com")
        responseIPs = IPPipe.read()[:-1].split("\n")
        IPPipe.close()

        # Making sure we catch it
        os.system("curl -s www.google.com -o /dev/null")

        # Let the logger handle whats up
        await trio.sleep(0.1)

        # Dig sometimes gives us multiple IPs, not all of which are used. If one is used, that's a successful read.
        ipObtained = False
        for ip in responseIPs:
            if (
                ip in s.RECORD.keys()
                and s.RECORD[ip][0].sourceIPAddress == ip
                and s.RECORD[ip][0].sourcePortNumber == 80
                and s.RECORD[ip][0].trafficType == "TCP"
            ):
                ipObtained = True
                break

        assert ipObtained
        s.stop()

    async def testConfigUpdate(self):
        """
        Checks if updated options work
        """
        host_ip = "192.168.42.51"
        # Start the sniffer
        s = Sniffer(
            config="onlyUDP",
            openPorts=[],
            whitelist=[],
            portWhitelist=[],
            honeypotIP=host_ip,
            managementIPs=("52.87.97.77", "54.80.228.0"),
        )
        s.start()

        assert len(s.openPorts) == 0
        assert len(s.whitelist) == 0
        assert len(s.portWhitelist) == 0
        assert s.config == "onlyUDP"
        assert len(s.managementIPs) == 2
        assert s.honeypotIP == "192.168.42.51"

        s.configUpdate(
            openPorts=[80, 443],
            whitelist=["8.8.8.8", "9.9.9.9"],
            portWhitelist=[777, 888, 999],
            honeypotIP="192.168.42.42",
            managementIPs="54.80.228.0",
        )
        # used to flush the Sniffer
        os.system("curl -s www.google.com -o /dev/null")
        assert len(s.openPorts) == 2
        assert len(s.whitelist) == 2
        assert len(s.portWhitelist) == 3
        assert s.managementIPs == "54.80.228.0"
        assert s.honeypotIP == "192.168.42.42"

        s.stop()
