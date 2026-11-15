import json, sys
a, b = [json.load(open(f"/scratch/cc-pr43/logs/{j}/suite.json"))["det"]["runs"] for j in sys.argv[1:3]]
print("runs", len(a), "prompts", len(a[0]))
for i, (x, y) in enumerate(zip(a[0], b[0])):
    lx, ly = x.get("logprobs") or [], y.get("logprobs") or []
    n = min(len(lx), len(ly))
    fd = next((k for k in range(n) if lx[k] != ly[k]), None)
    mx = max((abs(lx[k] - ly[k]) for k in range(n)), default=0.0)
    print(i, "same_text", x["content"] == y["content"], "ntok", len(lx), len(ly), "first_logprob_diff", fd, "max_abs_diff", mx)
