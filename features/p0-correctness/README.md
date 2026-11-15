# Correctness

## Summary

`zai-org/GLM-5-1028-Provider` (GLM LoopLM, `GlmLoopForConditionalGeneration`) correctness tracking covers model quality, API behavior, feature compatibility, and release-gating regressions. Status: In progress. E01–E03 and E05 use `a15aa7c3` on `glm-5-lp`; E04 uses `8451a1bf` on `fix/glm5-lp-implementation`; all use model revision `7e66c405`. The H200 bring-up ([E01](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md)) passed configuration, model, attention, checkpoint-map, text, image, and long-context checks. E02 recorded H200 baseline GSM8K-200 and the built-in MTP/decode-graph smoke. B300 MTP completed full GSM8K at 93.86% accuracy with 99.24% stop rate and GPQA-4096 at 45.52% pass@1 and 69.19% pass@8; GPQA truncation was 51.33% ([E03](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-b300-mtp-evaluation/repro.md)). The optional vision SwiGLU fix passed 42 unit tests, text/image E2E, and full GSM8K at 95.22% accuracy with 99.32% stop rate ([E04](data/data@2026-11-03-8451a1bf9d6156a8ff76f8d603abe9a89c1b1002-swiglu-fix/repro.md)). H200 MTP completed full GSM8K at 94.31% accuracy and GPQA at 52.53% pass@1 and 75.76% pass@8 with 43.31% truncation at context length 8192 ([E05](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-h200-mtp-evaluation/repro.md)). Release accuracy, API, configuration, and artifact gates remain open. After the window-slot KV fix at `710bcb2a` the hybrid window layout passes full GSM8K with MTP ([E06](data/data@2026-11-12-710bcb2a3e6e4abbc299b43860c6528f7bd81db8-window-layout-matrix/repro.md)); the upstream `main` merge passes TP8 and DEP8 gates on B300 ([E08](data/data@2026-11-14-c6a9b3411f3db9fa1a4244ec6eede2a43bbf5550-main-merge-gate/repro.md), [E09](data/data@2026-11-15-ec8bc57fde48466d602529752d428b466efc54cf-main-merge-dep8/repro.md)); the window layout as the default passes DEP8 on its first revision and TP8 on the head of pull request 67 ([E10](data/data@2026-11-15-5e6ee4ed50fc91fee9c5a0484667ce6de2ba5640-window-default-dep8/repro.md), [E13](data/data@2026-11-15-fb4015b5bdb6ed416beba624f365407089567b53-window-default-tp8/repro.md)) and serves at the same speed as the full-length layout ([E14](data/data@2026-11-15-fb4015b5bdb6ed416beba624f365407089567b53-window-layout-speed/repro.md)); long-context random-record retrieval misses at 60K tokens and above on every tested serving configuration and is treated as non-blocking ([E11](data/data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-retrieval/repro.md), [E12](data/data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-attribution/repro.md)).

## Scope

### In Scope

- Text generation quality and deterministic smoke tests.
- Chat-template and reasoning-mode behavior, consuming evidence from `features/p0-reasoning-parser/`.
- Tool use, structured output, and API compatibility, consuming evidence from `features/p0-tool-call-parser/`.
- Long-context, batching, parallelism, and cache correctness.
- Multimodal correctness when the model exposes multimodal inputs.
- Cross-platform and cross-configuration regression gates.

### Out of Scope

- Tool-call detector and reasoning parser implementation and their detailed validation matrices, owned by `features/p0-tool-call-parser/` and `features/p0-reasoning-parser/`.
- Performance tuning that does not change outputs.
- Unreleased capabilities outside `<RELEASE_SCOPE>`.
- Evaluation datasets without a stable revision and reproducible scorer.

## Success Criteria

