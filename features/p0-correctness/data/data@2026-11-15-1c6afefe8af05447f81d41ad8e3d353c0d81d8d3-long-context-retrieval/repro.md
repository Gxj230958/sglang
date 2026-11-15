# E11 Long-context random-record retrieval on DEP8 with FP8 KV — data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-retrieval

## Environment

- Machine: one node with 8× NVIDIA B300.
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`, served from a node-local copy; the checkpoint's own NextN head is the MTP draft. The copy was not re-hashed for this round.
- Software for the two `new` arms: image torch 2.14.1+cu130 and transformers 5.19.0; a first overlay adds sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5 and kernels 0.14.1; a second adds flashinfer-python / cubin / jit-cache 0.7.3. The code pins FlashInfer 0.7.4, which was not installed. `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.
- Software for the pre-merge arm: image torch 2.14.1+cu130, transformers 5.19.0, sglang-kernel 0.4.10; an overlay on `PYTHONPATH` adds flashinfer-python / cubin / jit-cache 0.7.3, sgl-deep-gemm 0.2.7 and sgl-flash-mla 1.0.4; `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.

## Setup

[`ab.sh`](ab.sh) starts three servers one after another with `--tp-size 8 --ep-size 8 --attn-dp-size 8 --moe-runner-backend flashinfer_trtllm --moe-a2a-backend none --dsa-prefill-backend trtllm --dsa-decode-backend trtllm --kv-cache-dtype fp8_e4m3 --context-length 147456 --mem-fraction-static 0.88 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --chunked-prefill-size 65536 --enable-fp32-lm-head`, `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model>`, `--enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47`:

| Arm | Tree | Layout selection |
|---|---|---|
| `new-window` | `1c6afefe8a` | default (window) |
| `new-full-length` | `1c6afefe8a` | `--disable-hybrid-swa-memory` |
| `pre-merge-window` | `e941d571f3` | `SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1` |

## Commit

- Code commit: `1c6afefe8af05447f81d41ad8e3d353c0d81d8d3`, a local, unpublished commit on top of pull request 58 that makes the window layout the default and removes its environment variable.
- Comparison commit: `e941d571f3877797b383d616e957f30c8936c52d`, from before the upstream `main` merge.
- Working tree: clean archives.
- Status: preview, non-release; the image digest is not recorded.

## Scripts

- Version: round-specific [`ab.sh`](ab.sh) and [`stress.py`](stress.py).
- Temporary changes: none.

## Workload

- Salted stress ([`stress.py`](stress.py)): uncached record documents with a per-request salt, one random record per request, greedy, thinking off, `max_tokens=64`. A request counts when it ends with `stop` and contains the expected code.
- Long set: 12 requests each at 60000 and 110000 target tokens (64.7K and about 120.9K prompt tokens), 2 concurrent.
- Short set: 25 requests each at 3000, 9000 and 24000 target tokens, 8 concurrent.

## Results

| Arm | 60K: correct / wrong code with `stop` / not `stop` (of 12) | 120.9K: correct / wrong code with `stop` / not `stop` (of 12) | 3K / 9K / 24K correct (of 25 each) |
|---|---|---|---|
| `new-window` | 7 / 0 / 5 | 7 / 4 / 1 | 25 / 25 / 24 |
| `new-full-length` | 8 / 1 / 3 | 7 / 4 / 1 | 24 / 25 / 25 |
| `pre-merge-window` | 6 / 0 / 6 | 6 / 5 / 1 | 25 / 25 / 23 |

"Not `stop`" requests open with reasoning instead of the answer and hit `max_tokens=64`. The `new-full-length` server logged `max_total_num_tokens=2058688` and no window pool; the window arms logged full_layer_tokens=2656064, swa_layer_tokens=265600 and full_layer_tokens=2655168, swa_layer_tokens=265472.

Conclusions:

1. On this configuration (DEP8, `trtllm` DSA backend, FP8 KV, greedy, thinking off) retrieval of a random record succeeds for 6 to 8 of 12 prompts (50–67%) at 60K and at 120.9K tokens, on every arm. Prompts up to 24K tokens succeed at 92–100%.
2. The miss rate does not depend on the layout, on the default-layout change, or on the upstream merge: the full-length arm and the pre-merge arm show it as well.
3. This is an open observation. Attribution to FP8 KV, attention DP routing, the thinking-off prompt format, or the model's own retrieval limit is pending; no conclusion is drawn. The earlier fixed-position probes at 120.9K tokens (three record positions per run) do not exercise random positions.
4. Each cell has 12 requests; differences of one or two requests between arms are not significant.

## Data and Figures

- [`new-window/`](new-window/), [`new-full-length/`](new-full-length/), [`pre-merge-window/`](pre-merge-window/) — launch script, compressed server log, `long.jsonl` / `short.jsonl` request rows and their console logs.
- `status`, `ab.out` — driver status and console.
- [`summary.json`](summary.json) — every number in the Results section, recomputed from the committed files by [`summarize_round.py`](../../scripts/v2/summarize_round.py).
- [`evidence-hashes.json`](evidence-hashes.json) — original path and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
