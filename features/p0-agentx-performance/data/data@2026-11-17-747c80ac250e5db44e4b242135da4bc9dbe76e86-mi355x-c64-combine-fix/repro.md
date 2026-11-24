# E04 MI355X DEP8 AgentX at concurrency 64 with the ROCm decode combine fix — data@2026-11-17-747c80ac250e5db44e4b242135da4bc9dbe76e86-mi355x-c64-combine-fix

This round repeats [E01](../data@2026-11-17-9ee63b69cd3093a6e0d2b5fba6c0618ca1bfce57-mi355x-dep8-c64-levers/repro.md)'s `sched_gv4` point at concurrency 64, at `747c80ac` (clean tree). That commit sends the equal-padded decode MoE combine through aiter's custom reduce-scatter instead of RCCL `reduce_scatterv` ([AMD E04](../../../p1-multi-platform/amd/data/data@2026-11-17-747c80ac250e5db44e4b242135da4bc9dbe76e86-mi355x-b300-parity/repro.md)). Protocol, client, corpus, server flags and acceptance contract are as E01; realized acceptance length is 2.490. It is a local 900-second iteration.

## Results

| Code | Requests (errors) | Total tok/s/GPU | Output tok/s/GPU | TTFT mean / p90 (s) | ITL mean / p90 (ms) | Interactivity mean / p90 (tok/s) | GPU prefix-cache hit |
|---|---:|---:|---:|---:|---:|---:|---:|
| `9ee63b69` (E01) | 1,219 (0) | 13,273 | 95.4 | 8.10 / 19.84 | 52.0 / 60.3 | 19.2 / 16.6 | 94.7% |
| `747c80ac` | 1,251 (0) | 13,673 | 100.1 | 7.00 / 16.14 | 48.5 / 56.1 | 20.6 / 17.8 | 95.0% |

Conclusion: the decode combine fix improves every metric of the concurrency-64 point. Throughput rises 3%, ITL falls 7%, TTFT falls 14% and p90 interactivity rises 7%. This is a single 900-second run per code version; the run-to-run spread at this protocol has not been measured.

## Data and Figures

- [`it900rs_dep8_fp8_sched_gv4_c64/`](it900rs_dep8_fp8_sched_gv4_c64/): the point's artifacts, with the same contents as E01.
- [`summary.txt`](summary.txt): both rows as computed by `agentx_summary.py`.
