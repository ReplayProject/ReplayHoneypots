# FROM rastasheep/ubuntu-sshd:18.04
FROM node:13-alpine

# Create app directory
WORKDIR /usr/src/frontend

# Install app dependencies
COPY ./frontend/package*.json ./

# RUN npm install
# Pre Install Setup
RUN apk --no-cache add --virtual native-deps \
  g++ gcc libgcc libstdc++ linux-headers make python && \
  npm install --quiet node-gyp -g &&\
  npm install --quiet && \
  apk del native-deps

# Copy source files
COPY ./frontend/ .

# Create Port Mappings for frontend & database
EXPOSE 8080
EXPOSE 8081

# Image Env Variables
ENV PARCEL_WORKERS 1

CMD [ "npm", "run", "start" ]
