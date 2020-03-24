#!/bin/bash

source config.txt

sudo scp -i $KEY $REPOPATH $REMOTE:$REMOTEPATH
echo pass | sudo ssh -i $KEY -tt $REMOTE << EOF
mkdir repo_test
mv $REMOTEPATH/$REPO $REMOTEPATH/repo_test/$REPO
tar -C $REMOTEPATH/repo_test -xf $REMOTEPATH/repo_test/$REPO
rm $REMOTEPATH/repo_test/$REPO
cd $CRONPATH; sudo python3 CronInstaller.py -p PortThreadManager.py -c ../config/new-config.json
$REMOTEPASS
