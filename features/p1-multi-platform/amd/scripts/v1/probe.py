import json, sys, urllib.request
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 30000
def gen(text, n=8):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}/generate",
        data=json.dumps({"text": text, "sampling_params": {"max_new_tokens": n, "temperature": 0},
                         "return_logprob": True, "top_logprobs_num": 5, "logprob_start_len": -1}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)
for p in ["The capital of France is", "1, 2, 3, 4, 5, 6,", "def fibonacci(n):\n    "]:
    d = gen(p)
    top = d["meta_info"]["output_top_logprobs"][0]
    print(repr(p), "->", repr(d["text"]))
    print("   first-token top5:", [(round(lp, 2), t) for lp, _, t in top])
