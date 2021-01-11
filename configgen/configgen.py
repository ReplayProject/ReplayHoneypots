import os
import socket
import sys
from nmapparser import parseNMAPXMLResults

from exporter import createTextDescriptionOfConfig
from exporter import dumpConfigToFile
from packetparser import process_pcap


class FillInData:
    __slots__ = (
        "ResponseDelay",
        "PortScanWindow",
        "PortScanThreshold",
        "WhitelistIPs",
        "WhitelistPorts",
        "MetricsInterval",
        "UpdateCheckInterval"
    )

    def __init__(
        self,
        responseDelay,
        portScanWindow,
        portScanThreshold,
        whitelistIPs,
        whitelistPorts,
        metricsInterval,
        updateCheckInterval,
    ):
        self.ResponseDelay = responseDelay
        self.PortScanWindow = portScanWindow
        self.PortScanThreshold = portScanThreshold
        self.WhitelistIPs = whitelistIPs
        self.WhitelistPorts = whitelistPorts
        self.MetricsInterval = metricsInterval
        self.UpdateCheckInterval = updateCheckInterval


def getAndProcessNmapScan(nmapFilename):
    if nmapFilename == None:
        nmapFilename = input("Enter the path to an Nmap result XML file: ")
    if not os.path.isfile(nmapFilename):
        print("The file given does not exist.\n")
        sys.exit(1)
    if not nmapFilename.endswith(".xml"):
        print("The file given is not an XML file.\n")
        sys.exit(1)

    return parseNMAPXMLResults(nmapFilename)

def getAndProcessPCAP(ports, pcapFilename):
    if pcapFilename == None:
        pcapFilename = input("Enter the path to a PCAP result file: ")
    if not os.path.isfile(pcapFilename):
        print("The file given does not exist.\n")
        sys.exit(1)
    if not pcapFilename.endswith(".pcap"):
        print("The file given is not a PCAP file.\n")
        sys.exit(1)

    # Get the target IP from the user
    targetIP = None
    while True:
        whitelistIPs = gatherInputUntilSuccess(
            "string",
            None,
            None,
            "Enter the IP of the target machine: ",
        )
        # Exit early if no answer is given
        if whitelistIPs == "":
            print("Nothing was entered. Please try again.")
            continue
        # Handle the error case if only a number was entered
        if isinstance(whitelistIPs, int):
            print("Only a number was entered. Please try again.")
            continue
        whitelistIPs = whitelistIPs.replace(" ", "")
        whitelistIPs = whitelistIPs.split(",")

        if len(whitelistIPs) != 1:
            print("Enter 1 and only 1 target IP address.")
            continue
        
        
        try:
            socket.inet_aton(whitelistIPs[0])
            targetIP = whitelistIPs[0]
            break
        except socket.error:
            print("The IP given was invalid. Note: Only IPv4 Addresses are supported.")
            continue
        
    return process_pcap(pcapFilename, targetIP, ports)


# Data that must be given by the user, and is not available via the nMap scan.
def userFillins():
    print()
    responseDelay = gatherInputUntilSuccess(
        "numeric", 0, 60, "Enter the response delay for all packets in seconds (0-60): "
    )
    print()
    portScanWindow = gatherInputUntilSuccess(
        "numeric",
        0,
        300,
        (
            "Enter the time window length for port "
            + "scan detection in seconds (0-300): "
        ),
    )
    print()
    portScanThreshold = gatherInputUntilSuccess(
        "numeric",
        0,
        10000,
        (
            "Enter the number of logs from a single "
            + "host that constitute a scan (0-10000): "
        ),
    )
    print()
    metricsInterval = gatherInputUntilSuccess(
        "numeric",
        1,
        120,
        "Enter the wait time between metrics collections in minutes (1-120): ",
    )
    print()
    updateChecksInterval = gatherInputUntilSuccess(
        "numeric",
        1,
        120,
        "Enter the wait time between honeypot settings update checks in minutes (1-120): ",
    )
    print()
    whitelistIPs = getWhitelistIPs()
    print()
    whitelistPorts = getWhitelistPorts()
    print()

    return FillInData(
        responseDelay, portScanWindow, portScanThreshold, whitelistIPs, whitelistPorts, metricsInterval, updateChecksInterval
    )


