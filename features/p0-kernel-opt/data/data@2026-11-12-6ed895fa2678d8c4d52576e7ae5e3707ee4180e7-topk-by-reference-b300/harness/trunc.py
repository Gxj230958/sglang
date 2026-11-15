import json, sys, glob
for job in sys.argv[1:]:
    f = glob.glob(f"/scratch/cc-pr43/logs/{job}/eval/*/output-rs0.jsonl")[0]
    rows = [json.loads(l) for l in open(f)]
    if job == sys.argv[1]:
        print("keys", list(rows[0].keys()))
    def g(r, *ks):
        for k in ks:
            if k in r: return r[k]
        for v in r.values():
            if isinstance(v, dict):
                for k in ks:
                    if k in v: return v[k]
    toks = sorted((g(r, "output_tokens", "completion_tokens") or 0) for r in rows)
    lat = sorted((g(r, "latency", "latency_s", "e2e_latency") or 0) for r in rows)
    print(job, "n", len(rows), "out_tok p50/p99/max", toks[len(toks)//2], toks[int(len(toks)*.99)], toks[-1], "sum", sum(toks), "lat p50/p99/max", lat[len(lat)//2], lat[int(len(lat)*.99)], lat[-1])
    for i, r in enumerate(rows):
        fr = g(r, "finish_reason")
        if fr != "stop":
            s = json.dumps(r, ensure_ascii=False)
            print("  non-stop idx", i, fr, "out_tok", g(r, "output_tokens", "completion_tokens"), "len", len(s), "tail:", s[-400:].replace("\n", " "))
