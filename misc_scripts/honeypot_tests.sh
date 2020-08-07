#! /bin/sh

# Installs reqs to run the honeypot test suite
# (expected to be installed inside of the replay-honeypot docker image)
pip3 install -q -r ../requirements.txt # honeypot reqs
pip3 install -q -r ../../requirements-dev.txt # honeypot testing reqs
command -v apk >/dev/null 2>&1 || { echo >&2 "I require apk but it's not installed.  Aborting."; exit 1; }
apk add -U -q curl bind-tools # testing tools needed for sniffing
python3 -m pytest --maxfail=2 ./test/ --cov="." -vk "not Cron" # run and report on tests
