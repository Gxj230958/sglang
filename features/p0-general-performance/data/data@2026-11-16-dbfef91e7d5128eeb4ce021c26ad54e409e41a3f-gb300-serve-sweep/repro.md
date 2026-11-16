# E03 GB300 serving-configuration sweep: TP4 and DEP4, KV dtype, DSA route, MTP and KV layout — data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-gb300-serve-sweep

## Environment

- Machine: one node with 4× NVIDIA GB300 (284,208 MiB each, driver 580.178.04), rank 0 of a two-rank allocation. The second rank ran another workload during the sweep.
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, node-local copy, the same files as target and MTP draft. [`preflight.txt`](preflight.txt) records the SHA-256 of `config.json`, `tokenizer.json`, `tokenizer_config.json` and `model.safetensors.index.json` and the shard total (756,945,709,348 bytes); the weight shards were not hashed and the repository revision was not recorded.
- Software ([`dependencies.txt`](dependencies.txt)): torch 2.14.1+cu130, transformers 5.19.0, flashinfer-python 0.7.3, flashinfer-cubin 0.7.3, flashinfer-jit-cache 0.7.3+cu130, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1, supplied by `PYTHONPATH` overlays in front of the source tree. The code pins `flashinfer_python[cu13]==0.7.4`; this sweep ran on 0.7.3. `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`, `CUDA_VISIBLE_DEVICES=0,1,2,3`.

## Setup

[`contract.md`](contract.md) is the measurement contract written before the sweep. [`serve_sweep.py`](serve_sweep.py) reads [`focused.json`](focused.json): per candidate it checks that the four GPUs hold at most 1,000 MiB each, launches the server, runs three sanity chats ([`sanity.py`](sanity.py)), then for each concurrency level and repeat flushes the cache, runs one warmup conversation and the measured batch through [`load_adapter.py`](load_adapter.py), and stops the server before the next candidate.

- Common launch flags: `--mem-fraction-static 0.80 --context-length 32768 --max-running-requests 64 --cuda-graph-max-bs-decode 64 --disable-prefill-cuda-graph --chunked-prefill-size 8192 --enable-fp32-lm-head --reasoning-parser glm45 --tool-call-parser glm47 --enable-cache-report --enable-metrics`.
- MTP, where enabled: `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model>`.
- Candidates (the recorded argv of each is in `focused/candidates/<name>/replica-0.process.json`; the resolved settings in its `get_server_info.txt` and server log match the request):

| Candidate | Parallelism and MoE runner | DSA routes | KV dtype | MTP | KV layout |
|---|---|---|---|---|---|
| `tp4-default-mtp` | `--tp-size 4 --moe-runner-backend deep_gemm` | `flashmla_sparse` | BF16 | on | window (default) |
| `tp4-default` | same | `flashmla_sparse` | BF16 | off | window |
| `tp4-trt-bf16-mtp` | same | `trtllm` | BF16 | on | window |
| `tp4-trt-fp8-mtp` | same | `trtllm` | FP8 | on | window |
| `dep4-trt-fp8-mtp` | `--tp-size 4 --ep-size 4 --attn-dp-size 4 --moe-runner-backend flashinfer_trtllm --moe-a2a-backend none` | `trtllm` | FP8 | on | window |
| `dep4-trt-fp8` | same | `trtllm` | FP8 | off | window |
| `dep4-trt-fp8-mtp-full` | same | `trtllm` | FP8 | on | full-length (`--disable-hybrid-swa-memory`) |
| `tp4-default-mtp-full` | `--tp-size 4 --moe-runner-backend deep_gemm` | `flashmla_sparse` | BF16 | on | full-length |

- Timeline (UTC, server logs): the eight candidates ran one after the other in the table order between 00:47:29 and 02:46:47, one server launch each.
- A first run with levels 1 / 8 / 32 / 64 completed only `tp4-default-mtp` (level 1 passed; P90 interactivity 98.6 / 16.3 / 6.3 / 4.1 tokens/s). The grid was then changed to 1 / 2 / 4 / 8 for all candidates in a fresh run, recorded in `contract.md` before that run; the first run is kept in [`coarse-run1.tar.gz`](coarse-run1.tar.gz) and is not mixed into the results below.

## Commit

