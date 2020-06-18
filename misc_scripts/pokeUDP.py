#! /usr/bin/python3
# This script is designed to be ran on a "rogue" host.
# It sends a few UDP packets to the provided IP address with a string payload
# Usage: sudo ./pokeUDP.py 192.168.42.51
import sys

from scapy.all import IP
from scapy.all import Raw
from scapy.all import send
from scapy.all import UDP

ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.42.51"

send(IP(dst=ip) / UDP(dport=1337) / Raw(load="whatever"), count=10)
