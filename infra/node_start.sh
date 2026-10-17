#!/usr/bin/env bash
# Startup script for every lab node. Docker runs it when a container starts.
# The node type comes from the container hostname (fw, server, legit, susp).
set -euo pipefail

CONF=/project/infra/server

case "$(hostname)" in
  legit|susp)
    # Reach the server network through fw, and use the lab DNS server
    ip route replace 10.0.2.0/24 via 10.0.1.1
    echo "nameserver 10.0.2.10" > /etc/resolv.conf
    ;;

  fw)
    # Start with no filtering (Baseline). Policies are loaded later
    # with automation/apply_policy.sh.
    nft flush ruleset
    ;;

  server)
    # Send replies to the client network back through fw
    ip route replace 10.0.1.0/24 via 10.0.2.1
    mkdir -p /var/log/lab /run/sshd

    # Web: a small page and a large file for download tests
    echo "lab server" > /var/www/html/index.html
    head -c "${LARGE_FILE_MB:-50}M" /dev/urandom > /var/www/html/large.bin
    rm -f /etc/nginx/sites-enabled/default
    cp "$CONF/nginx.conf" /etc/nginx/conf.d/lab.conf
    nginx

    # DNS: answers only lab names, no internet forwarding
    dnsmasq --conf-file="$CONF/dnsmasq.conf"

    # SSH: password login for the lab user (name and password from infra/.env)
    id "$LAB_SSH_USER" >/dev/null 2>&1 || useradd -m -s /bin/bash "$LAB_SSH_USER"
    echo "$LAB_SSH_USER:$LAB_SSH_PASSWORD" | chpasswd
    cp "$CONF/sshd.conf" /etc/ssh/sshd_config.d/lab.conf
    /usr/sbin/sshd -E /var/log/lab/sshd.log
    ;;

  *)
    echo "node_start.sh: unknown node $(hostname)" >&2
    exit 1
    ;;
esac

echo "$(hostname) ready"
exec sleep infinity
