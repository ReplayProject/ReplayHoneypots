#! /bin/bash
# Script to create docker configs for properties.cfg and senddata.json

# Set versioning tag
TAG=$(date +%s)
export TAG=$TAG
echo "Set TAG to: $TAG"

# Create config
docker config create honey-conf-defaults-$TAG $PWD/config/defaults.json >/dev/null
docker config create honey-sslcert-$TAG $PWD/config/cert.pem >/dev/null

# List existing configs
echo -e "\n"
docker config ls

# Do this so script should be sourced (to export TAG)
return $TAG
