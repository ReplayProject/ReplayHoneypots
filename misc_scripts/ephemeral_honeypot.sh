#! /bin/bash

# Starts a honeypot image so that it removes itself upon exit
# using "docker-compose up -d replay-honeypot" is best if you
# need more than a one-off environment

docker run --rm -it -v $PWD:/src -w /src 127.0.0.1:5000/seth/replay-honeypot:latest ash
