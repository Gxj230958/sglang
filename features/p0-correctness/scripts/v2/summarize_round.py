"""Recompute the headline numbers of an experiment round from its committed raw files.

usage: summarize_round.py <round-dir> [--write]

Walks every directory of the round and summarizes the files it recognizes:
sgl-eval `metrics.json` + `output-rs*.jsonl[.gz]`, `serve.log[.gz]`, `probe*.json`,
`midfork*.json`, and `*.jsonl[.gz]` written by `stress.py`, `sglang.bench_serving` or the
multi-turn client `mt.py`. Prints JSON; with
`--write` it also stores the result as `<round-dir>/summary.json`.
"""
import collections
import datetime
import gzip
import json
import os
import re
import sys

ACCEPT = re.compile(r"accept len: ([0-9.]+)")
POOL = re.compile(r"Use sliding window memory pool\. (full_layer_tokens=\d+, swa_layer_tokens=\d+)")
PATTERNS = {
    "traceback": "Traceback (most recent call last)",
    "decode_batches_cuda_graph_true": "cuda graph: True",
    "hicache_prefetch_success": "HiCache prefetch success",
    "transport_retry_counter_exceeded": "transport retry counter exceeded",
    "rail_paused": "Rail paused",
    "process_failed_for_slice": "Process failed for slice",
    "transfer_failed": "transfer failed",
    "mismatch": "mismatch",
}


def read(path):
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", errors="replace") as f:
        return f.read()


def serve_log(text):
    accept = [float(x) for x in ACCEPT.findall(text)]
    out = {"decode_batch_lines_with_accept_len": len(accept)}
    if accept:
        out["mean_accept_len"] = round(sum(accept) / len(accept), 4)
    pools = sorted(set(POOL.findall(text)))
    if pools:
        out["window_pool"] = pools
    for key, needle in PATTERNS.items():
        out[key] = text.count(needle)
    return out


STAMPED = re.compile(r"^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})[^\]]*\].*accept len: ([0-9.]+)", re.M)


