#!/opt/venv/bin/python
"""prof_dep8_prefill.py <port> <out_dir> [dp] [n_tokens]: profile long-context prefill on a DEP8 server.
One n-token random-ID prompt per attention-DP rank (routed_dp_rank), 1 output token each; once the
prefills are under way (a few chunks in, so chunks attend a long prefix), record 6 forward steps
(GPU activities). Prints the unloaded per-rank prefill time."""
import json, random, sys, threading, time, urllib.request
port, out = int(sys.argv[1]), sys.argv[2]
dp = int(sys.argv[3]) if len(sys.argv) > 3 else 8
n = int(sys.argv[4]) if len(sys.argv) > 4 else 65536
B = f"http://127.0.0.1:{port}"
def post(path, body, timeout=1800):
    r = urllib.request.Request(B + path, json.dumps(body).encode(), {"Content-Type": "application/json"})
    return urllib.request.urlopen(r, timeout=timeout).read()
post("/flush_cache", {})
times = {}
def run(rank):
    rnd = random.Random(500 + rank); ids = [rnd.randint(1000, 100000) for _ in range(n)]
    t = time.time()
    post("/generate", {"input_ids": ids, "sampling_params": {"max_new_tokens": 1, "temperature": 0}, "routed_dp_rank": rank})
    times[rank] = time.time() - t
th = [threading.Thread(target=run, args=(r,)) for r in range(dp)]
for t in th: t.start()
time.sleep(max(4.0, 0.12 * n / 4096 * 4))   # about 4 chunks in at ~2.5K tok/s per rank
print(post("/start_profile", {"output_dir": out, "num_steps": 6, "activities": ["GPU"]})[:60], flush=True)
for t in th: t.join()
print("per-rank prefill seconds:", {r: round(v, 1) for r, v in sorted(times.items())},
      f"aggregate {dp * n / max(times.values()):.0f} tok/s", flush=True)
