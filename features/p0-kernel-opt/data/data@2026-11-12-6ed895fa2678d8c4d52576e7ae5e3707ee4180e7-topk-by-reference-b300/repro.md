# E03 Top-K anchors by reference on B300: equivalence, serving and memory — data@2026-11-12-6ed895fa2678d8c4d52576e7ae5e3707ee4180e7-topk-by-reference-b300

## Environment

- Machine: one node with 8× NVIDIA B300.
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`, served from a node-local copy; the checkpoint's own NextN head is the MTP draft. The copy was not re-hashed for this round.
- Software: image torch 2.14.1+cu130, transformers 5.19.0, sglang-kernel 0.4.10; an overlay on `PYTHONPATH` adds flashinfer-python / cubin / jit-cache 0.7.3, sgl-deep-gemm 0.2.7 and sgl-flash-mla 1.0.4; `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.

## Setup

Deploy three trees with `git archive`: base `710bcb2a3e`, candidate `6ed895fa26` ("clean") and the original four-part pull request rebased onto the base, `4e49978395` ("full"). [`harness/driver.sh`](harness/driver.sh) runs the job lists [`harness/jobs1.txt`](harness/jobs1.txt) to [`harness/jobs3.txt`](harness/jobs3.txt) through [`harness/job.sh`](harness/job.sh), one cold server start per job, arms alternated between rounds. All servers use `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model>`.

- `tp8` (jobs `r*`, `v-tp8`): `--tp-size 8 --mem-fraction-static 0.75 --context-length 65536 --chunked-prefill-size 32768 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph`, `flashmla_sparse`, BF16 KV.
- `dep8` (jobs `d*`, `v-dep8`): `--tp-size 8 --ep-size 8 --attn-dp-size 8 --moe-runner-backend flashinfer_trtllm --moe-a2a-backend none --dsa-prefill-backend trtllm --dsa-decode-backend trtllm --kv-cache-dtype fp8_e4m3 --context-length 147456 --mem-fraction-static 0.88 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --chunked-prefill-size 65536 --enable-fp32-lm-head`.

The `v-*` jobs run the base tree with an instrumentation that compares the backend's Top-K tensor with its clone at every later-cycle read; the instrumentation is loaded from [`harness/sitecustomize.py`](harness/sitecustomize.py) and is not part of any commit.

## Commit

- Code commit: `6ed895fa2678d8c4d52576e7ae5e3707ee4180e7`, radixark/sglang-zai pull request 43 reduced to holding the cycle-0 Top-K anchors by reference (2 files, +17/-28).
- Baseline: `710bcb2a3e6e4abbc299b43860c6528f7bd81db8`. Comparison arm: `4e49978395f810c702d42b9e3856143d6c336393`.
- Working tree: clean archives.
- The change was rebased as `802d8157b7`, gated in [Correctness E07](../../../p0-correctness/data/data@2026-11-13-802d8157b74564997e350ffa981b5e567e391920-topk-by-reference-gate/repro.md) and merged as `8f5dff0f45`.
- Status: non-release. The image digest is not recorded and dependencies come from `PYTHONPATH` overlays, so the environment is not locked.

## Scripts

- Version: round-specific harness under [`harness/`](harness/); [`perf_summary.py`](perf_summary.py) recomputes the tables below.
- Temporary changes: the round-1 `bench_serving` step failed on every arm because the benchmark's dataset download hit a read-only cache; the cache path was moved and round 4 replaces that step.

## Workload

- GSM8K: full test split (1319 questions) through `sgl-eval` 0.1.3, `sgl-eval run gsm8k --base-url <server>/v1 --temperature 1.0 --top-p 0.95`, 64 client threads, server-default thinking, no `max_tokens`, one run per configuration. 300 questions on the `v-*` jobs.
- `bench_serving --flush-cache --seed <round>`: serve = 2000 input / 256 output tokens, 96 prompts, concurrency 16; decode = 200 input / 512 output tokens, 48 prompts, concurrency 8.
- Long prefill ([`harness/longprefill.py`](harness/longprefill.py)): single request with `max_tokens=1`, six repetitions per length (8192, 32000, and 120000 on `dep8`); memory is the allocator peak of the rank on GPU 0, sampled per epoch.
- Pre-checks ([`logs/pre/`](logs/pre/)): kernel and unit tests, a Top-K ownership probe over ten producers, and a microbenchmark of the clone.

## Results

Whole-model equivalence (base tree plus the compare instrumentation):

| Config | Ranks | Checks per rank | Mismatches | GSM8K 300 | Stop rate | Accept len |
|---|---|---|---|---|---|---|
| `tp8` | 8 | 197260 | 0 | 93.67% (281/300) | 99.33% | 2.64 |
| `dep8` | 8 | 124635–124663 | 0 | 94.33% (283/300) | 100.00% | 2.52 |

GSM8K, full 1319:

| Job | Accuracy | Stop rate | Truncated | Errors | Accept len |
|---|---|---|---|---|---|
| `r1-base` (`tp8`) | 95.00% (1253/1319) | 99.92% | 1 | 0% | 2.60 |
| `r1-clean` (`tp8`) | 95.30% (1257/1319) | 99.92% | 1 | 0% | 2.60 |
| `d1-base` (`dep8`) | 94.92% (1252/1319) | 100.00% | 0 | 0% | 2.61 |
| `d1-clean` (`dep8`) | 94.84% (1251/1319) | 99.92% | 1 | 0% | 2.67 |
| `d3-base` (`dep8`) | 96.06% (1267/1319) | 99.92% | 1 | 0% | 2.86 |
| `d3-clean` (`dep8`) | 95.15% (1255/1319) | 99.85% | 2 | 0% | 2.75 |

