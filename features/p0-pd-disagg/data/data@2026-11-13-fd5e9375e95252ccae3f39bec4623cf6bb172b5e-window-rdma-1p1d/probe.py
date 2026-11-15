"""Greedy retrieval probes: usage: probe.py <base-url> <out.json> [lengths...]"""
import json
import random
import sys
import urllib.request

base, out = sys.argv[1], sys.argv[2]
lengths = [int(x) for x in sys.argv[3:]] or [300, 3000, 9000, 24000, 60000]
model = json.load(urllib.request.urlopen(base + "/models"))["data"][0]["id"]


def chat(messages, max_tokens=96):
    body = {
        "model": model,
        "messages": messages,
        "temperature": 0,
        "max_tokens": max_tokens,
        "chat_template_kwargs": {"enable_thinking": False},
        "logprobs": True,
        "top_logprobs": 1,
    }
    req = urllib.request.Request(
        base + "/chat/completions",
        json.dumps(body).encode(),
        {"Content-Type": "application/json"},
    )
    r = json.load(urllib.request.urlopen(req, timeout=1800))
    c = r["choices"][0]
    toks = [t["token"] for t in (c.get("logprobs") or {}).get("content") or []]
    return {
        "tokens": toks[:100],
        "completion_tokens": r["usage"]["completion_tokens"],
        "text": c["message"]["content"],
        "finish_reason": c["finish_reason"],
        "prompt_tokens": r["usage"]["prompt_tokens"],
        "cached_tokens": (r["usage"].get("prompt_tokens_details") or {}).get(
            "cached_tokens"
        ),
    }


results = []
for n in lengths:
    rng = random.Random(n)
    count = max(4, n // 13)
    codes = [rng.randrange(100000, 999999) for _ in range(count)]
    doc = "\n".join(f"Record {i}: the code is {c}." for i, c in enumerate(codes))
    for where in (count // 7, count // 2, count - 3):
        q = f"{doc}\n\nWhat is the code of Record {where}? Answer with the number only."
        r = chat([{"role": "user", "content": q}])
        r.update(target=n, record=where, expected=str(codes[where]))
        r["correct"] = r["expected"] in (r["text"] or "")
        results.append(r)
        print(json.dumps(r), flush=True)
json.dump(results, open(out, "w"), indent=1)
