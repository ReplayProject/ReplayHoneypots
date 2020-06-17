#! /bin/bash

# This scripy attempts to remove the services for the honeypot and
# the services from the main compose file
# Note: does not delete volumes, networks, or images. See the docker prune command

docker service rm replay-honeypot # remove honeypots
sleep 2
docker stack rm honey # remove manager and data

# TODO: uncomment when using persistance databases
# WAIT=15
# echo "Waiting $WAIT  seconds for service removal"
# sleep $WAIT
# docker volume rm honey_couchdb_data # delete database
