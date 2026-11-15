# Long-context retrieval misses attributed to no serving configuration; treated as non-blocking

## Context

[E11](../data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-retrieval/repro.md) left the cause of the random-record retrieval misses at 60K tokens and above open, with FP8 KV, attention DP and the thinking-off prompt format as candidates.

## Outcome

Three more arms on the same 24 prompts (DEP8 BF16, TP8 BF16 with `flashmla_sparse`, thinking on) all miss: 6 to 10 of 12 correct per cell. Thinking on removes only the requests that opened with reasoning and hit `max_tokens`. No tested serving configuration changes the miss rate.

The project owner's working assessment is that the misses reflect the checkpoint's own retrieval limit at these lengths. The assessment has not been compared against a reference implementation. The observation does not block the default-layout change or other work on `glm-5-lp`.

## Evidence

- Code: `1c6afefe8a` (tree identical to `fb4015b5bd`)
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`
- Experiment: [E12](repro.md), [E11](../data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-retrieval/repro.md)

## Follow-up

- [ ] Compare the same prompts against a reference implementation of the checkpoint to confirm the assessment (`<OWNER>`).
