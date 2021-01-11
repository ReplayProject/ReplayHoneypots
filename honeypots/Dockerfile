# Multi Stage build to get us up and running with the honeypots!
# Based on - https://www.merixstudio.com/blog/docker-multi-stage-builds-python-development/

ARG PYTHON_VERSION=3.8-alpine

FROM python:${PYTHON_VERSION} AS build
ENV PYTHONUNBUFFERED 1

# Build Reqs
RUN apk add --update --no-cache tcpdump gcc g++ make libffi-dev openssl-dev

WORKDIR /wheels
COPY ./requirements.txt ./
RUN pip install -U pip && pip wheel -r ./requirements.txt

# Final Image
FROM python:${PYTHON_VERSION}
ENV PYTHONUNBUFFERED 1

# Install dependencies
# Also add wait for script (bash is for this)
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /opt/bin/
RUN apk add --update --no-cache tcpdump bash \
  && chmod +x /opt/bin/wait-for-it.sh \
  && rm -rf /var/cache/apk/*

# Use Builder image's wheels
COPY --from=build /wheels /wheels
RUN pip install -U pip \
  && pip install -r /wheels/requirements.txt \
  -f /wheels \
  && rm -rf /wheels \
  && rm -rf /root/.cache/pip/*

# Create working directory (bundled source)
WORKDIR /usr/src/app
# Get source files
COPY . .

# Database and ConfigTunnel Ports
EXPOSE 9998

# Mark as being in container
ENV AM_I_IN_A_DOCKER_CONTAINER=True

# Persistant Storage
VOLUME /storage

WORKDIR /usr/src/app/honeypot

# ENTRYPOINT ["/opt/bin/wait-for-it.sh", "-s", "-t", "0"]
# ENTRYPOINT [ "ls" ]
CMD ["python3", "-u", "./PortThreadManager.py"]
# CMD ["sh"]