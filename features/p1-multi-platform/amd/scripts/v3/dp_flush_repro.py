#!/opt/venv/bin/python
"""dp_flush_repro.py <port> <n> [--no-flush]: flush the cache, then one short request, n times
(the numcheck pattern), and report the first failure."""
import json, sys, time, urllib.request
port, n = int(sys.argv[1]), int(sys.argv[2]); flush = "--no-flush" not in sys.argv
B = f"http://127.0.0.1:{port}"
def post(path, body=None, timeout=300):
    r = urllib.request.Request(B + path, data=json.dumps(body).encode() if body is not None else b"",
                               headers={"Content-Type": "application/json"}, method="POST")
    return urllib.request.urlopen(r, timeout=timeout).read()
for i in range(n):
    try:
        if flush:
            post("/flush_cache")
        out = json.loads(post("/generate", {"text": f"Question {i}: what is {i} + {2*i}? Explain briefly.",
                                             "sampling_params": {"max_new_tokens": 48, "temperature": 0}}))
        print(i, "ok", repr(out["text"][:40]), flush=True)
    except Exception as e:
        print(i, "FAIL", type(e).__name__, str(e)[:120], flush=True)
        sys.exit(1)
print("all ok")
