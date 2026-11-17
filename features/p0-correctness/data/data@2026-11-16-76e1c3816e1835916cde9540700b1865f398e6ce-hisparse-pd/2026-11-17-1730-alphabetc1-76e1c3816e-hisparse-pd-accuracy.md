# HiSparse decode under PD keeps GSM8K, GPQA and RULER2 aggregates within 2.5 points of a plain decode

## Context

HiSparse now supports the window KV layout, where only the full-attention sub-pool is hierarchical (pull request 84). Before it is recommended for AgentX-style decode, it has to keep accuracy on the deployed PD shape: a TP4 prefill server with the Mooncake-store linker and a DPA4 + EP4 + MTP decode server.

## Outcome

Through the PD router at temperature 1.0 and top_p 0.95, with sgl-eval 0.1.3:

| Eval | Baseline decode | HiSparse decode (ratio 6) |
|---|---:|---:|
| GSM8K 200 | 96.00% | 94.00% |
| GPQA diamond, 2 repeats | 69.95% | 72.47% |
| RULER2 32K | 91.14% | 90.58% |

- Every request completed without error.
- RULER2 `mv_niah_hard` is 10.1 points lower with HiSparse, and `mv_niah_medium` 6.8 points higher. This is one run per arm at 100 examples per task, which is not enough to separate a regression from noise.

## Evidence

- Code: `76e1c3816e1835916cde9540700b1865f398e6ce` plus the round's `without-request-capacity.patch` (branch `hisparse-window-subpool-eval`).
- Model: `zai-org/GLM-5-1028-Provider` at `66c3fe71`.
- Experiment: [Correctness E29](repro.md).
- Pull request: `radixark/sglang-zai` pull request 84.

## Follow-up

- [ ] Repeat RULER2 32K with several seeds per arm and settle the `mv_niah_hard` difference (`alphabetc1`).
