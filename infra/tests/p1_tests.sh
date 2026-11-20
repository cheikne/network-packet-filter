#!/usr/bin/env bash
# Tests the P1 allowlist from the legitimate and suspicious clients.
# Run on the host with fw, server, legit, and susp running:
#   bash infra/tests/p1_tests.sh
set -u

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
SERVER=10.0.2.10
PASS=0
FAIL=0

# check "description" command... -> PASS if the command succeeds
check() {
  local desc=$1; shift
  if "$@" >/dev/null 2>&1; then echo "PASS  $desc"; PASS=$((PASS + 1))
  else echo "FAIL  $desc"; FAIL=$((FAIL + 1)); fi
}

# check_not "description" command... -> PASS if the command fails
check_not() {
  local desc=$1; shift
  if "$@" >/dev/null 2>&1; then echo "FAIL  $desc"; FAIL=$((FAIL + 1))
  else echo "PASS  $desc"; PASS=$((PASS + 1)); fi
}

RUNNING=$(docker ps --format '{{.Names}}')
for node in fw server legit susp; do
  if ! echo "$RUNNING" | grep -qx "$node"; then
    echo "Required container '$node' is not running. Start the lab with: make up"
    exit 1
  fi
done

echo "== Check and load P1"
if ! docker exec fw nft -c -f /project/policies/p1_basic.nft; then
  echo "P1 syntax check failed."
  exit 1
fi
"$ROOT/automation/apply_policy.sh" p1_basic

echo "== P1: legitimate client allowed services"
check "legit: DNS over UDP" \
  docker exec legit sh -c "dig +short +time=2 +tries=1 @$SERVER server.lab | grep -qx $SERVER"
check "legit: DNS over TCP" \
  docker exec legit sh -c "dig +tcp +short +time=2 +tries=1 @$SERVER server.lab | grep -qx $SERVER"
check "legit: HTTPS" \
  docker exec legit curl -skf --max-time 5 -o /dev/null "https://$SERVER/"
check "legit: SSH login" \
  docker exec legit sh -c 'timeout 10 sshpass -p "$LAB_SSH_PASSWORD" ssh \
    -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -o ConnectTimeout=5 "$LAB_SSH_USER@10.0.2.10" true'

echo "== P1: disallowed traffic blocked"
check_not "legit: HTTP is blocked" \
  docker exec legit curl -sf --max-time 3 -o /dev/null "http://$SERVER/"
check_not "susp: DNS over UDP is blocked" \
  docker exec susp sh -c "dig +short +time=2 +tries=1 @$SERVER server.lab | grep -qx $SERVER"
check_not "susp: DNS over TCP is blocked" \
  docker exec susp sh -c "dig +tcp +short +time=2 +tries=1 @$SERVER server.lab | grep -qx $SERVER"
check_not "susp: HTTPS is blocked" \
  docker exec susp curl -skf --max-time 3 -o /dev/null "https://$SERVER/"
check_not "susp: SSH is blocked" \
  docker exec susp sh -c 'timeout 3 bash -c \
    "exec 3<>/dev/tcp/10.0.2.10/22 && head -c 7 <&3 | grep -q SSH-2.0"'

echo
echo "Result: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
