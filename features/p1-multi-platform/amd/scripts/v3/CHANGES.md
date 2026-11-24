# scripts/v3

Additions to [v2](../v2/CHANGES.md) for the DEP8, HiCache and FP8 KV rounds (AMD E02). Files not listed here are unchanged in v2; v3 scripts call v2's `launch.sh`, `start_bg.sh`, `wait_bg.sh`, `doctor.py`, `numcheck.py` and `numcheck_compare.py`.

- `stop_bg.sh` (changed): after TERM/KILL of the process group, waits up to 10 minutes until no process holds a GPU (`rocm-smi --showpids`), so the next launch does not start on top of a server whose pinned HiCache pools are still being freed. It waits on processes, not VRAM, because the driver kept about 10–30 GB per GPU after crashed servers, which only a host reboot returns.
- `midfork.py`, `hicache.py` (from [HiCache E03](../../../../p0-hicache/data/data@2026-11-13-704d3082e1d68255ffb577f02262930b5f2f6d74-window-l2-l3/repro.md)): `DP_RANK=<r>` pins every request to one attention-DP rank with the `X-Data-Parallel-Rank` header, so the prefix-reuse probe and the eviction fill land on the same rank under DEP8.
- `hc_dep8.sh` (new): HiCache E03's sequence on DEP8 + window layout + MTP. L2: probe, fill rank 3 past its GPU pool, probe, full GSM8K. L3: file backend, probe, restart on the same directory, probe.
- `parser_smoke.py` (new): reasoning and tool-call parser API checks (thinking on/off, one call non-streaming and streaming, parallel calls, `tool_choice` none/required, follow-up turn with a tool result).
- `fp8_dep8.sh` (new): bf16 numcheck baseline, then raw fp8_e4m3 KV on DEP8 + window + MTP: pool sizes, parser smoke, prefix probe, numcheck on the same reference tokens, full GSM8K. Context 32768 as Correctness E06.
- `gpqa_tp8.sh` (new): GPQA-Diamond with 4096 output tokens (Correctness E03's workload) on the TP8 MTP configuration.
- `speedbench_prep_coding.py` (new): builds SPEED-Bench `qualitative`/`coding` as InferenceX's SPEED-Bench collector does (NeMo-Skills `prepare.py` at `5ac8609a`, then the collector's category filter), re-implemented for the coding category; livecodebench and code_contests rows resolve from the same pinned revisions.
- `agentx_rung.sh`, `agentx_ladder.sh` (new): one AgentX point on a fresh server behind `sglang-router` (`cache_aware`, `--dp-aware`, `x-correlation-id`), a saved `/flush_cache` reset, then InferenceX's replay-only driver (`python -m infx.bench agentic`) with scoring and validation; the ladder walks concurrencies and stops at the first failure. `AL` sets SGLang acceptance simulation (`match-expected`, `real-draft-token`).
- `dp_flush_repro.py` (new): flush the cache, then one short request, n times (the numerics probe's pattern), and report the first failure (AMD E03).
- `warm_long_ctx.py` (new): pre-loads the long-context kernel variants (KV-split indexer logits) on every DP rank before serving, routed by `routed_dp_rank`; `agentx_rung.sh` runs it after the sanity request.
- `agentx_summary.py` (new): one table row per AgentX point from its aggregate JSON.
- `prof_dep8_prefill.py`, `long_prefill_probe.py`, `mixed_stress.py` (new): DEP8 long-context prefill profile, single long-prompt probe, and mixed long-prefill/decode stress (AgentX E01).
- `agentx_ladder.sh` candidates `dep8_fp8_sched`, `dep8_fp8_sched_gv4`, `dep8_fp8_sched_gv`; `--mem-fraction-static` defaults to 0.80 (`MEM_FRAC`). `agentx_rung.sh` exports the aggregator's metadata.
- `prof_decode.py` (new): steady-decode profile at a given number of streams and context length, optionally all on DP rank 0 (AMD E04).
