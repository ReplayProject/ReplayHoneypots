#! /bin/bash

# Script used to create a hashed password for the frontend

# Reads in env variables from the .env file
set -a
. ./.env
set +a

read -p "What should the user's password be? " PASS
echo -e "\nHere is your salted hash:\n"
SALT=$(cat $AUTH_FILE_FALLBACK | python -c "import sys, json; print(json.load(sys.stdin)['documents'][0]['value'])")

echo -n "$SALT$PASS" | sha256sum -t
