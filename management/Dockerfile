# Multi Stage build to get us up and running with the frontend!
# Based on - https://medium.com/hackernoon/a-tale-of-two-docker-multi-stage-build-layers-85348a409c84

ARG NODE_VERSION=14-alpine

FROM node:${NODE_VERSION} AS build

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
RUN npm prune --production && apk del native-deps
# RUN npm ci --only=production

# Next Layer!
FROM node:${NODE_VERSION}

# Get curl and bash for healthcheck / waitfor script
RUN apk add --no-cache bash curl
# Get wait for it, for DB
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /opt/bin/
RUN chmod +x /opt/bin/wait-for-it.sh

# Create app directory
WORKDIR /usr/src/frontend

# Install running deps and get files
COPY --from=build /src/node_modules node_modules
COPY --from=build /src/package* ./
COPY --from=build /src/dist ./dist
COPY ./frontend/server ./server
COPY ./frontend/.env .

# Create Port Mappings for frontend & database
EXPOSE 8080

HEALTHCHECK --interval=5s \
  --timeout=5s \
  --retries=6 \
  CMD curl -fs http://localhost:8080/ || exit 1

# Image default start strategy
ENTRYPOINT ["/opt/bin/wait-for-it.sh", "-s", "-t", "0"]
CMD ["couchdb:5984", "--", "npm", "run", "start-serve" ]
