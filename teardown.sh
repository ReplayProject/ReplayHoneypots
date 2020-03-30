#! /bin/bash
docker service rm replay-honeypot # remove honeypots
sleep 2
docker stack rm honey # remove manager and data
echo "Waiting 7 seconds for service removal"
sleep 7
docker volume rm honey_couchdb_data # delete database
