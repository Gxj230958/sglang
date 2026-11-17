# Prefill–Decode Disaggregation

## Summary

**Backend validation:** E01, E02, E03 serving results used the Python tree core. They remain historical measurements; default-Rust validation and deployment selection require new runs. See the [Rust validation contract](../p0-correctness/data/data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-flashinfer-074-h200/2026-11-16-0845-xinyuan-dbfef91e7d-rust-validation-contract.md).

`zai-org/GLM-5-1028-Provider` tracking for separating prefill and decode resources for predictable token latency and independent capacity tuning. Status: In progress. Related code work: `radixark/sglang-zai` pull request 58 (merged into `glm-5-lp` as `59860082`), which transfers the hybrid window KV layout over PD. A cross-node 1P1D deployment on two 4×GB300 nodes with the Mooncake backend, MTP and KV checksums passes full GSM8K through the router: over forced TCP at `3f3a3985` ([E01](data/data@2026-11-12-3f3a3985acdae2aff39ab9d04c6b0047992dfeb2-window-tcp-1p1d/repro.md): 94.01% accuracy, 99.70% stop), over RDMA pinned to one RoCE plane at `fd5e9375` ([E02](data/data@2026-11-13-fd5e9375e95252ccae3f39bec4623cf6bb172b5e-window-rdma-1p1d/repro.md): 94.77%, 99.85%), and on the branch containing the upstream `main` merge at `bdbebf62` ([E03](data/data@2026-11-15-bdbebf62fca4af4e628e26f9e55d139bb7794047-rdma-window-full-hicache/repro.md): window layout 95.07% / 99.55%, full-length layout 94.69% / 99.70%, window layout with HiCache on the prefill server 94.84% / 99.55%). No checksum mismatch, transfer failure or traceback was logged in the RDMA runs. On this cluster RDMA requires `--disaggregation-ib-device` pinned to one port index, because RoCE rails reach the other node only within the same index. All results are single runs on unlocked environments and are non-release. Not validated: different attention TP sizes on the two sides, host receive, decode KV offload, decode-side HiCache, prefill CP under PD, and compressed index pools. The H200 baseline ([Correctness E01](../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md)) is a colocated TP8 server. Target workload and hardware: `<WORKLOAD>` on `<HARDWARE>`; acceptance thresholds remain to be defined.

## How It Works

Prefill processes the prompt and builds the KV cache; decode repeatedly reads that cache to generate tokens. SGLang assigns these phases to separate workers and transfers the computed KV state through a transfer engine such as Mooncake or NIXL. A router coordinates the prefill and decode workers. Separating their scheduling prevents a long prefill from interrupting active decode work and allows each worker pool to use a suitable configuration. Transfer bandwidth, cache-layout compatibility, and the worker ratio remain part of the deployment tradeoff.

