FROM python:3.8-alpine

# Create working directory (bundled source)
WORKDIR /usr/src/app

# Install dependencies
RUN apk add --update tcpdump
RUN apk add gcc g++ make libffi-dev openssl-dev
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Get source files
COPY . .

# Database and ConfigTunnel Ports
EXPOSE 9998

# Do not buffer python otput
ENV PYTHONUNBUFFERED=0
# Mark as being in container
ENV AM_I_IN_A_DOCKER_CONTAINER=True

# Persistant Storage
VOLUME /storage

WORKDIR /usr/src/app/honeypot

# Add wait for script
RUN apk add --no-cache bash
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /opt/bin/
RUN chmod +x /opt/bin/wait-for-it.sh

ENTRYPOINT ["/opt/bin/wait-for-it.sh", "-s", "-t", "0"]
CMD ["couchdb:5984", "--", "python3", "-u", "./PortThreadManager.py"]
