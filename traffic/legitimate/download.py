import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import get_args, save_result

args = get_args("Legitimate download test", default_rate=1)

start = time.monotonic()
total_bytes = 0
success = False
error = None

try:
    with urllib.request.urlopen(
        f"http://{args.target}/large.bin",
        timeout=max(10, args.duration)
    ) as response:
        while True:
            chunk = response.read(65536)
            if not chunk:
                break
            total_bytes += len(chunk)

    success = True

except Exception as exc:
    error = str(exc)

elapsed = time.monotonic() - start

save_result(args.output, "download", [{
    "label": "legitimate",
    "protocol": "HTTP",
    "success": success,
    "bytes": total_bytes,
    "duration_s": round(elapsed, 3),
    "throughput_mbps": round(
        total_bytes * 8 / elapsed / 1_000_000, 3
    ) if elapsed > 0 else 0,
    "error": error,
}])