FROM nikolaik/python-nodejs:python3.8-nodejs13

# Create working directory
WORKDIR /usr/src/app

# Get DB Dependency
RUN npm install -g pouchdb-server

# Install dependencies
RUN apt-get update -y && apt-get install tcpdump -y
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Get source files
COPY . .

# Expose some ports
EXPOSE 80
EXPOSE 445
EXPOSE 1437

WORKDIR /usr/src/app/honeypot
CMD ["python3", "./PortThreadManager.py"]
