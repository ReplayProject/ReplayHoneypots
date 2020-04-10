#! /bin/bash
ssh-keygen -f "/home/seth/.ssh/known_hosts" -R "[localhost]:2222"
ssh -i ./privatekey linuxserver.io@localhost -p 2222
