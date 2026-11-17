# Rust tree-core validation contract

## Outcome

The serving rounds below explicitly selected `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`. Their measurements describe the Python tree core and are ineligible for the required default-Rust validation or deployment recommendation. Rust reruns are pending. CPU checks and standalone kernel measurements retain their original scope.

## Evidence

Each linked reproduction record states the Python backend selection. The records and raw measurements remain immutable.

| Feature | Round | Recorded backend |
|---|---|---|
| `p0-correctness` | [E06](../data@2026-11-12-710bcb2a3e6e4abbc299b43860c6528f7bd81db8-window-layout-matrix/repro.md) | Python |
| `p0-correctness` | [E07](../data@2026-11-13-802d8157b74564997e350ffa981b5e567e391920-topk-by-reference-gate/repro.md) | Python |
| `p0-correctness` | [E08](../data@2026-11-14-c6a9b3411f3db9fa1a4244ec6eede2a43bbf5550-main-merge-gate/repro.md) | Python |
| `p0-correctness` | [E09](../data@2026-11-15-ec8bc57fde48466d602529752d428b466efc54cf-main-merge-dep8/repro.md) | Python |
| `p0-correctness` | [E10](../data@2026-11-15-5e6ee4ed50fc91fee9c5a0484667ce6de2ba5640-window-default-dep8/repro.md) | Python |
| `p0-correctness` | [E11](../data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-retrieval/repro.md) | Python |
| `p0-correctness` | [E12](../data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-attribution/repro.md) | Python |
| `p0-correctness` | [E13](../data@2026-11-15-fb4015b5bdb6ed416beba624f365407089567b53-window-default-tp8/repro.md) | Python |
| `p0-correctness` | [E14](../data@2026-11-15-fb4015b5bdb6ed416beba624f365407089567b53-window-layout-speed/repro.md) | Python |
| `p0-correctness` | [E15](repro.md) | Python |
| `p0-correctness` | [E16](../data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-flashinfer-073-074-accept-length/repro.md) | Python |
| `p0-correctness` | [E17](../data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-tp8-fp8-kv/repro.md) | Python |
| `p0-general-performance` | [E01](../../../p0-general-performance/data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-serving/repro.md) | Python |
| `p0-general-performance` | [E03](../../../p0-general-performance/data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-gb300-serve-sweep/repro.md) | Python |
| `p0-hicache` | [E02](../../../p0-hicache/data/data@2026-11-12-e1ac59e643f191eaf0f817474c9d8732c04a3b37-window-l2-l3/repro.md) | Python |
| `p0-hicache` | [E03](../../../p0-hicache/data/data@2026-11-13-704d3082e1d68255ffb577f02262930b5f2f6d74-window-l2-l3/repro.md) | Python |
| `p0-kernel-opt` | [E03](../../../p0-kernel-opt/data/data@2026-11-12-6ed895fa2678d8c4d52576e7ae5e3707ee4180e7-topk-by-reference-b300/repro.md) | Python |
| `p0-parallelism/dp-attention` | [E01](../../../p0-parallelism/dp-attention/data/data@2026-11-12-710bcb2a3e6e4abbc299b43860c6528f7bd81db8-window-dep4/repro.md) | Python |
| `p0-parallelism/dp-attention` | [E02](../../../p0-parallelism/dp-attention/data/data@2026-11-13-e941d571f3877797b383d616e957f30c8936c52d-window-dep8/repro.md) | Python |
| `p0-parallelism/prefill-cp` | [E01](../../../p0-parallelism/prefill-cp/data/data@2026-11-12-0c95a2b1d2f1cfcaa6bcc503acfe868cd8a6083e-window-cp4/repro.md) | Python |
| `p0-parallelism/prefill-cp` | [E02](../../../p0-parallelism/prefill-cp/data/data@2026-11-13-e941d571f3877797b383d616e957f30c8936c52d-window-cp4-cp8/repro.md) | Python |
| `p0-parallelism/prefill-cp` | [E03](../../../p0-parallelism/prefill-cp/data/data@2026-11-15-f02daab4df4c9ebfa854ecc7e2da3dd151496389-window-cp4-merged-dev/repro.md) | Python |
| `p0-pd-disagg` | [E01](../../../p0-pd-disagg/data/data@2026-11-12-3f3a3985acdae2aff39ab9d04c6b0047992dfeb2-window-tcp-1p1d/repro.md) | Python |
| `p0-pd-disagg` | [E02](../../../p0-pd-disagg/data/data@2026-11-13-fd5e9375e95252ccae3f39bec4623cf6bb172b5e-window-rdma-1p1d/repro.md) | Python |
| `p0-pd-disagg` | [E03](../../../p0-pd-disagg/data/data@2026-11-15-bdbebf62fca4af4e628e26f9e55d139bb7794047-rdma-window-full-hicache/repro.md) | Python |

