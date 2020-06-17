#! /bin/sh

# Installs reqs to run the honeypot test suite
# (expected to be installed inside of the replay-honeypot docker image)

pip3 install -r requirements-dev.txt
command -v apk >/dev/null 2>&1 || { echo >&2 "I require apk but it's not installed.  Aborting."; exit 1; }
apk add curl bind-tools
cd honeypots/honeypot
python3 -m pytest test -vk 'not Cron'
