#! /bin/bash
# Script to attempt to delete unused docker configs

ALL_CONFIGS=$(docker config ls | grep 'honey-*' | awk '{ print $1 }')

echo -e "Removed"
docker config rm $ALL_CONFIGS

echo -e "\nRemaining Configs"
docker config ls
