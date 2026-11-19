import sys
import time
import subprocess
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import save_result
import ipaddress

parser = argparse.ArgumentParser()
parser.add_argument("--target", required=True)
parser.add_argument("--duration", type=int, default=60)
parser.add_argument("--output", required=True)
parser.add_argument(
    "--type",
    choices=["syn", "null", "fin", "xmas"],
    required=True
)
args = parser.parse_args()

if ipaddress.ip_address(args.target) not in ipaddress.ip_network("10.0.0.0/8"):
    parser.error("Target must be in the isolated lab network")

flags = {
    "syn": "-sS",
    "null": "-sN",
    "fin": "-sF",
    "xmas": "-sX",
}

records = []
end = time.monotonic() + args.duration

while time.monotonic() < end:
    command = [
        "nmap",
        flags[args.type],
        "-Pn",
        "-n",
        "-p", "1-1024",
        "--max-retries", "0",
        args.target,
    ]

    start = time.monotonic()

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=max(10, args.duration + 10),
    )

    records.append({
        "label": "suspicious",
        "attack_type": f"{args.type}_scan",
        "target": args.target,
        "returncode": result.returncode,
        "duration_s": round(time.monotonic() - start, 3),
        "stdout": result.stdout,
        "stderr": result.stderr,
    })

save_result(args.output, f"{args.type}scan", records)