# E01 Small-head sparse-prefill serving A/B — data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-serving

## Environment

- Machine: 8× NVIDIA B300, TP8 / CP1 / attention DP1; FP8 weights and BF16 KV cache.
- Model and bundled tokenizer: `zai-org/GLM-5-1028-Provider` at revision `7e66c40540c64bbf85e2a3c6d7264fbc514b4b43`.
- Implementation: pre-rebase small-head change `aabfddd8214bee95b6b526af5f77c81398bda133`. The later rebase `f86559388173b8abc3c6db80e3ec78e797dd85f0` keeps the small-head patch unchanged. The original PR was closed unmerged and superseded by [upstream PR #48891](https://github.com/sgl-project/sglang/pull/48891), which this round does not claim to validate.
- Software: torch `2.14.1+cu130`, transformers `5.19.0`, sglang-kernel `0.4.10`, and `sgl-flash-mla==1.0.3`; DeepGEMM MoE, FlashMLA sparse prefill, and TRT-LLM decode.
- The installed transformers package lacked `glm_loop`. Both arms used the same compatibility configuration with SHA-256 `700b5d32efd4cebf618924c83edf586250c5d32d52b30db53f2bded9d22f9f7a`. It has no immutable source-commit pin, so this is a non-release experiment.

## Setup

Use the pre-rebase source and the shared compatibility configuration. Launch optimized with the PR's default public capability probe:

```bash
PYTHONPATH=/path/to/source/python:/path/to/flashmla-1.0.3 \
SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python \
python -m sglang.launch_server \
  --model-path /path/to/GLM-5-1028-Provider --served-model-name GLM-Loop \
  --tp-size 8 --mem-fraction-static 0.85 --kv-cache-dtype bfloat16 \
  --context-length 262144 --chunked-prefill-size 16384 \
  --dsa-prefill-backend flashmla_sparse --dsa-decode-backend trtllm \
  --reasoning-parser glm45 --tool-call-parser glm47 \
  --moe-runner-backend deep_gemm --disable-prefill-cuda-graph \
  --random-seed 463135866 --host 127.0.0.1 --port 30000 \
  --max-running-requests <CAP>
```

For baseline, use the same source and wheel, but disable only the public capability probe. The model, kernel wheel, and all other settings remain identical:

```bash
mkdir -p /path/to/native-overlay
cp baseline-sitecustomize.py /path/to/native-overlay/sitecustomize.py
PYTHONPATH=/path/to/native-overlay:/path/to/source/python:/path/to/flashmla-1.0.3 \
  python -m sglang.launch_server <THE_SAME_ARGUMENTS>
```

Wait for HTTP 200 from `/health`. Profile one prefill per arm and check `baseline-dispatch.json` and `optimized-dispatch.json`: baseline must show native head64 without small_heads; optimized must show small_heads. Dual-bank calls that need LSE remain native by design.

Run one case as follows, changing batch size, lengths, and seed according to the table below. Add `--skip-token-capacity-check` for 100K input.

```bash
HEAD32_BENCH_CAPTURE=/path/to/capture \
HEAD32_BENCH_SERVER_LOG=/path/to/server.log \
PYTHONPATH=/path/to/source/python:/path/to/flashmla-1.0.3 \
python bench_capture.py \
  --model None --base-url http://127.0.0.1:30000 \
  --batch-size 64 --enable-multi-batch \
  --input-len 8192 --output-len 1024 \
  --dataset-name random-ids --seed 42 \
  --local-tokenizer-path /path/to/GLM-5-1028-Provider \
  --no-append-to-github-summary --run-name optimized-cap64-8k1k \
  --result-filename /path/to/result.jsonl
```

`bench_one_batch_server` flushes the prefix cache before every case. Warmup and measured requests are separate. The harness checks input lengths, prompt hashes, completion counts, and finish reasons. Baseline and optimized process the same random IDs.

## Commit

- Code commit: `aabfddd8214bee95b6b526af5f77c81398bda133`.
- Working tree: shared GLM configuration compatibility file listed above; all other attention/interface blobs match the pre-rebase change.
- Status: non-release because the compatibility file and container are not locked, and the later rebase/upstream head was not rerun.

## Scripts

- Version: round-specific [`bench_capture.py`](bench_capture.py) and [`baseline-sitecustomize.py`](baseline-sitecustomize.py).
- Temporary changes: reproduction paths are parameterized; no product source is included.

## Workload

- Random-ID prompts at temperature 0 with EOS ignored and exact output lengths enforced.
- Cap 1 uses one request per arm; cap 64 uses 64 requests per arm and run.
- Cases: 8192/1024 at caps 1 and 64, seeds 42 and 43; 102400/2048 at cap 64, seed 42.
- Each table row is one paired run. Run A and run B are independent server rounds, not repeated samples from one timing distribution.
- Throughput is total output tokens divided by end-to-end wall time including prefill. TTFT and TPOT are per-request medians.
- The two controllers completed 323 requests across both arms with no early stopped requests. At 100K, the cap-64 case remains KV-resident limited even though 64 client requests are issued.

## Results

| Input/output | Cap | Run | Base tok/s | Opt tok/s | Gain | Median TTFT ms (base/opt) | Median TPOT ms (base/opt) |
|---|---:|---|---:|---:|---:|---:|---:|
| 8K/1K | 1 | seed 42 A | 50.127 | 50.481 | +0.71% | 2233.8 / 2087.8 | 17.79 / 17.79 |
| 8K/1K | 1 | seed 42 B | 48.514 | 50.321 | +3.73% | 2912.2 / 2154.9 | 17.79 / 17.79 |
| 8K/1K | 64 | seed 42 A | 946.351 | 946.207 | −0.02% | 16459.9 / 15763.1 | 51.60 / 52.29 |
| 8K/1K | 64 | seed 42 B | 940.933 | 951.737 | +1.15% | 16450.2 / 15749.3 | 52.00 / 51.91 |
| 8K/1K | 64 | seed 43 | 936.654 | 937.744 | +0.12% | 16503.0 / 15771.0 | 52.26 / 52.90 |
| 100K/2K | 64 | seed 42 | 170.385 | 175.516 | +3.01% | 335676.2 / 326235.3 | 42.68 / 41.66 |

The three cap-64 8K runs average +0.42% throughput and 4.31% lower median TTFT. The single 100K run gained 3.01% throughput and reduced TTFT by 2.81%.

Conclusions:

1. The PR default path dispatches to small_heads and produces the requested output lengths without early stops.
2. Cap-64 TTFT improved consistently, but the 8K throughput effect is small and not statistically established.
3. Cap-1 measurements varied substantially; the 100K result needs repetition before being treated as stable.
4. The kernel-only evidence is in [Kernel Optimization E01](../../../p0-kernel-opt/data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-prefill/repro.md).

## Data and Figures

- [`aggregate.json`](aggregate.json) — independently calculated serving metrics and averages.
- [`comparison.json`](comparison.json) — paired cap-64 and cap-1 measurements from the controlled controller.
- [`run-a-baseline-cap1.json`](run-a-baseline-cap1.json), [`run-a-optimized-cap1.json`](run-a-optimized-cap1.json), [`run-a-baseline-cap64.json`](run-a-baseline-cap64.json), and [`run-a-optimized-cap64.json`](run-a-optimized-cap64.json) — independent run-A raw summaries.
- [`baseline-dispatch.json`](baseline-dispatch.json) and [`optimized-dispatch.json`](optimized-dispatch.json) — observed kernel dispatch.
- [`paired-controller-exit.json`](paired-controller-exit.json) and [`run-a-controller-exit.json`](run-a-controller-exit.json) — controller completion and prompt-pair checks.
