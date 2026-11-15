# Upstream main merged into the model branch

## Context

`glm-5-lp` was 131 commits behind upstream `main`. The merge had seven textual conflicts, among them the Mooncake connection code and the DSA backend.

## Outcome

A local merge `c6a9b3411f` passed TP8 and DEP8 gates on B300. The branch advanced by one commit in the meantime, so the merge was recomposed as `ec8bc57fde`, pushed as a fast-forward on 2026-11-15, and confirmed on DEP8.

## Evidence

- Code: `c6a9b3411f` (gated), `ec8bc57fde` (pushed)
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`
- Experiment: [E08](../data@2026-11-14-c6a9b3411f3db9fa1a4244ec6eede2a43bbf5550-main-merge-gate/repro.md) and [E09](repro.md)

## Follow-up

- [x] Re-gate window prefill CP and PD on the merged branch; recorded in Prefill CP E03 and PD Disaggregation E03.
- [ ] Gate with FlashInfer 0.7.4, the version the merged code pins (`<OWNER>`).
