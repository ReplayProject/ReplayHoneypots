#! /bin/bash
docker service rm replay-honeypot # remove honeypots
sleep 2
docker stack rm honey # remove manager and data

# TODO: uncommend when using persistance databases
# WAIT=15
# echo "Waiting $WAIT  seconds for service removal"
# sleep $WAIT
# docker volume rm honey_couchdb_data # delete database
