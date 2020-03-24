#!/bin/bash

source config.txt

sudo scp -i /shared/manager_rsa $REPO $REMOTENAME@$REMOTEIP:/home/$REMOTENAME
echo pass | sudo ssh -i $KEYPATH -tt $REMOTENAME@$REMOTEIP << EOF
mkdir repo_test
mv /home/$REMOTENAME/repo.tar.gz /home/$REMOTENAME/repo_test/repo.tar.gz
tar -C /home/$REMOTENAME/repo_test -xf /home/$REMOTENAME/repo_test/repo.tar.gz
rm /home/$REMOTENAME/repo_test/repo.tar.gz
cd /home/$REMOTENAME/helloworld/2020SpringTeam18/honeypots/honeypot; sudo python3 CronInstaller.py -p PortThreadManager.py -c ../config/new-config.json
$REMOTEPASS
