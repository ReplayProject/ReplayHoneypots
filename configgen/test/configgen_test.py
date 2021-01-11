import sys
sys.path.insert(0,'..')
import filecmp
import unittest
import json 
import configgen
import unittest.mock
import exporter
import nmapparser
from jsondiff import diff


def test_txt_file(actual_file, expected_file):
    actual = filecmp.cmp(actual_file,expected_file)
    expected = True
    return actual == expected

def test_json_file(actual_file,expected_file):
    with open(actual_file) as f:
        act_json = json.load(f)
    with open(expected_file) as f:
        expt_json = json.load(f)

    return diff(act_json, expt_json)

def helper(text,json):
    nmapResults = configgen.getAndProcessNmapScan()
    userFillInData = configgen.userFillins()

    nmapResults.response_delay = userFillInData.ResponseDelay
    nmapResults.portscan_window = userFillInData.PortScanWindow
    nmapResults.portscan_threshold = userFillInData.PortScanThreshold
    nmapResults.whitelist_addrs = userFillInData.WhitelistIPs
    nmapResults.whitelist_ports = userFillInData.WhitelistPorts
    exporter.createTextDescriptionOfConfigs(text, nmapResults)
    exporter.dumpListOfConfigsToFile(json, nmapResults)

class TestMethods(unittest.TestCase):
    
    def test1(self):
        user_input = ["./testfile/example-scan.xml", "0","100", "1000","192.168.86.159, 1.1.1.1, 1.2.3.4","5555,8080","./testfile/test"]
        with unittest.mock.patch('builtins.input', side_effect= user_input):
            helper("./testfile/test.txt","./testfile/test.json")
            self.assertTrue(test_txt_file("./testfile/example-output.txt","./testfile/test.txt"))
            self.assertFalse(test_json_file("./testfile/example-output.json","./testfile/test.json"))
            
    # def test2(self):
    #     user_input = ["./testfile/input1.xml", "0","100", "1000","192.168.86.159, 1.1.1.1, 1.2.3.4","5555,8080","./testfile/test1"]
    #     with unittest.mock.patch('builtins.input', side_effect= user_input):
    #         helper("./testfile/test1.txt","./testfile/test1.json")
    #         self.assertTrue(test_txt_file("./testfile/example-output1.txt","./testfile/test1.txt"))
    #         self.assertFalse(test_json_file("./testfile/example-output1.json","./testfile/test1.json"))

    # def test3(self):
    #     user_input = ["./testfile/input2.xml", "0","100", "1000","192.168.86.159, 1.1.1.1, 1.2.3.4","5555,8080","./testfile/test2"]
    #     with unittest.mock.patch('builtins.input', side_effect= user_input):
    #         helper("./testfile/test2.txt","./testfile/test2.json")
    #         self.assertTrue(test_txt_file("./testfile/example-output1.txt","./testfile/test2.txt"))
    #         self.assertFalse(test_json_file("./testfile/example-output2.json","./testfile/test2.json"))

    # def test4(self):
    #     user_input = ["./testfile/input3.xml", "0","100", "1000","192.168.86.159, 1.1.1.1, 1.2.3.4","5555,8080","./testfile/test3"]
    #     with unittest.mock.patch('builtins.input', side_effect= user_input):
    #         helper("./testfile/test3.txt","./testfile/test3.json")
    #         self.assertTrue(test_txt_file("./testfile/example-output1.txt","./testfile/test3.txt"))
    #         self.assertFalse(test_json_file("./testfile/example-output3.json","./testfile/test3.json"))

    # def test5(self):
    #     user_input = ["./testfile/input4.xml", "0","100", "1000","192.168.86.159, 1.1.1.1, 1.2.3.4","5555,8080","./testfile/test4"]
    #     with unittest.mock.patch('builtins.input', side_effect= user_input):
    #         helper("./testfile/test4.txt","./testfile/test4.json")
    #         self.assertTrue(test_txt_file("./testfile/example-output1.txt","./testfile/test4.txt"))
    #         self.assertFalse(test_json_file("./testfile/example-output4.json","./testfile/test4.json"))

    # def test6(self):
    #     user_input = ["./testfile/input5.xml", "0","100", "1000","192.168.86.159, 1.1.1.1, 1.2.3.4","5555,8080","./testfile/test5"]
    #     with unittest.mock.patch('builtins.input', side_effect= user_input):
    #         helper("./testfile/test5.txt","./testfile/test5.json")
    #         self.assertTrue(test_txt_file("./testfile/example-output1.txt","./testfile/test5.txt"))
    #         self.assertFalse(test_json_file("./testfile/example-output5.json","./testfile/test5.json"))

    # def test7(self):
    #     user_input = ["./testfile/input6.xml", "0","100", "1000","192.168.86.159, 1.1.1.1, 1.2.3.4","5555,8080","./testfile/test6"]
    #     with unittest.mock.patch('builtins.input', side_effect= user_input):
    #         helper("./testfile/test6.txt","./testfile/test6.json")
    #         self.assertTrue(test_txt_file("./testfile/example-output1.txt","./testfile/test6.txt"))
    #         self.assertFalse(test_json_file("./testfile/example-output6.json","./testfile/test6.json"))

    # def test8(self):
    #     user_input = ["./testfile/input7.xml", "0","100", "1000","192.168.86.159, 1.1.1.1, 1.2.3.4","5555,8080","./testfile/test7"]
    #     with unittest.mock.patch('builtins.input', side_effect= user_input):
    #         helper("./testfile/test7.txt","./testfile/test7.json")
    #         self.assertTrue(test_txt_file("./testfile/example-output1.txt","./testfile/test7.txt"))
    #         self.assertFalse(test_json_file("./testfile/example-output7.json","./testfile/test7.json"))

    # def test9(self):
    #     user_input = ["./testfile/input8.xml", "0","100", "1000","192.168.86.159, 1.1.1.1, 1.2.3.4","5555,8080","./testfile/test8"]
    #     with unittest.mock.patch('builtins.input', side_effect= user_input):
    #         helper("./testfile/test8.txt","./testfile/test8.json")
    #         self.assertTrue(test_txt_file("./testfile/example-output1.txt","./testfile/test8.txt"))
    #         self.assertFalse(test_json_file("./testfile/example-output8.json","./testfile/test8.json"))

    # def test10(self):
    #     user_input = ["./testfile/input9.xml", "0","100", "1000","192.168.86.159, 1.1.1.1, 1.2.3.4","5555,8080","./testfile/test9"]
    #     with unittest.mock.patch('builtins.input', side_effect= user_input):
    #         helper("./testfile/test9.txt","./testfile/test9.json")
    #         self.assertTrue(test_txt_file("./testfile/example-output1.txt","./testfile/test9.txt"))
    #         self.assertFalse(test_json_file("./testfile/example-output9.json","./testfile/test9.json"))

    # def test11(self):
    #     user_input = ["./testfile/input10.xml", "0","100", "1000","192.168.86.159, 1.1.1.1, 1.2.3.4","5555,8080","./testfile/test10"]
    #     with unittest.mock.patch('builtins.input', side_effect= user_input):
    #         helper("./testfile/test10.txt","./testfile/test10.json")
    #         self.assertTrue(test_txt_file("./testfile/example-output1.txt","./testfile/test10.txt"))
    #         self.assertFalse(test_json_file("./testfile/example-output10.json","./testfile/test10.json"))

    # def test12(self):
    #     user_input = ["./testfile/input11.xml", "0","100", "1000","192.168.86.159, 1.1.1.1, 1.2.3.4","5555,8080","./testfile/test11"]
    #     with unittest.mock.patch('builtins.input', side_effect= user_input):
    #         helper("./testfile/test11.txt","./testfile/test11.json")
    #         self.assertTrue(test_txt_file("./testfile/example-output1.txt","./testfile/test11.txt"))
    #         self.assertFalse(test_json_file("./testfile/example-output11.json","./testfile/test11.json"))

    # def test13(self):
    #     user_input = ["./testfile/input12.xml", "0","100", "1000","192.168.86.159, 1.1.1.1, 1.2.3.4","5555,8080","./testfile/test12"]
    #     with unittest.mock.patch('builtins.input', side_effect= user_input):
    #         helper("./testfile/test12.txt","./testfile/test12.json")
    #         self.assertTrue(test_txt_file("./testfile/example-output1.txt","./testfile/test12.txt"))
    #         self.assertFalse(test_json_file("./testfile/example-output12.json","./testfile/test12.json"))

    # def test14(self):
    #     user_input = ["./testfile/input13.xml", "0","100", "1000","192.168.86.159, 1.1.1.1, 1.2.3.4","5555,8080","./testfile/test13"]
    #     with unittest.mock.patch('builtins.input', side_effect= user_input):
    #         helper("./testfile/test13.txt","./testfile/test13.json")
    #         self.assertTrue(test_txt_file("./testfile/example-output1.txt","./testfile/test13.txt"))
    #         self.assertFalse(test_json_file("./testfile/example-output13.json","./testfile/test13.json"))

    def test14(self):
        helper("./testfile/test14.txt","./testfile/test14.json")
        # user_input = ["./testfile/input14.xml", "0","100", "1000","192.168.86.159, 1.1.1.1, 1.2.3.4","5555,8080","./testfile/test14"]
        # with unittest.mock.patch('builtins.input', side_effect= user_input):
        #     helper("./testfile/test14.txt","./testfile/test14.json")
        #     self.assertTrue(test_txt_file("./testfile/example-output1.txt","./testfile/test14.txt"))
        #     self.assertFalse(test_json_file("./testfile/example-output14.json","./testfile/test14.json"))


if __name__ == '__main__':
    unittest.main()