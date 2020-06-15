from PortThreadManager import PortThreadManager
import trio
from functools import partial
import os


class TestRedeploy:
    async def test_redeploy(self, nursery):
        man = PortThreadManager()

        man_ctx = await nursery.start(
            partial(man.activate, r"../testing_configs/pt.cfg")
        )

        # Need time to make sure everything initially deploys
        await trio.sleep(5)

        # Socket testing with senddata.json
        assert len(man.responseData.keys()) == 13
        assert "49667" in man.responseData.keys()

        assert (
            man.processList["49667"].port == "49667"
            and man.processList["49667"].isRunning == True
        )

        assert len(man.sniffer.openPorts) == 13
        assert "192.2.2.1" in man.sniffer.whitelist
        assert man.sniffer.honeypotIP == "192.168.42.51"
        assert man.sniffer.portWhitelist[1] == 9000

        # Cleaning
        man_ctx.cancel()  # clean tasks
        man.processList = dict()  # clean listener objects

        # Redeploying
        man_ctx = await nursery.start(
            partial(
                man.activate,
                r"../testing_configs/pt_altered.cfg",
                updateSniffer=True,
                updateOpenPorts=True,
            )
        )

        await trio.sleep(2)

        assert len(man.responseData.keys()) == 7
        assert not ("49667" in man.responseData.keys())
        assert "430" in man.responseData.keys()
        assert (
            man.processList["430"].port == "430"
            and man.processList["430"].isRunning == True
        )

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

        # # We tell it to update sniffer and open ports, but nothing changes. Should return 0.
        # x = man.activate(
        #     r"../testing_configs/pt.cfg", updateSniffer=True, updateOpenPorts=True
        # )
        # assert x == 0
