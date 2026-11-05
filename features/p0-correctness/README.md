# Correctness

## Summary

`zai-org/GLM-5-1028-Provider` (GLM LoopLM, `GlmLoopForConditionalGeneration`) correctness tracking covers model quality, API behavior, feature compatibility, and release-gating regressions. Status: In progress. E01–E03 and E05 use `a15aa7c3` on `glm-5-lp`; E04 uses `8451a1bf` on `fix/glm5-lp-implementation`; all use model revision `7e66c405`. The H200 bring-up ([E01](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md)) passed configuration, model, attention, checkpoint-map, text, image, and long-context checks. E02 recorded H200 baseline GSM8K-200 and the built-in MTP/decode-graph smoke. B300 MTP completed full GSM8K at 93.86% accuracy with 99.24% stop rate and GPQA-4096 at 45.52% pass@1 and 69.19% pass@8; GPQA truncation was 51.33% ([E03](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-b300-mtp-evaluation/repro.md)). The optional vision SwiGLU fix passed 42 unit tests, text/image E2E, and full GSM8K at 95.22% accuracy with 99.32% stop rate ([E04](data/data@2026-11-03-8451a1bf9d6156a8ff76f8d603abe9a89c1b1002-swiglu-fix/repro.md)). H200 MTP completed full GSM8K at 94.31% accuracy and GPQA at 52.53% pass@1 and 75.76% pass@8 with 43.31% truncation at context length 8192 ([E05](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-h200-mtp-evaluation/repro.md)). Release accuracy, API, configuration, and artifact gates remain open.

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

All rows are pinned to code commit `a15aa7c3` and model revision `7e66c405`. "H200 TP8 baseline" means 8 H200 GPUs, TP8, Triton MoE, FlashMLA Sparse, BF16 KV cache, CUDA graph disabled, and MTP disabled.

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
| Expert parallelism, attention DP, FP8 KV cache, and `trtllm` DSA backend | Serving | `<CONFIGURATION>` | `<PASS_CRITERION>` | Not started | None | `<OWNER>` |
| Prefill–decode and encoder disaggregation | Serving | `<CONFIGURATION>` | `<PASS_CRITERION>` | Not started | None | `<OWNER>` |

## Reference Results

No reference results are recorded. The reference implementation and evaluation revisions are not yet pinned.

## Accuracy Results

GSM8K-200 on the H200 TP8 baseline reached 95.50% accuracy, 100% stop rate, 0% truncation, and 0% request errors at `a15aa7c3` and model revision `7e66c405` ([E02](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-mtp-cuda-graph/repro.md)).

B300 MTP full GSM8K reached 93.86% accuracy, 99.24% stop rate, 0.76% truncation, and 0% request errors. B300 MTP GPQA-4096 reached 45.52% pass@1, 69.19% pass@8, and 68.69% majority@8, with 48.67% stop rate and 51.33% truncation ([E03](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-b300-mtp-evaluation/repro.md)). The GPQA values are specific to the 4096-token output budget.

At `8451a1bf`, the optional vision SwiGLU fix passed full GSM8K with 95.22% accuracy, 99.32% stop rate, 0.68% truncation, and 0% request errors ([E04](data/data@2026-11-03-8451a1bf9d6156a8ff76f8d603abe9a89c1b1002-swiglu-fix/repro.md)).

H200 MTP full GSM8K reached 94.31% accuracy, 99.39% stop rate, 0.61% truncation, and 0% request errors. H200 MTP GPQA reached 52.53% pass@1, 75.76% pass@8, and 74.49% majority@8, with 56.69% stop rate and 43.31% truncation at context length 8192 ([E05](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-h200-mtp-evaluation/repro.md)).

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
