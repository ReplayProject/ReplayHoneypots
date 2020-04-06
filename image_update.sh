#! /bin/bash
docker service update replay-honeypot --image 127.0.0.1:5000/seth/replay-honeypot:latest --force --with-registry-auth
