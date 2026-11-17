# HiSparse lifts the KV-bound PD decode by 67–78% on AgentX, at twice the ITL

## Context

On this trace, the PD decode server (DPA4 + EP4 + MTP on 4× GB300) runs 2–3 requests per rank. A request reserves its whole context, up to 147K rows, against 208K rows per rank. HiSparse keeps the full-attention KV in host memory behind a per-request device buffer, so the decode can admit more requests. This round measures how much decode throughput that buys, what it costs per token, and how much of it reaches end-to-end throughput.

## Outcome

- **Decode side:** at decode saturation (c48, 4,096 output tokens per turn), output throughput rose from 471 to 788 tok/s at host ratio 6 (+67%) and to 837 tok/s at ratio 12 (+78%). Ratio 12 gave the same throughput at c64 as at c48.
- **Same batch:** HiSparse adds 12–35% ITL, so it is 8–17% slower when the decode is not KV-bound.
- **End to end:** on the native trace, +21.5% requests and +18.6% total throughput at c16, and +9–10% at c32, where the single prefill server binds.
- **Defect found:** the round found that the request-length limit and the scheduler's token capacity counted device rows instead of logical ids. Commit `76e1c381` carries the fix, which is part of pull request 84.

## Evidence

- Code: `76e1c3816e1835916cde9540700b1865f398e6ce` (branch `hisparse-window-subpool-eval`; pull request 84 carries the same change rebased).
- Model: `zai-org/GLM-5-1028-Provider` at `66c3fe71`.
- Experiment: [AgentX E05](repro.md); accuracy in [Correctness E29](../../../p0-correctness/data/data@2026-11-16-76e1c3816e1835916cde9540700b1865f398e6ce-hisparse-pd/repro.md).
- Pull request: `radixark/sglang-zai` pull request 84.

## Follow-up

- [ ] Sweep `--max-running-requests` on the HiSparse decode to map output throughput against ITL p90, and read the gain at a given interactivity SLO (`alphabetc1`).
- [ ] Profile the same-batch step to find where the +12–35% goes: swap-in, Top-K mapping or split-K (`alphabetc1`).
- [ ] Repeat each saturation point to put a noise band on the ratio-6 / ratio-12 difference (`alphabetc1`).
