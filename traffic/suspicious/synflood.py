import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import get_args, save_result

from scapy.all import IP, TCP, send

args = get_args("Controlled SYN traffic", default_rate=20)

if args.rate > 100:
    raise SystemExit(
        "Pilot limit is 100 packets/s; review before increasing"
    )

records = []
interval = 1.0 / args.rate
end = time.monotonic() + min(args.duration, 30)
sent = 0
next_send = time.monotonic()

while time.monotonic() < end:
    packet = IP(dst=args.target) / TCP(
        dport=80,
        flags="S"
    )

    send(packet, verbose=False)
    sent += 1

    next_send += interval
    delay = next_send - time.monotonic()

    if delay > 0:
        time.sleep(delay)

records.append({
    "label": "suspicious",
    "attack_type": "syn_traffic",
    "target": args.target,
    "packets_sent": sent,
    "requested_rate": args.rate,
})

save_result(args.output, "synflood", records)