- Code commit: `dbfef91e7d5128eeb4ce021c26ad54e409e41a3f`, the tip of `glm-5-lp`.
- Working tree: `git archive` of the commit; [`source-hashes.txt`](source-hashes.txt) records the archive digest, and [`accounting-check.txt`](accounting-check.txt) the digests of the runner, `pyproject.toml` and the benchmark client on the node. The tree was not verified file by file.
- Status: non-release. One server launch per candidate, two load repeats per level, no accuracy evaluation, FlashInfer 0.7.3 instead of the pinned 0.7.4, image digest not recorded.

## Scripts

- Version: round-specific [`serve_sweep.py`](serve_sweep.py), [`load_adapter.py`](load_adapter.py), [`sanity.py`](sanity.py), [`make_workload.py`](make_workload.py), [`make_config.py`](make_config.py). The tables below are recomputed from the per-repeat results by [`summarize_sweep.py`](summarize_sweep.py) into [`summary.json`](summary.json).
- Temporary changes: none to the served code.

## Workload

- Source: a synthetic service-debugging chat fixture generated for this round ([`make_workload.py`](make_workload.py), [`workload.json.gz`](workload.json.gz), token lengths in [`workload-lengths.json`](workload-lengths.json)), replayed by the `agentic-trace` multi-turn client of `sglang.benchmark` at the measured commit.
- Shape: 4 turns per conversation; 2,427 input tokens on the first turn, about 640 new user tokens per later turn, up to about 4,754 input tokens on turn 4. The full history, including the generated replies, is resent every turn.
- Output: 128 tokens per turn with `ignore_eos`; temperature 1.0, top_p 0.95; thinking disabled; request seed = repeat index.
- Load: closed loop without think time at concurrency 1, 2, 4 and 8; 16 conversations × 4 turns = 64 requests per run; 2 repeats per level; cache flushed before each run, then one warmup conversation. A finite batch, not a fixed-duration run and not a replay of production agentic traces.
- Sanity: three short chats per candidate, `max_tokens` 1024, natural stop, thinking disabled.
- SLO: P90 TTFT ≤ 3 s, P90 interactivity ≥ 30 tokens/s (1000 / P90 inter-token latency in ms, as reported by the client, which retokenizes streamed chunks when MTP delivers several tokens at once), every request successful and non-empty. A level passes when both repeats pass.
- Score: (input tokens including resent and cached ones + output tokens) / duration / 4 GPUs. Output tokens/s is for the whole node.

## Results

Median of the two repeats per point:

