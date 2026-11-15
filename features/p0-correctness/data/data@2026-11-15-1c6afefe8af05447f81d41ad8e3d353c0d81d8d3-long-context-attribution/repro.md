# E12 Long-context retrieval attribution: KV dtype, parallelism and thinking — data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-attribution

## Environment

- Machine: one node with 8× NVIDIA B300.
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`, served from a node-local copy; the checkpoint's own NextN head is the MTP draft. The copy was not re-hashed for this round.
- Software: image torch 2.14.1+cu130 and transformers 5.19.0; a first overlay adds sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5 and kernels 0.14.1; a second adds flashinfer-python / cubin / jit-cache 0.7.3. The code pins FlashInfer 0.7.4, which was not installed. `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.

## Setup

[`attrib.sh`](attrib.sh) starts three servers one after another on the default (window) layout. All arms add `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model> --enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47`.

| Arm | Flags | Resolved DSA backend | KV dtype | Sets run |
|---|---|---|---|---|
| `dep8-bf16` | `--tp-size 8 --ep-size 8 --attn-dp-size 8 --moe-runner-backend flashinfer_trtllm --moe-a2a-backend none --dsa-prefill-backend trtllm --dsa-decode-backend trtllm --context-length 147456 --mem-fraction-static 0.88 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --chunked-prefill-size 65536 --enable-fp32-lm-head --kv-cache-dtype bfloat16` | `trtllm` | BF16 | thinking off, thinking on |
| `tp8-bf16` | `--tp-size 8 --mem-fraction-static 0.75 --context-length 147456 --chunked-prefill-size 32768 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph` | `flashmla_sparse` | BF16 | thinking off, thinking on |
| `dep8-fp8-think` | the `dep8-bf16` flags with `--kv-cache-dtype fp8_e4m3` | `trtllm` | FP8 | thinking on |

The thinking-off DEP8 FP8 cell is the `new-window` arm of [E11](../data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-retrieval/repro.md), run on the same tree with the same prompts.

## Commit

- Code commit: `1c6afefe8af05447f81d41ad8e3d353c0d81d8d3`, a local commit that makes the window layout the default and removes its environment variable. Its tree is identical to `fb4015b5bd`, the head of radixark/sglang-zai pull request 67.
- Working tree: clean archive of the commit.
- Status: preview, non-release; the image digest is not recorded.

## Scripts

- Version: round-specific [`attrib.sh`](attrib.sh), [`stress.py`](stress.py) and [`stress-think.py`](stress-think.py).
- Temporary changes: none. `stress-think.py` is `stress.py` with `enable_thinking` true and `max_tokens=4096`.

## Workload

- Salted stress: record documents with a per-request salt, one random record per request, greedy. 12 requests each at 60000 and 110000 target tokens (64.7K and about 120.9K prompt tokens), 2 concurrent. The salt tag is the same as in E11, so every arm sees the same 24 prompts.
- Thinking off ([`stress.py`](stress.py)): `max_tokens=64`. Thinking on ([`stress-think.py`](stress-think.py)): `max_tokens=4096`.
- A request counts when it ends with `stop` and the answer contains the expected code.
- On `dep8-bf16` the thinking-on set ran after the thinking-off set on the same server; 12 of its 24 requests reported cached prefix tokens. The other arms reported none.

## Results

Each cell is correct / wrong code with `stop` / not `stop`, of 12.

| Arm | Thinking | 60K | 120.9K |
|---|---|---|---|
| DEP8, `trtllm`, FP8 KV (E11 `new-window`) | off | 7 / 0 / 5 | 7 / 4 / 1 |
| `dep8-bf16` | off | 8 / 2 / 2 | 7 / 5 / 0 |
| `tp8-bf16` | off | 10 / 0 / 2 | 6 / 4 / 2 |
| `dep8-fp8-think` | on | 10 / 2 / 0 | 8 / 4 / 0 |
| `dep8-bf16` | on | 9 / 3 / 0 | 8 / 4 / 0 |
| `tp8-bf16` | on | 10 / 2 / 0 | 9 / 3 / 0 |

No traceback was logged on any arm. Window pools: `dep8-bf16` full_layer_tokens=1367744, swa_layer_tokens=136768; `dep8-fp8-think` full_layer_tokens=2656064, swa_layer_tokens=265600; `tp8-bf16` full_layer_tokens=1195520, swa_layer_tokens=119552.

Conclusions:

1. Every arm misses: 6 to 10 of 12 prompts (50–83%) are answered correctly at 60K and at 120.9K tokens, with BF16 or FP8 KV, on DEP8 with `trtllm` or TP8 with `flashmla_sparse`, with thinking on or off.
2. FP8 KV, attention DP with expert parallelism, and the `trtllm` DSA backend are not the cause: the TP8 BF16 `flashmla_sparse` arm misses at the same rate.
3. Thinking on removes the "not `stop`" class (requests that open with reasoning and hit `max_tokens=64`) and leaves the wrong-code answers: 2 to 4 of 12 per cell.
4. Together with E11, no serving configuration tested changes the miss rate. The project owner's working assessment is that the misses reflect the checkpoint's own retrieval limit at these lengths. This has not been compared against a reference implementation, and the observation is treated as non-blocking.
5. Each cell has 12 requests; differences of one or two requests between arms are not significant.

## Data and Figures

- [`dep8-bf16/`](dep8-bf16/), [`tp8-bf16/`](tp8-bf16/), [`dep8-fp8-think/`](dep8-fp8-think/) — launch script, compressed server log, `long.jsonl` (thinking off) and `think.jsonl` (thinking on) request rows and their console logs.
- `status`, `attrib.out` — driver status and console.
- [`summary.json`](summary.json) — per-file tallies recomputed from the committed files by [`summarize_round.py`](../../scripts/v2/summarize_round.py). The split of misses into wrong code and not `stop` is counted from the `finish` and `correct` fields of the request rows.
- [`evidence-hashes.json`](evidence-hashes.json) — original path and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
