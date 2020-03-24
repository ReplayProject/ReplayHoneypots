#!/bin/bash

KEYPATH=$1
REMOTEIP=$2
REMOTENAME=$3
REMOTEPASS=$4

sudo scp -i $KEYPATH repo.tar.gz $REMOTENAME@$REMOTEIP:/home/$REMOTENAME
sudo ssh -i $KEYPATH -tt $REMOTENAME@$REMOTEIP << ENDSSH
mkdir repo_test
mv /home/$REMOTENAME/repo.tar.gz /home/$REMOTENAME/repo_test/repo.tar.gz
tar -C /home/$REMOTENAME/repo_test -xf /home/$REMOTENAME/repo_test/repo.tar.gz
rm /home/$REMOTENAME/repo_test/repo.tar.gz
cd /home/$REMOTENAME/repo_test/2020SpringTeam18/honeypots/honeypot; sudo python3 CronInstaller.py -p PortThreadManager.py -c ../config/new-config.json
$REMOTEPASS
ENDSSH