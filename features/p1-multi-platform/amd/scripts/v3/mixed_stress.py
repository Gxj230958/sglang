#!/opt/venv/bin/python
"""mixed_stress.py <port> <seconds> [dp]: per DP rank, a loop of random-length prefills (2K-60K random IDs,
1-64 output tokens) plus a few long-output short prompts, so MoE token counts and prefill/decode mixes vary
widely across ranks. Reports the first failure."""
import json, random, sys, threading, time, urllib.request
port, dur = int(sys.argv[1]), float(sys.argv[2]); dp = int(sys.argv[3]) if len(sys.argv) > 3 else 8
stop, fails, done = time.time() + dur, [], [0]
def gen(rank, ids, out):
    body = {"input_ids": ids, "sampling_params": {"max_new_tokens": out, "temperature": 0, "ignore_eos": True}, "routed_dp_rank": rank}
    r = urllib.request.Request(f"http://127.0.0.1:{port}/generate", json.dumps(body).encode(), {"Content-Type": "application/json"})
    urllib.request.urlopen(r, timeout=1800).read()
def worker(rank, seed, long_prompts):
    rnd = random.Random(seed)
    while time.time() < stop and not fails:
        n = rnd.randint(2000, 60000) if long_prompts else rnd.randint(50, 600)
        out = rnd.randint(1, 64) if long_prompts else rnd.randint(200, 800)
        try:
            gen(rank, [rnd.randint(1000, 100000) for _ in range(n)], out); done[0] += 1
        except Exception as e:
            fails.append(f"rank {rank} n={n}: {type(e).__name__} {str(e)[:150]}")
th = [threading.Thread(target=worker, args=(r, 10 + r, True)) for r in range(dp)]
th += [threading.Thread(target=worker, args=(r, 100 + r, False)) for r in range(dp) for _ in range(3)]
for t in th: t.start()
for t in th: t.join()
print(f"completed {done[0]} requests; failures: {fails[:3] or 'none'}")
