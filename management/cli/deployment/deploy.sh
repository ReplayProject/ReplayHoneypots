#!/bin/bash

KEYPATH=$1
REMOTEIP=$2
REMOTENAME=$3
REMOTEPASS=$4
REPOPATH=$5

function silentSsh {
    local connectionString="$1"
    local commands="$2"
    if [ -z "$commands" ]; then
        commands=`cat`
    fi
    # to stop ssh output switch from -tt to -T
    ssh -i $KEYPATH -tt $connectionString "$commands"
}

# Copy the repo archive
sudo scp -q -o LogLevel=QUIET -i $KEYPATH $REPOPATH $REMOTENAME@$REMOTEIP:~
# run string of commands over ssh
silentSsh $REMOTENAME@$REMOTEIP << ENDSSH
mkdir -p repo_test
tar --overwrite -xf ~/repo.tar.gz -C ~/repo_test
cd ~/repo_test/honeypots/honeypot;
echo $REMOTEPASS | sudo -kS -p "
" python3 CronInstaller.py -p PortThreadManager.py -c ../config/new-config.json
ENDSSH
