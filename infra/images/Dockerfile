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

# Firewall node (nftables, conntrack, tcpdump are added in Step 4)
FROM base AS fw

# Server node (nginx, dnsmasq, openssh are added in Step 4)
FROM base AS server

# Client nodes (traffic tools are added in Step 5)
FROM base AS client