| Candidate | Concurrency | Total tokens/s per GPU | Output tokens/s | P90 TTFT (s) | P90 interactivity (tokens/s) | Cache reuse | SLO |
|---|---:|---:|---:|---:|---:|---:|---|
| `tp4-default-mtp` | 1 | 681.4 | 93.8 | 0.354 | 98.9 | 78.0% | pass |
| `tp4-default-mtp` | 2 | 1009.3 | 139.0 | 0.366 | 71.8 | 77.2% | pass |
| `tp4-default-mtp` | 4 | 1382.7 | 190.4 | 0.642 | 35.0 | 75.0% | pass |
| `tp4-default-mtp` | 8 | 1801.7 | 248.1 | 1.153 | 14.5 | 74.5% | fail |
| `tp4-default` | 1 | 406.1 | 55.9 | 0.331 | 64.1 | 77.5% | pass |
| `tp4-default` | 2 | 689.7 | 95.0 | 0.630 | 59.5 | 76.5% | pass |
| `tp4-default` | 4 | 1211.2 | 166.8 | 0.684 | 51.5 | 73.4% | pass |
| `tp4-default` | 8 | 2060.1 | 283.7 | 0.913 | 43.1 | 74.2% | pass |
| `tp4-trt-bf16-mtp` | 1 | 679.4 | 93.6 | 0.366 | 98.1 | 78.1% | pass |
| `tp4-trt-bf16-mtp` | 2 | 1022.3 | 140.8 | 0.437 | 81.0 | 76.8% | pass |
| `tp4-trt-bf16-mtp` | 4 | 1341.8 | 184.8 | 0.689 | 34.7 | 75.8% | pass |
| `tp4-trt-bf16-mtp` | 8 | 1763.6 | 242.9 | 1.141 | 18.7 | 73.9% | fail |
| `tp4-trt-fp8-mtp` | 1 | 646.2 | 89.0 | 0.372 | 95.3 | 78.1% | pass |
| `tp4-trt-fp8-mtp` | 2 | 946.6 | 130.3 | 0.521 | 48.4 | 77.2% | pass |
| `tp4-trt-fp8-mtp` | 4 | 1345.1 | 185.2 | 0.682 | 34.4 | 75.5% | pass |
| `tp4-trt-fp8-mtp` | 8 | 1797.4 | 247.5 | 1.052 | 17.8 | 74.3% | fail |
| `dep4-trt-fp8-mtp` | 1 | 491.8 | 67.7 | 0.891 | 83.6 | 42.1% | pass |
| `dep4-trt-fp8-mtp` | 2 | 757.0 | 104.2 | 0.914 | 38.2 | 53.2% | pass |
| `dep4-trt-fp8-mtp` | 4 | 1050.1 | 144.6 | 1.217 | 32.1 | 61.5% | pass |
| `dep4-trt-fp8-mtp` | 8 | 1321.2 | 181.9 | 1.274 | 10.8 | 54.9% | fail |
| `dep4-trt-fp8` | 1 | 298.1 | 41.1 | 0.806 | 49.9 | 42.1% | pass |
| `dep4-trt-fp8` | 2 | 549.9 | 75.7 | 0.893 | 49.2 | 57.4% | pass |
| `dep4-trt-fp8` | 4 | 985.9 | 135.8 | 1.268 | 49.0 | 64.7% | pass |
| `dep4-trt-fp8` | 8 | 1735.4 | 239.0 | 1.615 | 40.7 | 54.2% | pass |
| `dep4-trt-fp8-mtp-full` | 1 | 497.4 | 68.5 | 0.850 | 83.9 | 45.1% | pass |
| `dep4-trt-fp8-mtp-full` | 2 | 791.7 | 109.0 | 0.831 | 38.6 | 57.5% | pass |
| `dep4-trt-fp8-mtp-full` | 4 | 1072.3 | 147.7 | 0.983 | 32.5 | 65.4% | pass |
| `dep4-trt-fp8-mtp-full` | 8 | 1344.9 | 185.2 | 1.188 | 11.2 | 58.0% | fail |
| `tp4-default-mtp-full` | 1 | 672.0 | 92.5 | 0.355 | 96.9 | 78.9% | pass |
| `tp4-default-mtp-full` | 2 | 1012.8 | 139.5 | 0.497 | 79.5 | 78.1% | pass |
| `tp4-default-mtp-full` | 4 | 1390.3 | 191.4 | 0.644 | 35.2 | 76.6% | pass |
| `tp4-default-mtp-full` | 8 | 1842.2 | 253.7 | 1.049 | 19.7 | 76.1% | fail |

Best passing point per candidate and KV pool:

| Candidate | Best passing concurrency | Repeat 1 | Repeat 2 | Median | Full-length KV tokens | Window KV tokens |
|---|---:|---:|---:|---:|---:|---:|
| `tp4-default-mtp` | 4 | 1396.9 | 1368.6 | 1382.7 | 422,400 | 42,240 |
| `tp4-default` | 8 | 2060.4 | 2059.7 | 2060.1 | 460,480 | 46,016 |
| `tp4-trt-bf16-mtp` | 4 | 1346.7 | 1336.9 | 1341.8 | 422,400 | 42,240 |
| `tp4-trt-fp8-mtp` | 4 | 1316.5 | 1373.7 | 1345.1 | 820,352 | 81,984 |
| `dep4-trt-fp8-mtp` | 4 | 1086.9 | 1013.3 | 1050.1 | 443,264 | 44,288 |
| `dep4-trt-fp8` | 8 | 1731.9 | 1739.0 | 1735.4 | 537,216 | 53,696 |
| `dep4-trt-fp8-mtp-full` | 4 | 1040.8 | 1103.8 | 1072.3 | 343,552 | full-length layout |
| `tp4-default-mtp-full` | 4 | 1395.3 | 1385.3 | 1390.3 | 325,184 | full-length layout |

- All 4,096 load requests (8 candidates × 4 levels × 2 repeats × 64) succeeded with non-empty replies; all 24 sanity replies ended with `stop`. No server log holds a traceback or a CUDA out-of-memory error.
- Every SLO failure is the interactivity gate; P90 TTFT stays below 1.7 s at every point.
- Accept length reported by the client for the MTP candidates is between 2.37 and 2.56 at the passing levels ([`focused/report.json`](focused/report.json)).

Conclusions:

