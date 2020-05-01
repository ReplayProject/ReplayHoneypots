#! /bin/bash
# Script to deploy the swarm's docker registry

echo "Deploying throwaway registry"

docker service create --name registry \
  --publish published=5000,target=5000 \
  --constraint node.role==manager \
  registry:2
