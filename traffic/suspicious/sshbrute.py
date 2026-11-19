import sys
import time
import socket
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import get_args, save_result, run_periodic

args = get_args("Repeated SSH connections", default_rate=20)


def attempt():
    start = time.monotonic()
    success = False

    try:
        with socket.create_connection(
            (args.target, 22), timeout=2
        ):
            success = True
    except OSError:
        pass

    return {
        "label": "suspicious",
        "attack_type": "ssh_connection_attempt",
        "success": success,
        "latency_ms": round(
            (time.monotonic() - start) * 1000, 3
        ),
    }


records = run_periodic(args.duration, args.rate, attempt)
save_result(args.output, "sshbrute", records)