#! /bin/bash

docker service create \
   --replicas 1 \
   --with-registry-auth \
   --network host \
   --env DB_URL="http://honeypots:securehoneypassword@192.168.23.50:5984" \
   --name replay-honeypot \
   --constraint node.role==worker \
   --placement-pref spread=node.id \
   cloud.canister.io:5000/seth/replay-honeypot:latest


# Optional configurations
#  --mount type=bind,src=/shared/2020SpringTeam18/honeypots/honeypot/Databaser.py,dst=/usr/src/app/honeypot/Databaser.py \
#  --mount type=bind,src=/shared/2020SpringTeam18/honeypots/honeypot/Sniffer.py,dst=/usr/src/app/honeypot/Sniffer.py \
#  --env DB_URL="" \
#  --mount dst=/usr/src/frontend/.data \
#  --env TARGET_ADDR="http://honeypots:securehoneypassword@192.168.23.50:5984" \
