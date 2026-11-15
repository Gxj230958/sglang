import json, sys
a = json.load(open(sys.argv[1])); b = json.load(open(sys.argv[2]))
def cmp(x, y):
    n = min(len(x["tokens"]), len(y["tokens"]))
    first = next((i for i in range(n) if x["tokens"][i] != y["tokens"][i]), None)
    m = n if first is None else first
    d = max((abs(x["logprobs"][i] - y["logprobs"][i]) for i in range(m)), default=0.0)
    return first, n, round(d, 5)
same = 0; rows = []
for i, (x, y) in enumerate(zip(a["det"]["runs"][0], b["det"]["runs"][0])):
    f, n, d = cmp(x, y); same += f is None; rows.append((i, f, n, d))
print(f"identical token sequences: {same}/{len(rows)}")
for r in rows: print("  prompt %d first_diff=%s n=%d max|dlogprob|=%s" % r)
