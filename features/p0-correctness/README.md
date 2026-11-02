# Correctness

## Summary

`zai-org/GLM-5-1028-Provider` (GLM LoopLM, `GlmLoopForConditionalGeneration`) correctness tracking covers model quality, API behavior, feature compatibility, and release-gating regressions. Status: In progress. Implementation work is on the `radixark/sglang-zai` branch `glm-5-lp`; all current evidence is pinned to code commit `a15aa7c3` and model revision `7e66c405`. The H200 bring-up ([E01](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md)) passed the configuration, model, attention, and checkpoint-map tests and returned correct text, image, and long-context answers that stop normally at TP8. Baseline GSM8K-200 reached 95.50% accuracy with 100% stop rate and 0% truncation; built-in NextN/MTP returned `accept len=2.27` with ordinary decode CUDA graph enabled ([E02](data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-mtp-cuda-graph/repro.md)). Release accuracy, API, configuration, and artifact gates remain open, and the reference implementation and quality gates are not yet defined.

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
