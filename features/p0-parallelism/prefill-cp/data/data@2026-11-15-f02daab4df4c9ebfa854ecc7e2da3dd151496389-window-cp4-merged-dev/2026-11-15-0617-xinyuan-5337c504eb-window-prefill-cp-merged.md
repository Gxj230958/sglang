# Window layout under prefill CP merged

## Context

The loop model rejected prefill CP for the window sub-pool. radixark/sglang-zai pull request 57 lifts that rejection.

## Outcome

After gates at three heads (CP4 on GB300, CP8 on B300, CP4 again on the merged branch) the pull request was squash-merged into `glm-5-lp` as `5337c504eb` on 2026-11-15.

## Evidence

- Code: `f02daab4df` (last gated head), `5337c504eb` (merged)
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`
- Experiment: [E01](../data@2026-11-12-0c95a2b1d2f1cfcaa6bcc503acfe868cd8a6083e-window-cp4/repro.md), [E02](../data@2026-11-13-e941d571f3877797b383d616e957f30c8936c52d-window-cp4-cp8/repro.md), [E03](repro.md)
- Pull request: radixark/sglang-zai pull request 57

## Follow-up

- [ ] Validate the `trtllm` DSA backend and HiCache under prefill CP (`<OWNER>`).
