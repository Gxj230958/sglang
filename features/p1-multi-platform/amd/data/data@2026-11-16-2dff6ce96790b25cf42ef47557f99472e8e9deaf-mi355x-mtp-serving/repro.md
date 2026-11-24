# E01 MI355X MTP serving, fusions, and B300-parity benchmark — data@2026-11-16-2dff6ce96790b25cf42ef47557f99472e8e9deaf-mi355x-mtp-serving

This round brings up MTP (EAGLE 3/1/4) on the standard MI355X serving path at the B300 TP8 deployment's feature set, and validates it with smokes and full GSM8K. It then measures Correctness E14's B300 workloads before and after two kernel fusions, and records an investigation of a node-wide degradation that two MTP launches hit.

The results mix code commits, so the round is non-release (see [Code](#code)).

## Environment

- Hardware: one node, 8x AMD Instinct MI355X (gfx950, 256 CUs, 288 GB each), XGMI. Host kernel `5.15.0-163-generic`, amdgpu DKMS `6.16.6`. amdgpu parameters: `noretry=1` (XNACK off), `sched_policy=0` (HWS), `mes=0`. Host settings: NUMA balancing off, KSM off, THP `madvise`.
- Container: SGLang ROCm 10.0 development image (digest not recorded). ROCm `10.0.0`, torch `2.11.0+rocm10.0.0`, triton `3.8.0+rocm10.0.0`, amd-aiter `0.1.26.dev144+g285579b62`, sglang-kernel `0.4.10`, transformers `5.19.0`.
- Model: `zai-org/GLM-5-1028-Provider` at revision `66c3fe71d4c4ab43efac5bb0d2be6dea3a75d089`, as in Correctness E36.
- Evaluator: sgl-eval `0.1.3`.

## Code

`radixark/sglang-zai`, branch `amd_support`:

| Commit | Content | Used by |
|---|---|---|
| `8a30c7bf578474d214210642c18a56b2db9a43a5` | E36 base plus per-bank split-K for later-cycle reads | `mtp_r1` (MTP baseline: bench, GSM8K, profile) |
| `7a8cff1060` + `2dff6ce96790b25cf42ef47557f99472e8e9deaf` | HIP shared-expert fusion admits the GLM LoopLM geometry; the AITER allreduce fusion is allowed; ROCm branches honor platform overrides | `mtp_r2` (fused: bench, GSM8K, profile, numerics A) |
| `8be97a6f86940f8f946dd8647b786286365c1318` | DSA indexer: eager fp32 head gate on ROCm | `nc_B` (numerics B), `mtp_r3` |
| `7147d9686db189b04b5b43cc2d8d938fd51e2b91` | Skip the multimem all-gather probe on ROCm | not yet measured |

`mtp_r2` and `nc_B` ran from working trees whose code equals `2dff6ce967` and `8be97a6f86`; those commits were created after the runs. `glm5_next.py` was ruff-formatted between the run and the commit, a formatting-only change.

## Setup

Scripts: [scripts/v2/](../../scripts/v2/) ([CHANGES.md](../../scripts/v2/CHANGES.md)). `launch.sh` sets TP8, a bf16 KV cache, `--reasoning-parser glm45 --tool-call-parser glm47` and `--watchdog-timeout 1800`, with AITER enabled. The model's ROCm defaults apply: `triton` DSA prefill and decode, which read a later cycle's two banks with the Triton split-K. Later flags override `launch.sh`'s defaults.

The B300 TP8 flags of [Correctness E14](../../../../p0-correctness/data/data@2026-11-15-fb4015b5bdb6ed416beba624f365407089567b53-window-layout-speed/repro.md), common to every MTP launch here:

```bash
scripts/v2/start_bg.sh <name> 30000 --mem-fraction-static 0.75 --context-length 65536 \
  --chunked-prefill-size 32768 --max-running-requests 32 --cuda-graph-max-bs-decode 32 \
  --disable-prefill-cuda-graph --speculative-algorithm EAGLE --speculative-num-steps 3 \
  --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 \
  --speculative-draft-model-path /path/to/GLM-5-1028-Provider --enable-cache-report
```

- `mtp_r1`: the common flags at `8a30c7bf57`. Shared-expert fusion is off there, because the HIP gate rejected this geometry.
- `mtp_r2`, `mtp_r3`: the common flags plus `--enable-aiter-allreduce-fusion`. Shared-expert fusion is on by default from `7a8cff1060`; the target log says "Shared experts fusion optimization enabled". The draft keeps its shared expert unfused.
- `nc_B`: the common flags plus `--disable-shared-experts-fusion`, without the allreduce fusion.

The servers use the full-length KV layout (`hybrid_swa=False`), the same layout as the B300 numbers.

## Workload

- Smokes: `scripts/v2/smoke.py` runs text, an image ("Red") and a 3130-token long-context retrieval, through chat completions.
- GSM8K: `sgl-eval run gsm8k --num-examples 1319 --temperature 1.0 --top-p 0.95 --num-threads 64`, with no output limit, as in Correctness E03/E36.
- Serving: `scripts/v2/bench_parity.sh` runs `bench_serving` on random IDs with `--random-range-ratio 1 --flush-cache --warmup-requests 2`, seeds 1 and 2, EOS ignored:
  - short-c1: 2000/500, 16 requests, concurrency 1;
  - short-c32: 2000/500, 128 requests, concurrency 32;
  - long-c4: 30000/300, 16 requests, concurrency 4.

  B300 targets are E14's TP8 BF16 full-layout arm.
- Numerics: `scripts/v2/numcheck.py` uses 32 GSM8K problems (chat template, thinking off). It collects a greedy continuation of 256 tokens, and teacher-forced logprobs plus top-1 on the reference continuations (`A_ref`, from `mtp_r2`). The cache is flushed before each request.
- Decode profile: SGLang `/start_profile` with GPU activities captures 8 steps during a 2000-token, concurrency-1 decode. Cycles are split at idle gaps over 50 µs (`decode_breakdown.py`).

## Results

### Correctness

| Check | `mtp_r1` (MTP, unfused) | `mtp_r2` (MTP, fused) | Reference |
|---|---:|---:|---:|
| Smokes text/image/long | 3/3 | 3/3 | — |
| GSM8K accuracy | 95.75% | 93.78% | E36 no-MTP 94.84%; B300 MTP 93.86%; H200 MTP 94.31% |
| GSM8K stop / truncated / errors | 99.92% / 0.08% / 0 | 99.77% / 0.23% / 0 | — |

Numerics probe (`numcheck_compare.py`; 8164 teacher-forced tokens):

| Pair | Mean \|Δlogp\| | p99 | Top-1 agreement | Identical greedy |
|---|---:|---:|---:|---:|
| A vs A, same fused server twice | 0.0319 | 0.460 | 97.84% | 0/32 |
| B vs B, same unfused server twice | 0.0310 | 0.466 | 97.98% | 0/32 |
| A vs B, fused against unfused (old vs new indexer gate) | 0.0339 | 0.486 | 97.82% | 2/32 |

### Serving against B300

Means of the two seeds:

| Workload | Metric | `mtp_r1` | `mtp_r2` | B300 E14 | `mtp_r2` / B300 |
|---|---|---:|---:|---:|---:|
| short-c1 | Output tok/s | 118.6 | 137.4 | 236.1 | 58% |
| | Mean TPOT (ms) | 7.90 | 6.92 | 3.62 | |
| | Median TTFT (ms) | 227 | 209 | 311 | |
| | Accept length | 2.79 | 2.74 | 3.09 | |
| short-c32 | Output tok/s | 1061.8 | 1161.9 | 1175 | 99% |
| | Mean TPOT (ms) | 25.36 | 23.51 | 23.1 | |
| | Median TTFT (ms) | 430 | 404 | 501 | |
| long-c4 | Output tok/s | 91.0 | 95.7 | 126.6 | 76% |
| | Mean TPOT (ms) | 30.20 | 28.96 | 19.2 | |
| | Median TTFT (ms) | 2536 | 2447 | 2805 | |

During `mtp_r1`'s benchmark, the doctor's first version raised a false capture alert. It ran `py-spy dump` on all ranks at 06:12:40 and 06:17:40, two short pauses inside short-c1/short-c32 seed 1. The `mtp_r2` run had the fixed doctor.

### Concurrency-1 decode profile (TP0, one MTP cycle)

| | Unfused (`mtp_r1`) | Fused (`mtp_r2`) |
|---|---:|---:|
| Kernels per cycle | 4211 | 3517 |
| GPU time per cycle (profiled) | 26.1 ms | 22.1 ms |

GPU busy time is 97% with no host gaps. Most small kernels sit at a floor of about 4.1 µs, so the kernel count sets the cycle time; B300's cycle is about 11.2 ms. After fusion the biggest items are:
- CK MoE GEMM: 212 calls, 3.1 ms. The configs are AITER's tuned E=257/top-9 configs for 256 CUs.
- Fused allreduce plus RMSNorm: 211 calls, 2.7 ms.
- Per-group activation quant: 575 calls, 2.4 ms.
- CK block-FP8 GEMM: 254 calls, 2.0 ms.

The DSA indexer's head gate ran a bf16×fp32 broadcast at about 22 µs in each of 24 full-indexer layers per cycle; `8be97a6f86` fixes it. Its serving gain was not measured, because `mtp_r3` hit the degradation below.

### Node degradation (open)

Symptom: every multi-process GPU operation on the node slows to about 156 ms (a 2 KB RCCL all-reduce normally takes 20 µs). The state persists after every GPU process exits, and only a host reboot clears it.

Onsets:
- `real_mtp`, Correctness E36 code with `--disable-custom-all-reduce` and draft graphs up to bs=64: the earlier "MTP hang".
- `mtp_r3`.

In both cases the onset came at the first eager forward of the **draft** model's CUDA graph capture:
- Target-verify capture was normal in both: about 1 s per shape.
- In `mtp_r3`, draft decode capture took 695 s (about 35 s per shape, from the first shape on). Draft extend took 289 s. Then the warmup request timed out after 600 s and the server stopped itself. No rank was killed and no core dump was written.
- `mtp_r1`, `mtp_r2` and `nc_B` captured all draft shapes in 3–4 s.

So two of five MTP launches hit it, with or without custom all-reduce, fusions or the new indexer gate.

Evidence, in [node-degradation/](node-degradation/):
- During the stall, the doctor's stacks show every rank busy-waiting on an HSA signal in `DsaGraphVariants.select` (`seq_lens.max().item()`): queued GPU work was not finishing.
- In the degraded state, a fresh 2-rank all-reduce process logs about 650 KFD `QUEUE_EVICTION` events, each with a matching `QUEUE_RESTORE`, per rank in about 10 s, and spends about 16 s of its first 25 s evicted (sysfs `evicted_ms`). With `HSA_USE_SVM=0` the SVM migrations disappear but the evictions do not. amdsmi decodes every eviction's trigger field as 0, which may be a parsing mismatch with this driver.
- GTT is 327 MB used of 1.5 TB and VRAM is free. During the storm there is no page migration, compaction, reclaim, KSM or khugepaged activity.
- In both slow launches, the draft model's `MultimemAllGatherer` probe ran 2 s before the onset. That probe is the second torch symmetric-memory build in each rank: a device buffer exported to and mapped by all 8 ranks, then dropped because ROCm has no multicast. The fast launches ran it too. `7147d9686d` removes it on ROCm as the prime suspect, and `scripts/v2/symm_stress.py` repeats it in isolation; neither has run on a healthy node yet.
- The host kernel log was not readable from the container (`dmesg`: operation not permitted).

Conclusions:
1. MTP works on the standard MI355X path at the B300 TP8 feature set: EAGLE 3/1/4, decode CUDA graph to bs=32, 64K context, image input, cache report and parsers. Smokes pass, and full GSM8K scores 95.75%.
2. Shared-expert fusion plus the AITER allreduce fusion raise throughput by 16% at concurrency 1, 9% at concurrency 32 and 5% on long-c4. Short-c32 reaches 99% of B300, and TTFT beats B300 on all three workloads. Fused against unfused, logprobs differ by no more than the run-to-run noise floor. That floor is itself sizable on ROCm: about 2% of top-1 tokens flip between identical prefills, fused or not. Fused GSM8K (93.78%) is within sampling noise of the reference.
3. At concurrency 1, MI355X reaches 58% of B300. The cycle is bound by kernel count (about 3500 kernels at a 4 µs floor), so closing the gap needs fewer launches per layer, not further kernel tuning.
4. Two MTP launches hit a node-wide KFD queue-eviction state that began at the draft's first forward. The trigger is unconfirmed; next come `symm_stress.py` and repeated MTP launches at `7147d9686d` on a freshly rebooted node, plus the host kernel log from the onset.

## Data and Figures

- `bench/mtp_r1/`, `bench/mtp_r2/`: `bench_serving` logs and per-request JSONL (gzip) for each workload and seed; `summary.txt`.
- `gsm8k/gsm8k_mtp/`, `gsm8k/gsm8k_mtp_fused/`: `metrics.json`, `output-rs0.jsonl.gz` (predictions), `eval.log`.
- `numcheck/`: probe outputs: `A_ref` (references), `A1f`/`A2f` (fused, twice), `B1`/`B2` (unfused, twice).
- `profile/`: TP0 torch-profiler traces (`c1-unfused-tp0.trace.json.gz`, `c1-fused-tp0.trace.json.gz`) and their `decode_breakdown.py` outputs.
- `logs/`: server logs (gzip) for `real_mtp` (the original slow run), `mtp_r1`, `mtp_r2`, `nc_B` and `mtp_r3`.
- `node-degradation/`: `mtp_r3.doctor.log` (per-rank eviction and progress samples), `mtp_r3-stacks/` (py-spy stacks of all ranks at 07:50:10 and 07:55:10), `kfd-evidence.txt` (degraded-state KFD events, memory accounting, host and driver settings).
