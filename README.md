# Day-0 Model Track

This repository template separates upstream SGLang mirrors, Day-0 model implementation work, reference implementations, and project tracking across four branches.

## Model

This branch tracks Day-0 support for `zai-org/GLM-5-1028-Provider`, a GLM LoopLM checkpoint (`GlmLoopForConditionalGeneration`): a multimodal FP8 MoE model of approximately 754B parameters whose 78 physical decoder layers run as 106 effective layer slots, with MLA and DSA sparse attention.

Current status: the cutoff commit and multi-architecture image are pinned, while exact-digest GPU qualification remains open. Correctness E22–E28 remain pinned to fallback candidate `52ef77912fd004f34cfe340b392018632ce69c2c`; General Performance E10–E13 add the initial delivery matrix, and E14–E15 complete the H200 and GB300 default-profile sweeps at `ac08d9be93598a62dda61191dcc91bda9cd6aa8b`. B300 FP8-only r4 has no final summary. A separate cutoff reference-method run has completed on B300, GB300 and H200, but its raw per-run outputs and immutable model revision have not been copied to the coordinator host, so no new official performance round is recorded yet. Correctness E30 records the #89 self-draft fix and requires NVFP4 natural-MTP performance to be rerun. [Correctness E31](features/p0-correctness/data/data@2026-11-20-7053ff0277bd27e1f3c76646b4a65bf76b0c7820-upstream-main-sync/repro.md) validates upstream-sync candidate `7053ff0277bd27e1f3c76646b4a65bf76b0c7820` on GB300 TP4 at 94.92% accuracy and 100% stop, against 94.69% and 99.92% for its matched baseline; the candidate has not landed and other serving paths remain unverified. PD E04 records the router health-check diagnosis. Quality acceptance and remaining feature coverage keep delivery acceptance open. NVFP4 is performance-only.

