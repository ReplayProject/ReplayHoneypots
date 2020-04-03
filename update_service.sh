#! /bin/bash
# Checks for a new config and tries to update services with it

OLDTAGS=$(docker service inspect replay-honeypot | grep ConfigName -m2 | awk '{ print $2}' | tr -d '"' | tr '\n' ' ')
TAG1=$(echo $OLDTAGS | awk '{print $1}')
TAG2=$(echo $OLDTAGS | awk '{print $2}')

if ([[ $TAG1 == "honey-cfg-$TAG" ]] || [[ $TAG2 == "honey-cfg-$TAG" ]]); then
  echo "New configs not found (run create_configs.sh)"
  exit
else
  echo "Updating Honeypot configs from $OLDTAGS to $TAG"

  docker service update \
    --config-rm $TAG1 \
    --config-rm $TAG2 \
    --config-add source="honey-cfg-$TAG",target="/properties.cfg"\
    --config-add source="honey-data-$TAG",target="/senddata.json"\
    --with-registry-auth \
    replay-honeypot
fi
