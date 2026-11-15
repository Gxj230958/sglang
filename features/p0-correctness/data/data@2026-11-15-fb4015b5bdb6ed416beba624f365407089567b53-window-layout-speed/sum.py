import json, glob, os, statistics as st
R = "/scratch/cc-speed"
for w in ["short-c1", "short-c32", "long-c4"]:
    for arm in ["window1", "full", "window2"]:
        for s in (1, 2):
            p = f"{R}/{arm}/{w}-s{s}.jsonl"
            if not os.path.exists(p): print(w, arm, s, "MISSING"); continue
            d = json.loads(open(p).read().strip().splitlines()[-1])
            print(w, arm, f"s{s}", "ok", d.get("completed"), "out_tps %.1f" % d["output_throughput"], "ttft_med %.0f" % d["median_ttft_ms"], "ttft_p99 %.0f" % d["p99_ttft_ms"], "tpot %.2f" % d.get("mean_tpot_ms", -1), "itl_med %.2f" % d["median_itl_ms"], "e2e_med %.0f" % d["median_e2e_latency_ms"], "acc", d.get("accept_length"), "dur %.1f" % d["duration"])
for arm in ["window1", "full", "window2"]:
    for s in (1, 2):
        rows = [json.loads(l) for l in open(f"{R}/{arm}/mt-s{s}.jsonl")]
        line = []
        for t in range(6):
            r = [x for x in rows if x["turn"] == t]
            line.append("t%d n%d ttft %.0f e2e %.0f p%d c%d" % (t, len(r), 1000*st.median(x["ttft"] for x in r), 1000*st.median(x["e2e"] for x in r), st.median(x["prompt"] for x in r), st.median(x["cached"] or 0 for x in r)))
        print("mt", arm, f"s{s}", " | ".join(line))
    print(arm, "traceback", os.popen(f"grep -c Traceback {R}/{arm}/serve.log").read().strip(), os.popen(f"grep -m1 -E 'sliding window|full_layer_tokens|max_total_num_tokens' {R}/{arm}/serve.log").read().strip()[-150:])
