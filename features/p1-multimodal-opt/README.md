# Multimodal Optimization

## Summary

`zai-org/GLM-5-1028-Provider` tracking for selecting encoder and serving optimizations for the target multimodal workloads. Status: Not started. Related code work: `radixark/sglang-zai` branch `glm-5-lp` at `a15aa7c3`. The GLM LoopLM guide at that commit documents encoder disaggregation (`--encoder-only` and `--language-only`) and its combination with prefill–decode disaggregation. None of these optimizations has been run for this tracking project. Basic image input is a correctness check and is recorded in [Correctness E01](../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md); it establishes no optimization result. Target workload and hardware: `<WORKLOAD>` on `<HARDWARE>`; acceptance thresholds remain to be defined.

## Subprojects

We select the features we need from the subdirectories below for implementation.

| Directory | Focus |
|---|---|
| [EPD Disaggregation](epd-disagg/README.md) (`epd-disagg/`) | Separate encoder, prefill, and decode services. |
| [DP Encoder](dp-encoder/README.md) (`dp-encoder/`) | Distribute encoder input batches across replicas. |
| [Encoder CUDA Graph](encoder-cuda-graph/README.md) (`encoder-cuda-graph/`) | Replay supported encoder shapes with CUDA graphs. |

## Scope

### In Scope

- Profile encoder and language-model work to select the necessary subprojects.
- Validate modality handling, composition, and end-to-end performance.

### Out of Scope

- Unselected configurations and unsupported feature combinations.
- Performance or support claims without reproducible evidence.

## Success Criteria

- [ ] Selected optimizations preserve multimodal correctness and request ordering.
- [ ] Encoder latency, TTFT, and end-to-end throughput meet `<MULTIMODAL_GATE>`.

## Assignees

- `<OWNER>` — Design, implementation coordination, and validation evidence.

## Stages

### Stage 1: Define requirements and design — Not started

- [ ] Record the target workloads, dependencies, configuration boundaries, and acceptance thresholds.
- [ ] Record selected and deferred subprojects with the reasons for each decision.
- Next action: profile encoder and language-model time on image requests at the H200 TP8 baseline, then decide whether to select [EPD Disaggregation](epd-disagg/README.md); if selected, compare an encoder-disaggregated language server with the colocated baseline on the same image prompts.

### Stage 2: Implement and validate the selected scope — Not started

- [ ] Link implementation work from an exact code commit or pull request.
- [ ] Record correctness and performance evidence in a self-contained experiment round.

## Experiments

No experiments recorded yet.
