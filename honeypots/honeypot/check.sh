#!/bin/bash

var=$(pgrep -af python | grep PortThreadManager.py | wc -l)

if [ $var -gt 0 ]
then
    echo $(date) "PortThreadManager.py is running" >> /home/winnie/daniel-cron/check.log
else
    echo $(date) "PortThreadManager.py is not running" >> /home/winnie/daniel-cron/check.log
fi
