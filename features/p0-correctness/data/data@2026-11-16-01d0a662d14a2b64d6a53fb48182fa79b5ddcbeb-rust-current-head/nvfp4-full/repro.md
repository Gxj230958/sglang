# E18 follow-up: full NVFP4 natural-MTP evaluation

The current integration completed both full evaluations on the same four GB300 GPUs. NVFP4 remains a performance-only artifact: its stop rate is lower than FP8 in this paired run, so the runtime quantization PR push gate is not satisfied.

## Environment and reproduction

Use the source, immutable checkpoints and dependency setup in the [E18 reproduction](../repro.md), including runtime `01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb` and the verified reconstruction tree `16b1249e58da225cac7e94a2e0fff80bf533e63d`.

The NVFP4 checkpoint is private `RadixArk/GLM-5-1028-Provider-NVFP4-perf` revision `f2c64cebac62b1888c92c9d317adbb0b0aef5955`. The draft is the original FP8 checkpoint with explicit FP8 draft quantization. Both targets use natural EAGLE with steps/top-k/draft-tokens 3/1/4. All simulation variables and the explicit tree-core override are unset; every TP rank logs `RustUnifiedTreeCore`.

Both evaluations use all 1,319 GSM8K questions, sgl-eval 0.1.3, temperature 1, top_p 0.95, seed 1, 64 threads and a 32,768-token output limit. Server context 65,536, BF16 KV, FlashMLA sparse, TRTLLM MoE, separate shared experts, memory fraction 0.80, chunk 8192, request/decode-graph cap 64, FP32 LM head and disabled prefill graphs match. The independent audit compares exact server environment and command arrays after normalizing only the target path and output directory. FP8 ran first, NVFP4 second, one run each.

Extract [evidence.tar.gz](evidence.tar.gz). Verify its hash with [SHA256SUMS](SHA256SUMS) and each extracted file against [files.json](files.json). Run the recorded `runs/nvfp4-full-current1/launch.json` server argv/environment, then `gsm8k-command.json`, on an exclusively idle devbox. Preserve the model/source/overlay versions while adapting filesystem paths. The full raw FP8 comparator remains in the parent E18 archive.

## Results

| Target weights | Correct | Accuracy | Stop | Length | Errors |
|---|---:|---:|---:|---:|---:|
| FP8 | 1256/1319 | 95.22% | 1316/1319 (99.77%) | 3 | 0 |
| NVFP4 | 1243/1319 | 94.24% | 1313/1319 (99.55%) | 6 | 0 |

NVFP4 is lower by 0.986 percentage points in accuracy and 0.227 points in stop rate. This single paired run does not establish quality parity. Both runs have 1,319 unique prediction IDs, three nonempty stopped chat probes and four verified Rust ranks. There are no request errors.

NVFP4 requests `gsm8k-87`, `gsm8k-652`, `gsm8k-135`, `gsm8k-984`, `gsm8k-858` and `gsm8k-1254` each hit 32,768 output tokens and were incorrect. FP8 truncated `gsm8k-423`, `gsm8k-87` and `gsm8k-1176`. The shared truncated ID alone does not establish a mechanism. The follow-up does not attribute truncation to the metadata-mapping change or claim a serving-performance gain.

An additional imported exclusion check verifies physical boundaries 0,26,53,54,77,78 map to target slots 0,26,53,54,81,82,105, preserve the non-layer exclusion and original configuration, and filter target-side NextN. Its final raw result is included.

## Decision and remaining work

Keep the checkpoint scoped to performance testing. The matched stop-rate nonregression check fails, and the runtime code remains local. The authorized matched FP8/NVFP4 performance sweeps continue with this limitation explicit; deployment quality acceptance remains open. B300/H200 Rust and required feature combinations still require their own evidence.

[Independent audit](audit.json) records source identity, normalized-command equality, all prediction counts, truncated IDs and the failed stop-rate nonregression comparison. [Raw evidence](evidence.tar.gz) preserves all 21 captured files unchanged, including server logs, resolved settings, predictions, metrics, GPU cleanup and exclusion-mapping evidence.
