import json, glob, re, sys, collections, statistics, os
gate = sys.argv[1]
run = sorted(glob.glob(f"{gate}/eval/sgl_eval_gsm8k_*"))[-1]
rows = [json.loads(l) for l in open(f"{run}/output-rs0.jsonl")]
fr = collections.Counter(r.get("finish_reason") for r in rows)
n = len(rows)
correct = sum(1 for r in rows if r.get("symbolic_correct"))
out = {"run_dir": run, "n": n, "finish_reason": dict(fr),
       "stop_rate": fr.get("stop", 0) / n if n else None,
       "acc_from_samples": correct / n if n else None,
       "mean_generated_tokens": statistics.mean(r.get("num_generated_tokens") or 0 for r in rows) if n else None}
m = f"{run}/metrics.json"
if os.path.exists(m):
    out["metrics_json"] = json.load(open(m))
log = open(f"{gate}/server.log", errors="replace").read()
acc = [float(x) for x in re.findall(r"accept len: ([0-9.]+)", log)]
out["accept_len_mean"] = statistics.mean(acc) if acc else None
out["accept_len_samples"] = len(acc)
out["cuda_graph_true_lines"] = len(re.findall(r"cuda graph: True", log))
out["cuda_graph_false_lines"] = len(re.findall(r"cuda graph: False", log))
out["tracebacks"] = log.count("Traceback (most recent call last)")
sa = re.search(r"server_args=(\{.*?\})\n", log)
for k in ("moe_runner_backend", "moe_a2a_backend", "attention_backend", "dsa_prefill_backend", "dsa_decode_backend", "speculative_num_steps", "speculative_num_draft_tokens", "speculative_eagle_topk", "max_running_requests", "page_size", "mem_fraction_static", "disable_cuda_graph"):
    mm = re.search(rf"'{k}': ([^,]+)", log)
    out[k] = mm.group(1) if mm else None
rust = [l[-200:] for l in log.splitlines() if re.search(r"(?i)rust|radix tree core", l)][:4]
out["rust_lines"] = rust
print(json.dumps(out, indent=1, default=str))
