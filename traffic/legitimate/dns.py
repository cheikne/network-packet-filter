import sys
import time
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import get_args, save_result, run_periodic

args = get_args("Legitimate DNS traffic", default_rate=10)


def query():
    start = time.monotonic()

    result = subprocess.run(
        [
            "dig",
            f"@{args.target}",
            "server.lab",
            "A",
            "+time=2",
            "+tries=1",
        ],
        capture_output=True,
        text=True,
        timeout=5,
    )

    return {
        "label": "legitimate",
        "protocol": "DNS",
        "success": (
            result.returncode == 0
            and "status: NOERROR" in result.stdout
        ),
        "latency_ms": round(
            (time.monotonic() - start) * 1000, 3
        ),
        "returncode": result.returncode,
    }


records = run_periodic(args.duration, args.rate, query)
save_result(args.output, "dns", records)