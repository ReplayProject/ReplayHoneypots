#!/bin/bash

var=$(pgrep -af PortThreadManager.py | wc -l)

if [ $var -gt 0 ]
then
	echo $(date) 'PortThreadManager.py is running.' >> /home/winnie/2020SpringTeam18/honeypots/logs/cron.txt
else
	echo $(date) 'Running: python3 /home/winnie/2020SpringTeam18/honeypots/honeypot/PortThreadManager.py -c /home/winnie/2020SpringTeam18/honeypots/config/new-config.json.' >> /home/winnie/2020SpringTeam18/honeypots/logs/cron.txt
	cd /home/winnie/2020SpringTeam18/honeypots && pip3 install -r requirements.txt
	cd /home/winnie/2020SpringTeam18/honeypots/honeypot && python3 /home/winnie/2020SpringTeam18/honeypots/honeypot/PortThreadManager.py -c /home/winnie/2020SpringTeam18/honeypots/config/new-config.json
fi
