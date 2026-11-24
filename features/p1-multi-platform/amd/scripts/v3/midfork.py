"""Prefix reuse and mid-fork probes. usage: midfork.py <base-url> <out.json> <tag> [n]
DP_RANK=<r> pins every request to one attention-DP rank."""
import json, os, random, sys, urllib.request

base, out, tag = sys.argv[1], sys.argv[2], sys.argv[3]
n = int(sys.argv[4]) if len(sys.argv) > 4 else 6600
model = json.load(urllib.request.urlopen(base + "/models"))["data"][0]["id"]


def chat(messages):
    body = {"model": model, "messages": messages, "temperature": 0, "max_tokens": 512,
            "chat_template_kwargs": {"enable_thinking": False}}
    req = urllib.request.Request(base + "/chat/completions", json.dumps(body).encode(),
                                 {"Content-Type": "application/json", **({"X-Data-Parallel-Rank": os.environ["DP_RANK"]} if os.environ.get("DP_RANK") else {})})
    r = json.load(urllib.request.urlopen(req, timeout=1800))
    c = r["choices"][0]
    return {"text": c["message"]["content"], "finish": c["finish_reason"],
            "prompt_tokens": r["usage"]["prompt_tokens"],
            "cached": (r["usage"].get("prompt_tokens_details") or {}).get("cached_tokens")}


rng = random.Random(tag)
count = n // 13
codes = [rng.randrange(100000, 999999) for _ in range(count)]
alt = [rng.randrange(100000, 999999) for _ in range(count)]
half = count // 2


def doc(cs):
    return f"Session {tag}.\n" + "\n".join(f"Record {i}: the code is {c}." for i, c in enumerate(cs))


def ask(i):
    return f"\n\nWhat is the code of Record {i}? Answer with the number only."


forked = codes[:half] + alt[half:]
results = []


def run(name, messages, expected):
    r = chat(messages)
    r.update(case=name, expected=str(expected), correct=str(expected) in (r["text"] or ""))
    results.append(r)
    print(json.dumps(r), flush=True)
    return r


q1 = doc(codes) + ask(count // 3)
first = run("first", [{"role": "user", "content": q1}], codes[count // 3])
run("identical", [{"role": "user", "content": q1}], codes[count // 3])
run("fork_at_end", [{"role": "user", "content": doc(codes) + ask(count - 5)}], codes[count - 5])
run("mid_fork_late_record", [{"role": "user", "content": doc(forked) + ask(count - 7)}], forked[count - 7])
run("mid_fork_early_record", [{"role": "user", "content": doc(forked) + ask(half // 2)}], forked[half // 2])
run("follow_up_turn",
    [{"role": "user", "content": q1}, {"role": "assistant", "content": first["text"]},
     {"role": "user", "content": f"And Record {count // 5}? Answer with the number only."}],
    codes[count // 5])
json.dump(results, open(out, "w"), indent=1)
