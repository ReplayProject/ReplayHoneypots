#! /bin/bash
docker stack deploy -c docker-compose.yml honey --with-registry-auth
