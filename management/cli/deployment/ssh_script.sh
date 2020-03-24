#!/bin/bash

sudo scp -i /shared/manager_rsa /shared/git_zips/repo.tar.gz yogi@192.168.42.52:/home/yogi
echo pass | sudo ssh -i /shared/manager_rsa -tt yogi@192.168.42.52 << EOF
mkdir helloworld
mv /home/yogi/repo.tar.gz /home/yogi/helloworld/repo.tar.gz
tar -C /home/yogi/helloworld -xf /home/yogi/helloworld/repo.tar.gz
rm /home/yogi/helloworld/repo.tar.gz
cd /home/yogi/helloworld/2020SpringTeam18/honeypots/honeypot; sudo python3 CronInstaller.py -p PortThreadManager.py -c ../config/new-config.json
@HoneyYogi
EOF
