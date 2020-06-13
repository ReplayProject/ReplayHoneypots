#
# TODO: REVISIT when move to TRIO is done
#

from PortThreadManager import PortThreadManager
import unittest
import os
import time

class TestRedeploy(unittest.TestCase):
    def test_redeploy(self):
        man = PortThreadManager()
        man.activate(r'../testing_configs/pt.cfg')
        #Need time to make sure everything initially deploys
        time.sleep(5)

        #Socket testing with senddata.json
        self.assertTrue(len(man.responseData.keys()) == 13)
        self.assertTrue("49667" in man.responseData.keys())
        self.assertTrue(man.processList["49667"].port == "49667" and man.processList["49667"].isRunning == True)

        self.assertTrue(len(man.snifferThread.openPorts) == 13)
        self.assertTrue("192.2.2.1" in man.snifferThread.whitelist)
        self.assertTrue(man.snifferThread.honeypotIP == "192.168.42.51")
        self.assertTrue(man.snifferThread.portWhitelist[1] == 9000)

        #Redeploying
        x = man.activate(r'../testing_configs/pt_altered.cfg',
                     updateSniffer=True, updateOpenPorts=True)

        #changed both, should return a 3
        self.assertTrue(x == 3)

        self.assertTrue(len(man.responseData.keys()) == 7)
        self.assertFalse("49667" in man.responseData.keys())
        self.assertTrue("430" in man.responseData.keys())
        self.assertTrue(man.processList["430"].port == "430" and man.processList["430"].isRunning == True)

        self.assertTrue(len(man.snifferThread.openPorts) == 7)
        self.assertTrue("5.6.7.8" in man.snifferThread.whitelist)
        self.assertTrue(man.snifferThread.honeypotIP == "192.168.42.55")
        self.assertTrue(man.snifferThread.portWhitelist[1] == 8000)

        x = man.activate(r'../testing_configs/pt.cfg',
                     updateSniffer=False, updateOpenPorts=True)
        self.assertTrue(x == 2)

        x = man.activate(r'../testing_configs/pt.cfg',
                     updateSniffer=True, updateOpenPorts=False)
        self.assertTrue(x == 1)

        #We tell it to update sniffer and open ports, but nothing changes. Should return 0.
        x = man.activate(r'../testing_configs/pt.cfg',
                     updateSniffer=True, updateOpenPorts=True)
        self.assertTrue(x == 0)



if __name__ == '__main__':
    unittest.main()