- [ ] The release capability matrix has no unexplained gaps.
- [ ] Every required evaluation meets `<QUALITY_GATE>` against `<REFERENCE_RESULT>`.
- [ ] Required APIs pass `<API_COMPATIBILITY_GATE>`.
- [ ] Required hardware and parallel configurations pass `<CONFIGURATION_GATE>`.
- [ ] All release results are pinned to `<CODE_SHA>` and `<MODEL_REVISION>`.
- [ ] Every failure has an owner, severity, reproduction record, and release decision.

## Capability Matrix

Rows are pinned to code commit `a15aa7c3` unless the row names another commit; all rows use model revision `7e66c405`. "H200 TP8 baseline" means 8 H200 GPUs, TP8, Triton MoE, FlashMLA Sparse, BF16 KV cache, CUDA graph disabled, and MTP disabled.

| Capability | Mode | Configuration | Gate | Status | Evidence | Owner |
|---|---|---|---|---|---|---|
| Loop config expansion (78 physical layers to 106 slots) | CPU unit test | `test_glm_loop_config.py` | all tests pass | Complete | [E01](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md) | `<OWNER>` |
| Loop and model logic | CPU unit test | `test_glm_loop.py` | all tests pass | Complete | [E01](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md) | `<OWNER>` |
| Dual-bank sparse attention | GPU kernel test | H200, FlashMLA Sparse | all applicable tests pass | Complete | [E01](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md) | `<OWNER>` |
| Checkpoint weight mapping | Metadata test | `test_glm_loop_checkpoint_map.py` | all tests pass | Complete | [E01](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md) | `<OWNER>` |
| Text chat | Greedy smoke | H200 TP8 baseline | expected answer and `finish_reason=stop` | Complete | [E01](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md) | `<OWNER>` |
| Image input | Greedy smoke | H200 TP8 baseline | expected answer and `finish_reason=stop` | Complete | [E01](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md) | `<OWNER>` |
| Long context beyond the 2048-token Top-K | Greedy smoke, 2747 prompt tokens | H200 TP8 baseline | expected answer and `finish_reason=stop` | Complete | [E01](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md) | `<OWNER>` |
| Text accuracy and stop rate | Evaluation | H200 TP8 baseline; GSM8K-200; temperature 1.0, top_p 0.95 | Report accuracy and stop rate; release threshold `<QUALITY_GATE>` | Complete | 95.50% accuracy, 100% stop rate, 0% truncation; [E02](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-mtp-cuda-graph/repro.md) | `<OWNER>` |
| Reasoning and tool-call parsing | API | `<CONFIGURATION>` | `<PASS_CRITERION>` | Not started | None | `<OWNER>` |
| MTP speculative decoding | Serving | H200 TP8; EAGLE 3/1/4; decode CUDA graph | Expected output, acceptance length, and normal stop behavior | Complete | `accept len=2.27`, normal stop; [E02](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-mtp-cuda-graph/repro.md) | `<OWNER>` |
| CUDA graph replay | Serving | H200 TP8; decode CUDA graph; MTP enabled | Successful capture and correct replay output | Complete | `cuda graph: True`; [E02](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-mtp-cuda-graph/repro.md) | `<OWNER>` |
| Expert parallelism, attention DP, FP8 KV cache, and `trtllm` DSA backend | Serving | 8x B300 DEP8, `trtllm`, FP8 KV, MTP at `c6a9b341` and `ec8bc57f`; 4x GB300 `trtllm` BF16 and FP8 at `710bcb2a` | Full GSM8K stop rate; release threshold `<QUALITY_GATE>` | In progress | DEP8 95.07% / 100% stop and 94.62% / 99.85% stop ([E08](data/data@2026-11-14-c6a9b3411f3db9fa1a4244ec6eede2a43bbf5550-main-merge-gate/repro.md), [E09](data/data@2026-11-15-ec8bc57fde48466d602529752d428b466efc54cf-main-merge-dep8/repro.md)); `trtllm` BF16 and FP8 ([E06](data/data@2026-11-12-710bcb2a3e6e4abbc299b43860c6528f7bd81db8-window-layout-matrix/repro.md)); long-context retrieval misses on every tested configuration, non-blocking ([E11](data/data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-retrieval/repro.md), [E12](data/data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-attribution/repro.md)) | `<OWNER>` |
| Prefill–decode and encoder disaggregation | Serving | 2 nodes x 4 GB300, 1P1D, Mooncake RDMA, KV checksum, MTP at `bdbebf62`; encoder disaggregation not run | Full GSM8K stop rate through the router; release threshold `<QUALITY_GATE>` | In progress | Window 95.07% / 99.55% stop, full-length 94.69% / 99.70% stop ([PD Disaggregation E03](../p0-pd-disagg/data/data@2026-11-15-bdbebf62fca4af4e628e26f9e55d139bb7794047-rdma-window-full-hicache/repro.md)) | `<OWNER>` |

