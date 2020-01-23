#!/bin/bash

if [ $# -ne 3 ]
    then
        echo "Wrong number of arguments supplied."
        echo "Usage: sh $0 <server_url> <deploy_key> <honeypot_type>."
        exit 1
fi

server_url=$1
deploy_key=$2
honeypot=$3
hostname=$(hostname)

if [ -f /etc/debian_version ]; then
    OS=Debian  # XXX or Ubuntu??
    sudo apt-get install -y curl python

elif [ -f /etc/redhat-release ]; then
    OS=RHEL
    sudo yum -y install curl

else
    echo -e "ERROR: Unknown OS\nExiting!"
    exit -1
fi


curl -s -X POST -H "Content-Type: application/json" -d "{
	\"name\": \"${hostname}-${honeypot}\", 
	\"hostname\": \"$hostname\", 
	\"deploy_key\": \"$deploy_key\",
	\"honeypot\": \"$honeypot\"
}" $server_url/api/sensor/ > /tmp/deploy.json

uuid=$(python -c 'import json;obj=json.load(file("/tmp/deploy.json"));print obj["uuid"]')

if [ -z "$uuid" ]
    then
        echo "Could not create sensor using name \"$hostname\"."
        exit 1
fi

set -e

echo "Created sensor: " $uuid

######################################################
# hpfeeds info
export HPF_HOST=$(echo $server_url | sed 's#^http://##; s#^https://##; s#/.*$##; s/:.*$//')
export HPF_PORT="10000"
export HPF_IDENT=$(python -c 'import json;obj=json.load(file("/tmp/deploy.json"));print obj["identifier"]')
export HPF_SECRET=$(python -c 'import json;obj=json.load(file("/tmp/deploy.json"));print obj["secret"]')
######################################################
