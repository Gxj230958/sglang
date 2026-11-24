# AMD

## Summary

`zai-org/GLM-5-1028-Provider` tracking for establishing and validating AMD Instinct configurations. Status: In progress. Related code work: `radixark/sglang-zai` branch `amd_support`, based on `glm-5-lp` at `59860082`. On 8 MI355X GPUs at TP8 (triton DSA backend, bf16 KV cache, AITER block-FP8 GEMMs and MoE, decode CUDA graph, no MTP), text, image and long-context requests answer correctly and stop normally, and full GSM8K reached 94.84% accuracy with 99.70% stop rate ([Correctness E36](../../p0-correctness/data/data@2026-11-16-8d5d043629dfede1abe081977bdf41d0b299ea8b-mi355x-bringup/repro.md)). With MTP (EAGLE 3/1/4) at the B300 TP8 feature set, smokes pass and full GSM8K reached 95.75% ([E01](data/data@2026-11-16-2dff6ce96790b25cf42ef47557f99472e8e9deaf-mi355x-mtp-serving/repro.md)). With shared-expert and AITER allreduce fusion, short-c32 serving reaches 99% of B300 TP8, long-c4 76% and short-c1 58%; TTFT beats B300 on all three, and the concurrency-1 gap is bound by kernel count. Two MTP launches hit a node-wide KFD queue-eviction state at the draft's first forward that only a host reboot clears; its trigger is under investigation. Expert plus attention data parallelism (DEP8) with the window layout and MTP passes full GSM8K at 94.92% / 99.92% stop after a fix that keeps every DP rank on the same decode graph, and HiCache host (L2) and file (L3) restores on it return the full cached prefix with all probe answers correct ([E02](data/data@2026-11-17-df840adba7a0dfa794a221ec49c57daa601ec7c1-mi355x-dep8-hicache/repro.md)). An fp8_e4m3 KV cache on that deployment holds 1.85x the bf16 tokens and passes GSM8K at 94.62% / 99.70% stop, matching the NVIDIA fp8 references; the same round fixes an out-of-bounds read in the MTP draft's logits gather under attention DP ([E03](data/data@2026-11-17-9ee63b69cd3093a6e0d2b5fba6c0618ca1bfce57-mi355x-fp8-kv/repro.md)). GPQA is blocked on access to the gated dataset; PD disaggregation remains open. Re-measured on Correctness E14's B300 workloads ([E04](data/data@2026-11-17-747c80ac250e5db44e4b242135da4bc9dbe76e86-mi355x-b300-parity/repro.md)), TP8 bf16 reaches 68% / 101% / 76% of B300 on short-c1 / short-c32 / long-c4, and DEP8 fp8 52% / 74% / 43% of B300's DEP8 after `747c80ac` moved the padded decode combine from RCCL to aiter's reduce-scatter; the remaining gaps are set by the number of small kernels per decode cycle. AgentX iterations on this deployment are tracked in [AgentX Performance E01](../../p0-agentx-performance/data/data@2026-11-17-9ee63b69cd3093a6e0d2b5fba6c0618ca1bfce57-mi355x-dep8-c64-levers/repro.md).

## Scope

### In Scope

- Pin the device type, runtime, dependencies, model revision, and execution backend.
- Track kernel coverage, supported precision, feature compatibility, and deployment requirements.

### Out of Scope

- Unselected configurations and unsupported feature combinations.
- Performance or support claims without reproducible evidence.

## Success Criteria

- [ ] The selected configurations reproduce from a documented environment and exact code commit.
- [ ] Correctness, capacity, and performance meet the platform-specific release gates.

## Assignees

- `<OWNER>` — Design, implementation coordination, and validation evidence.

## Stages

### Stage 1: Define requirements and design — In progress

- [x] Select the first target: 8x MI355X (gfx950), ROCm 10.0, TP8, bf16 KV cache, the `triton` DSA backend, AITER block-FP8 GEMMs and MoE.
- [ ] Record the target workloads, acceptance thresholds and the remaining layouts (MTP, FP8 KV cache, expert and attention data parallelism).
- Decision: a later cycle's dual-bank read runs on ROCm through `glm_loop_sparse_decode`'s Triton split-K behind the `triton` or `tilelang` DSA backend; FlashMLA and trtllm-gen are CUDA-only.

### Stage 2: Implement and validate the selected scope — In progress

