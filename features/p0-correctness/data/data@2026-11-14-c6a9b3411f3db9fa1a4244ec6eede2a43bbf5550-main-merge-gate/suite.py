import base64, io, json, sys, time, urllib.request

BASE = "http://127.0.0.1:31745"
MODEL = "/scratch/models/GLM-5-1028-Provider"
OUT = sys.argv[1]
PARTS = sys.argv[2].split(",") if len(sys.argv) > 2 else ["smoke", "det", "cache"]
res = {}


def http(path, payload=None, timeout=900):
    req = urllib.request.Request(
        BASE + path,
        data=None if payload is None else json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST" if payload is not None or path == "/flush_cache" else "GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
    try:
        return json.loads(body)
    except Exception:
        return body.decode(errors="replace")


def flush():
    time.sleep(1)
    http("/flush_cache")
    time.sleep(2)


def chat(messages, max_tokens=96, thinking=False, logprobs=True):
    p = {
        "model": MODEL, "messages": messages, "max_tokens": max_tokens,
        "temperature": 0, "top_p": 1, "logprobs": logprobs,
        "chat_template_kwargs": {"enable_thinking": thinking},
    }
    t = time.time()
    d = http("/v1/chat/completions", p)
    c = d["choices"][0]
    lp = (c.get("logprobs") or {}).get("content") or []
    u = d.get("usage", {})
    return {
        "finish_reason": c.get("finish_reason"),
        "content": c["message"].get("content"),
        "reasoning": c["message"].get("reasoning_content"),
        "tokens": [x["token"] for x in lp],
        "logprobs": [x["logprob"] for x in lp],
        "prompt_tokens": u.get("prompt_tokens"),
        "completion_tokens": u.get("completion_tokens"),
        "cached_tokens": (u.get("prompt_tokens_details") or {}).get("cached_tokens"),
        "latency_s": round(time.time() - t, 3),
    }


def has(r, *needles):
    text = (r["content"] or "")
    return all(n in text for n in needles)


def user(text):
    return [{"role": "user", "content": text}]


def cmp(a, b):
    n = min(len(a["tokens"]), len(b["tokens"]))
    first = next((i for i in range(n) if a["tokens"][i] != b["tokens"][i]), None)
    m = n if first is None else first
    d = max((abs(a["logprobs"][i] - b["logprobs"][i]) for i in range(m)), default=0.0)
    return {
        "same_tokens": first is None and len(a["tokens"]) == len(b["tokens"]),
        "first_diff": first, "n": n, "max_abs_logprob_diff_before_diff": d,
        "same_text": a["content"] == b["content"],
    }


def words(seed, n):
    import random
    r = random.Random(seed)
    vocab = ("river stone lantern copper orchard violet harbor signal meadow anchor "
             "ember quartz willow thunder paper compass falcon marble cedar tunnel").split()
    return " ".join(r.choice(vocab) + str(r.randrange(100)) for _ in range(n))


if "smoke" in PARTS:
    s = {}
    s["text"] = chat(user("What is 17 * 23? Answer with the number only."), 64)
    s["text_thinking"] = chat(user("A train travels 60 km in 45 minutes. What is its speed in km/h?"), 2048, thinking=True)
    for name, n in (("long_4k", 1500), ("long_12k", 4500), ("long_24k", 9000)):
        code = "ZEBRA-7419"
        mid = "The secret number in the middle is 88213."
        body = words(n, n // 2) + "\n" + mid + "\n" + words(n + 1, n // 2)
        prompt = (f"Remember this exact codeword: {code}.\n{body}\n"
                  "What is the exact codeword at the beginning, and what is the secret number in the middle? "
                  "Answer as: codeword, number.")
        s[name] = chat(user(prompt), 1024)
        s[name]["ok"] = code in (s[name]["content"] or "") and "88213" in (s[name]["content"] or "")
    try:
        from PIL import Image, ImageDraw
        im = Image.new("RGB", (128, 128), "white")
        ImageDraw.Draw(im).rectangle((16, 16, 111, 111), fill=(220, 0, 0))
        buf = io.BytesIO(); im.save(buf, format="PNG")
        url = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
        s["image"] = chat([{"role": "user", "content": [
            {"type": "text", "text": "What color is the large square in this image? Answer with one color."},
            {"type": "image_url", "image_url": {"url": url}}]}], 32)
    except Exception as e:
        s["image"] = {"error": repr(e)}
    res["smoke"] = s

DET = [
    "List the first ten prime numbers separated by commas.",
    "Explain in two sentences why the sky is blue.",
    "Write a Python function that reverses a linked list.",
    "Translate to French: The quick brown fox jumps over the lazy dog.",
    "Summarize the plot of Romeo and Juliet in three sentences.",
    "What are the main differences between TCP and UDP?",
    "Solve for x: 3x + 7 = 31. Show the steps.",
    "Name five countries in South America and their capitals.",
]
if "det" in PARTS:
    d = {"runs": []}
    for rep in range(2):
        flush()
        run = [chat(user(q), 128) for q in DET]
        run.append(chat(user(words(7, 3000) + "\nRepeat the last five words above exactly."), 64))
        d["runs"].append(run)
    d["self_cmp"] = [cmp(a, b) for a, b in zip(d["runs"][0], d["runs"][1])]
    res["det"] = d

if "cache" in PARTS:
    c = {}
    P = "Background notes:\n" + words(11, 3000) + "\n"
    q1 = P + "Question: what is the third word of the notes? Answer briefly."
    q2 = P + "Question: what is the last word of the notes? Answer briefly."
    # identical request
    nw = words(11, 3000).split()
    flush(); a = chat(user(q1), 1024); b = chat(user(q1), 1024)
    a["ok"] = has(a, nw[2]); b["ok"] = has(b, nw[2])
    c["identical"] = {"first": a, "second": b, "cmp": cmp(a, b)}
    # shared prefix: warm with q1, then q2 vs cold q2
    warm = chat(user(q2), 1024); flush(); cold = chat(user(q2), 1024)
    warm["ok"] = has(warm, nw[-1]); cold["ok"] = has(cold, nw[-1])
    c["shared_prefix"] = {"warm": warm, "cold": cold, "cmp": cmp(warm, cold)}
    # multi-turn tail continuation
    flush()
    t1 = user("Here is a document:\n" + words(13, 2500) + "\nReply with OK.")
    r1 = chat(t1, 16)
    t2 = t1 + [{"role": "assistant", "content": r1["content"] or "OK"},
               {"role": "user", "content": "Now state the first three words of the document."}]
    dw = words(13, 2500).split()
    warm = chat(t2, 1024)
    t3 = t2 + [{"role": "assistant", "content": warm["content"] or ""},
               {"role": "user", "content": "And the last three words?"}]
    warm3 = chat(t3, 1024)
    flush(); cold = chat(t2, 1024); flush(); cold3 = chat(t3, 1024)
    for r in (warm, cold): r["ok"] = has(r, *dw[:3])
    for r in (warm3, cold3): r["ok"] = has(r, *dw[-3:])
    c["tail_continuation"] = {"turn2_warm": warm, "turn2_cold": cold, "cmp2": cmp(warm, cold),
                              "turn3_warm": warm3, "turn3_cold": cold3, "cmp3": cmp(warm3, cold3)}
    # mid-sequence fork: cache a long sequence, then fork from its middle
    forks = {}
    for name, n_prefix in (("fork_at_1000_of_3000_words", 1000), ("fork_at_2000", 2000), ("fork_at_2990", 2990), ("fork_at_2999", 2999)):
        flush()
        base_words = words(17, 3000).split()
        head = "Remember this exact codeword: ZEBRA-7419.\n"
        seeded = chat(user(head + " ".join(base_words) + "\nReply with DONE."), 256)
        fork = (head + " ".join(base_words[:n_prefix]) + "\nThe checkpoint number is 5731.\n"
                "State the codeword from the beginning, the checkpoint number, and the last word before the checkpoint line. "
                "Answer as: codeword, number, word.")
        warm = chat(user(fork), 1024)
        flush(); cold = chat(user(fork), 1024)
        for r in (warm, cold): r["ok"] = has(r, "ZEBRA-7419", "5731", base_words[n_prefix - 1])
        forks[name] = {"seed": seeded, "warm": warm, "cold": cold, "cmp": cmp(warm, cold)}
    c["mid_fork"] = forks
    # cold-vs-cold noise floor
    flush(); x = chat(user(q2), 64); flush(); y = chat(user(q2), 64)
    c["cold_vs_cold"] = cmp(x, y)
    res["cache"] = c

json.dump(res, open(OUT, "w"), ensure_ascii=False, indent=1)


def brief(o, depth=0, key=""):
    if isinstance(o, dict) and "finish_reason" in o:
        print("  " * depth + f"{key}: fr={o['finish_reason']} pt={o['prompt_tokens']} cached={o['cached_tokens']} ct={o['completion_tokens']} ok={o.get('ok')} t={o['latency_s']} content={(o['content'] or '')[:70]!r}")
    elif isinstance(o, dict) and "same_tokens" in o:
        print("  " * depth + f"{key}: {o}")
    elif isinstance(o, dict):
        print("  " * depth + key)
        for k, v in o.items():
            brief(v, depth + 1, k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            brief(v, depth, f"{key}[{i}]")
brief(res)
