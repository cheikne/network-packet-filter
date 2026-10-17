#!/usr/bin/env python3
"""Run experiments: apply a policy, run a scenario's traffic, save the results.

Each run creates results/raw/<run_id>/ with metadata.json and the client logs.

Minimal first version. Coming later: captures on fw (M1/M2), firewall
counters, CPU samples, server logs, and a loop over all configurations.

Usage (from the repository root, with the lab running):
  python3 automation/run_experiment.py --config baseline --scenario A --reps 1
"""
import argparse
import json
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PLAN_FILE = ROOT / "automation" / "config" / "experiments.yaml"
TARGET = "10.0.2.10"


def git_commit():
    """Short commit hash of the code used for the run (for reproducibility)."""
    out = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                         capture_output=True, text=True)
    return out.stdout.strip() or "unknown"


def run_one(plan, config, scenario, rep, duration):
    """Do one run and return its result folder."""
    start = datetime.now().astimezone()
    run_id = f"{start:%Y%m%d-%H%M%S}_{config}_{scenario}_r{rep:02d}"
    run_dir = ROOT / "results" / "raw" / run_id
    run_dir.mkdir(parents=True)

    policy = plan["configurations"][config]
    subprocess.run([str(ROOT / "automation" / "apply_policy.sh"), policy],
                   check=True, stdout=subprocess.DEVNULL)

    # Start all traffic commands at the same time, then wait for all of them
    running = []
    for i, step in enumerate(plan["scenarios"][scenario]):
        output = f"/project/results/raw/{run_id}/clients/{step['node']}"
        cmd = step["cmd"].format(target=TARGET, duration=duration, output=output)
        proc = subprocess.Popen(["docker", "exec", step["node"], "sh", "-c",
                                 f"mkdir -p {output} && {cmd}"])
        running.append((step, cmd, proc))
    commands = [{"node": step["node"], "cmd": cmd, "exit_code": proc.wait()}
                for step, cmd, proc in running]
    end = datetime.now().astimezone()

    metadata = {
        "run_id": run_id,
        "configuration": config,
        "policy": policy,
        "scenario": scenario,
        "repetition": rep,
        "duration_s": duration,
        "target": TARGET,
        "start_time": start.isoformat(timespec="seconds"),
        "end_time": end.isoformat(timespec="seconds"),
        "commands": commands,
        "git_commit": git_commit(),
        "host": f"{platform.system()} {platform.machine()}",
    }
    (run_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")

    for c in commands:
        if c["exit_code"] != 0:
            print(f"  warning: {c['node']} command exited with {c['exit_code']}")
    return run_dir


def main():
    plan = yaml.safe_load(PLAN_FILE.read_text())

    parser = argparse.ArgumentParser(description="Run packet filtering experiments.")
    parser.add_argument("--config", required=True, choices=plan["configurations"])
    parser.add_argument("--scenario", required=True, choices=plan["scenarios"])
    parser.add_argument("--reps", type=int, default=plan["repetitions"],
                        help="number of repetitions (default from experiments.yaml)")
    parser.add_argument("--duration", type=int, default=plan["duration"],
                        help="seconds per run (default from experiments.yaml)")
    args = parser.parse_args()

    if not plan["scenarios"][args.scenario]:
        sys.exit(f"Scenario {args.scenario} has no commands yet in {PLAN_FILE.name}.")

    for rep in range(1, args.reps + 1):
        print(f"Run {rep}/{args.reps}: {args.config} / {args.scenario} ({args.duration} s)")
        run_dir = run_one(plan, args.config, args.scenario, rep, args.duration)
        print(f"  saved {run_dir.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
