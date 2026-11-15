import json, statistics as st
R = "/scratch/cc-speed"
for arm in ["window1", "full", "window2"]:
    for s in (1, 2):
        rows = [json.loads(l) for l in open(f"{R}/{arm}/mt-s{s}.jsonl")]
        for t in range(6):
            r = [x for x in rows if x["turn"] == t]
            tt = [x["ttft"] for x in r if x["ttft"] is not None]
            print(arm, f"s{s} t{t}", "null", len(r) - len(tt), "ttft_med %.0f" % (1000 * st.median(tt) if tt else -1), "e2e_med %.0f" % (1000 * st.median(x["e2e"] for x in r)), "prompt %d" % st.median(x["prompt"] for x in r), "cached", sorted(x["cached"] or 0 for x in r), "compl", sorted(x["completion"] for x in r))