- [x] ROCm enablement on `amd_support`: dual-bank route, unshuffled `kv_b_proj` before the `w_kc` / `w_vc` re-derivation, `MLA_ROCM` returning the cycle-0 Top-K, SGLang's MRoPE for GLM's interleaved layout, AITER-independent router numerics.
- [x] TP8 correctness: unit, kernel, smoke and full-GSM8K evidence in [Correctness E36](../../p0-correctness/data/data@2026-11-16-8d5d043629dfede1abe081977bdf41d0b299ea8b-mi355x-bringup/repro.md).
- [x] MTP at the B300 TP8 feature set: smokes 3/3, GSM8K 95.75% ([E01](data/data@2026-11-16-2dff6ce96790b25cf42ef47557f99472e8e9deaf-mi355x-mtp-serving/repro.md)). (`<OWNER>`, 2026-11-16)
- Decision: shared-expert fusion is admitted on gfx950 for the GLM LoopLM expert geometry (E=256/topk=8, unclamped SiLU), and `--enable-aiter-allreduce-fusion` is allowed; both stay within the run-to-run numerics noise floor ([E01](data/data@2026-11-16-2dff6ce96790b25cf42ef47557f99472e8e9deaf-mi355x-mtp-serving/repro.md)).
- [ ] Node degradation: two of five MTP launches entered a state where every process takes constant KFD queue evictions (~156 ms per cross-GPU op) from the draft model's first forward until a host reboot. The earlier "hang at batch size 52" was this state (capture crawled at ~143 s per shape), not a deadlock. Prime suspect: the ROCm multimem all-gather probe (removed in `7147d968`); confirm with `scripts/v2/symm_stress.py` and repeated launches, and read the host kernel log at onset.
- [x] DEP8 (`--attn-dp-size 8 --ep-size 8`) with the window layout and MTP: GSM8K 94.92%, 99.92% stop; HiCache L2 and L3 restores 6/6 correct with 6656 cached tokens; parsers checked ([E02](data/data@2026-11-17-df840adba7a0dfa794a221ec49c57daa601ec7c1-mi355x-dep8-hicache/repro.md)). (`<OWNER>`, 2026-11-17)
- Decision: under attention DP the ROCm DSA dense/sparse decode-graph split is off (`df840adb`); each rank chose a graph from its own batch, so ranks replayed different graphs around the shared MoE collectives.
- [x] FP8 KV cache: ROCm stores raw 576-wide e4m3 rows that both Triton dual-bank kernels read (`9ee63b69`); DEP8 + window + MTP GSM8K 94.62% / 99.70% stop, 1.85x tokens per rank ([E03](data/data@2026-11-17-9ee63b69cd3093a6e0d2b5fba6c0618ca1bfce57-mi355x-fp8-kv/repro.md)). (`<OWNER>`, 2026-11-17)
- Decision: under attention DP the draft extend's logits gather counts one row per request on every rank (`1d02ff8b`); the target's input-logprob row counts made it read out of bounds.
- Scripts: [scripts/v2/](scripts/v2/) — non-destructive stall/eviction monitor, B300-parity benchmark, numerics probe, trace breakdown, KFD event tools.
- Scripts: [scripts/v3/](scripts/v3/) — DP-pinned HiCache probes, parser smoke, FP8 and GPQA runs, SPEED-Bench prompt builder, AgentX controllers.
- [ ] GPQA-Diamond against the reference value: blocked, `Idavidrein/gpqa` is gated and the run's Hugging Face account has no access.
- [ ] Performance optimization: baseline and first fusions in [E01](data/data@2026-11-16-2dff6ce96790b25cf42ef47557f99472e8e9deaf-mi355x-mtp-serving/repro.md); concurrency 1 needs fewer launches per layer (about 3500 kernels at a 4 us floor per MTP cycle); the dual-bank decode kernel takes 1.5 to 3 times the single-bank kernel's time from 8 rows on.

## Experiments

| ID | Date | Topic | Basic Setting | Result | Round |
|---|---|---|---|---|---|
| Correctness E36 | `2026-11-16` | MI355X TP8 bring-up and full GSM8K | `8d5d0436`; 8x MI355X; TP8, triton DSA, bf16 KV, decode CUDA graph, no MTP | Smokes 3/3; GSM8K 94.84% accuracy, 99.70% stop | [round](../../p0-correctness/data/data@2026-11-16-8d5d043629dfede1abe081977bdf41d0b299ea8b-mi355x-bringup/repro.md) |
| E01 | `2026-11-16` | MI355X MTP serving, fusions, B300-parity benchmark | `8a30c7bf`→`2dff6ce9` (non-release window); 8x MI355X; TP8, MTP 3/1/4, B300 E14 flags | GSM8K 95.75% (MTP), 93.78% (fused); short-c1/c32/long-c4 137.4/1162/95.7 tok/s = 58/99/76% of B300; node KFD-eviction state in 2/5 launches | [round](data/data@2026-11-16-2dff6ce96790b25cf42ef47557f99472e8e9deaf-mi355x-mtp-serving/repro.md) |
| E02 | `2026-11-17` | DEP8 + window + MTP, HiCache L2/L3, parsers, SPEED-Bench acceptance | `df840adb`; 8x MI355X; DEP8, window layout, MTP 3/1/4, bf16 KV, context 262144 | GSM8K 94.92% / 99.92% stop; with HiCache 95.45% / 99.85%; L2 and L3 restores 6/6 correct, 6656 cached; SPEED-Bench coding AL 2.49 | [round](data/data@2026-11-17-df840adba7a0dfa794a221ec49c57daa601ec7c1-mi355x-dep8-hicache/repro.md) |
| E03 | `2026-11-17` | FP8 KV on DEP8 + window + MTP; DP draft-logits gather fault | `1d02ff8b` + `9ee63b69`; 8x MI355X; DEP8, window layout, MTP 3/1/4, fp8_e4m3 KV, context 32768 | GSM8K 94.62% / 99.70% stop; 2.14M tokens per rank (1.85x bf16); numcheck vs bf16 0.041 mean \|Δlogp\|, 97.0% top-1; fault fixed, 40/40 flush cycles | [round](data/data@2026-11-17-9ee63b69cd3093a6e0d2b5fba6c0618ca1bfce57-mi355x-fp8-kv/repro.md) |
| E04 | `2026-11-17` | B300 parity on E14 workloads; DEP8 decode combine | `9ee63b69`, `747c80ac`; TP8 bf16 E14 flags + AITER AR fusion; DEP8 fp8 window E14 shape | TP8 159.7 / 1184 / 96.3 tok/s = 68 / 101 / 76% of B300; DEP8 fp8 70.5 / 787 / 56.2 = 52 / 74 / 43% of B300 DEP8 (+14 / +5 / +6% from the combine fix) | [round](data/data@2026-11-17-747c80ac250e5db44e4b242135da4bc9dbe76e86-mi355x-b300-parity/repro.md) |
