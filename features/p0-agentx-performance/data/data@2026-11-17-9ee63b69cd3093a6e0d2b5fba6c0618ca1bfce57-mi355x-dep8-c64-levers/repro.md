# E01 MI355X DEP8 AgentX at concurrency 64: scheduling and prefill levers — data@2026-11-17-9ee63b69cd3093a6e0d2b5fba6c0618ca1bfce57-mi355x-dep8-c64-levers

This round runs AgentX replay against GLM LoopLM on 8x MI355X at concurrency 64 with DEP8, the window KV layout, MTP and an fp8 KV cache. It compares five server configurations under the same 900-second protocol. Every point is a **local 900-second iteration**: it is not dashboard-comparable, and there is no B300 or other reference point at this protocol.

## Environment

- Hardware, container and model as [AMD E03](../../../p1-multi-platform/amd/data/data@2026-11-17-9ee63b69cd3093a6e0d2b5fba6c0618ca1bfce57-mi355x-fp8-kv/repro.md): 8x MI355X (gfx950), ROCm 10.0.0, `zai-org/GLM-5-1028-Provider` at `66c3fe71d4c4ab43efac5bb0d2be6dea3a75d089`.
- Code: `radixark/sglang-zai` `amd_support` at `9ee63b69cd3093a6e0d2b5fba6c0618ca1bfce57`, clean tree. `identity.txt` in each point records it.
- Client: InferenceX `67c3ed26f9c196b3e8286053a44838b4f0024756`, replay-only driver `python -m infx.bench agentic`, in a separate venv with `agentx-harness==1.0.14`. AIPerf `agentx` scenario: seed 42, 10 warmup requests per lane, 1800-second warmup drain deadline, 300-second per-trajectory idle cap, recorded-assistant replay.
- Corpus: `semianalysis_cc_traces_weka_062126_256k` (393 trees). The model's `max_position_embeddings` is 262144, so the uncapped corpus would exceed the context.

## Setup

Scripts: AMD [scripts/v3/](../../../p1-multi-platform/amd/scripts/v3/), [`agentx_rung.sh`](../../../p1-multi-platform/amd/scripts/v3/agentx_rung.sh) and [`agentx_ladder.sh`](../../../p1-multi-platform/amd/scripts/v3/agentx_ladder.sh). Each point:

1. Launches a fresh server on `:30001`.
2. Starts `sglang-router` 0.3.2 on `:30000` with `--policy cache_aware --dp-aware --request-id-headers x-correlation-id`, as the DeepSeek-V4.1-Flash MI355X DP recipe does. The client sends `AIPERF_HTTP_X_SMG_ROUTING_KEY_FROM_CORRELATION_ID=true`.
3. Runs a sanity request.
4. Pre-loads the long-context kernel variants on every DP rank ([`warm_long_ctx.py`](../../../p1-multi-platform/amd/scripts/v3/warm_long_ctx.py)).
5. Resets the cache with `/flush_cache` (HTTP 200, saved in `cache-reset.body`).
6. Runs the replay and scoring.

The exact client command is in `benchmark_command.txt`.

Common server flags (`identity.txt`), with `SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1`:

```bash
--tp-size 8 --attn-dp-size 8 --ep-size 8 --moe-a2a-backend none --mem-fraction-static 0.80 \
--context-length 262144 --chunked-prefill-size 32768 --max-running-requests 256 \
--cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --kv-cache-dtype fp8_e4m3 \
--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 \
--speculative-num-draft-tokens 4 --speculative-draft-model-path <model> \
--enable-cache-report --enable-metrics --watchdog-timeout 3600
```

Under attention DP, SGLang divides `--chunked-prefill-size` by the DP size, so 32768 means 4096 tokens per rank.

| Point | Added to the common flags |
|---|---|
| `it900_dep8_fp8_c64` | none |
| `it900_dep8_fp8_sched_c64` | `--prefill-decode-interval 16 --enable-prefill-delayer --prefill-delayer-token-usage-low-watermark 0.7` |
| `it900_dep8_fp8_sched_gv4_c64` | the same plus `SGLANG_DP_USE_GATHERV=1` |
| `it900_dep8_fp8_sched_gv_c64` | the same plus `--chunked-prefill-size 65536` (8192 per rank) |
| `it900pdi32_dep8_fp8_sched_gv4_c64` | `sched_gv4` with `--prefill-decode-interval 32` |

**Acceptance.** InferenceX has no golden acceptance curve for this model. The servers force acceptance length 2.49 (`SGLANG_SIMULATE_ACC_LEN=2.49`, `SGLANG_SIMULATE_ACC_METHOD=match-expected`, `SGLANG_SIMULATE_ACC_TOKEN_MODE=real-draft-token`). That is the draft's SPEED-Bench coding acceptance at three draft tokens, measured on MI355X in [AMD E02](../../../p1-multi-platform/amd/data/data@2026-11-17-df840adba7a0dfa794a221ec49c57daa601ec7c1-mi355x-dep8-hicache/repro.md), so this is a disclosed local calibration. Each point's realized acceptance (`accept_length.txt`, mean of the `Decode batch` lines) is 2.488–2.497, with p10–p90 of 2.38–2.60. Generated text under forced acceptance is not quality evidence; correctness for this deployment is in AMD E02 and E03.

## Results

