# E10 Window layout as the default: DEP8 preview gate — data@2026-11-15-5e6ee4ed50fc91fee9c5a0484667ce6de2ba5640-window-default-dep8

## Environment

- Machine: one node with 8× NVIDIA B300.
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`, served from a node-local copy; the checkpoint's own NextN head is the MTP draft. The copy was not re-hashed for this round.
- Software: image torch 2.14.1+cu130 and transformers 5.19.0; a first overlay adds sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5 and kernels 0.14.1; a second adds flashinfer-python / cubin / jit-cache 0.7.3. The code pins FlashInfer 0.7.4, which was not installed. `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.

## Setup

Deploy `git archive 5e6ee4ed50` and run [`gate-swadef.sh`](gate-swadef.sh): `--tp-size 8 --ep-size 8 --attn-dp-size 8 --moe-runner-backend flashinfer_trtllm --moe-a2a-backend none --dsa-prefill-backend trtllm --dsa-decode-backend trtllm --kv-cache-dtype fp8_e4m3 --context-length 147456 --mem-fraction-static 0.88 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --chunked-prefill-size 65536 --enable-fp32-lm-head`, `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model>`, `--enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47`. No layout variable is set; the server selects the window layout by default.

## Commit

- Code commit: `5e6ee4ed50fc91fee9c5a0484667ce6de2ba5640`, a local commit on top of pull request 58 (`c7c93b3fd0`) that makes the window sub-pool the default layout.
- Working tree: clean archive of the commit.
- Status: preview, non-release. The change exists only as a local branch. Its current version, `1c6afefe8a`, additionally removes the `SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA` variable and leaves `--disable-hybrid-swa-memory` as the only switch; that version was not run through GSM8K (its long-context behaviour is in [E11](../data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-retrieval/repro.md)). The image digest is not recorded.

## Scripts

- Version: round-specific [`gate-swadef.sh`](gate-swadef.sh), [`suite.py`](suite.py), [`probe.py`](probe.py) and [`midfork.py`](midfork.py).
- Temporary changes: none.

## Workload

- GSM8K: full test split (1319 questions) through `sgl-eval` 0.1.3, `sgl-eval run gsm8k --base-url <server>/v1 --temperature 1.0 --top-p 0.95`, 64 client threads, server-default thinking, no `max_tokens`, one run per configuration.
- Smoke suite ([`suite.py`](suite.py) `smoke`): text, thinking, 4K / 12K / 24K long-context needle and image requests.
- Retrieval probes ([`probe.py`](probe.py)): a document of `Record i: the code is c.` lines sized to a target length, three questions per length (records at 1/7, 1/2 and near the end), greedy, thinking off, `max_tokens=96`. A request is correct when the expected code appears in the answer. Prompts span 320 to 120936 tokens.
- Prefix-reuse probe ([`midfork.py`](midfork.py)): a 6680-token record document; six greedy, thinking-off requests in order: first, identical, different question at the end, document forked in the middle (late record), the forked document again (early record), follow-up turn. `cached` lists the reported `cached_tokens` in that order.

## Results

| Configuration | Accuracy | Stop rate | Truncated | Errors | Accept len | Probes | Prefix reuse | KV pool per DP rank |
|---|---|---|---|---|---|---|---|---|
| DEP8, default layout | 95.45% (1259/1319) | 100.00% | 0 | 0% | 2.54 | 16/18 correct, 17/18 `stop` | 6/6 correct, 6/6 `stop`; cached 0 / 0 / 0 / 0 / 0 / 0 | full_layer_tokens=2656064, swa_layer_tokens=265600 |

Accept length is the mean of the `accept len` field over the `Decode batch` lines of the server log. Truncated counts requests that ended with `finish_reason=length`. All six smoke requests ended with `stop`; no traceback was logged.

Conclusions:

1. Without any layout variable the server builds the window pool and passes the full GSM8K gate with no truncated request.
2. Two of 18 retrieval probes missed: a 2938-token prompt opened with reasoning and hit `max_tokens`, and a 120935-token prompt returned a wrong code with `stop`. [E11](../data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-retrieval/repro.md) shows the long-context miss rate is the same on the full-length layout and on the pre-merge code.
3. These numbers are a preview of an unpublished change and do not describe `glm-5-lp`.

## Data and Figures

- [`dep8/`](dep8/) — launch script, compressed server log, smoke, probe and prefix-reuse results, `gsm8k.log` and sgl-eval output.
- `status`, `gate-swadef.out` — driver status and console.
- [`summary.json`](summary.json) — every number in the Results section, recomputed from the committed files by [`summarize_round.py`](../../scripts/v2/summarize_round.py).
- [`evidence-hashes.json`](evidence-hashes.json) — original path and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
