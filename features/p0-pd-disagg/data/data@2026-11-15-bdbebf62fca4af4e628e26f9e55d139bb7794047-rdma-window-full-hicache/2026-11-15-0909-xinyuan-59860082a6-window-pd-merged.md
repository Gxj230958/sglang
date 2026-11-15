# Window layout over PD merged

## Context

radixark/sglang-zai pull request 58 was open at head `c7c93b3fd0` after its re-gate on the merged branch ([earlier record](2026-11-15-0737-xinyuan-c7c93b3fd0-window-pd-regated-open.md)).

## Outcome

Pull request 58 merged into `glm-5-lp` as `59860082a6` on 2026-11-15. The merged head is the gated tree `bdbebf62fc` plus a documentation commit. `glm-5-lp` now transfers the window layout over PD.

## Evidence

- Code: `59860082a6` (merge), `c7c93b3fd0` (pull-request head), `bdbebf62fc` (gated)
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`
- Experiment: [E03](repro.md)
- Pull request: radixark/sglang-zai pull request 58

## Follow-up

- [ ] KV checksum addressing of the DSA tail buffers under a compressed index pool; not reachable with this checkpoint (`<OWNER>`).
