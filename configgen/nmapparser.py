import sys
import xml.etree.ElementTree as ET

########## ---------------------------------------------- ##########
########## ------ Model for internal data tracking ------ ##########
########## ---------------------------------------------- ##########


class Service:
    def __init__(self, service, port, protocol):
        self.name = service
        self.port = port
        self.protocol = protocol

    def Print(self, prependIndent):
        print(prependIndent + self.name + " | " + self.port + " | " + self.protocol)


class Config:
    def __init__(self, OSName, FingerPrint, FilteredPorts, Services):
        self.os = OSName
        self.fingerprint = FingerPrint
        self.filtered_ports = FilteredPorts
        self.services = Services

    def Print(self, includeFiltered, includeOpen):
        indent = "    "
        print("Config Data:")
        print(indent + self.os)
        print(indent + self.fingerprint)
        if includeFiltered:
            print(indent + "Filtered Ports:")
            for port in self.filtered_ports:
                print(indent + indent + port)
        if includeOpen:
            print(indent + "Services:")
            for service in self.services:
                service.Print(indent + indent)
                print()


########## ----------------------------------------- ##########
########## ------ Main document parsing logic ------ ##########
########## ----------------------------------------- ##########


def parseNMAPXMLResults(xmlfile):
    # TODO: Handle bad files (no host, host offline, etc)
    tree = ET.parse(xmlfile)
    root = tree.getroot()
    hosts = root.findall("host")

    if not validateNmapCommand(root):
        print(
            (
                "The command used in this Nmap scan does not match the "
                + 'required format: "nmap -d3 -v -A" is required. Exiting.'
            )
        )
        sys.exit(1)

    if len(hosts) == 0:
        print("There are no hosts defined in the XML input file. Exiting.")
        sys.exit(1)
    elif len(hosts) > 1:
        print(
            "The parser only accepts XML files with a single host result set. Exiting."
        )
        sys.exit(1)
    else:
        configData = processHostResults(hosts[0])
        return configData


def validateNmapCommand(root):
    NmapCommandRun = root.attrib["args"]
    if "-d3 -v -A" in NmapCommandRun:
        return True
    else:
        return False


def processHostResults(hostObject):
    portsList = hostObject.find("ports")
    nmapPorts = portsList.findall("port")
    openPorts = []
    filteredPorts = []

    for portData in nmapPorts:
        portNumber = portData.attrib["portid"]
        portStatusTag = portData.find("state")
        portStatus = portStatusTag.attrib["state"]

        if portStatus == "open":
            openPorts.append(parseAPortObject(portData))
        elif portStatus == "filtered":
            filteredPorts.append(int(portNumber))

    # Port data collection is done

    # Get the first osmatch entry - highest probability
    osDetails = hostObject.find("os")

    if osDetails is not None:
        osFingerprint = osDetails.find("osfingerprint")
        if osFingerprint is None:
            print("There is no fingerprint provided in the input file. Exiting.")
            exit(1)
        cleanedFingerprint = processOSFingerPrint(osFingerprint.attrib["fingerprint"])
        osMatches = osDetails.findall("osmatch")

        bestOSMatch = osMatches[0]
        OSName = bestOSMatch.attrib["name"]

        # Build the config with the discovered data and return
        return Config(OSName, cleanedFingerprint, filteredPorts, openPorts)
    else:
        return Config("undetermined", "undetermined", filteredPorts, openPorts)


def processOSFingerPrint(fingerprint):
    fingerprint = fingerprint.replace("&#xa;", "")
    fingerprint = fingerprint.replace("OS:", "")
    fingerprint = fingerprint.replace("\r", "")
    fingerprint = fingerprint.replace("\n", "")

    return fingerprint


def parseAPortObject(portData):
    portService = ""
    portServiceData = ""
    serviceName = ""

    portNumber = int(portData.attrib["portid"])
    portProtocol = portData.attrib["protocol"]

    serviceTag = portData.find("service")
    if serviceTag is not None:
        if serviceTag.attrib["method"] == "probed":
            serviceName = serviceTag.attrib["name"]

    portService = Service(serviceName, portNumber, portProtocol)
    return portService