## Reference Results

No reference results are recorded. The reference implementation and evaluation revisions are not yet pinned.

## Accuracy Results

GSM8K-200 on the H200 TP8 baseline reached 95.50% accuracy, 100% stop rate, 0% truncation, and 0% request errors at `a15aa7c3` and model revision `7e66c405` ([E02](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-mtp-cuda-graph/repro.md)).

B300 MTP full GSM8K reached 93.86% accuracy, 99.24% stop rate, 0.76% truncation, and 0% request errors. B300 MTP GPQA-4096 reached 45.52% pass@1, 69.19% pass@8, and 68.69% majority@8, with 48.67% stop rate and 51.33% truncation ([E03](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-b300-mtp-evaluation/repro.md)). The GPQA values are specific to the 4096-token output budget.

At `8451a1bf`, the optional vision SwiGLU fix passed full GSM8K with 95.22% accuracy, 99.32% stop rate, 0.68% truncation, and 0% request errors ([E04](data/data@2026-11-03-8451a1bf9d6156a8ff76f8d603abe9a89c1b1002-swiglu-fix/repro.md)).

H200 MTP full GSM8K reached 94.31% accuracy, 99.39% stop rate, 0.61% truncation, and 0% request errors. H200 MTP GPQA reached 52.53% pass@1, 75.76% pass@8, and 74.49% majority@8, with 56.69% stop rate and 43.31% truncation at context length 8192 ([E05](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-h200-mtp-evaluation/repro.md)).

On 4x GB300 at `710bcb2a` with the hybrid window KV layout, MTP and decode CUDA graphs, full GSM8K reached 95.68% accuracy with 99.47% stop rate; with the `trtllm` DSA backend 94.01% / 99.62% (BF16 KV) and 95.07% / 99.70% (FP8 KV) ([E06](data/data@2026-11-12-710bcb2a3e6e4abbc299b43860c6528f7bd81db8-window-layout-matrix/repro.md)). Window-layout results under prefill CP, attention DP, PD and HiCache are in their feature rounds.

On 8x B300 after the upstream `main` merge, full GSM8K reached 94.69% accuracy with 99.92% stop rate at TP8 and 95.07% with 100% stop rate at DEP8 on `c6a9b341` ([E08](data/data@2026-11-14-c6a9b3411f3db9fa1a4244ec6eede2a43bbf5550-main-merge-gate/repro.md)), and 94.62% with 99.85% stop rate at DEP8 on the pushed `ec8bc57f` ([E09](data/data@2026-11-15-ec8bc57fde48466d602529752d428b466efc54cf-main-merge-dep8/repro.md)). These runs used FlashInfer 0.7.3 although the merged code pins 0.7.4.

On 8x B300 at `fb4015b5`, the head of pull request 67 that makes the window layout the default, full GSM8K at TP8 reached 94.92% accuracy with 99.77% stop rate and 3 truncated requests ([E13](data/data@2026-11-15-fb4015b5bdb6ed416beba624f365407089567b53-window-default-tp8/repro.md)).

## Assignees

- `<OWNER>` — `<RESPONSIBILITY>`

## Stages

### Stage 1: Establish reference behavior — Not started

