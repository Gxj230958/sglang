# Top-K anchors by reference merged

## Context

radixark/sglang-zai pull request 43 proposed four memory changes for the loop state. B300 measurements supported only one of them.

## Outcome

The pull request was reduced to holding the cycle-0 Top-K anchors by reference, rebased as `802d8157b7`, gated against `a736925063`, and squash-merged as `8f5dff0f45` on 2026-11-13.

## Evidence

- Code: `802d8157b7` (gated), `8f5dff0f45` (merged)
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`
- Experiment: [E07](repro.md) and [Kernel Optimization E03](../../../p0-kernel-opt/data/data@2026-11-12-6ed895fa2678d8c4d52576e7ae5e3707ee4180e7-topk-by-reference-b300/repro.md)
- Pull request: radixark/sglang-zai pull request 43

## Follow-up

- None. The dropped parts (one-buffer blend, row chunking, startup estimate) are not planned.
