
import csv
from pathlib import Path
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "results" / "processed" / "summary.csv"
FIGURES = ROOT / "results" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

with CSV_PATH.open(newline="") as f:
    rows = list(csv.DictReader(f))

# Only compare baseline legitimate traffic in A and C.
traffic_types = ["http", "dns", "ssh"]
scenarios = ["A", "C"]

def collect(metric):
    grouped = defaultdict(list)

    for row in rows:
        if row["configuration"] != "baseline":
            continue
        if row["scenario"] not in scenarios:
            continue
        if row["traffic_type"] not in traffic_types:
            continue

        value = row.get(metric, "")
        if value:
            key = (row["scenario"], row["traffic_type"])
            grouped[key].append(float(value))

    return {
        key: sum(values) / len(values)
        for key, values in grouped.items()
    }

def plot_metric(metric, title, ylabel, filename, scale=1):
    data = collect(metric)

    fig, ax = plt.subplots(figsize=(9, 5))
    x = list(range(len(traffic_types)))
    width = 0.35

    for index, scenario in enumerate(scenarios):
        values = [
            data.get((scenario, traffic), float("nan")) * scale
            for traffic in traffic_types
        ]
        positions = [
            i + (index - 0.5) * width for i in x
        ]

        ax.bar(positions, values, width, label=f"Scenario {scenario}")

    ax.set_xticks(x)
    ax.set_xticklabels([t.upper() for t in traffic_types])
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    ax.grid(axis="y", alpha=0.2)

    fig.tight_layout()
    output = FIGURES / filename
    fig.savefig(output, dpi=200)
    plt.close(fig)
    print(f"Saved: {output}")

plot_metric(
    "success_rate",
    "Legitimate Traffic Success Rate - Baseline",
    "Success Rate (%)",
    "success_rate.png",
    scale=100,
)

plot_metric(
    "avg_latency_ms",
    "Average Latency - Baseline",
    "Latency (ms)",
    "latency.png",
)