- [ ] Pin `<REFERENCE_IMPLEMENTATION>`, `<MODEL_REVISION>`, and evaluation revisions.
- [ ] Define release capabilities and required configurations.
- [ ] Record reference results with raw evidence.

### Stage 2: Validate implementation — In progress

- Experiment [E01](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md): at `a15aa7c3`, the H200 TP8 baseline passed configuration, model, attention, and checkpoint-map tests and the text, image, and long-context smokes.
- Experiment [E02](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-mtp-cuda-graph/repro.md): GSM8K-200 reached 95.50% accuracy with 100% stop rate and 0% truncation; built-in MTP returned `accept len=2.27` with `cuda graph: True`.
- Experiment [E03](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-b300-mtp-evaluation/repro.md): B300 MTP full GSM8K reached 93.86% accuracy with 99.24% stop rate; GPQA-4096 reached 45.52% pass@1 and 69.19% pass@8 with 51.33% truncation.
- Experiment [E04](data/data@2026-11-03-8451a1bf9d6156a8ff76f8d603abe9a89c1b1002-swiglu-fix/repro.md): at `8451a1bf`, the optional vision SwiGLU fix passed 42 unit tests, text/image E2E, and full GSM8K at 95.22% accuracy with 99.32% stop rate.
- Experiment [E05](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-h200-mtp-evaluation/repro.md): H200 MTP full GSM8K reached 94.31% accuracy with 99.39% stop rate; GPQA reached 52.53% pass@1 and 75.76% pass@8 with 43.31% truncation at context length 8192.
- Experiment [E06](data/data@2026-11-12-710bcb2a3e6e4abbc299b43860c6528f7bd81db8-window-layout-matrix/repro.md): at `710bcb2a`, after the window-slot KV fix (pull request 42), the hybrid window layout passed full GSM8K with MTP and decode CUDA graphs at 95.68% accuracy and 99.47% stop on 4x GB300; the `trtllm` DSA backend passed with BF16 KV (94.01% / 99.62%) and FP8 KV (95.07% / 99.70%).
- Experiment [E07](data/data@2026-11-13-802d8157b74564997e350ffa981b5e567e391920-topk-by-reference-gate/repro.md): the Top-K-by-reference change (pull request 43, merged as `8f5dff0f`) truncated 3 of 2638 GSM8K requests on each arm against its base on 8x B300.
- Experiment [E08](data/data@2026-11-14-c6a9b3411f3db9fa1a4244ec6eede2a43bbf5550-main-merge-gate/repro.md): the local merge of upstream `main` (`c6a9b341`) passed TP8 (94.69% / 99.92% stop) and DEP8 (95.07% / 100% stop) on 8x B300. Experiment [E09](data/data@2026-11-15-ec8bc57fde48466d602529752d428b466efc54cf-main-merge-dep8/repro.md): the pushed merge `ec8bc57f` passed DEP8 at 94.62% / 99.85% stop.
- Experiment [E10](data/data@2026-11-15-5e6ee4ed50fc91fee9c5a0484667ce6de2ba5640-window-default-dep8/repro.md): a local, unpublished change that makes the window layout the default passed DEP8 at 95.45% / 100% stop with no layout variable set. Preview, non-release; its current version `1c6afefe` also removes the layout environment variable and has no GSM8K run.
- Experiment [E13](data/data@2026-11-15-fb4015b5bdb6ed416beba624f365407089567b53-window-default-tp8/repro.md): the same change as pull request 67 (open, head `fb4015b5`, tree identical to `1c6afefe`) passed TP8 at 94.92% / 99.77% stop with 3 of 1319 truncated and no layout flag. DEP8 was not rerun on this head.
- Experiment [E14](data/data@2026-11-15-fb4015b5bdb6ed416beba624f365407089567b53-window-layout-speed/repro.md): on the same head, `bench_serving` random-ID workloads and an 8-turn chat show no speed difference between the default layout and `--disable-hybrid-swa-memory` on DEP8 `trtllm` FP8 and TP8 BF16; differences stay within seed and relaunch spread.
- Open observation, experiment [E11](data/data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-retrieval/repro.md): on DEP8 with the `trtllm` DSA backend and FP8 KV, greedy thinking-off retrieval of a random record succeeds for 6 to 8 of 12 prompts at 60K and at 120.9K tokens on the window layout, the full-length layout and the pre-merge code alike. The layout and the merge are ruled out; attribution is pending and no conclusion is drawn.
- Experiment [E12](data/data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-attribution/repro.md): on the same prompts, DEP8 with BF16 KV, TP8 with BF16 KV and `flashmla_sparse`, and thinking on all miss as well (6 to 10 of 12 correct per cell); thinking on removes only the requests that hit `max_tokens`. No tested serving configuration changes the miss rate. The project owner's working assessment is a retrieval limit of the checkpoint itself; it is not verified against a reference implementation and is treated as non-blocking.
- [ ] Run smoke, quality, API, and configuration matrices on `<CODE_SHA>`.
- [ ] Triage deltas and bind each issue to `<OWNER>`.
- [ ] Add regression coverage for every fixed release-blocking issue.
- Next action: validate reasoning and tool-call behavior, then evaluate performance and alternative parallel and KV-cache configurations.

