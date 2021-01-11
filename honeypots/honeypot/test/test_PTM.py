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
        with open("../../config/default_hp_config.json") as f:
            m1.return_value = json.load(f)

        mocker.patch.object(man.db, "saveAlertObject")
        mocker.patch.object(man.db, "watchConfig")

        man_ctx = await nursery.start(man.activate)

        # Need time to make sure everything initially deploys
        await trio.sleep(5)

        # Socket testing with senddata.json
        assert len(man.config.services) == 2
        assert 80 in man.config.open_ports
        assert 22 in man.config.open_ports

        assert (
            man.processList[80].port == 80
            and man.processList[80].isRunning
            and man.processList[22].port == 22
            and man.processList[22].isRunning
        )

        # Cleaning
        man_ctx.cancel()  # clean tasks
        man.processList = dict()  # clean listener objects

        s2 = mocker.patch.object(man.db, "getConfig")
        with open("./test/defaults_altered.json") as f:
            s2.return_value = json.load(f)

        mocker.patch.object(man.db, "saveAlertObject")

        # Redeploying
        man_ctx = await nursery.start(
            partial(man.activate, updateSniffer=True, updateOpenPorts=True,)
        )

        await trio.sleep(2)

        assert len(man.config.services) == 1
        assert 2223 in man.config.open_ports

        assert (
            man.processList[2223].port == 2223
            and man.processList[2223].isRunning
        )

        man_ctx.cancel()  # clean tasks
        man.processList = dict()  # clean listener objects