## Rerun contract

- Historical baseline: `dbfef91e7d5128eeb4ce021c26ad54e409e41a3f`, FlashInfer Python/cubin/JIT 0.7.4, pinned checkpoint and tokenizer hashes. Reverify deployed source files and record imported package locations.
- B300: TP8 BF16 KV with FlashMLA sparse, TP8 FP8 KV with TRT-LLM DSA, and DEP8 FP8 KV with TRT-LLM DSA. H200: TP8 BF16 with FlashMLA sparse and `sgl-fa3==0.1.0`.
- Unset `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND`; record Rust build mode and toolchain. A source deployment requires the matching `rust/` sources and a usable toolchain. An inherited `SGLANG_RUST_BUILD_MODE=never` can prevent a missing extension from building; use `auto` for the source-build setup and record that choice.
- Require `Tree Core: RustUnifiedTreeCore` in every scheduler's startup log before accepting measurements. Record any compatibility fallback or build/runtime failure as a blocker for that configuration.
- Keep the historical launch settings for the first backend comparison, including disabled prefill CUDA graphs. Evaluate prefill graph behavior in a separate paired round.
- Run full GSM8K (1319 questions) through `sgl-eval`, temperature 1.0 and top_p 0.95. Preserve per-request finish reasons, errors and accuracy; evaluate stop rate against the recorded baseline as well as accuracy. A successful evaluator exit alone is not a gate pass.
- Run serving speed with input/output lengths 2000/500 at concurrency 1 and 32 and 30000/300 at concurrency 4, seeds 1 and 2, cache flush and two warmup requests. Preserve the generated request/token accounting with each result.
- Snapshot generation-token and speculative-verify counters immediately before and after each eval. Report their delta ratio as the counter-based acceptance length.
- Revalidate HiCache, DP, CP and PD configurations individually. Some configurations have explicit Python compatibility fallbacks; a successful fallback does not establish Rust support.
- Record GPU process ownership throughout measurement, including startup intervals; a zero-memory snapshot between another driver's launches does not establish exclusive use.

## Current code coverage

The implementation branch was observed at `8a6cdc9d7c71798e307f098f0d3998d4d0de3d00` on 2026-11-16. It adds FP8 sparse-decode and Mega MoE changes after the historical baseline. Validation of the historical commit does not cover that head; record a separate exact-commit round for the current candidate.

## Serving comparison attribution

General Performance E03 compares `tp4-trt-fp8-mtp` using DeepGEMM MoE with `dep4-trt-fp8-mtp` using FlashInfer TRT-LLM MoE. Their workload, DSA route, KV dtype and MTP settings match, but MoE runner and request placement differ. The measured score difference is a comparison of those deployments, not an isolated TP-versus-DP effect. The round's Python-core data remains historical.

## Follow-up

- [ ] Complete the B300 and H200 Rust runs and publish raw evidence in new experiment rounds.
- [ ] Complete the GB300 MoE/BCG and agentic workload Rust runs before selecting a deployment profile.
- [ ] Revalidate feature combinations under their resolved cache backend.
- [ ] Bind release claims to the selected code head and artifact lock.
