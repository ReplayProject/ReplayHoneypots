#!/bin/bash

KEYPATH=$1
REMOTEIP=$2
REMOTENAME=$3
REMOTEPASS=$4
PORT=$5

function silentSsh {
    local connectionString="$1"
    local commands="$2"
    local port=$3

    if [ -z "$commands" ]; then
        commands=`cat`
    fi
    # to stop ssh output switch from -tt to -T
    ssh -i $KEYPATH -p $PORT -tt $connectionString "$commands"
}

# catch errors
trap 'catch $? $LINENO' ERR

# if an error is caught print out the line number and exit
function catch {
    echo "Error $1 has occurred on line $2"
    exit
}

# run string of commands over ssh
silentSsh $REMOTENAME@$REMOTEIP << ENDSSH
cd ~/repo_test/shared/2020SpringTeam18/honeypots/honeypot;
echo $REMOTEPASS | sudo -kS -p "
" python3 CronUninstaller.py
ENDSSH
echo "Honeypot stopped successfully"
