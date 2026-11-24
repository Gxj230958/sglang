#!/opt/venv/bin/python
"""long_prefill_probe.py <port> <n_tokens> [rank] [max_new_tokens]: one long random-ID prompt on one DP rank, 1 output
token; prints elapsed or the error. Used to find a context length at which a prefill kernel fails."""
import json, random, sys, time, urllib.request
port, n = int(sys.argv[1]), int(sys.argv[2]); rank = int(sys.argv[3]) if len(sys.argv) > 3 else 0
rnd = random.Random(7); ids = [rnd.randint(1000, 100000) for _ in range(n)]
out_n = int(sys.argv[4]) if len(sys.argv) > 4 else 1
body = {"input_ids": ids, "sampling_params": {"max_new_tokens": out_n, "temperature": 0, "ignore_eos": True}, "routed_dp_rank": rank}
t = time.time()
try:
    r = urllib.request.Request(f"http://127.0.0.1:{port}/generate", json.dumps(body).encode(), {"Content-Type": "application/json"})
    out = json.load(urllib.request.urlopen(r, timeout=3600))
    print(f"{n} tokens ok in {time.time()-t:.1f}s finish={out['meta_info'].get('finish_reason')}")
except Exception as e:
    print(f"{n} tokens FAILED after {time.time()-t:.1f}s: {type(e).__name__} {str(e)[:200]}")
