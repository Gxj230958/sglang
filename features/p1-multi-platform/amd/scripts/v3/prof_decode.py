#!/opt/venv/bin/python
"""prof_decode.py <port> <out_dir> <streams> <input_len> [rank0_only]: steady-decode profile. <streams>
random-ID prompts of <input_len> tokens decode 600 tokens each (EOS ignored); once every stream has its
first token, record 12 forward steps (GPU activities). With rank0_only, all streams go to DP rank 0."""
import json, random, sys, threading, time, urllib.request
port, out, streams, n = int(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
rank0 = len(sys.argv) > 5
B = f"http://127.0.0.1:{port}"
def post(path, body, timeout=1800):
    r = urllib.request.Request(B + path, json.dumps(body).encode(), {"Content-Type": "application/json"})
    return urllib.request.urlopen(r, timeout=timeout).read()
post("/flush_cache", {})
first = {}
def run(i):
    rnd = random.Random(900 + i)
    body = {"input_ids": [rnd.randint(1000, 100000) for _ in range(n)], "stream": True,
            "sampling_params": {"max_new_tokens": 600, "temperature": 0, "ignore_eos": True}}
    if rank0: body["routed_dp_rank"] = 0
    r = urllib.request.Request(B + "/generate", json.dumps(body).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=1800) as resp:
        for line in resp:
            if line.startswith(b"data:") and i not in first:
                first[i] = time.time()
th = [threading.Thread(target=run, args=(i,)) for i in range(streams)]
for t in th: t.start()
while len(first) < streams: time.sleep(0.05)
time.sleep(1.0)
print(post("/start_profile", {"output_dir": out, "num_steps": 12, "activities": ["GPU"]})[:40], flush=True)
for t in th: t.join()
print("done", flush=True)
