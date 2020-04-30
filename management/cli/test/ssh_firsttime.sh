#! /bin/bash

PORT=2222

ssh-keygen -f "$HOME/.ssh/known_hosts" -R "[0.0.0.0]:$PORT"

ssh -i ./privatekey fakehoney@0.0.0.0 -p $PORT "sudo -S su -c \"apk upgrade --update && apk add --no-cache python3 python3-dev gcc gfortran freetype-dev musl-dev libpng-dev g++ lapack-dev && apk add openssh\""

ssh -i ./privatekey fakehoney@0.0.0.0 -p $PORT