### Stage 3: Certify release artifacts — Not started

- [ ] Rerun gates on the locked code, model, and container artifacts.
- [ ] Resolve every failed or missing cell with an explicit release decision.
- [ ] Link final evidence from `day0-delivery/README.md`.

## Experiments

| ID | Date | Topic | Basic Setting | Result | Round |
|---|---|---|---|---|---|
| E01 | `2026-11-02` | H200 TP8 bring-up | 8x H200; unit, kernel, and checkpoint-map tests plus text, image, and long-context smokes; TP8, Triton MoE, FlashMLA Sparse, BF16 KV, no CUDA graph, no MTP | All tests and smokes passed at `a15aa7c3` with model revision `7e66c405`. | [round](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md) |
| E02 | `2026-11-02` | Baseline accuracy and MTP smoke | Subrun A: 8x H200, TP8, Triton MoE, BF16 KV, no CUDA graph and no MTP. Subrun B: same base with EAGLE 3/1/4 and decode CUDA graph. | Subrun A: 95.50% accuracy, 100% stop rate, 0% truncation. Subrun B: `accept len=2.27`; `cuda graph: True`. Results are bound to their respective subruns. | [round](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-mtp-cuda-graph/repro.md) |
| E03 | `2026-11-02` | B300 MTP full evaluation | 8x B300, TP8, DeepGEMM MoE, EAGLE 3/1/4 and decode CUDA graph; full GSM8K and GPQA-Diamond with 4096 output tokens | GSM8K: 93.86% accuracy, 99.24% stop rate. GPQA-4096: 45.52% pass@1, 69.19% pass@8, 51.33% truncation. | [round](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-b300-mtp-evaluation/repro.md) |
| E04 | `2026-11-03` | Optional vision SwiGLU fix | `8451a1bf`; 8x B300, TP8, DeepGEMM MoE, EAGLE 3/1/4 and decode CUDA graph; unit tests, text/image E2E and full GSM8K | 42 tests passed; all requests stopped normally. GSM8K: 95.22% accuracy, 99.32% stop rate, 0% request errors. | [round](data/data@2026-11-03-8451a1bf9d6156a8ff76f8d603abe9a89c1b1002-swiglu-fix/repro.md) |
| E05 | `2026-11-02` | H200 MTP full evaluation | 8x H200, TP8, Triton MoE, EAGLE 3/1/4 and decode CUDA graph; full GSM8K and GPQA-Diamond with context length 8192 | GSM8K: 94.31% accuracy, 99.39% stop rate. GPQA: 52.53% pass@1, 75.76% pass@8, 43.31% truncation. | [round](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-h200-mtp-evaluation/repro.md) |
| E06 | `2026-11-12` | Window layout validation matrix | `710bcb2a`; 4x GB300, TP4, EAGLE 3/1/4 and decode CUDA graph; hybrid window KV layout; `flashmla_sparse`, `trtllm` BF16 and `trtllm` FP8 | GSM8K 95.68% / 99.47% stop; `trtllm` BF16 94.01% / 99.62%; `trtllm` FP8 95.07% / 99.70%; prefix reuse correct on both layouts. | [round](data/data@2026-11-12-710bcb2a3e6e4abbc299b43860c6528f7bd81db8-window-layout-matrix/repro.md) |
| E07 | `2026-11-13` | Top-K anchors by reference: merge gate | `802d8157` against `a7369250`; 8x B300, TP8, two GSM8K runs per arm | Candidate 94.24% / 99.85% and 94.77% / 99.92%; base 95.38% / 100% and 94.09% / 99.77%; 3 of 2638 truncated on each arm. | [round](data/data@2026-11-13-802d8157b74564997e350ffa981b5e567e391920-topk-by-reference-gate/repro.md) |
| E08 | `2026-11-14` | Upstream main merge: TP8 and DEP8 gate | `c6a9b341` (local merge); 8x B300; TP8 BF16 and DEP8 `trtllm` FP8 | TP8 94.69% / 99.92% stop; DEP8 95.07% / 100% stop; smoke 6/6 on both. | [round](data/data@2026-11-14-c6a9b3411f3db9fa1a4244ec6eede2a43bbf5550-main-merge-gate/repro.md) |
| E09 | `2026-11-15` | Pushed main merge: DEP8 confirmation | `ec8bc57f`; 8x B300; DEP8 `trtllm` FP8 | 94.62% accuracy, 99.85% stop; smoke 6/6. | [round](data/data@2026-11-15-ec8bc57fde48466d602529752d428b466efc54cf-main-merge-dep8/repro.md) |
| E10 | `2026-11-15` | Window layout as the default: preview | `5e6ee4ed` (local, unpublished); 8x B300; DEP8 `trtllm` FP8; no layout variable | 95.45% accuracy, 100% stop; probes 16/18; prefix reuse 6/6. Preview, non-release. | [round](data/data@2026-11-15-5e6ee4ed50fc91fee9c5a0484667ce6de2ba5640-window-default-dep8/repro.md) |
| E11 | `2026-11-15` | Long-context random-record retrieval | `1c6afefe` (local) and `e941d571`; 8x B300; DEP8 `trtllm` FP8; greedy, thinking off | 6 to 8 of 12 correct at 60K and at 120.9K tokens on window, full-length and pre-merge arms; 92–100% up to 24K. Open observation. | [round](data/data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-retrieval/repro.md) |
| E12 | `2026-11-15` | Long-context retrieval attribution | `1c6afefe` (local; tree of pull request 67); 8x B300; DEP8 `trtllm` BF16, TP8 `flashmla_sparse` BF16, DEP8 `trtllm` FP8 with thinking on; greedy | 6 to 10 of 12 correct per cell on every arm; thinking on removes only the `max_tokens` misses. No serving configuration attributed; non-blocking. | [round](data/data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-attribution/repro.md) |
| E13 | `2026-11-15` | Window layout as the default: TP8 gate on the pull-request head | `fb4015b5` (pull request 67, open); 8x B300; TP8 BF16; no layout flag | 94.92% accuracy, 99.77% stop, 3 truncated; smoke 6/6. | [round](data/data@2026-11-15-fb4015b5bdb6ed416beba624f365407089567b53-window-default-tp8/repro.md) |
| E14 | `2026-11-15` | Window layout against full-length layout: serving speed | `fb4015b5` (pull request 67, open); 8x B300; DEP8 `trtllm` FP8 and TP8 BF16; MTP; default layout against `--disable-hybrid-swa-memory` | No difference attributable to the layout in throughput, TTFT, TPOT or multi-turn TTFT; +29% / +30% full-length tokens. Non-release. | [round](data/data@2026-11-15-fb4015b5bdb6ed416beba624f365407089567b53-window-layout-speed/repro.md) |
