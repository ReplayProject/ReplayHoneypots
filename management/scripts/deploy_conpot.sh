#!/bin/bash

if [ $# -ne 2 ]
    then
        echo "Wrong number of arguments supplied."
        echo "Usage: $0 <server_url> <deploy_key>."
        exit 1
fi

server_url=$1
deploy_key=$2

echo "deb http://en.archive.ubuntu.com/ubuntu precise main multiverse" | sudo tee -a /etc/apt/sources.list
apt-get update
apt-get install -y git libmysqlclient-dev libsmi2ldbl snmp-mibs-downloader python-dev libevent-dev libxslt1-dev libxml2-dev python-pip python-mysqldb pkg-config libvirt-dev supervisor
apt-get install -y zlib1g-dev # needed for Ubuntu 14.04
pip install --upgrade distribute
pip install virtualenv

CONPOT_HOME=/opt/conpot
mkdir -p $CONPOT_HOME
cd $CONPOT_HOME
virtualenv env
. env/bin/activate
pip install -U setuptools
pip install -e git+https://github.com/pwnlandia/hpfeeds.git#egg=hpfeeds-dev
pip install -e git+https://github.com/mushorg/conpot.git@Release_0.5.2#egg=conpot-dev
pip install -e git+https://github.com/mushorg/modbus-tk.git#egg=modbus-tk

# Register sensor with MHN server.
wget $server_url/static/registration.txt -O registration.sh
chmod 755 registration.sh
# Note: this will export the HPF_* variables
. ./registration.sh $server_url $deploy_key "conpot"

cat > conpot.cfg <<EOF
[common]
sensorid = default
[session]
timeout = 30
[daemon]
;user = conpot
;group = conpot
[json]
enabled = False
filename = /var/log/conpot.json
[sqlite]
enabled = False
[mysql]
enabled = False
[syslog]
enabled = False
device = /dev/log
host = localhost
port = 514
facility = local0
socket = dev        ; udp (sends to host:port), dev (sends to device)
[hpfriends]
enabled = True
host = $HPF_HOST
port = $HPF_PORT
ident = $HPF_IDENT
secret = $HPF_SECRET
channels = ["conpot.events", ]
[taxii]
enabled = False
host = taxiitest.mitre.org
port = 80
inbox_path = /services/inbox/default/
use_https = False
include_contact_info = False
contact_name = ...
contact_email = ...
[fetch_public_ip]
enabled = True
urls = ["http://www.telize.com/ip", "http://icanhazip.com/", "http://ifconfig.me/ip"]
[change_mac_addr]
enabled = False
iface = eth0
addr = 00:de:ad:be:ef:00
EOF

# setup supervisor

cat > /etc/supervisor/conf.d/conpot.conf <<EOF
[program:conpot]
command=/opt/conpot/env/bin/conpot --template default -c /opt/conpot/conpot.cfg -l /var/log/conpot.log
directory=/opt/conpot
stdout_logfile=/var/log/conpot.out
stderr_logfile=/var/log/conpot.err
autostart=true
autorestart=true
redirect_stderr=true
stopsignal=QUIT
EOF

supervisorctl update
