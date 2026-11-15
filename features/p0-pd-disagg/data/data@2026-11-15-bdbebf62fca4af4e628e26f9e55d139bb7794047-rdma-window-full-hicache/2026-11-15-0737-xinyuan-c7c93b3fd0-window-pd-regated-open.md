# Window layout over PD re-gated on the merged branch; pull request open

## Context

radixark/sglang-zai pull request 58 transfers the window layout over PD. After the upstream merge and the prefill-CP merge it needed a new gate.

## Outcome

The merged tree `bdbebf62fc` passed window, full-length and prefill-HiCache legs over RDMA. The pull request head is `c7c93b3fd0` (that tree plus a documentation commit); it is open and not merged.

## Evidence

- Code: `bdbebf62fc` (gated), `c7c93b3fd0` (pull-request head)
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`
- Experiment: [E03](repro.md)
- Pull request: radixark/sglang-zai pull request 58

## Follow-up

- [ ] Merge decision for pull request 58 (`<OWNER>`).
- [ ] KV checksum addressing of the DSA tail buffers under a compressed index pool, found in review and left out of this pull request (`<OWNER>`).