1. On this workload and grid the highest passing score is `tp4-default` (TP4, BF16 KV, `flashmla_sparse`, MTP off) at concurrency 8: 2060.1 total tokens/s per GPU, 283.7 output tokens/s, P90 TTFT 0.913 s, P90 interactivity 43.1 tokens/s. Its two repeats (2059.7, 2060.4) do not overlap those of the next candidate, `dep4-trt-fp8` at concurrency 8 (1731.9, 1739.0), and its median is 18.7% higher. Concurrency 8 is the highest level tested and both MTP-off candidates still pass there, so their limit was not reached.
2. MTP raises output throughput at low concurrency and lowers it at concurrency 8: at TP4 with the default routes, 93.8 against 55.9 output tokens/s at concurrency 1 and 248.1 against 283.7 at concurrency 8, where the MTP candidates fall to 10.8–19.7 tokens/s P90 interactivity and fail the gate. Every MTP candidate passes up to concurrency 4.
3. At equal settings TP4 is ahead of DEP4 on this workload: `tp4-trt-fp8-mtp` against `dep4-trt-fp8-mtp` gives 1345.1 against 1050.1 total tokens/s per GPU at concurrency 4 and P90 TTFT 0.37 s against 0.89 s at concurrency 1. Cache reuse is 73–79% at TP4 and 42–65% at DEP4 under the server's own attention-DP request placement.
4. At TP4 with MTP, the `trtllm` routes with FP8 KV score within 3% of the `flashmla_sparse` and `trtllm` BF16 candidates at concurrency 4 (1345.1 against 1382.7 and 1341.8) and hold 820,352 full-length KV tokens against 422,400.
5. The window and full-length layouts score within 4.4% of each other at every passing level (TP4: within 1.4%, 1382.7 against 1390.3 at concurrency 4; DEP4: 757.0 against 791.7 at concurrency 2 and 1050.1 against 1072.3 at concurrency 4); the window layout holds 30% (TP4) and 29% (DEP4) more full-length tokens.

Limits of these results:

- One narrow synthetic workload: inputs up to about 4.7K tokens, 128 output tokens per turn, thinking off, `ignore_eos`. Long contexts, long outputs and thinking are not covered.
- Concurrency up to 8 only; 64 requests per run.
- FlashInfer 0.7.3; performance on the pinned 0.7.4 is not measured here.
- One server launch per candidate in a fixed order; launch-to-launch variation is not measured.
- Exclusive use of the GPUs during the measurements is not verified: the idle-memory check passed before every launch and the KV pool sizes are consistent, but no continuous GPU process record was kept and GPU accounting is disabled on the devices.
- No accuracy evaluation; the three sanity chats per candidate only check that replies are sensible and stop.
- The TP4 candidates pass `--moe-runner-backend deep_gemm`; TP4 with the default MoE runner was not measured.

## Data and Figures

- [`contract.md`](contract.md) — the measurement contract and the grid change, written before the runs.
- [`focused.json`](focused.json), [`focused-plan.json`](focused-plan.json), [`sweep.json`](sweep.json), [`plan.json`](plan.json), [`smoke.json`](smoke.json) — runner configurations and resolved plans of the measured run, the first run and the smoke run.
- [`focused/`](focused/) — the measured run: `config.json`, the runner's `report.json` / `report.md`, and per candidate under `candidates/<name>/`: `replica-0.process.json` (argv and environment), compressed server log, `get_server_info.txt`, compressed `/metrics`, sanity requests and result, `result.json`, and `levels.tar.gz` with `level-<N>/repeat-<R>/` (client command, per-request records, load log, `/metrics`, server info, `result.json`, `summary.json`).
- [`coarse-run1.tar.gz`](coarse-run1.tar.gz), [`smoke.tar.gz`](smoke.tar.gz) — the first run (levels 1 / 8 / 32 / 64, one candidate) and the smoke run.
- [`preflight.txt`](preflight.txt), [`dependencies.txt`](dependencies.txt), [`source-hashes.txt`](source-hashes.txt), [`accounting-check.txt`](accounting-check.txt), [`audit.txt`](audit.txt), [`audit.json`](audit.json), [`workload-generation.txt`](workload-generation.txt) — environment, identity and post-run audit records.
- [`recommended-serve.sh`](recommended-serve.sh) — the launch command of `tp4-default` as recorded.
- [`summary.json`](summary.json) — per candidate and level: medians, per-repeat scores, gate outcome, request counts, pool sizes and traceback counts recomputed from the committed files.
- [`evidence-hashes.json`](evidence-hashes.json) — original location and SHA-256 of every captured file, taken before compression; archives are hashed as their uncompressed tar stream and generated files as committed.
