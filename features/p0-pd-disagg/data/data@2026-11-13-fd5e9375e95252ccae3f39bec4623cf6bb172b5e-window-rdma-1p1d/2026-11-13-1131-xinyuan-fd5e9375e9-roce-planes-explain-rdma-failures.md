# RDMA transfer failures traced to RoCE plane layout

## Context

The first PD run fell back to forced TCP after 2011 `transport retry counter exceeded` failures between the two GB300 nodes.

## Outcome

Each node has 16 RoCE rails `ibp{0-3}p{0-3}`. Rails reach the other node only within the same port index; Mooncake's automatic discovery pairs rails across indices. Pinning one plane on both servers with `--disaggregation-ib-device ibp0p0,ibp1p0,ibp2p0,ibp3p0` gives a clean RDMA run. The failures were not caused by the window layout or the transfer code.

## Evidence

- Code: `fd5e9375e9`
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`
- Experiment: [E01](../data@2026-11-12-3f3a3985acdae2aff39ab9d04c6b0047992dfeb2-window-tcp-1p1d/repro.md) (failures), [E02](repro.md) (pinned plane)

## Follow-up

- [ ] Carry the device pinning into the deployment guidance for this cluster type (`<OWNER>`).
