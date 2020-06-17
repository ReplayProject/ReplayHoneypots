#! /bin/bash

# This script deployed the basic swarm visualizer service
docker stack deploy -c viz.yml viz --with-registry-auth
