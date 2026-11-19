import csv
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "results" / "raw"
OUTPUT = ROOT / "results" / "processed" / "summary.csv"

rows = []

for metadata_path in sorted(RAW.glob("*/metadata.json")):
    run_dir = metadata_path.parent
    metadata = json.loads(metadata_path.read_text())

    for path in sorted((run_dir / "clients").rglob("*.json")):
        data = json.loads(path.read_text())
        records = data.get("records", [])

        if not records:
            continue

        successes = [
            r["success"]
            for r in records
            if isinstance(r.get("success"), bool)
        ]

        latencies = [
            r["latency_ms"]
            for r in records
            if isinstance(r.get("latency_ms"), (int, float))
        ]

        throughputs = [
            r["throughput_mbps"]
            for r in records
            if isinstance(r.get("throughput_mbps"), (int, float))
        ]

        rows.append({
            "run_id": metadata["run_id"],
            "configuration": metadata["configuration"],
            "scenario": metadata["scenario"],
            "repetition": metadata["repetition"],
            "traffic_type": data.get("traffic_type", path.stem),
            "total_events": len(records),
            "success_rate": (
                round(sum(successes) / len(successes), 4)
                if successes else ""
            ),
            "avg_latency_ms": (
                round(statistics.mean(latencies), 3)
                if latencies else ""
            ),
            "avg_throughput_mbps": (
                round(statistics.mean(throughputs), 3)
                if throughputs else ""
            ),
        })

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

fields = [
    "run_id",
    "configuration",
    "scenario",
    "repetition",
    "traffic_type",
    "total_events",
    "success_rate",
    "avg_latency_ms",
    "avg_throughput_mbps",
]

with OUTPUT.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"Processed {len(rows)} traffic logs")
print(f"Saved: {OUTPUT}")