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
CMD ["python3", "-u", "./PortThreadManager.py"]