def accept_len_in_window(text, timestamp, latency_seconds):
    """Mean accept length over the decode lines logged while one sgl-eval run was in flight."""
    start = datetime.datetime.strptime(timestamp, "%Y%m%d-%H%M%S")
    end = start + datetime.timedelta(seconds=latency_seconds)
    values = [float(v) for stamp, v in STAMPED.findall(text)
              if start <= datetime.datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S") <= end]
    if not values:
        return None
    return {"decode_batch_lines": len(values), "mean_accept_len": round(sum(values) / len(values), 4)}


def gsm8k(directory, names):
    metrics = json.loads(read(os.path.join(directory, "metrics.json")))
    out = {
        "num_examples": metrics.get("num_examples"),
        "sgl_eval_version": metrics.get("sgl_eval_version"),
        "num_threads": metrics.get("num_threads"),
        "temperature": metrics["gen"]["temperature"],
        "top_p": metrics["gen"]["top_p"],
        "aggregate": metrics["aggregate"],
        "latency_seconds": metrics.get("latency_seconds"),
        "output_throughput_tps": metrics.get("output_throughput_tps"),
        "timestamp": metrics.get("timestamp"),
    }
    rows = []
    for name in names:
        if name.startswith("output-rs") and ".jsonl" in name:
            rows += [json.loads(x) for x in read(os.path.join(directory, name)).splitlines() if x.strip()]
    if rows:
        out["rows"] = len(rows)
        out["finish_reason"] = dict(collections.Counter(r.get("finish_reason") for r in rows))
        out["symbolic_correct"] = sum(str(r.get("symbolic_correct")) == "True" for r in rows)
        out["max_generated_tokens"] = max(int(r.get("num_generated_tokens") or 0) for r in rows)
    return out


def probe(rows):
    out = {"total": len(rows), "correct": sum(bool(r.get("correct")) for r in rows),
           "stop": sum(r.get("finish_reason") == "stop" for r in rows),
           "prompt_tokens": sorted({r.get("prompt_tokens") for r in rows})}
    bad = [{k: r.get(k) for k in ("target", "record", "prompt_tokens", "finish_reason", "correct")}
           for r in rows if not r.get("correct") or r.get("finish_reason") != "stop"]
    if bad:
        out["not_stop_and_correct"] = bad
    return out


def midfork(rows):
    return {"total": len(rows), "correct": sum(bool(r.get("correct")) for r in rows),
            "stop": sum(r.get("finish") == "stop" for r in rows),
            "cached_by_case": {r.get("case"): r.get("cached") for r in rows}}


def stress(rows):
    by_n = {}
    for r in rows:
        s = by_n.setdefault(str(r["n"]), {"total": 0, "stop": 0, "correct": 0, "error": 0,
                                           "stop_and_correct": 0})
        s["total"] += 1
        s["error"] += "error" in r
        s["stop"] += r.get("finish") == "stop"
        s["correct"] += bool(r.get("correct"))
        s["stop_and_correct"] += bool(r.get("correct")) and r.get("finish") == "stop"
    tokens = [r["prompt_tokens"] for r in rows if "prompt_tokens" in r]
    out = {"total": len(rows), "stop_and_correct": sum(s["stop_and_correct"] for s in by_n.values()),
           "by_target_length": by_n}
    if tokens:
        out["prompt_tokens_min_max"] = [min(tokens), max(tokens)]
    return out


BENCH_KEYS = ("completed", "output_throughput", "median_ttft_ms", "p99_ttft_ms", "mean_tpot_ms",
              "median_itl_ms", "median_e2e_latency_ms", "accept_length", "duration",
              "random_input_len", "random_output_len", "max_concurrency")


def bench(row):
    return {k: row.get(k) for k in BENCH_KEYS}


def median(values):
    values = sorted(values)
    mid = len(values) // 2
    return values[mid] if len(values) % 2 else (values[mid - 1] + values[mid]) / 2


def multiturn(rows):
    later = [r for r in rows if r["turn"] > 0]
    timed = [r["ttft"] for r in later if r["ttft"] is not None]
    last = max(r["turn"] for r in rows)
    final = [r for r in rows if r["turn"] == last]
    return {"requests": len(rows), "turns": last + 1,
            "requests_without_ttft": sum(r["ttft"] is None for r in rows),
            "median_ttft_ms_after_first_turn": 1000 * median(timed) if timed else None,
            "uncached_prompt_tokens_after_first_turn": sum(r["prompt"] - (r["cached"] or 0) for r in later),
            "last_turn_median_prompt_tokens": median([r["prompt"] for r in final]),
            "last_turn_median_cached_tokens": median([r["cached"] or 0 for r in final]),
            "completion_tokens": sum(r["completion"] for r in rows),
            "e2e_seconds_sum": sum(r["e2e"] for r in rows)}


def summarize(root):
    result = {}
    logs = {}
    for directory, _, names in sorted(os.walk(root)):
        rel = os.path.relpath(directory, root)
        entry = {}
        for name in sorted(names):
            path = os.path.join(directory, name)
            base = name[:-3] if name.endswith(".gz") else name
            try:
                if base == "metrics.json":
                    entry["gsm8k"] = gsm8k(directory, names)
                elif base.startswith("serve") and base.endswith(".log"):
                    logs[os.path.normpath(os.path.join(rel, name))] = read(path)
                    entry.setdefault("server_logs", {})[name] = serve_log(logs[os.path.normpath(os.path.join(rel, name))])
                elif base.startswith("probe") and base.endswith(".json"):
                    entry.setdefault("probes", {})[name] = probe(json.loads(read(path)))
                elif base.startswith("midfork") and base.endswith(".json"):
                    entry.setdefault("midfork", {})[name] = midfork(json.loads(read(path)))
                elif base.endswith(".jsonl") and not base.startswith("output-rs"):
                    rows = [json.loads(x) for x in read(path).splitlines() if x.strip()]
                    if rows and "n" in rows[0] and "k" in rows[0]:
                        entry.setdefault("stress", {})[name] = stress(rows)
                    elif rows and "output_throughput" in rows[-1]:
                        entry.setdefault("bench_serving", {})[name] = bench(rows[-1])
                    elif rows and "turn" in rows[0] and "ttft" in rows[0]:
                        entry.setdefault("multiturn", {})[name] = multiturn(rows)
            except (ValueError, KeyError) as e:
                entry.setdefault("unparsed", {})[name] = repr(e)[:120]
        if entry:
            result[rel] = entry
    for rel, entry in result.items():
        g = entry.get("gsm8k")
        if not g or not g.get("timestamp"):
            continue
        for log_path, text in sorted(logs.items()):
            log_dir = os.path.dirname(log_path)
            if log_dir and not (rel + "/").startswith(log_dir + "/"):
                continue
            window = accept_len_in_window(text, g["timestamp"], g["latency_seconds"])
            if window:
                g.setdefault("accept_len_during_run", {})[log_path] = window
    return result


if __name__ == "__main__":
    root = sys.argv[1]
    summary = summarize(root)
    text = json.dumps(summary, indent=1, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        with open(os.path.join(root, "summary.json"), "w") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
