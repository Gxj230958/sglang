import json, sys, time, urllib.request, concurrent.futures as cf
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 30000
def gen(text, n):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}/generate",
        data=json.dumps({"text": text, "sampling_params": {"max_new_tokens": n, "temperature": 0, "ignore_eos": True}}).encode(),
        headers={"Content-Type": "application/json"})
    t = time.time()
    with urllib.request.urlopen(req, timeout=1800) as r:
        d = json.load(r)
    return d["meta_info"]["completion_tokens"], d["meta_info"]["prompt_tokens"], time.time() - t
print("short", gen("Hello", 64))
print("long", gen("word " * 6000, 32))
with cf.ThreadPoolExecutor(16) as ex:
    futs = [ex.submit(gen, f"req {i} " + "abc " * (50 * i), 48) for i in range(16)]
    print("batch", [f.result()[:2] for f in futs])
