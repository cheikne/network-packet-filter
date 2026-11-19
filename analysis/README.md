
# Role 4 — Experiment Results Analysis

## Overview

This module processes traffic generation logs from the network packet filtering experiments.

It supports:
- Parsing experiment metadata and JSON traffic logs
- Calculating traffic success rates
- Calculating average latency and throughput
- Aggregating results across experiment repetitions
- Generating comparison charts

## Directory Structure

- `analysis/analyze_results.py` — Parses raw experiment logs
- `analysis/aggregate_results.py` — Aggregates results across runs
- `analysis/generate_plots.py` — Generates baseline comparison charts
- `results/raw/` — Raw experiment data
- `results/processed/` — CSV summaries
- `results/figures/` — Generated charts

## Requirements

Python 3 and matplotlib.

Install dependencies:

```bash
python3 -m pip install matplotlib
```

## Usage

Run the scripts from the repository root:

```bash
python3 analysis/analyze_results.py
python3 analysis/aggregate_results.py
python3 analysis/generate_plots.py
```

## Output

### summary.csv

Contains per-run metrics:
- Configuration
- Scenario
- Repetition
- Traffic type
- Total events
- Success rate
- Average latency
- Average throughput

### aggregated.csv

Contains aggregated metrics:
- Number of runs
- Mean success rate
- Standard deviation of success rate
- Mean latency and standard deviation
- Mean throughput and standard deviation

### Figures

- `success_rate.png` — Baseline legitimate traffic success rate
- `latency.png` — Baseline average latency

## Metric Interpretation

Success rate measures successful traffic operations, not firewall detection accuracy.

For Nmap-based scans, exit code 0 indicates successful command execution, not successful firewall bypass.

SSH traffic currently tests connection/banner availability rather than authenticated sessions.

Firewall blocking rates, false positives, and false negatives require additional packet-level or firewall decision data.

## Testing

The initial smoke-test dataset contains:
- Scenario A: Legitimate traffic
- Scenario B: Six suspicious traffic scenarios
- Scenario C: Mixed traffic

All eight scenarios completed successfully on the baseline configuration using 10-second runs with one repetition.

Full policy comparisons and 60-second experiments with 10 repetitions remain pending.

## Reproducibility

Run the analysis scripts again after collecting new experiment data. Generated CSV files and figures are derived from the JSON logs.

Standard deviation is left blank when fewer than two valid observations are available.
