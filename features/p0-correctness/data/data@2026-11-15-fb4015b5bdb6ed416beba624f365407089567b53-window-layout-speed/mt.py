"""Multi-turn streaming chat: usage: mt.py <base-url> <out.jsonl> <convs> <turns> <threads> <tag>"""
import json, random, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

base, out, convs, turns, threads, tag = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
model = json.load(urllib.request.urlopen(base + "/models"))["data"][0]["id"]


def conv(k):
    rng = random.Random(f"{tag}-{k}")
    messages, rows = [], []
    for t in range(turns):
        codes = [rng.randrange(100000, 999999) for _ in range(150)]
        doc = "\n".join(f"Record {tag}-{k}-{t}-{i}: the code is {c}." for i, c in enumerate(codes))
        messages.append({"role": "user", "content": f"{doc}\n\nWrite a short paragraph describing the records above."})
        body = {"model": model, "messages": messages, "temperature": 0, "max_tokens": 200, "stream": True,
                "stream_options": {"include_usage": True}, "chat_template_kwargs": {"enable_thinking": False}}
        req = urllib.request.Request(base + "/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json"})
        t0 = time.perf_counter(); ttft = None; text = ""; usage = None
        with urllib.request.urlopen(req, timeout=1800) as r:
            for line in r:
                line = line.decode().strip()
                if not line.startswith("data: ") or line == "data: [DONE]":
                    continue
                d = json.loads(line[6:])
                if d.get("usage"):
                    usage = d["usage"]
                for c in d.get("choices") or []:
                    delta = c.get("delta") or {}
                    if ttft is None and (delta.get("content") or delta.get("reasoning_content")):
                        ttft = time.perf_counter() - t0
                    text += delta.get("content") or ""
        e2e = time.perf_counter() - t0
        messages.append({"role": "assistant", "content": text})
        rows.append({"k": k, "turn": t, "ttft": ttft, "e2e": e2e, "prompt": usage["prompt_tokens"],
                     "completion": usage["completion_tokens"],
                     "cached": (usage.get("prompt_tokens_details") or {}).get("cached_tokens")})
    return rows


with ThreadPoolExecutor(threads) as ex, open(out, "w") as f:
    for rows in ex.map(conv, range(convs)):
        for row in rows:
            f.write(json.dumps(row) + "\n")
