#!/usr/bin/env bash
# Connectivity test with the Baseline (no filtering).
# Proves that the running clients (legit, susp) reach every service on the
# server, and that they reach it ONLY through fw.
# Run on the host, with the lab started:  ./infra/tests/connectivity.sh
set -u

SERVER=10.0.2.10
PASS=0
FAIL=0

# check "description" command...      -> PASS if the command succeeds
check() {
  local desc=$1; shift
  if "$@" >/dev/null 2>&1; then echo "PASS  $desc"; PASS=$((PASS + 1))
  else echo "FAIL  $desc"; FAIL=$((FAIL + 1)); fi
}

# check_not "description" command...  -> PASS if the command fails
check_not() {
  local desc=$1; shift
  if "$@" >/dev/null 2>&1; then echo "FAIL  $desc"; FAIL=$((FAIL + 1))
  else echo "PASS  $desc"; PASS=$((PASS + 1)); fi
}

# Packet counter of a fw interface (rx or tx)
fw_count() { docker exec fw cat "/sys/class/net/$1/statistics/$2_packets"; }

CLIENTS=$(docker ps --format '{{.Names}}' | grep -xE 'legit|susp' | sort)
if [ -z "$CLIENTS" ] || ! docker ps --format '{{.Names}}' | grep -qx fw; then
  echo "The lab is not running. Start it with: cd infra && docker compose up -d"
  exit 1
fi

echo "== Baseline: remove all firewall rules"
check "fw ruleset flushed" docker exec fw nft flush ruleset

for c in $CLIENTS; do
  echo "== $c -> server"
  check "$c: route to server goes via fw (10.0.1.1)" \
    docker exec "$c" sh -c "ip route get $SERVER | grep -q 'via 10.0.1.1'"
  check "$c: ping"  docker exec "$c" ping -c 2 -W 2 "$SERVER"
  check "$c: HTTP"  docker exec "$c" curl -sf -o /dev/null --max-time 5 "http://$SERVER/"
  check "$c: HTTPS" docker exec "$c" curl -skf -o /dev/null --max-time 5 "https://$SERVER/"
  check "$c: large file download" \
    docker exec "$c" curl -sf -o /dev/null --max-time 30 "http://$SERVER/large.bin"
  check "$c: DNS (server.lab -> $SERVER)" \
    docker exec "$c" sh -c "dig +short +time=2 +tries=1 @$SERVER server.lab | grep -qx $SERVER"
  check "$c: SSH banner" \
    docker exec "$c" timeout 3 bash -c "exec 3<>/dev/tcp/$SERVER/22 && head -c 7 <&3 | grep -q SSH-2.0"
  check "$c: SSH login with the lab account" \
    docker exec "$c" sh -c "timeout 10 sshpass -p \"\$LAB_SSH_PASSWORD\" ssh -o StrictHostKeyChecking=no \
      -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 \"\$LAB_SSH_USER@$SERVER\" true"
  check "$c: server log shows the real client IP (no NAT)" \
    docker exec server sh -c "grep -q \"^$(docker exec "$c" hostname -i | awk '{print $1}') \" /var/log/lab/nginx_access.log"
done

echo "== Server setup"
check "SSH lab account exists on server" docker exec server sh -c 'id "$LAB_SSH_USER"'

echo "== Traffic crosses fw"
c=$(echo "$CLIENTS" | head -1)
rx1=$(fw_count eth1 rx); tx2=$(fw_count eth2 tx)
docker exec "$c" ping -c 20 -i 0.05 -W 1 "$SERVER" >/dev/null 2>&1
rx1_new=$(fw_count eth1 rx); tx2_new=$(fw_count eth2 tx)
check "20 pings seen on fw eth1 (in) and eth2 (out)" \
  test $((rx1_new - rx1)) -ge 20 -a $((tx2_new - tx2)) -ge 20

echo "== No path around fw (fw eth2 switched off for a moment)"
trap 'docker exec fw ip link set eth2 up' EXIT
docker exec fw ip link set eth2 down
for c in $CLIENTS; do
  check_not "$c: cannot reach server without fw" docker exec "$c" ping -c 2 -W 1 "$SERVER"
done
docker exec fw ip link set eth2 up
trap - EXIT
sleep 1
check "server reachable again after eth2 is back" docker exec "$c" ping -c 2 -W 2 "$SERVER"

echo "== Lab isolation (no internet)"
for n in fw server $CLIENTS; do
  check_not "$n: no internet" docker exec "$n" ping -c 1 -W 2 1.1.1.1
done

echo
echo "Result: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
