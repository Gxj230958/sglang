import json, sys, collections, os
for d in sys.argv[1:]:
    p = f"agentx/{d}/profile_export_aiperf.json"
    if not os.path.exists(p):
        continue
    j = json.load(open(p))
    def g(k, s="avg"):
        v = j.get(k) or {}
        return v.get(s) if isinstance(v, dict) else v
    errs = collections.Counter()
    for l in open(f"agentx/{d}/profile_export.jsonl"):
        r = json.loads(l)
        if r.get("error") and r["metadata"].get("benchmark_phase") == "profiling":
            errs[r["error"].get("type")] += 1
    r1 = lambda x: None if x is None else round(x, 1)
    print(d, "req", g("request_count"), "out_tok", g("total_output_tokens"),
          "dec_tps", r1(g("effective_decode_throughput")), "tot_tps", r1(g("effective_total_throughput")),
          "dec_conc", r1(g("effective_decode_concurrency")), "pre_conc", r1(g("effective_prefill_concurrency")),
          "ttft_avg/p50", r1(g("time_to_first_token")), r1(g("time_to_first_token", "p50")),
          "itl_avg/p50", r1(g("inter_token_latency")), r1(g("inter_token_latency", "p50")),
          "lat_avg", r1(g("request_latency")), "errs", dict(errs))
