import argparse
import ipaddress
import json
import time
from pathlib import Path

LAB_NETWORK = ipaddress.ip_network("10.0.0.0/8")


def get_args(description, default_rate=5):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--target", required=True)
    parser.add_argument("--duration", type=int, default=60)
    parser.add_argument("--rate", type=float, default=default_rate)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    address = ipaddress.ip_address(args.target)
    if address not in LAB_NETWORK:
        parser.error("Target must be inside the isolated lab network")

    if args.duration <= 0 or args.rate <= 0:
        parser.error("Duration and rate must be positive")

    return args


def save_result(output, name, records):
    folder = Path(output)
    folder.mkdir(parents=True, exist_ok=True)

    path = folder / f"{name}.json"

    data = {
        "traffic_type": name,
        "timestamp": time.time(),
        "total_events": len(records),
        "records": records,
    }

    path.write_text(json.dumps(data, indent=2))
    print(f"Saved {path}")


def run_periodic(duration, rate, operation):
    records = []
    end = time.monotonic() + duration
    interval = 1.0 / rate
    next_run = time.monotonic()

    while time.monotonic() < end:
        records.append(operation())
        next_run += interval
        remaining = next_run - time.monotonic()

        if remaining > 0:
            time.sleep(remaining)

    return records