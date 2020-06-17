#! /bin/bash

# This script runs 10 virtual honeypots on the
# current machine with docker-compose

docker-compose up --scale replay-honeypot=10 replay-honeypot
