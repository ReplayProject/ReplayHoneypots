#! /bin/bash

# This script is designed to be ran on a "rogue" host.
# It performs a basic NMAP scan against the provided IP address
# Usage: sudo ./scanHost.sh 192.168.42.51

ip="${1:-192.168.42.51}"
nmap -n -A -p0-9997 "$ip"
