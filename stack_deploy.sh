#! /bin/bash
export REGISTRY_HOST=cloud.canister.io:5000
docker stack deploy -c docker-compose.yml honey --with-registry-auth
