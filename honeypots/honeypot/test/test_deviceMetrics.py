import sys
sys.path.insert(0,'..')
from DeviceMetrics import DeviceMetrics
import unittest
from jsondiff import diff


uuid1 = 'b484542ec578480587320a8c08c993e3'
hostname1 = 'honeypot1'
cpu1 = 5.3
ram1 = 75.0
storage1 = 159.00
device1_json1 = {"uuid": "b484542ec578480587320a8c08c993e3", "hostname": "honeypot1", "timestamp": 1601523567, "cpu": 5.3, "ram": 75.0, "storage": 159.0}

hostname2 = ''
cpu3_min = -1
cpu3_max = 101
ram4_min = -1
ram4_max = 101
storage5 = -1

class TestMethods(unittest.TestCase):
    
    def test1(self):
        device1 = DeviceMetrics(uuid1, hostname1, cpu1, ram1, storage1)
        self.assertTrue(diff(device1.json(),device1_json1))
        # self.assertTrue(device1.validate())

    # def test2(self):
    #     device2 = DeviceMetrics(uuid1, hostname2, cpu1, ram1, storage1)
    #     with self.assertRaises(Exception): device2.validate()

    # def test3(self):
    #     device3 = DeviceMetrics(uuid1, hostname1, cpu3_min, ram1, storage1)
    #     with self.assertRaises(Exception): device3.validate()
    #     device3 = DeviceMetrics(uuid1, hostname1, cpu3_max, ram1, storage1)
    #     with self.assertRaises(Exception): device3.validate()

    # def test4(self):
    #     device4 = DeviceMetrics(uuid1, hostname1, cpu1, ram4_min, storage1)
    #     with self.assertRaises(Exception): device4.validate()
    #     device4 = DeviceMetrics(uuid1, hostname1, cpu1, ram4_max, storage1)
    #     with self.assertRaises(Exception): device4.validate()

    # def test5(self):
    #     device5 = DeviceMetrics(uuid1, hostname1, cpu1, ram1, storage5)
    #     with self.assertRaises(Exception): device5.validate()

if __name__ == '__main__':
    unittest.main()