#! /bin/bash

# This script deployed the basic swarm visualizer service
docker stack deploy -c meta.yml meta --with-registry-auth
