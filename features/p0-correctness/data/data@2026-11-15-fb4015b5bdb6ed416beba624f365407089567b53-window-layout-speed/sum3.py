import json, os, statistics as st
R = "/scratch/cc-speed"
for w in ["short-c1", "short-c32", "long-c4"]:
    for arm in ["tp8-window-r2", "tp8-full"]:
        for s in (1, 2):
            d = json.loads(open(f"{R}/{arm}/{w}-s{s}.jsonl").read().strip().splitlines()[-1])
            print(w, arm, f"s{s}", "ok", d.get("completed"), "out_tps %.1f" % d["output_throughput"], "ttft_med %.0f" % d["median_ttft_ms"], "ttft_p99 %.0f" % d["p99_ttft_ms"], "tpot %.2f" % d["mean_tpot_ms"], "itl_med %.2f" % d["median_itl_ms"], "e2e_med %.0f" % d["median_e2e_latency_ms"], "acc %.2f" % d["accept_length"])
for th in (1, 4):
    for s in (1, 2):
        for arm in ["tp8-window-r2", "tp8-full"]:
            rows = [json.loads(l) for l in open(f"{R}/{arm}/mt-t{th}-s{s}.jsonl")]
            out = []
            for t in range(8):
                r = [x for x in rows if x["turn"] == t]
                tt = [x["ttft"] for x in r if x["ttft"] is not None]
                out.append("t%d ttft %.0f p%d c%d n0=%d" % (t, 1000 * st.median(tt) if tt else -1, st.median(x["prompt"] for x in r), st.median(x["cached"] or 0 for x in r), len(r) - len(tt)))
            tt = [x["ttft"] for x in rows if x["turn"] > 0 and x["ttft"] is not None]
            print("mt th%d s%d" % (th, s), arm, "turn>0 ttft med %.0f mean %.0f" % (1000 * st.median(tt), 1000 * st.mean(tt)), "uncached_sum", sum(x["prompt"] - (x["cached"] or 0) for x in rows if x["turn"] > 0), "compl_sum", sum(x["completion"] for x in rows), "e2e_sum %.1f" % sum(x["e2e"] for x in rows))
            print("   ", " | ".join(out))
for arm in ["tp8-window-r2", "tp8-full"]:
    print(arm, "traceback", os.popen(f"grep -c Traceback {R}/{arm}/serve.log").read().strip(), os.popen(f"grep -m1 -E 'sliding window|max_total_num_tokens=' {R}/{arm}/serve.log").read().strip()[-160:])
