"""Builds SPEED-Bench qualitative/coding as InferenceX's speedbench collector does
(NeMo-Skills prepare.py at 5ac8609a, then the collector's category filter that restores "turns").
Re-implemented for the coding category only: livecodebench and code_contests rows are
resolved from the same pinned revisions. usage: prep_coding.py <out.jsonl>"""
import json, sys
from datasets import load_dataset

PH = "FULL BENCHMARK DATA SHOULD BE FETCHED FROM THE SOURCE USING SPECDEC_BENCH"
LCB = "livecodebench/code_generation_lite"
CC = "deepmind/code_contests"

ds = load_dataset("nvidia/SPEED-Bench", "qualitative", split="test")
rows = [r for r in ds if r["category"] == "coding"]
need = {s for r in rows for s in (LCB, CC) if s in r["source"]}
lcb = cc = None
if LCB in need:
    lcb = load_dataset("json", split="test", data_files={"test": [
        f"https://huggingface.co/datasets/{LCB}/resolve/0fe84c3912ea0c4d4a78037083943e8f0c4dd505/{f}.jsonl"
        for f in ["test", "test2", "test3", "test4", "test5", "test6"]]}).to_pandas()
if CC in need:
    cc = load_dataset(CC, revision="802411c3010cb00d1b05bad57ca77365a3c699d6",
                      data_files={"test": "data/test-*"}, split="test").to_pandas()
out = []
for r in rows:
    t0 = r["turns"][0]
    if LCB in r["source"]:
        e = lcb[lcb["question_id"] == r["src_id"]].iloc[0]
        r["turns"] = [t0.removeprefix(f"{PH}\n\n").format(question=e["question_content"], starter_code=e["starter_code"])]
    elif CC in r["source"]:
        e = cc[cc["name"] == r["src_id"]].iloc[0]
        r["turns"] = [t0.removeprefix(f"{PH}\n\n").format(question=e["description"])]
    assert PH not in r["turns"][0], r["question_id"]
    r["messages"] = [{"role": "user", "content": t} for t in r["turns"]]
    out.append(r)
with open(sys.argv[1], "w") as f:
    for r in out:
        f.write(json.dumps(r) + "\n")
print("coding rows", len(out))
