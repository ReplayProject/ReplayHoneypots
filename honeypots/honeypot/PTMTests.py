from PortThreadManager import PortThreadManager
import unittest
import os
import time

class TestRedeploy(unittest.TestCase):
    def test_redeploy(self):
        man = PortThreadManager()
        man.deploy(r'../config/pt.cfg')
        #Need time to make sure everything initially deploys
        time.sleep(5)

        #Socket testing with senddata.json
        self.assertTrue(len(man.responseData.keys()) == 13)
        self.assertTrue("49667" in man.responseData.keys())
        self.assertTrue(man.processList["49667"].port == "49667" and man.processList["49667"].isRunning == True)
        
        self.assertTrue(len(man.snifferThread.openPorts) == 13)
        self.assertTrue("192.2.2.1" in man.snifferThread.whitelist)
        self.assertTrue(man.snifferThread.honeypotIP == "192.168.42.51")

        #Redeploying
        man.deploy(r'../config/pt_altered.cfg', updateSniffer=True, updateOpenPorts=True)

        self.assertTrue(len(man.responseData.keys()) == 7)
        self.assertFalse("49667" in man.responseData.keys())
        self.assertTrue("430" in man.responseData.keys())
        self.assertTrue(man.processList["430"].port == "430" and man.processList["430"].isRunning == True)
        
        self.assertTrue(len(man.snifferThread.openPorts) == 7)
        self.assertTrue("5.6.7.8" in man.snifferThread.whitelist)
        self.assertTrue(man.snifferThread.honeypotIP == "192.168.42.55")

if __name__ == '__main__':
    unittest.main()