`tp8` serving and memory (MiB, max allocated / max reserved at 32K rows):

| Job | Serve tok/s | Serve mean TTFT ms | Serve mean ITL ms | Decode tok/s | Decode mean ITL ms | Prefill 8192 median s | Prefill 32000 median / min s | Memory |
|---|---|---|---|---|---|---|---|---|
| `r2-base` | 624.47 | 628.0 | 22.58 | 604.84 | 12.16 | 0.5423 | 1.9066 / 1.9050 | 210126 / 214824 |
| `r2-full` | 598.69 | 635.8 | 23.65 | 607.30 | 12.14 | 0.5433 | 1.9569 / 1.9150 | 210126 / 212834 |
| `r2-clean` | 623.57 | 605.3 | 22.78 | 610.66 | 11.97 | 0.5428 | 1.9066 / 1.9036 | 210126 / 214828 |
| `r3-base` | 607.08 | 632.9 | 23.48 | 586.50 | 12.61 | 0.5418 | 1.9095 / 1.9043 | 210126 / 214826 |
| `r3-full` | 604.82 | 610.2 | 23.67 | 588.94 | 12.52 | 0.5470 | 1.9164 / 1.9090 | 210126 / 212834 |
| `r3-clean` | 608.78 | 603.9 | 23.45 | 584.84 | 12.71 | 0.5464 | 1.9091 / 1.9072 | 210126 / 214826 |
| `r4-base` | 626.53 | 662.6 | 22.58 | 581.56 | 12.67 | 0.5432 | 1.9092 / 1.9049 | 210126 / 214826 |
| `r4-full` | 616.75 | 637.0 | 23.07 | 586.78 | 12.51 | 0.5443 | 1.9142 / 1.9087 | 210126 / 212838 |
| `r4-clean` | 617.46 | 613.2 | 23.00 | 591.93 | 12.42 | 0.5424 | 1.9075 / 1.9034 | 210126 / 214826 |

Means over rounds 2–4: serve 619.4 / 606.8 / 616.6 tok/s (base / full / clean); decode 591.0 / 594.3 / 595.8 tok/s; 32000-row prefill median 1.9084 / 1.9292 / 1.9077 s.

`dep8` serving and memory (MiB, max allocated / max reserved at 120K rows):

| Job | Serve tok/s | Decode tok/s | Prefill 32000 median s | Prefill 120000 median / min s | Memory |
|---|---|---|---|---|---|
| `d1-base` | 523.36 | 489.05 | 2.1401 | 8.5776 / 8.5312 | 236682 / 262060 |
| `d1-full` | 528.55 | 496.11 | 2.1625 | 8.6680 / 8.6215 | 236682 / 261422 |
| `d1-clean` | 530.29 | 494.42 | 2.1410 | 8.5953 / 8.5238 | 236682 / 261934 |
| `d2-base` | 538.68 | 515.95 | 2.1877 | 8.5867 / 8.5297 | 236682 / 262060 |
| `d2-full` | 531.71 | 517.41 | 2.1630 | 8.6489 / 8.6033 | 236682 / 261422 |
| `d2-clean` | 519.65 | 518.80 | 2.1554 | 8.5859 / 8.5139 | 236682 / 261934 |

Conclusions:

1. Holding the Top-K anchors by reference is equivalent to cloning them: zero mismatches at every later-cycle read on all eight ranks of both configurations.
2. Base and candidate are indistinguishable on serving throughput, TTFT, ITL, long-prefill latency and allocator peaks; the spread between rounds is larger than any difference between these two arms. The change is a code simplification only.
3. The other three parts of the original pull request leave the allocated peak unchanged, lower the reserved peak by about 1990 MiB at 32K rows on `tp8` and about 640 MiB at 120K rows on `dep8`, and make long prefill slower (32000 rows on `tp8` in every round, 120000 rows on `dep8` in both). They were dropped.
4. On `dep8` the candidate truncated 3 of 2638 GSM8K requests against 1 of 2638 for the base. The merge decision used a further two-run comparison on the rebased commit, where both arms truncated 3 of 2638 ([Correctness E07](../../../p0-correctness/data/data@2026-11-13-802d8157b74564997e350ffa981b5e567e391920-topk-by-reference-gate/repro.md)).

## Data and Figures

- [`logs/`](logs/) — one directory per job with launch script, compressed server logs, `job.status`, benchmark consoles and rows, long-prefill results, per-rank memory samples, smoke-suite results, and sgl-eval output where GSM8K ran; `logs/pre/` holds the pre-checks.
- [`harness/`](harness/) — the driver, job lists, probes and summarizers used on the node.
- [`perf-summary.json`](perf-summary.json) — per-job benchmark, long-prefill, memory and Top-K compare numbers recomputed by [`perf_summary.py`](perf_summary.py).
- [`summary.json`](summary.json) — every number in the Results section, recomputed from the committed files by [`summarize_round.py`](../../../p0-correctness/scripts/v2/summarize_round.py).
- [`evidence-hashes.json`](evidence-hashes.json) — original path and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
