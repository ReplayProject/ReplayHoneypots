#!/bin/bash

KEYPATH=$1
REMOTEIP=$2
REMOTENAME=$3
REPOPATH=$4
PORT=$5

function silentSsh {
    local connectionString="$1"
    local commands="$2"
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

# Copy the repo archive
sudo scp -P $PORT -q -o LogLevel=QUIET -i $KEYPATH $REPOPATH $REMOTENAME@$REMOTEIP:~
# run string of commands over ssh
silentSsh $REMOTENAME@$REMOTEIP << ENDSSH
mkdir -p repo_test
tar --overwrite -xf ~/repo.tar.gz -C ~/repo_test
ENDSSH
echo "Honeypot installed successfully"
