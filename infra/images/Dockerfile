# One Dockerfile for all lab nodes. Each node uses one target:
#   fw      -> firewall
#   server  -> web, DNS, SSH server
#   client  -> legit and susp
# Packages are installed only here, at build time. At runtime the lab
# networks have no internet access.

FROM debian:bookworm-slim AS base
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      bash iproute2 iputils-ping procps \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /project

# Firewall node
FROM base AS fw
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends nftables conntrack tcpdump \
 && rm -rf /var/lib/apt/lists/*

# Server node: nginx (HTTP/HTTPS), dnsmasq (DNS), OpenSSH
FROM base AS server
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      nginx openssl dnsmasq-base openssh-server \
 && rm -rf /var/lib/apt/lists/*
# Self-signed certificate for HTTPS (created at build time, never in Git)
RUN openssl req -x509 -nodes -newkey rsa:2048 -days 3650 -subj "/CN=server.lab" \
      -keyout /etc/ssl/private/lab.key -out /etc/ssl/certs/lab.crt
# The SSH lab account is created at startup from infra/.env (node_start.sh)

# Client nodes: tools for legitimate and suspicious traffic (used by Role 2)
FROM base AS client
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      curl wrk dnsutils openssh-client sshpass \
      nmap hping3 python3 python3-scapy \
 && rm -rf /var/lib/apt/lists/*
