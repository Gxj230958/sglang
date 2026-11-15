import json, sys, time, urllib.request, random
BASE = "http://127.0.0.1:31743"; MODEL = "/scratch/models/GLM-5-1028-Provider"
out, epoch_file = sys.argv[1], sys.argv[2]
sizes = [int(x) for x in sys.argv[3].split(",")]
REPS = 6
def http(path, payload=None, timeout=1800):
    req = urllib.request.Request(BASE + path, data=None if payload is None else json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        b = r.read()
    try: return json.loads(b)
    except Exception: return b.decode(errors="replace")
vocab = "river stone lantern copper orchard violet harbor signal meadow anchor ember quartz willow thunder paper compass falcon marble cedar tunnel".split()
res = []
for n in sizes:
    for rep in range(REPS):
        r = random.Random(n * 10 + rep)
        text = " ".join(r.choice(vocab) + str(r.randrange(100)) for _ in range(int(n / 2.217))) + "\nReply with OK."
        http("/flush_cache"); time.sleep(2)
        open(epoch_file, "w").write("lp-%d-%d" % (n, rep)); time.sleep(5)
        t = time.time()
        try:
            d = http("/v1/chat/completions", {"model": MODEL, "messages": [{"role": "user", "content": text}], "max_tokens": 1, "temperature": 0, "chat_template_kwargs": {"enable_thinking": False}})
            row = {"target": n, "rep": rep, "prompt_tokens": d["usage"]["prompt_tokens"], "latency_s": round(time.time() - t, 4)}
        except Exception as e:
            row = {"target": n, "rep": rep, "error": repr(e)[:300]}
        time.sleep(6); res.append(row); print(row, flush=True)
open(epoch_file, "w").write("after-lp")
json.dump(res, open(out, "w"), indent=1)
