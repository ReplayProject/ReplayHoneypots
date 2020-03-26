FROM nikolaik/python-nodejs:python3.8-nodejs13

# Create working directory (bundled source)
WORKDIR /usr/src/app

# Get DB Dependency
RUN npm install -g pouchdb-server

# Install dependencies
RUN apt-get update -y && apt-get install tcpdump -y
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Get source files
COPY . .

# Expose some ports for "poking"
EXPOSE 5040
# Database and ConfigTunnel Ports
EXPOSE 1437
EXPOSE 9998

# Do not buffer python otput
ENV PYTHONUNBUFFERED=0

WORKDIR /usr/src/app/honeypot
CMD ["python3", "-u", "./PortThreadManager.py"]
