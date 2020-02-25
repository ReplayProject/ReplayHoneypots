#!/bin/bash

var=$(pgrep -af python | grep PortThreadManager.py | wc -l)

if [ $var -gt 0 ]
then
	echo $(date) 'PortThreadManager.py is running.' >> /home/winnie/check.log
else
	echo $(date) 'Running: python3 /home/yogi/2020SpringTeam18/honeypots/honeypot/PortThreadManager.py -c /home/yogi/2020SpringTeam18/honeypots/config/new-config.json.' >> /home/winnie/check.log
	cd /home/yogi/2020SpringTeam18/honeypots && pip3 install -r requirements.txt
	cd /home/yogi/2020SpringTeam18/honeypots/honeypot && python3 /home/yogi/2020SpringTeam18/honeypots/honeypot/PortThreadManager.py -c /home/yogi/2020SpringTeam18/honeypots/config/new-config.json
fi