# Multi Stage build to get us up and running with the frontend!
# Based on - https://medium.com/hackernoon/a-tale-of-two-docker-multi-stage-build-layers-85348a409c84

ARG NODE_VERSION=14-alpine

FROM node:${NODE_VERSION} AS build

RUN apk --update --no-cache add --virtual native-deps g++ gcc libgcc libstdc++ linux-headers make python

WORKDIR /src
COPY ./frontend/package* ./
RUN npm ci
# Setup parcel workers
ENV PARCEL_WORKERS 1

# Copy source files
COPY ./frontend/.env ./
COPY ./frontend/client ./client
RUN npm run build

# Prune out packages and dependencies
RUN npm prune --production && apk del native-deps
# RUN npm ci --only=production

# Next Layer!
FROM node:${NODE_VERSION}

# Get curl and bash for healthcheck
RUN apk add --no-cache bash curl

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

HEALTHCHECK --interval=15s --timeout=5s --retries=3 CMD curl -kfs https://localhost:8443 || exit 1

# Image default start strategy
CMD ["npm", "run", "start-serve"]
