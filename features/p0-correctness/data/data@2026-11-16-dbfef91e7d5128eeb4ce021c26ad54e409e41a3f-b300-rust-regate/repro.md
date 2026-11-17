# E19 B300 Rust correctness gates

## Environment

Eight NVIDIA B300 SXM6 AC GPUs, 275040 MiB and 1100 W per GPU, driver 590.48.01. The existing SGLang devbox image digest and interconnect topology were not recorded. Overlay distribution versions: Torch 2.14.1+cu130, Transformers 5.19.0, FlashInfer Python/cubin 0.7.4, JIT and sm103a provider 0.7.4+cu130, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1 and sgl-eval 0.1.3. [environment.json](environment.json) captures the TP8 BF16 environment; the three launches reuse the same source and overlay paths.

Model: the existing local `zai-org/GLM-5-1028-Provider` checkpoint and its own NextN draft, as in [E15 setup](../data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-flashinfer-074-h200/repro.md). E15's checkpoint receipt records config SHA256 `99d7088de1960a51c0f1ae58553815c4c6c223fdbde44d13dc3ebca479e0c80f` and index SHA256 `55979a9446143325fac64918861333910a3f776d5719d2021d2b75a5c16112c1`. This rerun reused the checkpoint; it did not independently rehash the model inventory.

## Commit and setup

Runtime `dbfef91e7d5128eeb4ce021c26ad54e409e41a3f`. All 12,580 source-manifest files matched before and after the run. This historical baseline is separate from current integration `01d0a662d1` in E18.

Verify `SHA256SUMS`, extract `evidence.tar.gz` and check all files against `files.json`. Obtain the exact source commit, provision the E15 dependency overlay, and adapt the source/model/overlay paths in `start.sh`. Run `bash start.sh` on an exclusively held eight-GPU devbox. The wrapper verifies source and idleness, bounds the sequential suite at six hours, and writes `exit-code`. `runner.sh` builds the Rust extension on the devbox, launches each arm, records ownership/metrics and terminates each owned process group. Each `results/<arm>/argv.txt` preserves the exact command.

Set `SGLANG_RUST_BUILD_MODE=auto` and unset `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND`. All eight ranks in all three arms logged RustUnifiedTreeCore and mapped the native extension SHA256 `2ef3093b301a9302ceb0ab0208d65ad27cece3220fb1591b16d7a8e47af4c64f`. Per-rank PID, mapping path, hash and source evidence are in `tree-core-mapped.json`. Historical comparison arms explicitly selected the Python tree core.

Common server settings: EAGLE 3 steps/topk 1/4 draft tokens, the original model's NextN draft, maximum running requests/decode graph batch 32, prefill graphs disabled, default window layout, glm45/glm47 parsers, cache reports and metrics enabled. Three configurations:

- TP8 BF16: memory fraction 0.75, context 65536, chunk 32768; resolved TRTLLM MoE and FlashMLA sparse DSA.
- TP8 FP8 KV: same TP8 budget, FP8 E4M3 KV and TRTLLM DSA.
- DEP8: TP8/EP8/attention-DP8, TRTLLM MoE, a2a `none`, FP8 E4M3 KV/TRTLLM DSA, context 147456, memory fraction 0.88, chunk 65536 and FP32 LM head.

## Workload and comparison

Each arm runs all 1,319 GSM8K examples through sgl-eval 0.1.3: `sgl-eval run gsm8k --base-url http://127.0.0.1:31749/v1 --temperature 1.0 --top-p 0.95 --out-dir <arm>/eval-t1`. The original evaluator defaults remain: 64 threads, no request seed and no explicit max-token limit. Read `metrics.json` for complete sampling settings. No performance load was invoked.

Compare TP8 BF16 with the [E16 FI0.7.4 Python arm](../data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-flashinfer-073-074-accept-length/repro.md), TP8 FP8 KV with [E17 Python](../data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-tp8-fp8-kv/repro.md), and DEP8 with [E15 Python](../data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-flashinfer-074-h200/repro.md). All server flags match their chosen baseline except port; backend selection changes from explicit Python to default Rust. Baseline prediction files were independently recounted. These are single unseeded runs, so observed deltas do not establish a causal Rust effect.

## Results

| Configuration | Correct / 1319 | Accuracy | Stop / 1319 | Length | Python correct / stop | Accuracy delta pp | Stop delta pp |
|---|---:|---:|---:|---:|---:|---:|---:|
| TP8 BF16 | 1243 | 94.2381% | 1315 | 4 | 1254 / 1318 | -0.8340 | -0.2274 |
| TP8 FP8 KV | 1251 | 94.8446% | 1319 | 0 | 1254 / 1316 | -0.2274 | +0.2274 |
| DEP8 | 1245 | 94.3897% | 1318 | 1 | 1254 / 1319 | -0.6823 | -0.0758 |

All 3,957 records have unique, complete per-arm IDs, valid finish reasons and zero request errors. TP8 FP8 KV passes the observed accuracy-within-one-percentage-point and stopping-nonregression check for that configuration. TP8 BF16 and DEP8 do not meet stopping nonregression. Overall release quality remains unmet.

TP8 BF16 truncates IDs 87, 135, 796 and 1176. DEP8 truncates ID 1176 at 147,273 generated tokens; its answer is incorrect. The final long DEP8 request ran to the original context-derived limit. No failing request was discarded or retried.

Counter-derived natural acceptance is generated-token delta divided by verify-call delta: TP8 BF16 842847/312098 = 2.700584; TP8 FP8 KV 709019/269609 = 2.629805; DEP8 904180/333542 = 2.710843. Each generated-token delta equals the sum of all prediction token counts. These correctness workloads are not controlled throughput comparisons.

## Data and audit

[evidence.tar.gz](evidence.tar.gz) contains 55 raw files. [files.json](files.json) verifies every extracted file; [audit.json](audit.json) retains independent row counts, finish reasons, launch comparisons, per-arm counters and final source/cleanup evidence. All observed GPU processes were owned: 5,151 samples for TP8 BF16, 4,625 for TP8 FP8 KV and 8,098 for DEP8; no unresolved ancestry. Sampling cannot exclude activity between samples.

The suite exited 0 after completing all measurements. The final source check passed, all three server groups were gone, and all eight GPUs reported 0 MiB. The watcher completed and released its lock; the export audit also released its own lock. H200 Rust and current-source feature validation continue separately. An exit code of zero records execution completion, not a passing stopping gate.
