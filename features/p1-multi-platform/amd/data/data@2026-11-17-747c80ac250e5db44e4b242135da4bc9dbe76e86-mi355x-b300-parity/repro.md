# E04 MI355X against B300 on Correctness E14's workloads, and the DEP8 decode combine — data@2026-11-17-747c80ac250e5db44e4b242135da4bc9dbe76e86-mi355x-b300-parity

This round re-measures [Correctness E14](../../../../p0-correctness/data/data@2026-11-15-fb4015b5bdb6ed416beba624f365407089567b53-window-layout-speed/repro.md)'s B300 workloads on MI355X after E01–E03. It covers TP8 bf16, which E01 compared, and, for the first time, DEP8 with fp8 KV, the deployment E14 also measured on B300 and AgentX uses at high concurrency. It profiles the decode step behind each gap, and fixes a decode combine that ran on plain RCCL under DEP8.

Status: non-release; two seeds per workload on an unlocked environment.

## Environment

As [E03](../data@2026-11-17-9ee63b69cd3093a6e0d2b5fba6c0618ca1bfce57-mi355x-fp8-kv/repro.md) (8x MI355X, ROCm 10.0.0, model revision `66c3fe71d4c4ab43efac5bb0d2be6dea3a75d089`).

## Code

`radixark/sglang-zai`, branch `amd_support`:

| Commit | Content | Used by |
|---|---|---|
| `9ee63b69cd3093a6e0d2b5fba6c0618ca1bfce57` | E03's head | `par_tp8_9ee63b6`, `par_dep8_9ee63b6`, the profiles |
| `747c80ac250e5db44e4b242135da4bc9dbe76e86` | DP attention: return padded decode FFN outputs with aiter's reduce-scatter | `par_dep8_rsfix` (working tree equal to this commit, committed after the run) |

## Setup

Workloads are E14's, run with [`bench_parity.sh`](../../scripts/v2/bench_parity.sh): `sglang.bench_serving`, random IDs, `--flush-cache --warmup-requests 2`, seeds 1 and 2.

| Workload | Input / output tokens | Requests | Concurrency |
|---|---|---:|---:|
| `short-c1` | 2000 / 500 | 16 | 1 |
| `short-c32` | 2000 / 500 | 128 | 32 |
| `long-c4` | 30000 / 300 | 16 | 4 |

- **TP8 bf16:** E14's TP8 flags (`--mem-fraction-static 0.75 --context-length 65536 --chunked-prefill-size 32768 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph`, full-length layout) plus `--enable-aiter-allreduce-fusion`, with MTP 3/1/4.
- **DEP8 fp8:** E14's DEP8 shape (`--tp-size 8 --ep-size 8 --attn-dp-size 8 --moe-a2a-backend none --kv-cache-dtype fp8_e4m3 --context-length 147456 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph`, window layout, MTP 3/1/4).
  - Its kernels are ROCm's: triton DSA backends and AITER MoE.
  - `--mem-fraction-static 0.85` instead of 0.88, for the headroom AgentX E01 needed.
  - `SGLANG_DP_USE_GATHERV=1`.
  - Long-context kernel variants pre-loaded with [`warm_long_ctx.py`](../../scripts/v3/warm_long_ctx.py).

## Results

