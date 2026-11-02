# Encoder–Prefill–Decode Disaggregation

## Summary

`<MODEL_NAME>` tracking for scaling multimodal encoding separately from language-model prefill and decode. Status: Not started. Related code work: `<CODE_BRANCH_OR_PR>`. Target workload and hardware: `<WORKLOAD>` on `<HARDWARE>`; acceptance thresholds remain to be defined.

## How It Works

EPD separates visual encoding from the language-model workers. Encoder services preprocess and encode multimodal inputs, then transfer embeddings to the language or prefill service. Prefill builds the language-model KV cache, and a separate decode service can continue generation when PD disaggregation is enabled. Independent encoder capacity helps accommodate image-heavy workloads without coupling its scaling to the language model. Embedding transport and optional embedding caching are distinct mechanisms; the embeddings are also distinct from the language-model KV cache.

Reference: [EPD disaggregation guide](https://docs.sglang.io/docs/advanced_features/epd_disaggregation).

## Scope

### In Scope

- Encoder service integration, embedding transfer, and request association.
- Independent stage capacity and composition with PD disaggregation.

### Out of Scope

- Unselected configurations and unsupported feature combinations.
- Performance or support claims without reproducible evidence.

## Success Criteria

- [ ] Transferred embeddings and generated outputs match the colocated baseline.
- [ ] Encoder utilization, transfer overhead, and end-to-end latency meet `<EPD_GATE>`.

## Assignees

- `<OWNER>` — Design, implementation coordination, and validation evidence.

## Stages

### Stage 1: Define requirements and design — Not started

- [ ] Record the target workloads, dependencies, configuration boundaries, and acceptance thresholds.

### Stage 2: Implement and validate the selected scope — Not started

- [ ] Link implementation work from an exact code commit or pull request.
- [ ] Record correctness and performance evidence in a self-contained experiment round.

## Experiments

No experiments recorded yet.
