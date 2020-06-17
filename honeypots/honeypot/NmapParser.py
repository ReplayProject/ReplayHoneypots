"""
This file is used for parsing an nmap
scan for configuration information.
  Usage: python3 NmapParser.py <file name of nmap file>
"""

import sys
import json


class NmapParser:
    def __init__(self, filename):
        self.ports = self.parseScan(filename)

    """
        This function parses a given scan file for
        configuration info and returns a port list.

        Args:
            fileName: file name of the given nmap file.

        Returns:
            a list of int port numbers

        Raise:
            FileNotFound if file doesn't exist
    """

    def parseScan(self, filename):
        found_port = False
        ports = []
        with open(filename, "r") as f:
            for line in f.readlines():
                if "PORT" in line:
                    found_port = True
                if line[0] == "|":
                    continue
                if found_port and "/tcp" in line and "open" in line:
                    slashLoc = line.find("/")
                    port = line[:slashLoc]
                    ports.append(int(port))
        return ports

    """
    Returns:
        the list of ports from the nmap file
    """

    def getPorts(self):
        return self.ports


if __name__ == "__main__":
    filename = sys.argv[1]
    parser = NmapParser(filename)
    ports = parser.getPorts()
    print(ports)
    startnum = filename.rfind("/") + 1
    endnum = filename.find(".nmap")
    newfilename = filename[startnum:endnum] + ".json"
    with open("../config/" + newfilename, "w") as newfile:
        json.dump(ports, newfile)
