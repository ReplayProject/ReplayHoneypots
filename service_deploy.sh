#! /bin/bash
# Script to deploy the honeypot service(s), $1 is the replicas you want
# The env variable $TAG should be set with latest config revision
# Also, if given DB endpoints, those endpoints must be reachable fromt he honeypot

echo "Deploying Honeypots with config revision: $TAG"

if [ -z "$TAG" ]; then
    echo "ERROR: \$TAG is not set (run \". create_configs.sh\")"
    exit
fi

docker service create \
   --with-registry-auth \
   --env DB_URL="http://honeypots:securehoneypassword@192.168.23.50:5984" \
   --env HONEY_CFG="/properties.cfg" \
   --replicas "${1:-1}" \
   --replicas-max-per-node 1 \
   --constraint node.role==worker \
   --placement-pref spread=node.id \
   --restart-condition on-failure \
   --network host \
   --name replay-honeypot \
   --config src="honey-cfg-$TAG",target="/properties.cfg" \
   --config src="honey-data-$TAG",target="/senddata.json" \
   127.0.0.1:5000/seth/replay-honeypot:latest


# Optional configurations
#  --mount type=bind,src=/shared/2020SpringTeam18/honeypots/honeypot/Databaser.py,dst=/usr/src/app/honeypot/Databaser.py \
#  --mount type=bind,src=/shared/2020SpringTeam18/honeypots/honeypot/Sniffer.py,dst=/usr/src/app/honeypot/Sniffer.py \
#  --mount dst=/usr/src/frontend/.data \
#  --env TARGET_ADDR="http://honeypots:securehoneypassword@192.168.23.50:5984" \
