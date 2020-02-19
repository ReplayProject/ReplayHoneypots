#!/bin/bash

var=$(pgrep -af python | grep PortThreadManager.py | wc -l)

if [ $var -gt 0 ]
then
	echo $(date) 'PortThreadManager.py is running.' >> /home/winnie/check.log
else
	echo $(date) 'Running: python3 /home/winnie/2020SpringTeam18/honeypots/honeypot/PortThreadManager.py -c /home/winnie/2020SpringTeam18/honeypots/config/new-config.json.' >> /home/winnie/check.log
	cd /home/winnie/2020SpringTeam18/honeypots/honeypot && /usr/bin/python3 /home/winnie/2020SpringTeam18/honeypots/honeypot/PortThreadManager.py -c /home/winnie/2020SpringTeam18/honeypots/config/new-config.json
fi