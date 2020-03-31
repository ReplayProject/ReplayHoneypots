#! /bin/bash

docker service create \
   --replicas 1 \
   --with-registry-auth \
   --network host \
   --env DB_URL="" \
   --name replay-honeypot \
   --constraint node.role==worker \
   --placement-pref spread=node.id \
   cloud.canister.io:5000/seth/replay-honeypot:latest


# Optional configurations
#  --mount dst=/usr/src/frontend/.data \
#  --env DB_URL="http://honeypots:securehoneypassword@192.168.23.50:5984" \
#  --env TARGET_ADDR="http://honeypots:securehoneypassword@192.168.23.50:5984" \
