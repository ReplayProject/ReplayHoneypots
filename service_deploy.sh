#! /bin/bash

docker service create \
   --with-registry-auth \
   --env DB_URL="http://honeypots:securehoneypassword@192.168.23.50:5984" \
   --replicas "${1:-1}" \
   --replicas-max-per-node 1 \
   --constraint node.role==worker \
   --placement-pref spread=node.id \
   --restart-condition on-failure \
   --network host \
   --name replay-honeypot \
   cloud.canister.io:5000/seth/replay-honeypot:latest


# Optional configurations
#  --mount type=bind,src=/shared/2020SpringTeam18/honeypots/honeypot/Databaser.py,dst=/usr/src/app/honeypot/Databaser.py \
#  --mount type=bind,src=/shared/2020SpringTeam18/honeypots/honeypot/Sniffer.py,dst=/usr/src/app/honeypot/Sniffer.py \
#  --env DB_URL="" \
#  --mount dst=/usr/src/frontend/.data \
#  --env TARGET_ADDR="http://honeypots:securehoneypassword@192.168.23.50:5984" \
