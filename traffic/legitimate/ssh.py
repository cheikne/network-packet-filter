import sys
import time
import socket
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import get_args, save_result, run_periodic

args = get_args("Legitimate SSH connectivity", default_rate=1)


def connect():
    start = time.monotonic()
    banner = ""
    success = False

    try:
        with socket.create_connection(
            (args.target, 22), timeout=3
        ) as sock:
            sock.settimeout(3)
            banner = sock.recv(256).decode(
                errors="replace"
            ).strip()
            success = banner.startswith("SSH-")

    except OSError as exc:
        banner = str(exc)

    return {
        "label": "legitimate",
        "protocol": "SSH",
        "success": success,
        "banner": banner,
        "latency_ms": round(
            (time.monotonic() - start) * 1000, 3
        ),
    }


records = run_periodic(args.duration, args.rate, connect)
save_result(args.output, "ssh", records)