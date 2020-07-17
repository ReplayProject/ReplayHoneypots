# Multi Stage build to get us up and running with the frontend!
FROM node:14-alpine AS build

RUN apk --update --no-cache add --virtual native-deps \
  g++ gcc libgcc libstdc++ linux-headers make python

WORKDIR /src
COPY ./frontend/package* ./
RUN npm ci
# Setup parcel workers
ENV PARCEL_WORKERS 1

# Copy source files
COPY ./frontend/.env .
COPY ./frontend/client ./client
RUN npm run build

# Prune out packages and dependencies
RUN npm prune --production
RUN apk del native-deps

# Next Layer!
FROM node:14-alpine

# Get curl for healthcheck
RUN apk add --update --no-cache --virtual native-deps\
  g++ gcc libgcc libstdc++ linux-headers make python
# Get wait for it, for DB
RUN apk add --no-cache bash
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /opt/bin/
RUN chmod +x /opt/bin/wait-for-it.sh

# Create app directory
WORKDIR /usr/src/frontend

# Install running deps
COPY ./frontend/package* ./
RUN npm install --only=production
RUN apk del native-deps

COPY --from=build /src/dist ./dist
COPY ./frontend/server ./server
COPY ./frontend/.env .

# Create Port Mappings for frontend & database
EXPOSE 8080

# Image default start strategy
ENTRYPOINT ["/opt/bin/wait-for-it.sh", "-s", "-t", "0"]
CMD ["couchdb:5984", "--", "npm", "run", "start-serve" ]
