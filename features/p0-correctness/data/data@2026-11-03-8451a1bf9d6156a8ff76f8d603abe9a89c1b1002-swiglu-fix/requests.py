import base64, io, json, sys, time, urllib.request
from PIL import Image, ImageDraw, ImageFont

from sglang.srt.configs.glm_loop import GlmLoopConfig
cfg = GlmLoopConfig.from_pretrained("/path/to/GLM-5-1028-Provider")
print("config vision swiglu_limit:", cfg.vision_config.swiglu_limit, "text swiglu_limit:", getattr(cfg.text_config, "swiglu_limit", "<absent>"))

def img_b64(img):
    buf = io.BytesIO(); img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

shapes = Image.new("RGB", (512, 256), "white")
d = ImageDraw.Draw(shapes)
d.rectangle([40, 48, 200, 208], fill=(220, 20, 20))
d.ellipse([312, 48, 472, 208], fill=(20, 40, 220))
text_img = Image.new("RGB", (640, 200), "white")
ImageDraw.Draw(text_img).text((40, 50), "PURPLE ELEPHANT 734", fill="black", font=ImageFont.load_default(size=56))
for name, im in (("shapes", shapes), ("text", text_img)):
    im.save(f"/scratch/glm5-swiglu-{name}.png")

def chat(content, max_tokens=4096):
    body = {"model": "default", "messages": [{"role": "user", "content": content}],
            "max_tokens": max_tokens, "temperature": 1.0, "top_p": 0.95}
    req = urllib.request.Request("http://127.0.0.1:30000/v1/chat/completions",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    t = time.time()
    with urllib.request.urlopen(req, timeout=600) as r:
        out = json.load(r)
    ch = out["choices"][0]
    return ch["message"].get("content") or "", ch["finish_reason"], out["usage"], time.time() - t

cases = [
    ("text-arith", "What is 17 * 23? Reply with just the number.", ["391"]),
    ("text-capital", "What is the capital of France? Reply with one word.", ["paris"]),
    ("image-shapes", [{"type": "image_url", "image_url": {"url": img_b64(shapes)}},
                      {"type": "text", "text": "Describe the two shapes in this image and their colors, left to right. Be brief."}],
     ["red", "blue", "circle"]),
    ("image-text", [{"type": "image_url", "image_url": {"url": img_b64(text_img)}},
                    {"type": "text", "text": "Read the text in this image exactly. Reply with the text only."}],
     ["purple", "elephant", "734"]),
]
ok = True
results = []
for name, content, must in cases:
    ans, fr, usage, dt = chat(content)
    hit = all(m in ans.lower() for m in must)
    good = hit and fr == "stop"
    ok &= good
    results.append({"case": name, "finish_reason": fr, "content_ok": hit, "usage": usage, "latency_s": round(dt, 1), "answer": ans})
    print(json.dumps(results[-1], ensure_ascii=False))
json.dump(results, open("/scratch/glm5-swiglu-requests.json", "w"), indent=2, ensure_ascii=False)
print("ALL_OK" if ok else "SOME_FAILED")
sys.exit(0 if ok else 1)
