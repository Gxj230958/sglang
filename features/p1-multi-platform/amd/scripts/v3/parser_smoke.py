"""parser_smoke.py <base-url/v1> <out.json>: reasoning/tool-call parser API checks (glm45 / glm47).
Greedy. Thinking on/off routing, a tool call (non-streaming and streaming reconstruction),
a parallel-call prompt, tool_choice=none/required, and a follow-up turn with the tool result."""
import json, sys, urllib.request

B, OUT = sys.argv[1], sys.argv[2]
MODEL = json.load(urllib.request.urlopen(B + "/models"))["data"][0]["id"]
TOOLS = [{"type": "function", "function": {
    "name": "get_weather", "description": "Get the current weather for a city.",
    "parameters": {"type": "object", "properties": {
        "city": {"type": "string"}, "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}},
        "required": ["city"]}}}]


def post(body, stream=False):
    body = {"model": MODEL, "temperature": 0, "max_tokens": 2048, **body, "stream": stream}
    r = urllib.request.Request(B + "/chat/completions", json.dumps(body).encode(), {"Content-Type": "application/json"})
    resp = urllib.request.urlopen(r, timeout=600)
    if not stream:
        return json.load(resp)
    content, reasoning, calls, finish = "", "", {}, None
    for line in resp:
        line = line.strip()
        if not line.startswith(b"data:") or line.endswith(b"[DONE]"):
            continue
        ch = json.loads(line[5:])["choices"]
        if not ch:
            continue
        d = ch[0].get("delta") or {}
        content += d.get("content") or ""
        reasoning += d.get("reasoning_content") or ""
        for tc in d.get("tool_calls") or []:
            c = calls.setdefault(tc["index"], {"name": "", "arguments": ""})
            f = tc.get("function") or {}
            c["name"] += f.get("name") or ""
            c["arguments"] += f.get("arguments") or ""
        finish = ch[0].get("finish_reason") or finish
    return {"content": content, "reasoning": reasoning, "calls": [calls[k] for k in sorted(calls)], "finish": finish}


def msg(r):
    c = r["choices"][0]
    m = c["message"]
    return m, c["finish_reason"]


res, ok = {}, {}
LEAK = ("<think>", "</think>", "<tool_call>", "</tool_call>", "<arg_key>", "<arg_value>")
leak = lambda *s: any(t in (x or "") for x in s for t in LEAK)

m, f = msg(post({"messages": [{"role": "user", "content": "What is 17*23? Reply with the number."}]}))
res["think_on"] = {"content": m["content"], "reasoning_len": len(m.get("reasoning_content") or ""), "finish": f}
ok["think_on"] = bool(m.get("reasoning_content")) and "391" in (m["content"] or "") and f == "stop" and not leak(m["content"], m.get("reasoning_content"))

m, f = msg(post({"messages": [{"role": "user", "content": "What is 17*23? Reply with the number."}],
                 "chat_template_kwargs": {"enable_thinking": False}}))
res["think_off"] = {"content": m["content"], "reasoning": m.get("reasoning_content"), "finish": f}
ok["think_off"] = not m.get("reasoning_content") and "391" in (m["content"] or "") and f == "stop" and not leak(m["content"])

q = [{"role": "user", "content": "What's the weather in Paris right now? Use celsius."}]
r = post({"messages": q, "tools": TOOLS})
m, f = msg(r)
tc = m.get("tool_calls") or []
args = json.loads(tc[0]["function"]["arguments"]) if tc else {}
res["tool"] = {"content": m["content"], "tool_calls": tc, "finish": f}
ok["tool"] = f == "tool_calls" and len(tc) == 1 and tc[0]["function"]["name"] == "get_weather" and args.get("city", "").lower().startswith("paris") and not leak(m["content"])

s = post({"messages": q, "tools": TOOLS}, stream=True)
res["tool_stream"] = s
ok["tool_stream_matches"] = (s["finish"] == "tool_calls" and len(s["calls"]) == 1 and s["calls"][0]["name"] == "get_weather"
                             and json.loads(s["calls"][0]["arguments"]) == args and not leak(s["content"], s["reasoning"]))

m, f = msg(post({"messages": [{"role": "user", "content": "Get the weather in Tokyo and in Berlin, both in celsius."}], "tools": TOOLS}))
tc2 = m.get("tool_calls") or []
res["parallel"] = {"tool_calls": tc2, "finish": f}
cities = sorted(json.loads(t["function"]["arguments"]).get("city", "").lower() for t in tc2)
ok["parallel"] = f == "tool_calls" and len(tc2) == 2 and cities == ["berlin", "tokyo"] and len({t["id"] for t in tc2}) == 2

m, f = msg(post({"messages": q, "tools": TOOLS, "tool_choice": "none"}))
res["choice_none"] = {"content": (m["content"] or "")[:200], "tool_calls": m.get("tool_calls"), "finish": f}
ok["choice_none"] = not m.get("tool_calls") and f == "stop" and not leak(m["content"])

m, f = msg(post({"messages": [{"role": "user", "content": "Hi! How are you?"}], "tools": TOOLS, "tool_choice": "required"}))
res["choice_required"] = {"tool_calls": m.get("tool_calls"), "finish": f}
ok["choice_required"] = bool(m.get("tool_calls")) and m["tool_calls"][0]["function"]["name"] == "get_weather"

if tc:
    follow = q + [{"role": "assistant", "content": m0 if (m0 := res["tool"]["content"]) else "", "tool_calls": tc},
                  {"role": "tool", "tool_call_id": tc[0]["id"], "content": json.dumps({"city": "Paris", "temp_c": 14, "sky": "light rain"})}]
    m, f = msg(post({"messages": follow, "tools": TOOLS}))
    res["follow_up"] = {"content": m["content"], "finish": f}
    ok["follow_up"] = f == "stop" and "14" in (m["content"] or "") and not m.get("tool_calls") and not leak(m["content"])

json.dump({"ok": ok, "results": res}, open(OUT, "w"), indent=1)
for k, v in ok.items():
    print(f"{k:22s} {'PASS' if v else 'FAIL'}")
print(f"{sum(ok.values())}/{len(ok)} pass")
