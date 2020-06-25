#! /bin/bash
docker service update replay-honeypot --image 127.0.0.1:5000/replay/replay-honeypot:latest --force --with-registry-auth
docker service update honey_replay-manager --image 127.0.0.1:5000/replay/replay-manager:latest --force --with-registry-auth