Highest priority: validate the [published cutoff image](day0-delivery/docker/data/data@2026-11-18-a22079906bf873d1c888b9a0c4b7fdc70a4432f2-multiarch-image/repro.md) by digest on B300, H200 and GB300, and import the raw reference-method evidence before selecting final profiles. Freeze the accepted artifacts only after correctness and stop-rate review. The eager-prefill rows are historical measurements, not final deployment recommendations; see [execution priorities](features/p0-general-performance/README.md#execution-priorities) and the [2026-11-18 status refresh](day0-delivery/2026-11-18-0317-xinyuan-26c4816830-default-results-and-pd-diagnosis.md).

The [backend audit and Rust validation contract](features/p0-correctness/data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-flashinfer-074-h200/2026-11-16-0845-xinyuan-dbfef91e7d-rust-validation-contract.md) identifies Python-core serving rounds, including Correctness E06–E17 and General Performance E03. Their historical measurements below do not establish default-Rust correctness or a deployment recommendation. The current integration is recorded separately in Correctness E18.

- Current implementation: `radixark/sglang-zai` branch `glm-5-lp` at `13fa8258d2404deedfac9c114c43c4e4069f39b5` (remote head observed 2026-11-20). Upstream-sync candidate `7053ff0277bd27e1f3c76646b4a65bf76b0c7820` integrates that branch with upstream `main` `2b248971db8c8c349586c3757663be9cba5e366d` and passes the [Correctness E31](features/p0-correctness/data/data@2026-11-20-7053ff0277bd27e1f3c76646b4a65bf76b0c7820-upstream-main-sync/repro.md) TP4 gate; it has not landed. The cutoff candidate is pinned separately at `a22079906bf873d1c888b9a0c4b7fdc70a4432f2`. The earlier integration at `26c4816830c53d867583f3d69117e23b44608481` includes #85 default BCG/self-draft, #86 mixed-precision loop slots, #87 HiSparse pending-buffer reservation and #89 NVFP4 self-draft fused-projection resolution. Model revisions for the default performance rounds are FP8 `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff` and NVFP4 `f2c64cebac62b1888c92c9d317adbb0b0aef5955`. Earlier evidence remains pinned to its original commits.
- Cutoff image: `xinyuantongradixark/sglang-private:dev-glm-loop-1118` at OCI index `sha256:c1c0e04063a4e176047ee9f9bcdda82626b8ca63efd3530e958ef3ee8c64a6c9`, with separate AMD64 and ARM64 manifests. Native CPU build, source and import checks pass; exact-digest GPU validation is pending. See the [build and publication record](day0-delivery/docker/data/data@2026-11-18-a22079906bf873d1c888b9a0c4b7fdc70a4432f2-multiarch-image/repro.md).
- On 8 H200 GPUs at TP8 (Triton MoE, FlashMLA Sparse, BF16 KV cache, CUDA graph and MTP disabled), the configuration, model, attention, and checkpoint-map tests pass, and text, image, and long-context requests return correct answers that stop normally ([Correctness E01](features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md)).
- GSM8K-200 reached 95.50% accuracy with 100% stop rate and 0% truncation. Built-in NextN/MTP generated with `accept len=2.27`, and decode execution logged `cuda graph: True` ([Correctness E02](features/p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-mtp-cuda-graph/repro.md)). Disaggregated deployment has not been validated.
- Small-head FlashMLA prefill passed 36 exact kernel comparisons with 6.63–16.26% lower median latency ([Kernel Optimization E01](features/p0-kernel-opt/data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-prefill/repro.md)). Serving showed 4.31% lower cap-64 8K TTFT and +0.42% throughput ([General Performance E01](features/p0-general-performance/data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-serving/repro.md)); the original PR was closed unmerged and superseded by [upstream PR #48891](https://github.com/sgl-project/sglang/pull/48891).
- [HiCache E04](features/p0-hicache/data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-paired-rust-hicache/repro.md) validates current Rust FP8/NVFP4 host and file restoration, prefix probes and fresh-store negative controls. All four full GSM8K runs retain length truncations; stopping nonregression remains unmet. Other storage and parallelism combinations require separate validation.
- On 2×4 Vera Rubin GPUs at TP8 with 131072 input tokens, the FlashInfer TRT-LLM MoE runner that plain TP selects by default decodes 36% faster at batch 1 and 22% faster at batch 8 than an explicit DeepGEMM runner, with equal GSM8K accuracy ([General Performance E02](features/p0-general-performance/data/data@2026-11-11-0a30c79a92e3428c74e249a0270eb0ce8a42c32f-vr-moe-backend/repro.md)); a split-K sparse decode config by local head count is 0.71–1.00× the previous time per call ([Kernel Optimization E02](features/p0-kernel-opt/data/data@2026-11-11-b04b763b055e1a04358f03f6666280e00c54389c-vr-split-decode/repro.md)). Both are non-release.
- The hybrid window KV layout passes full GSM8K with MTP after the window-slot KV fix ([Correctness E06](features/p0-correctness/data/data@2026-11-12-710bcb2a3e6e4abbc299b43860c6528f7bd81db8-window-layout-matrix/repro.md)), under prefill CP4 and CP8 ([Prefill CP E01–E03](features/p0-parallelism/prefill-cp/README.md)), under DEP4 and DEP8 ([DP Attention E01–E02](features/p0-parallelism/dp-attention/README.md)), with host and file HiCache ([HiCache E02–E03](features/p0-hicache/README.md)), and over cross-node PD with Mooncake RDMA ([PD Disaggregation E01–E03](features/p0-pd-disagg/README.md)); the PD change is merged. All are single runs on unlocked environments and non-release.
- The upstream `main` merge passes TP8 and DEP8 GSM8K gates on B300 ([Correctness E08](features/p0-correctness/data/data@2026-11-14-c6a9b3411f3db9fa1a4244ec6eede2a43bbf5550-main-merge-gate/repro.md), [E09](features/p0-correctness/data/data@2026-11-15-ec8bc57fde48466d602529752d428b466efc54cf-main-merge-dep8/repro.md)). Open observation: on DEP8 with FP8 KV, greedy retrieval of a random record succeeds for 6 to 8 of 12 prompts at 60K tokens and above on every layout; BF16 KV, TP8 and thinking-on arms miss at the same rate, so no serving configuration is attributed and the observation is treated as non-blocking ([Correctness E11](features/p0-correctness/data/data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-retrieval/repro.md), [E12](features/p0-correctness/data/data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-attribution/repro.md)). Pull request 67, merged as `dbfef91e`, makes the window layout the default and passed the TP8 gate on its head ([Correctness E13](features/p0-correctness/data/data@2026-11-15-fb4015b5bdb6ed416beba624f365407089567b53-window-default-tp8/repro.md)); on that head the window and full-length layouts serve at the same speed on DEP8 and TP8 ([Correctness E14](features/p0-correctness/data/data@2026-11-15-fb4015b5bdb6ed416beba624f365407089567b53-window-layout-speed/repro.md)). Unified memory is unsupported for this model; a staged port is scoped in [Unified Memory](features/p1-unified-memory/README.md).
- On `dbfef91e` with FlashInfer 0.7.4, the version the code pins, full GSM8K with MTP and the default window layout passes on 8 B300 GPUs at TP8 and DEP8 and on 8 H200 GPUs at TP8; H200 holds about 12% of the B300 KV tokens under the same flags and needs `sgl-fa3` added to its image ([Correctness E15](features/p0-correctness/data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-flashinfer-074-h200/repro.md)). Run back to back at TP8 on B300, FlashInfer 0.7.3 and 0.7.4 give counter-based MTP accept lengths within 0.9% of each other (2.65 against 2.64 at temperature 1.0 / top_p 0.95) in single unseeded runs ([Correctness E16](features/p0-correctness/data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-flashinfer-073-074-accept-length/repro.md)). TP8 with FP8 KV on the `trtllm` DSA routes completes full GSM8K on B300 at 95.07% accuracy and 99.77% stop rate and holds 1.94× the full-length KV tokens of BF16; against a same-day BF16 server its output throughput was 6–9% lower at concurrency 1 and 2–13% higher at concurrency 32 and on 30K-token inputs, in one launch per arm ([Correctness E17](features/p0-correctness/data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-tp8-fp8-kv/repro.md)).
- On 4 GB300 GPUs at `dbfef91e`, a sweep of eight serving configurations on a four-turn chat workload (inputs up to about 4.7K tokens, 128 output tokens per turn, concurrency 1 to 8) scores TP4 with BF16 KV and MTP off highest at concurrency 8 (2060 total tokens/s per GPU, 284 output tokens/s, P90 TTFT 0.91 s); MTP raises throughput at concurrency 1 and lowers it at concurrency 8, where the MTP configurations miss the 30 tokens/s interactivity target. Run on FlashInfer 0.7.3 with one launch per configuration and no accuracy evaluation; non-release ([General Performance E03](features/p0-general-performance/data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-gb300-serve-sweep/repro.md)).
- The Rust MoE sweep at `dbfef91e7d` covers six FP8-weight configurations and 72 loads. TRTLLM MoE with FP8 KV/TRTLLM DSA and MTP off reaches the highest passing measured score at C32: 5261.1 total tok/s/GPU. Paired NVFP4 coverage remains in progress; MTP P90 retains a raw-data limitation ([General Performance E05](features/p0-general-performance/data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-rust-moe-sweep/repro.md)).
- Current integration `01d0a662d1` completes the paired Rust FP8/NVFP4 KV matrix: 48 loads and 5,120 successful requests. C32 NVFP4 gains 21.35% with BF16 KV and 19.24% with FP8 KV over matched FP8 weights; full-GSM8K stop nonregression remains unmet ([General Performance E06](features/p0-general-performance/data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-paired-kv-mtp-off/repro.md)).
- Current integration `01d0a662d1` completes the paired natural-MTP sweep: 48 loads/5,120 successful requests, all four weight/KV configurations passing through C4. NVFP4 gains 3.78% with BF16 KV and 7.75% with FP8 KV at C4; server seeds differ and full stopping nonregression remains unmet ([General Performance E07](features/p0-general-performance/data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-paired-natural-mtp/repro.md)).
- B300 Rust revalidation at historical `dbfef91e7d` completes three full GSM8K arms: TP8 BF16 94.24% accuracy/99.70% stop, TP8 FP8 KV 94.84%/100%, DEP8 94.39%/99.92%. BF16 and DEP8 stopping nonregression remains unmet ([Correctness E19](features/p0-correctness/data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-b300-rust-regate/repro.md)).
- [General Performance E08](features/p0-general-performance/data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-paired-fixed-seed-mtp/repro.md) completes the current fixed-seed FP8/NVFP4 controlled comparison: 100 loads, with NVFP4 C32 gains of 17.90–18.43% under simulated acceptance 3.5 and 19.08–20.66% with MTP off. All tested points pass through C32; stopping nonregression remains unmet.
- [Correctness E20](features/p0-correctness/data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-h200-rust-regate/repro.md) completes the historical H200 TP8 Rust gate: 1251/1319 correct, 1316 stop, three length truncations and zero errors. Eight actual Rust worker mappings are verified; stopping nonregression remains unmet.
- [Correctness E21](features/p0-correctness/data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-current-h200-rust/repro.md) completes current H200 TP8 Rust validation at `01d0a662d1`: 1258/1319 correct, 1317 stop, two length truncations and zero errors. One truncated answer is correct; stopping nonregression remains unverified for these settings. Eight live Rust mappings, actual imports, source integrity and cleanup are verified.
- [Correctness E22](features/p0-correctness/data/data@2026-11-16-52ef77912fd004f34cfe340b392018632ce69c2c-fallback-h200-rust/repro.md) records candidate `52ef77912f` on H200 TP8: 1251/1319 correct, 1314 stop, five length truncations and zero errors. Exact source and eight live Rust mappings are verified; stopping qualification remains open.
- [Correctness E23](features/p0-correctness/data/data@2026-11-16-52ef77912fd004f34cfe340b392018632ce69c2c-h200-python-reference/repro.md) adds the same-candidate H200 Python TreeCore reference: 1256/1319 correct, 1316 stop, three length truncations and zero errors. Both backends truncate; stopping qualification remains open.
- [Correctness E24](features/p0-correctness/data/data@2026-11-16-52ef77912fd004f34cfe340b392018632ce69c2c-fallback-paired-tp4/repro.md) records fallback-candidate TP4 full GSM8K: FP8 1258 correct/1318 stop; NVFP4 1240 correct/1312 stop, each out of 1319 with zero errors. All four live Rust workers and both complete raw outputs are verified; NVFP4 remains performance-only.
- [Correctness E25](features/p0-correctness/data/data@2026-11-16-52ef77912fd004f34cfe340b392018632ce69c2c-fallback-paired-cp4/repro.md) records the fallback CP4 pair: FP8 retrieval17/18, NVFP4 retrieval18/18, prefix6/6 each. Full GSM8K has7/5 length truncations; CP4 and stopping qualification remain open.
- [Correctness E26](features/p0-correctness/data/data@2026-11-17-52ef77912fd004f34cfe340b392018632ce69c2c-fallback-paired-b300/repro.md) completes the candidate B300 TP8 BF16-KV, TP8 FP8-KV and DEP8 FP8/NVFP4 pairs. All six full GSM8K runs have zero errors; normal stops range from 1311 to 1316 of 1319. Exact source, eight live Rust workers, controlled ownership and cleanup verify; final stopping and image qualification remain open.
- [Correctness E27](features/p0-correctness/data/data@2026-11-17-52ef77912fd004f34cfe340b392018632ce69c2c-fallback-paired-dp4/repro.md) completes candidate DP4: FP8/NVFP4 have 1250/1247 correct and 1313 normal stops each; both have zero errors. Retrieval passes 17/18 and 18/18; directed routing/cache passes 16/16 each. The FP8 retrieval failure and final stopping acceptance remain open.
- [Correctness E28](features/p0-correctness/data/data@2026-11-17-52ef77912fd004f34cfe340b392018632ce69c2c-fallback-retrieval-diagnosis/repro.md) completes bounded FP8 retrieval diagnosis: CP4/TP4 at cap 96 return 22/22 and 20/22 exact stopped answers; the matched TP4 cap 2048 follow-up returns22/22. The original CP4 wrong answer is unreproduced; the follow-up has recorded runtime evidence but lacks a separate independent live startup receipt.
- On 2×4 GB300 under PD (TP4 prefill with the Mooncake-store linker, DPA4 + EP4 + MTP decode, BF16 KV), HiSparse on the decode server, from `radixark/sglang-zai` pull request 84 evaluated as `76e1c381`, was tested on AgentX trace replay. At decode saturation it raises decode output throughput from 471 to 788–837 tok/s (+67–78%), with ITL p50 rising from 20.5 to 37–41 ms. At the same decode batch it adds 12–35% ITL. End to end it adds 18.6% total throughput at c16 and 10.3% at c32, where the single prefill binds ([AgentX E05](features/p0-agentx-performance/data/data@2026-11-17-76e1c3816e1835916cde9540700b1865f398e6ce-hisparse-pd/repro.md)). GSM8K, GPQA diamond and RULER2 32K aggregates stay within 2.5 points of the plain decode, with RULER2 `mv_niah_hard` 10 points lower in one run as an open observation ([Correctness E29](features/p0-correctness/data/data@2026-11-16-76e1c3816e1835916cde9540700b1865f398e6ce-hisparse-pd/repro.md)). Model revision `66c3fe71`; non-release. When to enable it: the [HiSparse decode](features/p0-agentx-performance/README.md#hisparse-decode) tuning entry.
- Release scope, owners, gates, and artifacts are tracked in [Day-0 Delivery](day0-delivery/README.md).

[Breakable prefill E02](features/p1-breakable-cuda-graph/data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-paired-prefill-graphs/repro.md) records 144 paired FP8/NVFP4 loads on current `01d0a662d1`. Natural MTP passes through C4 with eager prefill and C8 with breakable; NVFP4 gains 26.00% at breakable C8. Off and controlled grids pass through C32; full stopping qualification remains unmet.

Current Rust [paired CP4 validation](features/p0-parallelism/prefill-cp/data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-paired-rust-cp4/repro.md) records FP8 1238/1319 correct and 1313 stop; NVFP4 1250 correct and 1315 stop. NVFP4 retrieval 17/18 keeps its feature gate unmet; full evidence is separate from the TP4 non-CP comparison.

- [General Performance E09](features/p0-general-performance/data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-moe-dispatch-coverage/repro.md) pins current MoE dispatch coverage: NVFP4 DeepGEMM is unsupported on the standard path; FP8 CUTLASS/CuTeDSL requests resolve to Triton. Alternative-runner GPU validation remains pending.

- [DP Attention E03](features/p0-parallelism/dp-attention/data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-paired-rust-dp4/repro.md) completes current FP8/NVFP4 Rust DP4 measurements: correct/stop 1249/1308 and 1251/1313 of 1319, with zero errors. Retrieval 18/18 and directed routing/cache 16/16 pass for each; stopping nonregression remains unmet.
- [DP Attention E04](features/p0-parallelism/dp-attention/data/data@2026-11-16-01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb-paired-tp4-dep4-performance/repro.md) records 100 paired TP4/DEP4 loads with FP8/NVFP4. MTP-off best passing concurrency is C32 TP4/C16 DEP4; NV gains 16.65%/15.00%. Controlled DEP4 C16 observed delta is +4.68%; TP4 C32 is a near tie (+1.32%) with repeat dispersion retained. Actual scheduler subdivisions and failed SLO points are preserved; stopping qualification remains unmet.

## Branches

- `track`(default): Stores planning, validation, feature evidence, and release-delivery records on standalone orphan history.
- `sglang-main`: Mirrors the latest upstream SGLang `main` and provides the clean baseline for starting or updating Day-0 model work. It is deliberately not named `main`, so upstream's `push: branches: [main]` workflows do not fire in this repository on every sync.
- `dev`: Maintains a second exact, fast-forward-only mirror of upstream SGLang `main` and serves as the base for short-lived Day-0 implementation branches. Do not commit or merge Day-0 changes directly into it.
- `ref-code`: Stores simple, readable reference implementations, such as naïve PyTorch implementations, for correctness validation and comparison.

## Repository Structure

```text
(branch root)
├── .github/
│   └── workflows/
│       └── sync-sglang-main.yml
├── README.md
├── AGENTS.md
├── CLAUDE.md
├── scripts/
│   └── sync_sglang_main.sh
├── features/
│   ├── p0-correctness/
│   ├── p0-tool-call-parser/
│   ├── p0-reasoning-parser/
│   ├── p0-general-performance/
│   ├── p0-agentx-performance/
│   ├── p0-kernel-opt/
│   ├── p0-spec-decoding-training/
│   ├── p0-pd-disagg/
│   ├── p0-hicache/
│   ├── p0-megamoe/
│   ├── p0-parallelism/
│   │   ├── analysis-and-design/
│   │   ├── dp-attention/
│   │   ├── prefill-cp/
│   │   ├── decode-cp/
│   │   ├── pp/
│   │   └── wide-ep/
│   ├── p1-breakable-cuda-graph/
│   ├── p1-unified-memory/
│   ├── p1-multimodal-opt/
│   │   ├── epd-disagg/
│   │   ├── dp-encoder/
│   │   └── encoder-cuda-graph/
│   ├── p1-multi-platform/
│   │   ├── nvidia-hopper/
│   │   ├── amd/
│   │   ├── intel-xpu-xeon/
│   │   ├── ascend-npu/
│   │   └── tpu/
│   └── p1-rl/
└── day0-delivery/
    ├── README.md
    ├── cookbook/
    │   └── README.md
    ├── docker/
    │   └── README.md
    └── blog/
        └── README.md
```

Every feature and subproject directory contains a `README.md`.

The template intentionally starts without experiment data, reproduction scripts, or release assets. Add those artifacts only when real work produces them.

## Directory Responsibilities

| Path | Responsibility |
|---|---|
| `.github/workflows/` | Scheduled and manually dispatched repository automation. |
| `AGENTS.md` | Canonical operating rules, content-routing rules, and reusable templates for agents and contributors. |
| `CLAUDE.md` | Entry point that directs Claude-compatible agents to the canonical rules. |
| `scripts/` | Implementations for repository automation. |
| `features/` | Capability projects and selectable subprojects, each with its own summary, assignees, stages, and experiment index. |
| `day0-delivery/` | Release coordination, artifact locks, and the cookbook, Docker, and blog deliverables. |

## Feature Catalog

The catalog contains P0 and P1 tracking projects. New top-level features follow `features/p<X>-<feature-name>`; subprojects use lowercase, hyphen-separated directory names. Select the required subprojects within Parallelism, Multimodal Optimization, and Multi-Platform Support. Complete Parallelism Analysis and Design before implementing any concrete parallelism feature.

| Project | Purpose | Status | Assignees |
|---|---|---|---|
| `features/p0-correctness/` | Validate model quality, API behavior, feature compatibility, and regression gates. | In progress | `<OWNER>` |
| [Tool-Call Parser](features/p0-tool-call-parser/README.md) | Implement and validate the tool-call detector and parser auto-detection against the model's native call format. | Not started | `<OWNER>` |
| [Reasoning Parser](features/p0-reasoning-parser/README.md) | Implement and validate the reasoning parser, thinking defaults, and supported reasoning levels. | Not started | `<OWNER>` |
| `features/p0-general-performance/` | Track one-batch and serving performance across representative workloads and hardware. | In progress | `<OWNER>` |
| `features/p0-agentx-performance/` | Measure agentic-workload latency, throughput, concurrency scaling, and cache behavior. | In progress | `<OWNER>` |
| `features/p0-kernel-opt/` | Track kernel bottlenecks, optimization stages, microbenchmarks, and end-to-end impact. | In progress | `<OWNER>` |
| `features/p0-spec-decoding-training/` | Track draft-model training, checkpoint selection, evaluation, and release readiness. | In progress | `<OWNER>` |
| [Prefill–Decode Disaggregation](features/p0-pd-disagg/README.md) | Separate prefill and decode resources and validate routing, KV transfer, and latency. | In progress | `<OWNER>` |
| [Hierarchical KV Caching (HiCache)](features/p0-hicache/README.md) | Reuse prompt prefixes across GPU, host, and storage cache tiers. | In progress | `<OWNER>` |
| [MegaMoE](features/p0-megamoe/README.md) | Evaluate and integrate the selected MegaMoE implementation. | Not started | `<OWNER>` |
| [Parallelism](features/p0-parallelism/README.md) | Complete the shared design, then implement selected parallelism strategies. | In progress | `<OWNER>` |
| [Breakable CUDA Graph](features/p1-breakable-cuda-graph/README.md) | Combine captured graph segments with operations that require eager execution. | In progress; enabled by default after #85; E03 FP8-KV sweep complete | `<OWNER>` |
| [Unified Memory](features/p1-unified-memory/README.md) | Evaluate memory-management support, capacity, and latency tradeoffs. | In progress | `<OWNER>` |
| [Multimodal Optimization](features/p1-multimodal-opt/README.md) | Select and validate encoder and serving optimizations for multimodal workloads. | Not started | `<OWNER>` |
| [Multi-Platform Support](features/p1-multi-platform/README.md) | Select and validate hardware platforms required for the model release. | In progress | `<OWNER>` |
| [Reinforcement Learning](features/p1-rl/README.md) | Define and validate serving integration for reinforcement-learning workflows. | Not started | `<OWNER>` |

Recommended status values are `Not started`, `In progress`, `Blocked`, and `Complete`.

## Content Routing

| Content | Destination |
|---|---|
| Reusable benchmark and operation-record formats | `AGENTS.md` |
| Feature goal, technical decision, todo, or progress update | The corresponding `features/<project>/README.md` stage |
| Reproduction script used by one feature | `features/<project>/scripts/vN/` |
| One reproducible experiment round | `features/<project>/data/data@<YYYY-MM-DD>-<CODE_SHA>/` |
| Release-wide status or immutable artifact pin | `day0-delivery/README.md` |
| Deployment guidance for users | `day0-delivery/cookbook/` |
| Container build and publication material | `day0-delivery/docker/` |
| Release announcement and supporting prose | `day0-delivery/blog/` |

## Placeholder Convention

Angle-bracket tokens identify information that must be supplied by a model-support team. Common placeholders include:

- `<MODEL_NAME>`
- `<OWNER>`
- `<STATUS>`
- `<YYYY-MM-DD>`
- `<CODE_SHA>`
- `<MODEL_REVISION>`
- `<HARDWARE>`
- `<IMAGE_DIGEST>`
- `<METRIC>`
- `<PR_URL>`

Replace placeholders only when the value is known and can be linked to reproducible evidence. Do not publish unbound performance or correctness numbers.
