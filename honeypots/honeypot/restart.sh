#!/bin/bash

var=$(pgrep -af python | grep PortThreadManager.py | wc -l)

if [ $var -gt 0 ]
then
	echo $(date) 'PortThreadManager.py is running.' >> /home/winnie/check.log
else
	echo $(date) 'Running: python3 /home/winnie/2020SpringTeam18/honeypots/honeypot/PortThreadManager.py -n /home/winnie/2020SpringTeam18/honeypots/nmap/default.nmap.' >> /home/winnie/check.log
	cd /home/winnie/2020SpringTeam18/honeypots && pip3 install -r requirements.txt
	cd /home/winnie/2020SpringTeam18/honeypots/honeypot && python3 /home/winnie/2020SpringTeam18/honeypots/honeypot/PortThreadManager.py -n /home/winnie/2020SpringTeam18/honeypots/nmap/default.nmap
fi