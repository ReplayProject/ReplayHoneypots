#! /bin/bash

tar --exclude /shared/2020SpringTeam18/management --exclude /shared/2020SpringTeam18/.git --exclude __pycache__ -czvf repo.tar.gz /shared/2020SpringTeam18
