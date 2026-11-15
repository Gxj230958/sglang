# Window layout as the default: pull request 67 opened

## Context

The default-layout change was a local preview ([E10](../data@2026-11-15-5e6ee4ed50fc91fee9c5a0484667ce6de2ba5640-window-default-dep8/repro.md)). After pull request 58 merged it was rebased onto `glm-5-lp` at `59860082` and gated on its final head.

## Outcome

radixark/sglang-zai pull request 67 is open at head `fb4015b5bd` against `glm-5-lp`; it is not merged. The head passed the TP8 GSM8K gate at 94.92% accuracy and 99.77% stop rate with the window pool built by default. The change removes the `SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA` variable; `--disable-hybrid-swa-memory` selects the full-length layout. Serving speed of the two layouts had not been compared when the pull request opened.

## Evidence

- Code: `fb4015b5bd` (pull-request head), `5e6ee4ed50` (first revision, DEP8 gate)
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`
- Experiment: [E13](repro.md), [E10](../data@2026-11-15-5e6ee4ed50fc91fee9c5a0484667ce6de2ba5640-window-default-dep8/repro.md)
- Pull request: radixark/sglang-zai pull request 67

## Follow-up

- [x] Compare serving speed of the window and full-length layouts: no difference attributable to the layout ([E14](../data@2026-11-15-fb4015b5bdb6ed416beba624f365407089567b53-window-layout-speed/repro.md)).
- [ ] Merge decision for pull request 67 (`<OWNER>`).
