
import csv
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "results" / "processed" / "summary.csv"
OUTPUT = ROOT / "results" / "processed" / "aggregated.csv"

groups = defaultdict(list)

with INPUT.open(newline="") as f:
    for row in csv.DictReader(f):
        key = (
            row["configuration"],
            row["scenario"],
            row["traffic_type"],
        )
        groups[key].append(row)


def numeric_values(rows, field):
    values = []
    for row in rows:
        if row[field] != "":
            values.append(float(row[field]))
    return values


def mean_or_blank(values):
    return round(statistics.mean(values), 4) if values else ""


def std_or_blank(values):
    return round(statistics.stdev(values), 4) if len(values) >= 2 else ""


output_rows = []

for (config, scenario, traffic), rows in sorted(groups.items()):
    success = numeric_values(rows, "success_rate")
    latency = numeric_values(rows, "avg_latency_ms")
    throughput = numeric_values(rows, "avg_throughput_mbps")

    output_rows.append({
        "configuration": config,
        "scenario": scenario,
        "traffic_type": traffic,
        "runs": len(rows),
        "mean_success_rate": mean_or_blank(success),
        "std_success_rate": std_or_blank(success),
        "mean_latency_ms": mean_or_blank(latency),
        "std_latency_ms": std_or_blank(latency),
        "mean_throughput_mbps": mean_or_blank(throughput),
        "std_throughput_mbps": std_or_blank(throughput),
    })

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

fields = [
    "configuration",
    "scenario",
    "traffic_type",
    "runs",
    "mean_success_rate",
    "std_success_rate",
    "mean_latency_ms",
    "std_latency_ms",
    "mean_throughput_mbps",
    "std_throughput_mbps",
]

with OUTPUT.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(output_rows)

print(f"Aggregated {len(groups)} configuration/scenario/traffic groups")
print(f"Saved: {OUTPUT}")
