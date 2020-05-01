#! /bin/bash

# This script defines all the ports needed to run the system
# When ran on a NCSU VM it will open all required ports.
# Usage: sudo ./open_ports.sh

# campus allows access from ncsu internet
# public allows access from internal VM network

# 8080 - Replay Frontend
sudo firewall-cmd --zone=campus --add-port=8080/tcp
sudo firewall-cmd --zone=public --add-port=8080/tcp

# 8000 - Fauxton Frontend
sudo firewall-cmd --zone=campus --add-port=8000/tcp
sudo firewall-cmd --zone=public --add-port=8000/tcp

# 8082 - Viz Frontend
sudo firewall-cmd --zone=campus --add-port=8082/tcp
sudo firewall-cmd --zone=public --add-port=8082/tcp

# 5984 - Couchdb Ports (DB)
sudo firewall-cmd --zone=campus --add-port=5984/tcp
sudo firewall-cmd --zone=public --add-port=5984/tcp
# 4369 - Couchdb Ports
sudo firewall-cmd --zone=campus --add-port=4369/tcp
sudo firewall-cmd --zone=public --add-port=4369/tcp
# 9100 - Couchdb Ports
sudo firewall-cmd --zone=campus --add-port=9100/tcp
sudo firewall-cmd --zone=public --add-port=9100/tcp

# 9998 - Replay Honeypot Config tunnel
sudo firewall-cmd --zone=campus --add-port=9998/tcp
sudo firewall-cmd --zone=public --add-port=9998/tcp

# Docker (Swarm) Ports

# TCP port 2376 for secure Docker client communication.
# This port is required for Docker Machine to work. Docker Machine is used to orchestrate Docker hosts.
sudo firewall-cmd --zone=campus --add-port=2376/tcp
sudo firewall-cmd --zone=public --add-port=2376/tcp

# TCP port 2377. This port is used for communication between the nodes of a Docker Swarm or cluster.
# It only needs to be opened on manager nodes.
sudo firewall-cmd --zone=campus --add-port=2377/tcp
sudo firewall-cmd --zone=public --add-port=2377/tcp

# Docker registry
sudo firewall-cmd --zone=campus --add-port=5000/tcp
sudo firewall-cmd --zone=campus --add-port=5000/udp
sudo firewall-cmd --zone=public --add-port=5000/tcp
sudo firewall-cmd --zone=public --add-port=5000/udp

# TCP and UDP port 7946 for communication among nodes (container network discovery).
sudo firewall-cmd --zone=public --add-port=7946/tcp
sudo firewall-cmd --zone=campus --add-port=7946/tcp
sudo firewall-cmd --zone=public --add-port=7946/udp
sudo firewall-cmd --zone=campus --add-port=7946/udp

# UDP port 4789 for overlay network traffic (container ingress networking).
sudo firewall-cmd --zone=public --add-port=4789/udp
sudo firewall-cmd --zone=campus --add-port=4789/udp
