"""Recompute the per-job performance and memory table of this round from its raw files.

usage: perf_summary.py <round-dir> [--write]   (writes <round-dir>/perf-summary.json)
"""
import collections
import glob
import gzip
import json
import os
import re
import statistics
import sys


def read(path):
    if os.path.exists(path + ".gz"):
        path += ".gz"
    if not os.path.exists(path):
        return None
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", errors="replace") as f:
        return f.read()


def bench(text):
    def grab(label):
        m = re.search(re.escape(label) + r"[^0-9]*([0-9.]+)", text)
        return float(m.group(1)) if m else None
    return {"successful_requests": grab("Successful requests:"),
            "output_tok_per_s": grab("Output token throughput (tok/s):"),
            "mean_ttft_ms": grab("Mean TTFT (ms):"), "mean_itl_ms": grab("Mean ITL (ms):")}


def job(directory):
    out = {}
    status = read(os.path.join(directory, "job.status"))
    if status:
        out["status"] = status.split("\n")[:-1]
    for kind in ("serve", "decode"):
        text = read(os.path.join(directory, f"perf-{kind}.log"))
        if text:
            out[f"bench_{kind}"] = bench(text)
    text = read(os.path.join(directory, "longprefill.json"))
    if text:
        by = collections.defaultdict(list)
        for row in json.loads(text):
            by[row["target"]].append(row.get("latency_s"))
        out["long_prefill_s"] = {str(n): {"reps": len(v), "median": round(statistics.median(v), 4), "min": min(v)}
                                 for n, v in by.items() if all(x is not None for x in v)}
    peaks = collections.defaultdict(lambda: [0, 0, 0])
    for path in sorted(glob.glob(os.path.join(directory, "mem", "mem-*.log*"))):
        for line in read(path[:-3] if path.endswith(".gz") else path).splitlines():
            m = re.search(r"epoch=(\S+) dev=0 alloc_mib=(\d+) max_alloc_mib=(\d+) max_reserved_mib=(\d+)", line)
            if m:
                epoch = re.sub(r"-\d+$", "", m.group(1)) if m.group(1).startswith("lp-") else m.group(1)
                peaks[epoch] = [max(a, int(b)) for a, b in zip(peaks[epoch], m.groups()[1:])]
    if peaks:
        out["gpu0_rank_mib_by_epoch"] = {k: dict(zip(("alloc", "max_alloc", "max_reserved"), v))
                                         for k, v in sorted(peaks.items()) if v[1] >= 1000}
    text = read(os.path.join(directory, "serve.log"))
    if text:
        checks = re.findall(r"GLMLOOP_VAL pid=(\d+) topk_checks=(\d+) topk_mismatches=(\d+)", text)
        if checks:
            last = {pid: (int(c), int(m)) for pid, c, m in checks}
            out["topk_compare"] = {"ranks": len(last), "checks_per_rank": sorted({c for c, _ in last.values()}),
                                   "mismatches": sum(m for _, m in last.values())}
    return out


if __name__ == "__main__":
    root = sys.argv[1]
    result = {name: job(os.path.join(root, "logs", name)) for name in sorted(os.listdir(os.path.join(root, "logs")))
              if os.path.isdir(os.path.join(root, "logs", name))}
    result = {k: v for k, v in result.items() if v}
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        with open(os.path.join(root, "perf-summary.json"), "w") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
