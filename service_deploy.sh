#! /bin/bash

  #  --mount dst=/usr/src/frontend/.data \
docker service create \
   --replicas 1 \
   --with-registry-auth \
   --network host \
   --name replay-honeypot \
   --constraint node.role==worker \
   --placement-pref spread=node.id \
   cloud.canister.io:5000/seth/replay-honeypot:latest
