# E04 Router health-check failure diagnosis — data@2026-11-18-a22079906b-health-check-failures

## Environment

- Machine: one 8x B300 node, 1P1D with prefill on GPUs 0–3 and decode on GPUs 4–7.
- Deployment: TP4 + EP4 + DP attention 4 on each side, NIXL, prefill MegaMoE, FP8 KV, EAGLE, max-running-requests 64, simulated accept length 2.
- Code commit: `a22079906bf873d1c888b9a0c4b7fdc70a4432f2`.
- Model revision: not independently re-read during this investigation; this limitation is retained and the round is non-release.

## Setup

Two runs send 128 requests with random-input-len 131072, random-output-len 1, max-concurrency 64 through the router. The router request timeout is 7200 seconds and both PD bootstrap/waiting timeouts are 3600 seconds. Raw client, router, prefill and decode logs remain on the benchmark allocation and are not imported into this branch.

## Workload

- First run: `prefill_131072_1_c64_r1`.
- Second run: `prefill_131072_1_c64_r2`.
- Comparison points: 32K/1 at C16/C32/C64, 128K/1 at C16/C32, and all 32K/8K and 128K/8K points completed fully.

## Results

| Run | Successful requests | Failed requests | Failure window |
|---|---:|---:|---|
| r1 | 101 / 128 | 27 | 01:43:55–01:44:00 UTC |
| r2 | 128 / 128 | 0 | None |

The 27 errors are HTTP 503 `server_selection_failed`, not client timeouts. Decode `/health` timed out at 01:41:50, 01:42:50 and 01:43:50. After the third failure, the router marked the only decode worker unhealthy and rejected new requests. Decode continued serving paired `/generate` requests and later returned health 200 twice; r2 then completed normally.

The default `/health` path performs generation and permits a 20-second internal wait, while the router's periodic health check times out after 5 seconds. Three consecutive failures remove the worker; two successes restore it. This mechanism exactly matches the observed failure and recovery timeline.

Conclusions:

1. The direct cause is the router health monitor, with high confidence. NIXL errors, PD bootstrap/waiting timeouts, fatal OOM, process crashes and aborted requests are not supported by the logs.
2. Disabling the circuit breaker is not the targeted fix: the demonstrated mechanism is the health monitor's unhealthy mark, not independently proven circuit-breaker activation.
3. Suggested validation A: disable endpoint generation for `/health` on both workers and repeat the same point, keeping explicit `/health_generate` for deep checks.
4. Suggested validation B: retain generation semantics and set router `--health-check-timeout-secs 30`, greater than the server default of 20 seconds. These are hypotheses to validate, not yet production-verified settings.
5. Decode KV capacity is a separate risk: 1,035,840 tokens per DP rank supports about seven complete 128K requests per rank, or 28 across four ranks before other reservations. No log ties that capacity limitation to these 27 router rejections.
6. Benchmark process exit code zero does not certify per-request success; gates must check completed count and per-request errors.

## Data and Figures

- `prefill_131072_1_c64_r1.jsonl` and `prefill_131072_1_c64_r2.jsonl` — retained on the benchmark allocation with the router and server logs.
- Decisive router lines: health timeouts at 01:41:50, 01:42:50 and 01:43:50, followed by `server_selection_failed` at 01:43:55.
- Decisive decode lines: health 200 at 01:44:48 and 01:45:46, demonstrating recovery rather than process death.
- Raw logs are not copied into this branch; the investigation remains non-release until the proposed controls are rerun.
