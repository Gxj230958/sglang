"""Recompute the focused-sweep table from the committed per-repeat results.

usage: summarize_sweep.py <round-dir> [--write]

Reads focused/candidates/<name>/levels.tar.gz (level-<N>/repeat-<R>/result.json) and
replica-0.log.gz. Per candidate and level it reports the median of the two repeats and
applies the SLO of contract.md. With --write it stores <round-dir>/summary.json.
"""
import gzip
import io
import json
import os
import re
import statistics
import sys
import tarfile

KEYS = ["total_tps_per_gpu", "output_tps", "ttft_p90", "interactivity_p90", "cache_hit"]
POOL = re.compile(r"Use sliding window memory pool\. (full_layer_tokens=\d+, swa_layer_tokens=\d+)")
TOTAL = re.compile(r"max_total_num_tokens=(\d+)")


def passes(m):
    return m["ttft_p90"] <= 3.0 and m["interactivity_p90"] >= 30.0 and m["errors"] == 0 and m["empty_responses"] == 0 and m["ok"] == m["sent"]


def candidate(directory):
    points = {}
    with tarfile.open(os.path.join(directory, "levels.tar.gz")) as tar:
        for member in tar.getmembers():
            match = re.fullmatch(r"level-(\d+)/repeat-(\d+)/result\.json", member.name)
            if match:
                result = json.load(io.TextIOWrapper(tar.extractfile(member)))
                points.setdefault(int(match.group(1)), {})[int(match.group(2))] = result["raw_metrics"]
    log = gzip.open(os.path.join(directory, "replica-0.log.gz"), "rt", errors="replace").read()
    out = {
        "max_total_num_tokens": sorted(set(int(x) for x in TOTAL.findall(log))),
        "window_pool": sorted(set(POOL.findall(log))),
        "traceback": log.count("Traceback (most recent call last)"),
        "cuda_out_of_memory": log.count("CUDA out of memory") + log.count("OutOfMemoryError"),
        "levels": {},
    }
    sanity = json.load(open(os.path.join(directory, "sanity-requests.json")))
    out["sanity_finish_reasons"] = [r["response"]["choices"][0]["finish_reason"] for r in sanity]
    for level in sorted(points):
        repeats = [points[level][r] for r in sorted(points[level])]
        out["levels"][level] = {
            "repeats": len(repeats),
            "median": {k: round(statistics.median(m[k] for m in repeats), 3) for k in KEYS},
            "repeat_total_tps_per_gpu": [round(m["total_tps_per_gpu"], 3) for m in repeats],
            "requests_ok": sum(m["ok"] for m in repeats),
            "requests_sent": sum(m["sent"] for m in repeats),
            "repeat_pass": [passes(m) for m in repeats],
        }
    passing = [(v["median"]["total_tps_per_gpu"], lvl) for lvl, v in out["levels"].items() if all(v["repeat_pass"])]
    if passing:
        score, level = max(passing)
        out["best_passing"] = {"level": level, "total_tps_per_gpu": score}
    return out


def main():
    root = sys.argv[1]
    base = os.path.join(root, "focused", "candidates")
    summary = {name: candidate(os.path.join(base, name)) for name in sorted(os.listdir(base))}
    text = json.dumps(summary, indent=1, sort_keys=True)
    print(text)
    if "--write" in sys.argv:
        with open(os.path.join(root, "summary.json"), "w") as f:
            f.write(text + "\n")


main()
