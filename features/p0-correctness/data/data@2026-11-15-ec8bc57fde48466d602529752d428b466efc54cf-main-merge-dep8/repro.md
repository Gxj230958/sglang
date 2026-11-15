# E09 Pushed main merge: DEP8 confirmation — data@2026-11-15-ec8bc57fde48466d602529752d428b466efc54cf-main-merge-dep8

## Environment

- Machine: one node with 8× NVIDIA B300.
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`, served from a node-local copy; the checkpoint's own NextN head is the MTP draft. The copy was not re-hashed for this round.
- Software: image torch 2.14.1+cu130 and transformers 5.19.0; a first overlay adds sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5 and kernels 0.14.1; a second adds flashinfer-python / cubin / jit-cache 0.7.3. The code pins FlashInfer 0.7.4, which was not installed. `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.

## Setup

Deploy `git archive ec8bc57fde` and run [`gate-dep8.sh`](gate-dep8.sh). The first launch fails on the kernel version check until the dependency overlay with sglang-kernel 0.4.11 is ahead of the image packages. All servers use `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model>` and `--enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47`; no layout variable is set, so these runs use the full-length layout.

- DEP8: `--tp-size 8 --ep-size 8 --attn-dp-size 8 --moe-runner-backend flashinfer_trtllm --moe-a2a-backend none --dsa-prefill-backend trtllm --dsa-decode-backend trtllm --kv-cache-dtype fp8_e4m3 --context-length 147456 --mem-fraction-static 0.88 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --chunked-prefill-size 65536 --enable-fp32-lm-head`.

## Commit

- Code commit: `ec8bc57fde48466d602529752d428b466efc54cf`, the merge of upstream `main` at `6de483b326` pushed to `glm-5-lp` on 2026-11-15.
- Working tree: clean archive of the commit. Its tree differs from the gated `c6a9b3411f` ([E08](../data@2026-11-14-c6a9b3411f3db9fa1a4244ec6eede2a43bbf5550-main-merge-gate/repro.md)) by one refactor of the FP8 sparse decode kernel header that had landed on the branch in between.
- Status: non-release. The image digest is not recorded and dependencies come from `PYTHONPATH` overlays, so the environment is not locked.

## Scripts

- Version: round-specific [`gate-dep8.sh`](gate-dep8.sh) and [`suite.py`](suite.py).
- Temporary changes: none.

## Workload

- GSM8K: full test split (1319 questions) through `sgl-eval` 0.1.3, `sgl-eval run gsm8k --base-url <server>/v1 --temperature 1.0 --top-p 0.95`, 64 client threads, server-default thinking, no `max_tokens`, one run per configuration.
- Smoke suite ([`suite.py`](suite.py) `smoke`): text, thinking, 4K / 12K / 24K long-context needle and image requests.

## Results

| Configuration | Accuracy | Stop rate | Truncated | Errors | Accept len | Smoke | KV pool |
|---|---|---|---|---|---|---|---|
| DEP8, `trtllm`, FP8 KV | 94.62% (1248/1319) | 99.85% | 2 | 0% | 2.87 | 6/6 `stop` | 2058688 tokens per DP rank |

Accept length is the mean of the `accept len` field over the `Decode batch` lines of the server log. Truncated counts requests that ended with `finish_reason=length`.

Conclusions:

1. The exact pushed head passes the DEP8 stop-rate gate and the smoke suite with no traceback.
2. TP8 was gated on `c6a9b3411f` only.

## Data and Figures

- [`dep8/`](dep8/) — launch script, compressed server log, smoke results, `gsm8k.log` and sgl-eval output.
- `status-dep8-ec8b`, `gate-dep8b.out` — driver status and console.
- [`summary.json`](summary.json) — every number in the Results section, recomputed from the committed files by [`summarize_round.py`](../../scripts/v2/summarize_round.py).
- [`evidence-hashes.json`](evidence-hashes.json) — original path and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
