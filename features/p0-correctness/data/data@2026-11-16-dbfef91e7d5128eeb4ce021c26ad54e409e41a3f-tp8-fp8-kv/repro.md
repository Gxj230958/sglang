# E17 TP8 with FP8 KV: GSM8K gate and serving speed against BF16 KV — data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-tp8-fp8-kv

## Environment

- Machine: one node with 8× NVIDIA B300, the B300 node of [E15](../data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-flashinfer-074-h200/repro.md).
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, served from the node-local copy hashed in E15 (`b300/checkpoint.sha256` there); the checkpoint's own NextN head is the MTP draft.
- Software: the E15 overlay in front of the same source tree and image for both arms: flashinfer-python 0.7.4, flashinfer-cubin 0.7.4, flashinfer-jit-cache 0.7.4+cu130, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1, sgl-eval 0.1.3 (versions as recorded in E15; this round did not write an import record). `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.

## Setup

[`run.sh`](run.sh) runs the two arms one after the other on the same node. Per arm it checks that every GPU is idle, writes `launch.sh`, starts the server, waits for `/health`, runs the serving benchmark (three workloads, seeds 1 and 2), and stops the server. On `tp8-fp8` it then runs GSM8K against the same server process before stopping it, storing the `sglang:generation_tokens_total` and `sglang:spec_verify_calls_total` lines of `/metrics` before and after.

- Common launch flags ([`tp8-fp8/launch.sh`](tp8-fp8/launch.sh), [`tp8-bf16/launch.sh`](tp8-bf16/launch.sh)): `--tp-size 8 --mem-fraction-static 0.75 --context-length 65536 --chunked-prefill-size 32768 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model> --enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47 --enable-metrics`. These are the `b300-tp8` flags of E15; the window layout is the default.
- `tp8-fp8` adds `--dsa-prefill-backend trtllm --dsa-decode-backend trtllm --kv-cache-dtype fp8_e4m3`.
- `tp8-bf16` adds nothing.
- Resolved settings, from the `server_args` line of each server log: `tp8-fp8` runs `kv_cache_dtype='fp8_e4m3'`, `dsa_prefill_backend='trtllm'`, `dsa_decode_backend='trtllm'`; `tp8-bf16` runs `kv_cache_dtype='bfloat16'`, `dsa_prefill_backend='flashmla_sparse'`, `dsa_decode_backend='flashmla_sparse'`. Both resolve `moe_runner_backend='flashinfer_trtllm'`, `tp_size=8` and attention TP 8.
- Timeline (UTC, [`status`](status) and the server logs): `tp8-fp8` server 06:50:13–07:18:02 (benchmarks 06:54:55–06:59:59, GSM8K 07:00:00–07:18:01), `tp8-bf16` server 07:18:47–07:28:44.

## Commit

- Code commit: `dbfef91e7d5128eeb4ce021c26ad54e409e41a3f`, the tip of `glm-5-lp`.
- Working tree: the `git archive` tree deployed and verified file by file in E15 (`b300/source-verify.json` there). It was not re-verified before this round.
- Status: non-release. One server launch per arm in a fixed order, one unseeded GSM8K run, image digest not recorded.

## Scripts

- Version: round-specific [`run.sh`](run.sh). Numbers are recomputed by [`summarize_round.py`](../../scripts/v2/summarize_round.py); the counter ratio is computed from the two `*.metrics` files as described under Results.
- Temporary changes: none to the served code.

## Workload

- GSM8K (`tp8-fp8` only): full test split (1319 questions) through `sgl-eval run gsm8k --base-url <server>/v1 --temperature 1.0 --top-p 0.95`, 64 client threads, server-default thinking, no `max_tokens`, no seed.
- Serving benchmark (both arms): `sglang.bench_serving --backend sglang --dataset-name random-ids --random-range-ratio 1 --flush-cache --warmup-requests 2`, seeds 1 and 2.
  - `short-c1`: 2000 input / 500 output tokens, 16 prompts, concurrency 1.
  - `short-c32`: 2000 / 500, 128 prompts, concurrency 32.
  - `long-c4`: 30000 / 300, 16 prompts, concurrency 4.

## Results

GSM8K on `tp8-fp8`:

| Arm | Accuracy | Stop rate | Truncated | Errors | Accept len (counters) | Accept len (log lines) | Completion tokens |
|---|---|---|---|---|---|---|---|
| `tp8-fp8` | 95.07% (1254/1319) | 99.77% (1316/1319) | 3 | 0 | 2.6320 | 2.6505 (780 lines) | 959,597 |

- Accept len (counters) is the ratio of the `sglang:generation_tokens_total` delta to the `sglang:spec_verify_calls_total` delta between `before-t1.metrics` and `after-t1.metrics`: 959597 / 364591. The generation-token delta equals `total_completion_tokens` in `metrics.json`.
- Accept len (log lines) is the unweighted mean of the `accept len` field over the `Decode batch` lines logged while the run was in flight (`accept_len_during_run` in [`summary.json`](summary.json)).
- Truncated counts requests that ended with `finish_reason=length`: questions 675, 1074 and 1176, which generated 65,396, 65,462 and 65,353 tokens, that is, ran until the 65,536-token context was full.
- For reference, the BF16 gate with the same common flags, node, head and overlay is the `b300-tp8` leg of E15 (96.06%, 100% stop, counters 2.6577) and the `fi074` arm of [E16](../data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-flashinfer-073-074-accept-length/repro.md) (95.07%, 99.92% stop with question 1074 truncated, counters 2.6423).

Serving speed, seed 1 / seed 2:

| Workload | Metric | `tp8-fp8` | `tp8-bf16` |
|---|---|---|---|
| `short-c1` | Output tokens/s | 211.3 / 220.3 | 231.8 / 234.7 |
| `short-c1` | Median TTFT (ms) | 329 / 341 | 327 / 323 |
| `short-c1` | Mean TPOT (ms) | 4.06 / 3.86 | 3.66 / 3.61 |
| `short-c1` | Accept length | 2.94 / 3.07 | 3.07 / 3.11 |
| `short-c32` | Output tokens/s | 1203.8 / 1215.2 | 1125.4 / 1193.5 |
| `short-c32` | Median TTFT (ms) | 410 / 635 | 655 / 601 |
| `short-c32` | Mean TPOT (ms) | 23.47 / 23.43 | 25.30 / 23.10 |
| `short-c32` | Accept length | 2.88 / 2.88 | 2.94 / 2.99 |
| `long-c4` | Output tokens/s | 145.2 / 144.2 | 128.9 / 127.6 |
| `long-c4` | Median TTFT (ms) | 2711 / 2955 | 3669 / 3272 |
| `long-c4` | Mean TPOT (ms) | 16.69 / 17.67 | 16.84 / 18.61 |
| `long-c4` | Accept length | 2.65 / 2.56 | 2.81 / 2.61 |

- Every benchmark run completed all its requests (16, 128 and 16).
- KV pool: `tp8-fp8` `full_layer_tokens=2321664, swa_layer_tokens=232128`; `tp8-bf16` `full_layer_tokens=1195520, swa_layer_tokens=119552`.
- Both arms: every `Decode batch` line with `cuda graph: True`, no traceback, no KV retraction, server healthy after the last run.

Conclusions:

1. TP8 with FP8 KV and the `trtllm` DSA routes launches on the merged head and completes full GSM8K with MTP at 95.07% accuracy and 99.77% stop rate; 3 of 1319 requests ran until the context was full. The BF16 runs of E15 and E16 on the same head had 0 and 1 such requests; with single unseeded runs the difference is not attributed to the KV dtype or the DSA route.
2. The counter-based MTP accept length during GSM8K is 2.6320, against 2.6577 and 2.6423 in the BF16 runs of E15 and E16.
3. Under the same `--mem-fraction-static 0.75`, the FP8 arm holds 1.94× the full-length KV tokens of the BF16 arm (2,321,664 against 1,195,520).
4. In this one launch per arm, output throughput of the FP8 arm is 6–9% lower at concurrency 1 (211.3 / 220.3 against 231.8 / 234.7 tokens/s), 2–7% higher at concurrency 32 (1203.8 / 1215.2 against 1125.4 / 1193.5) and 13% higher on 30K-token inputs at concurrency 4 (145.2 / 144.2 against 128.9 / 127.6), where median TTFT is 10–26% lower. The arms differ in both the KV dtype and the DSA backend, so the differences are not attributed to either one.

Not covered: FP8 KV on the `flashmla_sparse` routes or BF16 KV on the `trtllm` routes at TP8; a BF16 GSM8K run in this round; more seeds or launches; alternating the order of the arms; re-verifying the source tree and recording package versions for this round; long-context retrieval probes; H200 and GB300.

## Data and Figures

- [`run.sh`](run.sh), [`status`](status) — the driver and its progress log (times in UTC).
- [`tp8-fp8/`](tp8-fp8/), [`tp8-bf16/`](tp8-bf16/) — per arm: `launch.sh`, compressed `serve.log`, and per benchmark run the `bench_serving` result (`<workload>-s<seed>.jsonl`) and client log. `tp8-fp8/` also holds compressed `gsm8k-t1.log`, the two `*.metrics` counter snapshots and the sgl-eval output under `eval-t1/` (`metrics.json`, compressed `output-rs0.jsonl`).
- [`summary.json`](summary.json) — sgl-eval aggregates, finish reasons, log-line accept length, benchmark metrics, pool sizes and traceback counts recomputed from the committed files.
- [`evidence-hashes.json`](evidence-hashes.json) — original location and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
- `.gitattributes` — exempts the captured client logs and `launch.sh` files, kept byte for byte, from the whitespace check.