Reference: [PD disaggregation guide](https://docs.sglang.io/docs/advanced_features/pd_disaggregation).

## Scope

### In Scope

- Worker roles, request routing, and KV transfer for the selected model.
- Prefill/decode capacity balance, transfer overhead, and recovery behavior.

### Out of Scope

- Unselected configurations and unsupported feature combinations.
- Performance or support claims without reproducible evidence.

## Success Criteria

- [ ] Disaggregated outputs pass the same correctness gates as the colocated baseline.
- [ ] TTFT, inter-token latency, throughput, and transfer overhead meet `<PERFORMANCE_GATE>` at the target load.

## Assignees

- `<OWNER>` — Design, implementation coordination, and validation evidence.

## Stages

### Stage 1: Define requirements and design — In progress

- [ ] Record the target workloads, dependencies, configuration boundaries, and acceptance thresholds.
- [x] Run a prefill server and a decode server on separate nodes with the Mooncake transfer backend and the accuracy evaluation through the router; completed 2026-11-12 ([E01](data/data@2026-11-12-3f3a3985acdae2aff39ab9d04c6b0047992dfeb2-window-tcp-1p1d/repro.md)).
- Decision: on nodes whose RoCE rails form isolated planes by port index, pin Mooncake to one plane on both servers (`--disaggregation-ib-device ibp0p0,ibp1p0,ibp2p0,ibp3p0`). Automatic device discovery pairs rails across planes and produced 2011 `transport retry counter exceeded` failures in [E01](data/data@2026-11-12-3f3a3985acdae2aff39ab9d04c6b0047992dfeb2-window-tcp-1p1d/repro.md); the pinned run in [E02](data/data@2026-11-13-fd5e9375e95252ccae3f39bec4623cf6bb172b5e-window-rdma-1p1d/repro.md) is clean.
- Constraint: at `710bcb2a` the window layout was rejected at launch under PD; the rejection hid a missing index-K transfer for that layout. Pull request 58 adds the transfer.

### Stage 2: Implement and validate the selected scope — In progress

- [x] Link implementation work: `radixark/sglang-zai` pull request 58, gated at `3f3a3985`, `fd5e9375` and `bdbebf62`; merged as `59860082` on 2026-11-15 from head `c7c93b3f` (the last gated tree plus a documentation commit); recorded 2026-11-15.
- [x] Record correctness evidence in self-contained rounds: [E01](data/data@2026-11-12-3f3a3985acdae2aff39ab9d04c6b0047992dfeb2-window-tcp-1p1d/repro.md), [E02](data/data@2026-11-13-fd5e9375e95252ccae3f39bec4623cf6bb172b5e-window-rdma-1p1d/repro.md), [E03](data/data@2026-11-15-bdbebf62fca4af4e628e26f9e55d139bb7794047-rdma-window-full-hicache/repro.md); completed 2026-11-15.
- Experiment [E03](data/data@2026-11-15-bdbebf62fca4af4e628e26f9e55d139bb7794047-rdma-window-full-hicache/repro.md): a prefill server with HiCache restores an evicted prefix from host memory and, after a restart of both servers, from file storage; the restored prefix transfers and all probe answers are correct.
- Open review finding: the KV checksum addresses the DSA tail buffers with full-KV page ids. It is reachable only with a compressed index pool (`index_kpool > 1`; this checkpoint uses 1) and is not addressed by pull request 58.
- [x] Merge decision for pull request 58: merged as `59860082`; completed 2026-11-15.
- [ ] Validate different attention TP sizes on the two sides, host receive, decode KV offload, decode-side HiCache, and prefill CP under PD.
- [ ] Record TTFT, inter-token latency, throughput and transfer overhead; no performance evidence exists yet.

## Experiments

| ID | Date | Topic | Basic Setting | Result | Round |
|---|---|---|---|---|---|
| E01 | 2026-11-12 | Window layout over 1P1D, forced TCP | 2 nodes × 4 GB300; TP4 per side; MTP; Mooncake with `MC_FORCE_TCP=1`; KV checksum; `3f3a3985` | Python tree core; Rust rerun pending. GSM8K 94.01% accuracy, 99.70% stop; probes 12/12 correct; stress 64/64 and 398/400; no checksum mismatch | [round](data/data@2026-11-12-3f3a3985acdae2aff39ab9d04c6b0047992dfeb2-window-tcp-1p1d/repro.md) |
| E02 | 2026-11-13 | Window layout over 1P1D, RDMA on one RoCE plane | Same nodes; Mooncake RDMA pinned to `ibp{0-3}p0`; `fd5e9375` | Python tree core; Rust rerun pending. GSM8K 94.77% accuracy, 99.85% stop; probes 12/12; stress 99/100; no transfer failure or mismatch | [round](data/data@2026-11-13-fd5e9375e95252ccae3f39bec4623cf6bb172b5e-window-rdma-1p1d/repro.md) |
| E03 | 2026-11-15 | Window, full-length and prefill-HiCache legs after the main merge | Same nodes; RDMA on one plane; `bdbebf62` | Python tree core; Rust rerun pending. Window 95.07% / 99.55% stop; full-length 94.69% / 99.70%; window + prefill HiCache 94.84% / 99.55% with host and storage restores correct | [round](data/data@2026-11-15-bdbebf62fca4af4e628e26f9e55d139bb7794047-rdma-window-full-hicache/repro.md) |