| Point | Requests (errors) | Total tok/s/GPU | Output tok/s/GPU | TTFT mean / p90 (s) | ITL mean / p90 (ms) | Interactivity mean / p90 (tok/s) | GPU prefix-cache hit |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline | 910 (0) | 9,675 | 66.6 | 4.26 / 7.96 | 98.7 / 149.3 | 10.1 / 6.7 | 94.4% |
| + prefill-decode interval 16, prefill delayer | 1,211 (0) | 13,283 | 97.4 | 7.90 / 19.34 | 52.0 / 60.7 | 19.2 / 16.5 | 94.8% |
| + exact DP gather | 1,219 (0) | 13,273 | 95.4 | 8.10 / 19.84 | 52.0 / 60.3 | 19.2 / 16.6 | 94.7% |
| + 8192-token chunks per rank | 1,163 (0) | 12,495 | 89.4 | 5.48 / 10.71 | 62.0 / 75.1 | 16.1 / 13.3 | 94.6% |
| exact DP gather, interval 32 | 1,144 (0) | 12,644 | 94.7 | 16.61 / 42.56 | 40.9 / 46.8 | 24.4 / 21.4 | 94.7% |

All values are from each point's aggregate (`agentx_*.json`):

- **Throughput:** `request_metrics.throughput.per_gpu`, logical input plus output tokens per second per GPU.
- **ITL:** request-mean inter-token latency.
- **Interactivity:** `request_metrics.latency.intvty`; its p90 column is the 90th-percentile-worst user.

Every point passed the upstream validator (0 errors, at most 10% allowed) with 100% TTFT and ITL coverage. Measured input averaged 78–81K tokens per request and output 544–597 tokens.

The baseline's aggregate was produced after the run, from its saved artifacts, by the same `process_agentic_result`. Its controller had not exported the required metadata (`KV_OFFLOADING`, TP/EP/DP attention, speculation). Later points export it.

### Prefill profile (`prefill-profile/`)

One 65536-token prompt per DP rank was sent concurrently, and six forward rounds were profiled on rank 0. These rounds attend contexts of up to 64K tokens with all eight ranks prefilling, at 1.86 s per round:

| Kernel group | Share of GPU time |
|---|---:|
| RCCL collectives: the MoE token gather and combine around every layer | 35% |
| AITER fused MoE (fp8 blockscale) | 23% |
| Sparse MLA prefill (Triton) | 21% |
| CK block-FP8 dense GEMMs | 9% |
| Host gaps (eager prefill, about 4,300 kernels per round) | 14% of the span |

`SGLANG_DP_USE_GATHERV=1` replaces the default all-reduce of a zero-filled buffer of all ranks' rows with an exact variable-length all-gather. It cuts collective time 16% and raises aggregate prefill from 17,868 to 19,736 tokens/s (+10%). With 8192-token chunks per rank as well, aggregate prefill reaches 21,051 tokens/s.

`SGLANG_ENABLE_DP_GATHER_FP8=1` fails on ROCm at the first prefill: `per_token_group_quant` is undefined in its quantize path. It was not used.

### Failed attempts (`failed-attempts/`)

Two earlier baseline attempts at `--mem-fraction-static 0.85` lost a rank during warmup:

- **First:** a late Triton load of the DSA indexer's KV-split `fp8_mqa_logits` variant found 0.00 GiB free.
- **Second:** after a long-context warmup was added, `hipErrorLaunchOutOfResources`. A late load at 0.00 GiB had again been logged.

Neither reproduced in isolation: one 200K-token prefill with decode, eight concurrent 150K-token prefills, and a 15-minute mixed stress all ran clean. Under concurrent long-context prefill, the PyTorch allocator absorbed all of the post-initialization headroom, leaving nothing for code objects or kernel scratch.

At `--mem-fraction-static 0.80`, with the warmup routed to every rank by `routed_dp_rank`, no point lost a rank and no late load was logged before replay.

Conclusions:

1. **Decode stalls behind prefill.** At concurrency 64, DEP8 with fp8 KV keeps 94–95% of prompt tokens in the GPU prefix cache, so KV capacity does not bind. Under attention DP every rank waits at the MoE collectives for any rank's long prefill round. Decode for the 2–3 running requests per rank therefore waits behind prefill, and the baseline's ITL is 99 ms.
2. **Scheduling helps most.** Sixteen decode rounds between prefills, with ranks prefilling together, raise total throughput 37% and p90 interactivity from 6.7 to 16.5 tokens/s; TTFT rises from 4.3 to 7.9 s mean.
3. **The exact DP gather speeds prefill but not this point.** Prefill is 10% faster in isolation, but fresh prefill here is only about 4.4K tokens/s, so the AgentX point is unchanged within noise.
4. **Chunk size and interval trade TTFT against ITL.** Larger chunks shorten TTFT and lengthen ITL, and lose 6% throughput. An interval of 32 gains 29% p90 interactivity for 5% throughput and twice the TTFT.
5. **What would move ITL further.** At 2–3 requests per rank the decode step is latency-bound, as at concurrency 1, and prefill rounds still interleave. Faster decode steps (fewer kernels per layer) and shorter prefill rounds would move ITL further.

## Data and Figures

- One directory per point: aggregate JSON, AIPerf summary (`profile_export_aiperf.json`), raw request records (`profile_export.jsonl.gz`), client command and environment, identity, controller status, warmup output, cache reset, realized acceptance, and the server log without AITER's per-kernel lines.
- [`summary.txt`](summary.txt): the Results table as computed by [`agentx_summary.py`](../../../p1-multi-platform/amd/scripts/v3/agentx_summary.py).
- [`prefill-profile/`](prefill-profile/): kernel summaries of the default and `SGLANG_DP_USE_GATHERV=1` prefill profiles.
- [`failed-attempts/`](failed-attempts/): status, server logs and client logs of the two warmup aborts.

The AIPerf 1-second timeslice exports and server-metric exports (about 400 MB per point) were not committed.
