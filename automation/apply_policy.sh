#!/usr/bin/env bash
# Load a firewall policy into fw.
# Usage: ./automation/apply_policy.sh <name>
#   <name> = policy file in policies/ without ".nft" (for example p1_basic)
#   "baseline" with no policies/baseline.nft simply removes all rules.
set -euo pipefail

NAME=${1:?usage: apply_policy.sh <name>}
ROOT=$(cd "$(dirname "$0")/.." && pwd)
FILE="policies/$NAME.nft"

if [ -f "$ROOT/$FILE" ]; then
  # nft -f is atomic: if the file has an error, nothing is changed
  docker exec fw nft -f "/project/$FILE"
elif [ "$NAME" = baseline ]; then
  docker exec fw nft flush ruleset
else
  echo "apply_policy.sh: $FILE not found" >&2
  exit 1
fi

echo "Policy '$NAME' loaded on fw. Active rules:"
docker exec fw nft list ruleset
