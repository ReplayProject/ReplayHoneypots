#! /bin/bash

# Create a certfile for config tunnel - https://stackoverflow.com/questions/11255530/python-simple-ssl-socket-server
# this should live in the /config folder

openssl req -new -x509 -days 365 -nodes -out cert.pem -keyout cert.pem
