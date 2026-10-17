#!/usr/bin/env bash
# Checks that every tool is installed on every running lab node.
# Run on the host, with the lab started:  ./infra/tests/tools.sh
set -u

PASS=0
FAIL=0

# has <node> <command>  -> PASS if the command exists on the node
has() {
  if docker exec "$1" sh -c "command -v $2" >/dev/null 2>&1; then
    echo "PASS  $1: $2"; PASS=$((PASS + 1))
  else
    echo "FAIL  $1: $2 missing"; FAIL=$((FAIL + 1))
  fi
}

RUNNING=$(docker ps --format '{{.Names}}')
running() { echo "$RUNNING" | grep -qx "$1"; }

if ! running fw || ! running server; then
  echo "The lab is not running. Start it with: cd infra && docker compose up -d"
  exit 1
fi

for t in nft conntrack tcpdump; do has fw "$t"; done
for t in nginx dnsmasq sshd; do has server "$t"; done

for c in legit susp; do
  running "$c" || continue
  for t in curl wrk dig ssh sshpass nmap hping3 python3; do has "$c" "$t"; done
  if docker exec "$c" python3 -c "import scapy.all" >/dev/null 2>&1; then
    echo "PASS  $c: python3 scapy"; PASS=$((PASS + 1))
  else
    echo "FAIL  $c: python3 scapy missing"; FAIL=$((FAIL + 1))
  fi
  # Raw packets are needed by nmap -sS, hping3 and Scapy: send one SYN to the server
  if docker exec "$c" timeout 5 hping3 -c 1 -S -p 80 10.0.2.10 2>&1 | grep -q "flags=SA"; then
    echo "PASS  $c: raw packets (1 SYN, got SYN-ACK)"; PASS=$((PASS + 1))
  else
    echo "FAIL  $c: raw packets do not work"; FAIL=$((FAIL + 1))
  fi
done

echo
echo "Result: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
