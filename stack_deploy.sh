#! /bin/bash

# This script deploys the stack defined in the main compose file

docker stack deploy -c docker-compose.yml honey --with-registry-auth
