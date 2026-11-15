"""Salted greedy retrieval at several lengths, concurrently.
usage: stress.py <base-url> <out.jsonl> <per-length> <threads> <tag> [lengths...]"""
import json, random, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

base, out, per, threads, tag = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
lengths = [int(x) for x in sys.argv[6:]] or [600, 3000, 9000, 20000]
model = json.load(urllib.request.urlopen(base + "/models"))["data"][0]["id"]


def one(job):
    n, k = job
    rng = random.Random(f"{tag}-{n}-{k}")
    count = max(4, n // 13)
    codes = [rng.randrange(100000, 999999) for _ in range(count)]
    where = rng.randrange(count)
    doc = f"Session {tag}-{n}-{k}.\n" + "\n".join(
        f"Record {i}: the code is {c}." for i, c in enumerate(codes)
    )
    q = f"{doc}\n\nWhat is the code of Record {where}? Answer with the number only."
    body = {"model": model, "messages": [{"role": "user", "content": q}], "temperature": 0,
            "max_tokens": 64, "chat_template_kwargs": {"enable_thinking": False},
            "logprobs": True, "top_logprobs": 1}
    req = urllib.request.Request(base + "/chat/completions", json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    try:
        r = json.load(urllib.request.urlopen(req, timeout=1800))
    except Exception as e:  # recorded as an error row
        return {"n": n, "k": k, "error": repr(e)[:200]}
    c = r["choices"][0]
    toks = [t["token"] for t in (c.get("logprobs") or {}).get("content") or []]
    return {"n": n, "k": k, "prompt_tokens": r["usage"]["prompt_tokens"],
            "cached": (r["usage"].get("prompt_tokens_details") or {}).get("cached_tokens"),
            "finish": c["finish_reason"], "ntok": r["usage"]["completion_tokens"],
            "correct": str(codes[where]) in (c["message"]["content"] or ""),
            "tokens": toks[:24]}


jobs = [(n, k) for k in range(per) for n in lengths]
with ThreadPoolExecutor(threads) as ex, open(out, "w") as f:
    rows = []
    for row in ex.map(one, jobs):
        rows.append(row)
        f.write(json.dumps(row) + "\n")
        f.flush()
summary = {}
for row in rows:
    s = summary.setdefault(row["n"], {"total": 0, "stop": 0, "correct": 0, "error": 0})
    s["total"] += 1
    s["error"] += "error" in row
    s["stop"] += row.get("finish") == "stop"
    s["correct"] += bool(row.get("correct"))
print(json.dumps(summary))
for row in rows:
    if row.get("finish") != "stop" or not row.get("correct"):
        print("BAD", json.dumps(row)[:600])
