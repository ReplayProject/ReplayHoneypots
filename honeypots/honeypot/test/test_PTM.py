import json
import os
from functools import partial

import mock
import trio
from PortThreadManager import PortThreadManager


class TestRedeploy:
    """
    Test that runs the PTM file with different configs,
     to check that configuration changes are handled correctly.
    """

    async def test_redeploy(self, mocker, nursery):
        man = PortThreadManager()

        m1 = mocker.patch.object(man.db, "getConfig")
        with open("../../config/defaults.json") as f:
            m1.return_value = json.load(f)

        mocker.patch.object(man.db, "alert")

        man_ctx = await nursery.start(man.activate)

        # Need time to make sure everything initially deploys
        await trio.sleep(5)

        # Socket testing with senddata.json
        assert len(man.responseData.keys()) == 14
        assert "80" in man.responseData.keys()
        assert "135" in man.responseData.keys()
        assert "139" in man.responseData.keys()
        assert "445" in man.responseData.keys()
        assert "1338" in man.responseData.keys()
        assert "5040" in man.responseData.keys()
        assert "5938" in man.responseData.keys()
        assert "49664" in man.responseData.keys()
        assert "49665" in man.responseData.keys()
        assert "49666" in man.responseData.keys()
        assert "49667" in man.responseData.keys()
        assert "49668" in man.responseData.keys()
        assert "49669" in man.responseData.keys()
        assert "49670" in man.responseData.keys()

        assert (
            man.processList["80"].port == "80"
            and man.processList["80"].isRunning
            and man.processList["135"].port == "135"
            and man.processList["135"].isRunning
            and man.processList["139"].port == "139"
            and man.processList["139"].isRunning
            and man.processList["445"].port == "445"
            and man.processList["445"].isRunning
            and man.processList["1338"].port == "1338"
            and man.processList["1338"].isRunning
            and man.processList["5040"].port == "5040"
            and man.processList["5040"].isRunning
            and man.processList["5938"].port == "5938"
            and man.processList["5938"].isRunning
            and man.processList["49664"].port == "49664"
            and man.processList["49664"].isRunning
            and man.processList["49665"].port == "49665"
            and man.processList["49665"].isRunning
            and man.processList["49666"].port == "49666"
            and man.processList["49666"].isRunning
            and man.processList["49667"].port == "49667"
            and man.processList["49667"].isRunning
            and man.processList["49668"].port == "49668"
            and man.processList["49668"].isRunning
            and man.processList["49669"].port == "49669"
            and man.processList["49669"].isRunning
            and man.processList["49670"].port == "49670"
            and man.processList["49670"].isRunning
        )

        assert len(man.sniffer.openPorts) == 14
        assert "192.2.2.1" in man.sniffer.whitelist
        assert man.sniffer.honeypotIP == m1.return_value["ip_addresses"]["honeypotIP"]
        assert man.sniffer.portWhitelist[1] == m1.return_value["configtunnel"]["port"]

        # Cleaning
        man_ctx.cancel()  # clean tasks
        man.processList = dict()  # clean listener objects

        s2 = mocker.patch.object(man.db, "getConfig")
        with open("./test/defaults_altered.json") as f:
            s2.return_value = json.load(f)

        mocker.patch.object(man.db, "alert")

        # Redeploying
        man_ctx = await nursery.start(
            partial(man.activate, updateSniffer=True, updateOpenPorts=True,)
        )

        await trio.sleep(2)

        assert len(man.responseData.keys()) == 7
        assert not ("49667" in man.responseData.keys())
        assert "430" in man.responseData.keys()
        assert man.processList["430"].port == "430" and man.processList["430"].isRunning

        assert len(man.sniffer.openPorts) == 7
        assert "5.6.7.8" in man.sniffer.whitelist
        assert man.sniffer.honeypotIP == "192.168.42.55"
        assert man.sniffer.portWhitelist[1] == 8000

        man_ctx.cancel()  # clean tasks
        man.processList = dict()  # clean listener objects

        # TODO: test PTM reconfiguration (if still supported)
        # x = man.activate(
        #     r"../testing_configs/pt.cfg", updateSniffer=False, updateOpenPorts=True
        # )
        # assert x == 2

        # x = man.activate(
        #     r"../testing_configs/pt.cfg", updateSniffer=True, updateOpenPorts=False
        # )
        # assert x == 1

        # # We tell it to update sniffer and open ports, but nothing changes.
        # # this Should return 0.
        # x = man.activate(
        #     r"../testing_configs/pt.cfg", updateSniffer=True, updateOpenPorts=True
        # )
        # assert x == 0
