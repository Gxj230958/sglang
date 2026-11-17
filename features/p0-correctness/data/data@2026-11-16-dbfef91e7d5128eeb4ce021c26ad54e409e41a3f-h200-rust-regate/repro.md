# E20 H200 TP8 Rust full GSM8K gate

## Environment

Eight NVIDIA H200 GPUs, TP8. The existing devbox image digest, topology and power mode were not captured. The recorded overlay and Python executable contain Torch 2.14.1, Transformers 5.19.0, FlashInfer Python/cubin 0.7.4, CUDA 13 JIT provider 0.7.4+cu130, sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1, sgl-eval 0.1.2 and sgl-fa3 0.1.0. postrun-environment.json is a postrun metadata inventory, not a live import receipt. Its versions match the historical Python server's import receipt. The Rust launch directly verified the FA3 import; complete live dependency imports were not captured.

Model: the existing local `zai-org/GLM-5-1028-Provider` checkpoint and its own FP8 NextN draft, retained from [E15](../data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-flashinfer-074-h200/repro.md). E15 records config SHA256 `99d7088de1960a51c0f1ae58553815c4c6c223fdbde44d13dc3ebca479e0c80f` and index SHA256 `55979a9446143325fac64918861333910a3f776d5719d2021d2b75a5c16112c1`. This run reused that checkpoint; it did not rehash every weight shard. This is a correctness measurement, with no NVFP4 performance comparison.

## Commit

Runtime `dbfef91e7d5128eeb4ce021c26ad54e409e41a3f`; all 12,580 source-manifest files match before and after execution. This historical runtime is separate from the current integration in Correctness E18.

## Setup and scripts

Verify SHA256SUMS, extract evidence.tar.gz and check every member against files.json. Provision the exact source commit and E15 overlay, including sgl-fa3 0.1.0. Adapt source, model, overlay and output paths in start.sh; preserve source and exclusive-idle checks. Run `bash start.sh` on the eight-GPU devbox. The wrapper bounds execution at six hours and writes exit-code. runner.sh builds the Rust extension remotely, launches the server, records metrics and process ownership, runs sgl-eval and cleans up the owned process group.

Set SGLANG_RUST_BUILD_MODE=auto; leave the explicit tree-core selector unset and clear acceptance-simulation variables. All eight worker ranks logged RustUnifiedTreeCore and mapped Rust extension SHA256 `5465ff96ba96e1dc4f0e41387bda0c5608ec86303b9ac95dfd6a622ea785f947`. Live worker PIDs, process start identities, GPU assignments, mapped extension hashes, environments and resolved settings are in results/h200-tp8/live-runtime-evidence.json. The server parent also appears on GPU0; all nine observed GPU process identities belong to its process group.

Server settings: TP8, BF16 KV, FlashMLA sparse DSA, context 65536, memory fraction 0.75, chunk 32768, maximum running requests and decode graph batch 32, prefill graphs disabled, default window KV layout, glm45/glm47 parsers, metrics/cache reports, natural EAGLE steps/topk/draft-tokens 3/1/4 and the original checkpoint as draft. Exact argv is archived. Request output limits match the historical evaluator defaults.

## Workload and baseline

Run all 1319 GSM8K examples with the recorded evaluator:

```bash
sgl-eval run gsm8k --base-url http://127.0.0.1:31876/v1 --temperature 1.0 --top-p 0.95 --out-dir eval-t1
```

The evaluator uses 64 threads, no explicit request seed and no explicit max_tokens. metrics.json preserves all sampling settings. No throughput sweep was run. Compare against the [E15 H200 Python arm](../data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-flashinfer-074-h200/h200/h200-tp8-fa3/launch.json): flags match except port; the baseline explicitly selects Python tree core while this launch uses default Rust. baseline-launch-audit.json records the comparison. Both are single unseeded runs and do not isolate a causal Rust effect.

## Results

| Tree core | Correct / 1319 | Accuracy | Stop / 1319 | Stop rate | Length | Errors |
|---|---:|---:|---:|---:|---:|---:|
| Historical Python | 1250 | 94.7688% | 1317 | 99.8484% | 2 | 0 |
| Rust | 1251 | 94.8446% | 1316 | 99.7726% | 3 | 0 |

Rust has one additional correct answer and one fewer naturally stopped response. Stopping nonregression remains unmet. Successful execution and accuracy within the gate tolerance do not establish release qualification.

Length IDs are gsm8k-306, gsm8k-119 and gsm8k-652, with 65449, 65421 and 65450 completion tokens respectively; all three answers are incorrect. All 1319 unique examples are preserved, with no errors, discarded rows or retries. The Python baseline predictions were independently recounted; compressed prediction SHA256 is `9dfa6298aa4d4bdc175e251b1cfd22ddd61b8f77f75c78c75445b4d65bbdd4fc`.

Generation-token delta 896553 equals the sum of prediction completion tokens. Dividing by 327375 verification calls gives natural acceptance 2.738611684. This describes the correctness workload and is not a controlled performance estimate.

## Data and audit

evidence.tar.gz preserves 33 raw files, SHA256 `50ea05f0246861a7de41a1f330c4bb9741aa3b69b80bc4b341674ee22b19cb07`. files.json verifies each member. audit.json independently recounts IDs, accuracy, finish reasons, completion-token sums and counters, and verifies all eight native Rust mappings. All 8604 sampled GPU-process records resolve to the owned server group; no foreign or unresolved processes were observed. Sampling cannot exclude activity between samples.

The driver exited zero after measurement completion. Final source verification passed; the postrun probe reports no GPU processes and eight GPUs at 0 MiB. The completed watcher and evidence collection released their locks; the shared devbox remains allocated. Required current-source DP/PD and other combinations are tracked separately.
