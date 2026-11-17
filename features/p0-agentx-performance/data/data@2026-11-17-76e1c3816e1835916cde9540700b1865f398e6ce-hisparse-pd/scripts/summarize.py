"""Summarize AIPerf AgentX exports into the round's result table.

Usage: python3 summarize.py <agentx-dir> <run> [<run> ...]
Reads <agentx-dir>/<run>/profile_export_aiperf.json and profile_export.jsonl(.gz);
prints one Markdown row per run. Latencies are in ms, throughputs in tokens/s.
"""

import gzip
import json
import os
import sys


def load_records(run_dir):
    path = os.path.join(run_dir, "profile_export.jsonl")
    opener = open
    if not os.path.exists(path):
        path += ".gz"
        opener = gzip.open
    with opener(path, "rt") as f:
        for line in f:
            yield json.loads(line)


def stat(export, key, field="avg"):
    value = export.get(key)
    return value.get(field) if isinstance(value, dict) else value


def main():
    root, runs = sys.argv[1], sys.argv[2:]
    print(
        "| Run | Requests | Errors | Output tok/s | Total tok/s | Decode conc. | Prefill conc. "
        "| TTFT p50 / p90 (s) | ITL p50 / p90 (ms) | Per-user tok/s p50 |"
    )
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for run in runs:
        run_dir = os.path.join(root, run)
        with open(os.path.join(run_dir, "profile_export_aiperf.json")) as f:
            export = json.load(f)
        errors = sum(
            1
            for r in load_records(run_dir)
            if r.get("error") and r["metadata"].get("benchmark_phase") == "profiling"
        )
        print(
            f"| {run} | {stat(export, 'request_count'):.0f} | {errors} "
            f"| {stat(export, 'effective_decode_throughput'):.1f} "
            f"| {stat(export, 'effective_total_throughput'):.0f} "
            f"| {stat(export, 'effective_decode_concurrency'):.1f} "
            f"| {stat(export, 'effective_prefill_concurrency'):.1f} "
            f"| {stat(export, 'time_to_first_token', 'p50') / 1e3:.1f} / "
            f"{stat(export, 'time_to_first_token', 'p90') / 1e3:.1f} "
            f"| {stat(export, 'inter_token_latency', 'p50'):.1f} / "
            f"{stat(export, 'inter_token_latency', 'p90'):.1f} "
            f"| {stat(export, 'output_token_throughput_per_user', 'p50'):.1f} |"
        )


if __name__ == "__main__":
    main()
