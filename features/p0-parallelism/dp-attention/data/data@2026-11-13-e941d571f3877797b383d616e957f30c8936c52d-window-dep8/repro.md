# E02 Window layout under DEP8 on B300 — data@2026-11-13-e941d571f3877797b383d616e957f30c8936c52d-window-dep8

## Environment

- Machine: one node with 8× NVIDIA B300.
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`, served from a node-local copy; the checkpoint's own NextN head is the MTP draft. The copy was not re-hashed for this round.
- Software: image torch 2.14.1+cu130, transformers 5.19.0, sglang-kernel 0.4.10; an overlay on `PYTHONPATH` adds flashinfer-python / cubin / jit-cache 0.7.3, sgl-deep-gemm 0.2.7 and sgl-flash-mla 1.0.4; `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.

## Setup

Deploy `git archive e941d571f3` and run the second job of [`combo.sh`](combo.sh): `--tp-size 8 --ep-size 8 --attn-dp-size 8 --moe-runner-backend flashinfer_trtllm --moe-a2a-backend none --dsa-prefill-backend trtllm --dsa-decode-backend trtllm --kv-cache-dtype fp8_e4m3 --context-length 147456 --mem-fraction-static 0.88 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --chunked-prefill-size 65536 --enable-fp32-lm-head`, `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model>`, with `SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1`.

## Commit

- Code commit: `e941d571f3877797b383d616e957f30c8936c52d` (`glm-5-lp` at `a736925063` plus the prefill-CP change, which this configuration does not use).
- Working tree: clean archive of the commit.
- Status: non-release. The image digest is not recorded and dependencies come from `PYTHONPATH` overlays, so the environment is not locked.

## Scripts

- Version: round-specific [`combo.sh`](combo.sh), [`probe.py`](probe.py) and [`midfork.py`](midfork.py).
- Temporary changes: none. The driver's status file was not retained.

## Workload

- GSM8K: full test split (1319 questions) through `sgl-eval` 0.1.3, `sgl-eval run gsm8k --base-url <server>/v1 --temperature 1.0 --top-p 0.95`, 64 client threads, server-default thinking, no `max_tokens`, one run per configuration.
- Retrieval probes ([`probe.py`](probe.py)): a document of `Record i: the code is c.` lines sized to a target length, three questions per length (records at 1/7, 1/2 and near the end), greedy, thinking off, `max_tokens=96`. A request is correct when the expected code appears in the answer. Prompts span 320 to 120936 tokens.
- Prefix-reuse probe ([`midfork.py`](midfork.py)): a 6680-token record document; six greedy, thinking-off requests in order: first, identical, different question at the end, document forked in the middle (late record), the forked document again (early record), follow-up turn. `cached` lists the reported `cached_tokens` in that order.

## Results

| Configuration | Accuracy | Stop rate | Truncated | Errors | Accept len | Probes | Prefix reuse | KV pool per DP rank |
|---|---|---|---|---|---|---|---|---|
| DEP8, `trtllm`, FP8 KV, window layout | 94.16% (1242/1319) | 99.85% | 2 | 0% | 2.75 | 18/18 correct, 18/18 `stop` | 6/6 correct, 6/6 `stop`; cached 0 / 0 / 0 / 0 / 0 / 0 | full_layer_tokens=2655168, swa_layer_tokens=265472 |

Accept length is the mean of the `accept len` field over the `Decode batch` lines of the server log. Truncated counts requests that ended with `finish_reason=length`.

Conclusions:

1. The window layout passes the stop-rate gate under TP8 + EP8 + attention DP8 with the `trtllm` DSA backend and FP8 KV; no traceback was logged.
2. The 18 fixed-position retrieval probes are correct up to 120936 tokens. Random-record retrieval at 60K tokens and above on this configuration is a separate open observation ([Correctness E11](../../../../p0-correctness/data/data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-retrieval/repro.md)).
3. Under DP8 routing no request of the prefix-reuse probe reports cached tokens; all answers are correct.

## Data and Figures

- [`dep8/`](dep8/) — launch script, compressed server log, probe and prefix-reuse results, `gsm8k.log` and sgl-eval output.
- [`summary.json`](summary.json) — every number in the Results section, recomputed from the committed files by [`summarize_round.py`](../../../../p0-correctness/scripts/v2/summarize_round.py).
- [`evidence-hashes.json`](evidence-hashes.json) — original path and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