Output tokens/s per run, mean of the two seeds (each seed's log is in `bench/`):

| Configuration | Workload | MI355X | B300 (E14) | MI355X / B300 | Mean TPOT, MI355X / B300 (ms) | Median TTFT, MI355X / B300 (ms) |
|---|---|---:|---:|---:|---:|---:|
| TP8 bf16 | `short-c1` | 159.7 | 236.1 | 68% | 5.86 / 3.62 | 207 / 311 |
| | `short-c32` | 1183.6 | 1175 | 101% | 22.95 / 23.1 | 407 / 501 |
| | `long-c4` | 96.3 | 126.6 | 76% | 27.96 / 19.2 | 2451 / 2805 |
| DEP8 fp8, `9ee63b69` | `short-c1` | 61.9 | 134.6 | 46% | 15.32 / 6.63 | 441 / 387 |
| | `short-c32` | 745.8 | 1061 | 70% | 35.46 / 25.5 | 1612 / 1274 |
| | `long-c4` | 52.9 | 129.6 | 41% | 53.23 / 20.8 | 5407 / 2613 |
| DEP8 fp8, `747c80ac` | `short-c1` | 70.5 | 134.6 | 52% | 12.90 / 6.63 | 451 / 387 |
| | `short-c32` | 786.5 | 1061 | 74% | 33.43 / 25.5 | 1711 / 1274 |
| | `long-c4` | 56.2 | 129.6 | 43% | 47.95 / 20.8 | 6352 / 2613 |

E14's B300 references are TP8 bf16 with the full-length layout and DEP8 trtllm fp8 with the window layout. On TP8, E01 measured 58%, 99% and 76%. Concurrency 1 rose to 68% with the DSA indexer's fp32 head gate (`8be97a6f`) and the removed multimem probe (`7147d968`).

### Decode profiles (`profile/`)

**TP8 `long-c4`** (4 x 30K context, 10 profiled forwards, 274.5 ms, 98% busy):

- AITER fused MoE takes 29%, at 77 µs per call. That is about the HBM time to read the TP8 slices of the roughly 128 experts 16 tokens touch.
- About 8,900 kernels run per MTP cycle, and 83% of them average under 8 µs. Together those take half of all GPU time, at the ~4 µs per-kernel floor of graph replay.
- B300's cycle is about 50 ms (19.2 ms TPOT x 2.59 accepted tokens) against about 72 ms here. Closing the gap needs far fewer kernels per layer. Single fusions each remove about one kernel per layer, about 1–1.5% of the cycle.

**DEP8 `short-c1`** (rank 0, 12 forwards, 563 ms):

- CK block-FP8 dense GEMMs take 30% (5,520 calls x 28.6 µs). Each attention-DP rank reads the attention weights unsharded, eight times TP8's bytes per token.
- CK MoE GEMMs take 14%.
- RCCL kernels take 12.5% (1,308 calls x 50 µs): one per layer, the MoE combine.

### DEP8 decode combine (`747c80ac`)

With `--moe-a2a-backend none` under attention DP and EP, `boundary_reduction` resolves to `rs+rsv`, and `_select_dp_reduce_scatter` returned the variable-size `dp_reduce_scatterv` for every batch. On CUDA that path has an optimized collective; on ROCm it calls RCCL's `reduce_scatterv`.

An equal-padded (MAX_LEN) decode batch can use the equal-chunk reduce-scatter, which on ROCm is AITER's custom kernel. The fix selects it on ROCm for padded batches; unpadded batches and CUDA keep `reduce_scatterv`. A temporary log confirmed that the custom path accepts every decode combine, with no fallback. The unit tests `TestSelectDpReduceScatter` in `test_ffn_exit.py` fail on the ROCm case before the fix.

GSM8K-200 on DEP8 fp8 with the fix scored 93.5% with 98.5% stop, the same as before the fix ([`gsm8k200_dep8_combine_fix.log`](gsm8k200_dep8_combine_fix.log)), and no NaN was logged. The fix raises DEP8 throughput by 14% at concurrency 1, 5% at 32 and 6% on `long-c4`.

The `long-c4` median TTFT moved from 5.4 to 6.4 s between the two DEP8 runs. The change does not touch prefill, and that difference is not explained.

Conclusions:

1. TP8 bf16 matches B300 at concurrency 32 (101%) and trails at concurrency 1 (68%) and on `long-c4` (76%). Both gaps are set by the number of small kernels per decode cycle, not by one slow kernel.
2. DEP8 fp8 reaches 43–74% of B300's DEP8. Besides the kernel count, every rank reads the full attention weights for its few tokens, so DP attention's per-rank decode cost at low batch is higher than TP8's.
3. The RCCL decode combine was a ROCm-specific gap; `747c80ac` closes it. Further DEP8 decode gains need fewer kernels per layer and cheaper attention-projection GEMMs at small M.

## Data and Figures

- [`bench/`](bench/): `bench_serving` logs and per-request outputs for the three runs.
- [`profile/`](profile/): kernel summaries of the two decode profiles.
- [`gsm8k200_dep8_combine_fix.log`](gsm8k200_dep8_combine_fix.log): the correctness check of the fix.
