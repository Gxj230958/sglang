# Window-slot KV write fix merged

## Context

The hybrid window sub-pool wrote window-slot KV at full-pool ids. radixark/sglang-zai pull request 42 writes it at the window ids.

## Outcome

Squash-merged into `glm-5-lp` as `710bcb2a3e` on 2026-11-12. The post-merge gate on the window layout with MTP and decode CUDA graphs passed.

## Evidence

- Code: `710bcb2a3e`
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`
- Experiment: [E06](repro.md)
- Pull request: radixark/sglang-zai pull request 42

## Follow-up

- [x] Validate the remaining window-layout combinations (prefill CP, PD, HiCache, attention DP); recorded in their feature rounds.