# Used to perform additional validation surrounding
# the ports that will not be watched for logging
def getWhitelistPorts():
    while True:
        whitelistPorts = gatherInputUntilSuccess(
            "string",
            None,
            None,
            "Enter a comma separated list of ports to ignore packets from: ",
        )
        outputPorts = []

        # Exit early if no answer is given
        if whitelistPorts == "":
            return []

        # Handle single port number given - gatherInputUntilSucess
        # returns an int in this case
        if not isinstance(whitelistPorts, str):

            if whitelistPorts < 0 or whitelistPorts > 65535:
                print(
                    (
                        "A single port was given, but the number is not "
                        + "in the valid port range [0,65535]. Please try again."
                    )
                )
                continue
            else:
                outputPorts.append(whitelistPorts)
                return outputPorts

        whitelistPorts = whitelistPorts.replace(" ", "")
        whitelistPorts = whitelistPorts.split(",")
        errorFound = False
        for port in whitelistPorts:
            # Cast to number
            try:
                port = int(port)
            except Exception:
                print(
                    (
                        "The list of values given contains at least "
                        + "one value that is not numeric. Please try again."
                    )
                )
                errorFound = True
                break

            # Check possible port range
            if port < 0 or port > 65535:
                print(
                    (
                        "The list of values given contains at least one "
                        + "value that is not a valid port number. Please try again."
                    )
                )
                errorFound = True
                break

            outputPorts.append(port)

        if errorFound:
            continue

        return outputPorts


# Used to perform additional validation surrounding the ip
# addresses that will not be watched for logging
def getWhitelistIPs():
    while True:
        whitelistIPs = gatherInputUntilSuccess(
            "string",
            None,
            None,
            (
                "Enter a comma separated list of IP "
                + "addresses to ignore packets from: "
            ),
        )
        # Exit early if no answer is given
        if whitelistIPs == "":
            return []
        # Handle the error case if only a number was entered
        if isinstance(whitelistIPs, int):
            print("Only a number was entered. Please try again.")
            continue
        whitelistIPs = whitelistIPs.replace(" ", "")
        whitelistIPs = whitelistIPs.split(",")

        outputIPs = []
        errorFound = False
        for ip in whitelistIPs:
            try:
                socket.inet_aton(ip)
                outputIPs.append(ip)
            except socket.error:
                print(
                    (
                        "The list of values given contains at least one invalid "
                        + "IP address. Note: Only IPv4 Addresses are supported."
                    )
                )
                errorFound = True
                break

        if errorFound:
            continue

        return outputIPs


# Helper function that gets input, validates based on parameters,
# and will infinitly poll for responses until a valid one is given.
def gatherInputUntilSuccess(datatype, min, max, prompt):
    errorMessage = "This value is not a valid " + datatype
    errorMessage = errorMessage + ". Please try again."
    rangeErrorMessage = (
        "The value given is not within the range ["
        + str(min)
        + ","
        + str(max)
        + "]. Please try again."
    )
    while True:
        value = input(prompt)

        # Try number conversion for check
        try:
            value = int(value)
        except Exception:
            pass

        if (datatype == "string" and not isinstance(value, (str, int))) or (
            datatype == "numeric" and not isinstance(value, int)
        ):
            print(errorMessage)
        elif datatype == "numeric" and (value < min or value > max):
            print(rangeErrorMessage)
        else:
            return value


if __name__ == "__main__":
    nmapFilename = None
    pcapFilename = None
    if (len(sys.argv) == 2):
        nmapFilename = sys.argv[1]
    elif (len(sys.argv) == 3):
        nmapFilename = sys.argv[1]
        pcapFilename = sys.argv[2]
    elif (len(sys.argv) > 3):
        print("Command line parameters formatted incorrectly. You can include no paths, an nmap path, or an nmap and pcap path.")
        sys.exit(1)
    print()

    # Get all Data - do user input second to prevent
    # re-inputting values if nmap parse fails
    nmapResults = getAndProcessNmapScan(nmapFilename)

    # Build the list of open ports
    openPorts = []
    for service in nmapResults.services:
        openPorts.append(service.port)
    pcapResults = getAndProcessPCAP(openPorts, pcapFilename)

    # Assign the response models to the services
    for service in nmapResults.services:
        for port in pcapResults:
            if service.port == port:
                service.response_model = pcapResults[port]
                break

    # User supplied data
    userFillInData = userFillins()

    # Add the user provided information to the config object
    nmapResults.response_delay = userFillInData.ResponseDelay
    nmapResults.portscan_window = userFillInData.PortScanWindow
    nmapResults.portscan_threshold = userFillInData.PortScanThreshold
    nmapResults.whitelist_addrs = userFillInData.WhitelistIPs
    nmapResults.whitelist_ports = userFillInData.WhitelistPorts
    nmapResults.metrics_interval = userFillInData.MetricsInterval
    nmapResults.update_interval = userFillInData.UpdateCheckInterval

    # Create output
    outfileName = input("Please enter a filename for the output files: ")
    createTextDescriptionOfConfig(outfileName + ".txt", nmapResults)
    dumpConfigToFile(outfileName + ".json", nmapResults)

    # fullLogic('../test-scan.xml', 'configgentest')
