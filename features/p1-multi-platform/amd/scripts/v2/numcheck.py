#!/opt/venv/bin/python
"""numcheck.py <port> <out.json> [--ref ref.json] [--n 32]: numerics probe for A/B of kernel paths.

For n GSM8K problems (chat template, thinking off), records the greedy continuation (256 tokens,
temperature 0) and, given --ref, the teacher-forced logprob and top-1 token of every reference
continuation token (one prefill each). Compare two outputs with numcheck_compare.py.
"""
import argparse
import glob
import json
import urllib.request

from transformers import AutoTokenizer

MODEL = "/persistent/models/GLM-5-1028-Provider"
PRED = sorted(glob.glob("/persistent/work/glm_loop_amd/evals/gsm8k_mtp/sgl_eval_gsm8k_*/output-rs0.jsonl"))[0]


def flush(port):
    urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{port}/flush_cache", data=b"", method="POST"), timeout=120).read()


def post(port, body):
    flush(port)  # every request computes its whole prompt: no KV from another batch shape
    r = urllib.request.Request(
        f"http://127.0.0.1:{port}/generate",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    return json.load(urllib.request.urlopen(r, timeout=900))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("port", type=int)
    ap.add_argument("out")
    ap.add_argument("--ref")
    ap.add_argument("--n", type=int, default=32)
    a = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(MODEL)
    problems = [json.loads(l)["problem"] for l in open(PRED)][: a.n]
    ref = json.load(open(a.ref)) if a.ref else None
    out = []
    for i, p in enumerate(problems):
        msgs = [{"role": "user", "content": p + "\nPlease reason step by step, and put your final answer within \\boxed{}."}]
        ids = tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=True, enable_thinking=False)
        if not isinstance(ids, list):
            ids = list(ids["input_ids"])
        g = post(a.port, {"input_ids": ids, "sampling_params": {"max_new_tokens": 256, "temperature": 0}})
        rec = {"prompt_ids": ids, "greedy_ids": g["output_ids"]}
        if ref:
            cont = ref[i]["greedy_ids"]
            tf = post(
                a.port,
                {
                    "input_ids": ids + cont,
                    "sampling_params": {"max_new_tokens": 1, "temperature": 0},
                    "return_logprob": True,
                    "logprob_start_len": len(ids) - 1,
                    "top_logprobs_num": 1,
                },
            )
            m = tf["meta_info"]
            rec["tf_logprob"] = [x[0] for x in m["input_token_logprobs"][1:]][: len(cont)]
            rec["tf_top1"] = [x[0][1] for x in m["input_top_logprobs"][1:]][: len(cont)]
            rec["ref_ids"] = cont
        out.append(rec)
    json.dump(out, open(a.out, "w"))
    print(f"wrote {a.out}: {len(out)} problems")


if __name__ == "__main__":
    main()
