import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import get_args, save_result, run_periodic

args = get_args("Legitimate HTTP traffic", default_rate=20)


def request():
    start = time.monotonic()

    try:
        with urllib.request.urlopen(
            f"http://{args.target}/", timeout=3
        ) as response:
            status = response.status
            response.read()

        success = 200 <= status < 400
        error = None

    except Exception as exc:
        status = None
        success = False
        error = str(exc)

    return {
        "label": "legitimate",
        "protocol": "HTTP",
        "success": success,
        "status": status,
        "latency_ms": round(
            (time.monotonic() - start) * 1000, 3
        ),
        "error": error,
    }


records = run_periodic(args.duration, args.rate, request)
save_result(args.output, "http", records)