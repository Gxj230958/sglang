#!/opt/venv/bin/python
"""warm_long_ctx.py <port> <dp_size> [n_tokens]: pre-load the long-context kernel variants on every
attention-DP rank before serving traffic. Triton loads each specialization at first use, which needs
free device memory outside torch's allocator; once serving has grown the allocator, a first use can fail
(the DSA indexer's KV-split fp8 MQA logits kernel aborted a rank this way). Per rank: one n-token prompt
(prefill chunks attend > 16K keys: the BLOCK_M=2 KV-split variant), then the same prompt plus a short turn
(a few rows over the cached prefix: the BLOCK_M=1 KV-split variant), each with 1 output token."""
import json, random, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
port, dp = int(sys.argv[1]), int(sys.argv[2]); n = int(sys.argv[3]) if len(sys.argv) > 3 else 40000
def gen(rank, ids):
    # /generate takes the DP rank in the body (the X-Data-Parallel-Rank header is read by the OpenAI routes).
    body = {"input_ids": ids, "sampling_params": {"max_new_tokens": 1, "temperature": 0}, "routed_dp_rank": rank}
    r = urllib.request.Request(f"http://127.0.0.1:{port}/generate", json.dumps(body).encode(),
                               {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r, timeout=1800))["meta_info"].get("cached_tokens")
def warm(rank):
    rnd = random.Random(1000 + rank); ids = [rnd.randint(1000, 100000) for _ in range(n)]
    t = time.time(); gen(rank, ids); t1 = time.time() - t
    cached = gen(rank, ids + [rnd.randint(1000, 100000) for _ in range(96)])
    return rank, round(t1, 1), cached
with ThreadPoolExecutor(dp) as ex:
    for rank, t1, cached in ex.map(warm, range(dp)):
        print(f"rank {rank}: {n}-token prefill {t1}s, follow-up cached {cached}", flush=True)
