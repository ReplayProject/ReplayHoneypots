#! /bin/bash
docker service update replay-honeypot --image cloud.canister.io:5000/seth/replay-honeypot:latest --force --with-registry-auth
