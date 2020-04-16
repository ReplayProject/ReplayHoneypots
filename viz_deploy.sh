#! /bin/bash
docker stack deploy -c viz.yml viz --with-registry-auth
