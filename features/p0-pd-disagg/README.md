# Prefill–Decode Disaggregation

## Summary

`zai-org/GLM-5-1028-Provider` tracking for separating prefill and decode resources for predictable token latency and independent capacity tuning. Status: Not started. Related code work: `radixark/sglang-zai` branch `glm-5-lp` at `a15aa7c3`. The GLM LoopLM guide at that commit documents prefill–decode disaggregation with the Mooncake transfer backend, including with MTP. No disaggregated deployment has been run for this tracking project, so there is no support claim; the H200 baseline ([Correctness E01](../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md)) is a colocated TP8 server. Target workload and hardware: `<WORKLOAD>` on `<HARDWARE>`; acceptance thresholds remain to be defined.

## How It Works

Prefill processes the prompt and builds the KV cache; decode repeatedly reads that cache to generate tokens. SGLang assigns these phases to separate workers and transfers the computed KV state through a transfer engine such as Mooncake or NIXL. A router coordinates the prefill and decode workers. Separating their scheduling prevents a long prefill from interrupting active decode work and allows each worker pool to use a suitable configuration. Transfer bandwidth, cache-layout compatibility, and the worker ratio remain part of the deployment tradeoff.

Reference: [PD disaggregation guide](https://docs.sglang.io/docs/advanced_features/pd_disaggregation).

## Scope

### In Scope

- Worker roles, request routing, and KV transfer for the selected model.
- Prefill/decode capacity balance, transfer overhead, and recovery behavior.

### Out of Scope

- Unselected configurations and unsupported feature combinations.
- Performance or support claims without reproducible evidence.

## Success Criteria

- [ ] Disaggregated outputs pass the same correctness gates as the colocated baseline.
- [ ] TTFT, inter-token latency, throughput, and transfer overhead meet `<PERFORMANCE_GATE>` at the target load.

## Assignees

- `<OWNER>` — Design, implementation coordination, and validation evidence.

## Stages

### Stage 1: Define requirements and design — Not started

- [ ] Record the target workloads, dependencies, configuration boundaries, and acceptance thresholds.
- Next action: run a prefill server and a decode server on separate nodes with the same checkpoint and the Mooncake transfer backend, then compare greedy outputs with the colocated TP8 baseline and run the correctness accuracy evaluation through the router.

### Stage 2: Implement and validate the selected scope — Not started

- [ ] Link implementation work from an exact code commit or pull request.
- [ ] Record correctness and performance evidence in a self-contained experiment round.

## Experiments

No experiments recorded yet.
