"""HiCache restore probe.
usage: hicache.py <base-url> <state.json> write|ref|read|fill [count]\nwrite: first uncached request; ref: save a cached-prefix run; read: compare to ref."""
import json, random, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

base, state, phase = sys.argv[1], sys.argv[2], sys.argv[3]
model = json.load(urllib.request.urlopen(base + "/models"))["data"][0]["id"]


def doc(tag, n=6600):
    rng = random.Random(tag)
    codes = [rng.randrange(100000, 999999) for _ in range(n // 13)]
    return f"Session {tag}.\n" + "\n".join(
        f"Record {i}: the code is {c}." for i, c in enumerate(codes)
    ), codes


def chat(content, max_tokens):
    body = {"model": model, "messages": [{"role": "user", "content": content}],
            "temperature": 0, "max_tokens": max_tokens,
            "chat_template_kwargs": {"enable_thinking": False},
            "logprobs": True, "top_logprobs": 1}
    req = urllib.request.Request(base + "/chat/completions", json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=1800))
    c = r["choices"][0]
    lp = (c.get("logprobs") or {}).get("content") or []
    return {"finish": c["finish_reason"], "text": c["message"]["content"],
            "prompt_tokens": r["usage"]["prompt_tokens"],
            "cached": (r["usage"].get("prompt_tokens_details") or {}).get("cached_tokens"),
            "tokens": [t["token"] for t in lp], "logprobs": [t["logprob"] for t in lp]}


if phase == "fill":
    count = int(sys.argv[4])
    fill_tag = sys.argv[5] if len(sys.argv) > 5 else "fill"

    def one(k):
        return chat(doc(f"{fill_tag}-{k}")[0] + "\n\nReply with OK.", 2)["finish"]

    with ThreadPoolExecutor(8) as ex:
        print("fill", len(list(ex.map(one, range(count)))))
    sys.exit(0)

d, codes = doc("hicache-anchor")
half = len(codes) // 2
question = (
    d + f"\n\nList the codes of Records {half}, {half + 1}, {half + 2}, 3 and "
    f"{len(codes) - 2}, separated by commas."
)
expected = [codes[half], codes[half + 1], codes[half + 2], codes[3], codes[-2]]
r = chat(question, 64)
r["correct"] = all(str(c) in (r["text"] or "") for c in expected)
if phase in ("write", "ref"):
    if phase == "ref":
        json.dump(r, open(state, "w"))
    print("write", r["prompt_tokens"], r["cached"], r["finish"], r["correct"], r["tokens"])
else:
    ref = json.load(open(state))
    same_tokens = ref["tokens"] == r["tokens"]
    diff = max((abs(a - b) for a, b in zip(ref["logprobs"], r["logprobs"])), default=None)
    print("read", r["prompt_tokens"], r["cached"], r["finish"], r["correct"],
          "same_tokens", same_tokens, "max_abs_logprob_diff", diff,
          "bitwise", ref["logprobs"] == r["logprobs"])
