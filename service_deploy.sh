#! /bin/bash

  #  --mount dst=/usr/src/frontend/.data \
docker service create \
   --replicas 1 \
   --with-registry-auth \
   --network host \
   --env DB_URL="http://honeypots:securehoneypassword@192.168.23.50:5984" \
   --name replay-honeypot \
   --constraint node.role==worker \
   --placement-pref spread=node.id \
   cloud.canister.io:5000/seth/replay-honeypot:latest

# When we want to test replication and not direct writing
# TARGET_ADDR='http://admin:couchdb@couchdb:5984'
