"""Text, image and long-context smoke requests (H200 E01 workload) against a server.

Usage: python smoke.py [port] [out_dir]
Each request passes when the answer matches and finish_reason is "stop".
"""

import base64
import io
import json
import os
import sys
import time
import urllib.request

from PIL import Image, ImageDraw

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 30000
OUT = sys.argv[2] if len(sys.argv) > 2 else "."
URL = f"http://127.0.0.1:{PORT}/v1/chat/completions"
os.makedirs(OUT, exist_ok=True)


def post(name, content, max_tokens=512):
    payload = {
        "model": "glm-loop",
        "messages": [{"role": "user", "content": content}],
        "max_tokens": max_tokens,
        "temperature": 0,
        "top_p": 1,
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=1800) as response:
        d = json.load(response)
    dt = time.time() - t0
    with open(os.path.join(OUT, f"{name}-smoke.json"), "w") as handle:
        json.dump(d, handle, ensure_ascii=False, indent=2)
    choice = d["choices"][0]
    msg = choice["message"]
    return msg.get("content") or "", msg.get("reasoning_content") or "", choice["finish_reason"], d["usage"], dt


def check(name, content, expect, max_tokens=512):
    answer, reasoning, finish, usage, dt = post(name, content, max_tokens)
    ok = expect.lower() in answer.lower() and finish == "stop"
    print(
        f"[{'PASS' if ok else 'FAIL'}] {name}: answer={answer.strip()[:120]!r} "
        f"finish={finish} usage={usage} time={dt:.1f}s"
    )
    if reasoning:
        print(f"    reasoning[:300]={reasoning.strip()[:300]!r}")
    return ok


results = []
results.append(check("text", "What is 2+3? Answer briefly.", "5", max_tokens=1024))

image = Image.new("RGB", (128, 128), "white")
ImageDraw.Draw(image).rectangle((16, 16, 111, 111), fill=(220, 0, 0))
buf = io.BytesIO()
image.save(buf, format="PNG")
url = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
results.append(
    check(
        "image",
        [
            {"type": "image_url", "image_url": {"url": url}},
            {"type": "text", "text": "What color is the square? Answer with one word."},
        ],
        "red",
    )
)

filler = " ".join(
    f"Record {i}: the weather was mild and the river was calm." for i in range(220)
)
long_prompt = (
    "Read the notes and answer the question.\n"
    + filler[: len(filler) // 2]
    + " The secret code is BLUE-4721. "
    + filler[len(filler) // 2 :]
    + "\nQuestion: What is the secret code? Reply with the code only."
)
results.append(check("long", long_prompt, "BLUE-4721"))
print("ALL PASS" if all(results) else "SOME FAILED")
