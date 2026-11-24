# E03 MI355X FP8 KV cache on DEP8 + window + MTP, and the DP draft-logits gather fault — data@2026-11-17-9ee63b69cd3093a6e0d2b5fba6c0618ca1bfce57-mi355x-fp8-kv

This round enables an fp8_e4m3 KV cache for GLM LoopLM on ROCm and validates it on the DEP8, window-layout, MTP deployment of [E02](../data@2026-11-17-df840adba7a0dfa794a221ec49c57daa601ec7c1-mi355x-dep8-hicache/repro.md). It also fixes a server crash that the FP8 run's numerics probe exposed on both the bf16 and fp8 servers. That crash was an out-of-bounds read in the MTP draft's logits gather under attention DP, which is not ROCm-specific.

Status: non-release; single runs on an unlocked environment.

## Environment

As E02 (8x MI355X, ROCm 10.0.0, torch 2.11.0+rocm10.0.0, model revision `66c3fe71d4c4ab43efac5bb0d2be6dea3a75d089`, sgl-eval 0.1.3).

The amdgpu driver kept device memory of servers that had crashed or been killed. It grew from 0 to about 44 GB per GPU over the day, while `rocm-smi --showpids` listed no process. In this round, available memory at load was 245 GB per GPU instead of 281 GB, so the KV pools below are smaller than on a freshly booted host. Only a host reboot returns this memory.

## Code

`radixark/sglang-zai`, branch `amd_support`:

| Commit | Content |
|---|---|
| `1d02ff8bae4ec7b5d86d7c60b69f4c0a1af5b610` | DP attention: size the draft extend's logits gather by requests |
| `9ee63b69cd3093a6e0d2b5fba6c0618ca1bfce57` | glm-loop: read a raw fp8_e4m3 KV cache in the ROCm dual-bank path |

The FP8 server ran from a working tree equal to `9ee63b69cd`, which was committed after the run.

## Setup

E02's DEP8 command at `--context-length 32768`, the context of [Correctness E06](../../../../p0-correctness/data/data@2026-11-12-710bcb2a3e6e4abbc299b43860c6528f7bd81db8-window-layout-matrix/repro.md)'s window-layout matrix that includes the fp8 run. The FP8 server adds `--kv-cache-dtype fp8_e4m3`. Script: [`fp8_dep8.sh`](../../scripts/v3/fp8_dep8.sh).

The bf16 numerics baseline comes from the same command with `--kv-cache-dtype bfloat16` (`dp_fix2`, after `1d02ff8b`).

## Results

### FP8 KV dual-bank read

On ROCm the triton and tilelang DSA backends store fp8 KV as raw 576-wide e4m3 rows without per-block scales. Both Triton kernels of a later cycle's dual-bank read already accepted that layout; only the server-args hook and `forward_dual_bank_triton` rejected it. Kernel error against a reference on the same fp8 values (`test_triton_two_banks_read_a_raw_fp8_cache`, DECODE and EXTEND, 8 and 64 heads):

| Route | Rows | Relative L2 error |
|---|---|---:|
| Fused split-K (keys upcast to bf16, bf16 query) | ≤ 8 | 0.04–0.18% |
| Per-bank split-K + LSE merge (fp8 dots, query rounded to fp8, as the regular slots) | > 8 | 2–4% |

### Serving

| | bf16 KV | fp8 KV |
|---|---:|---:|
| Full-layer tokens per DP rank | 1,153,216 | 2,138,112 (1.85x) |
| Window tokens per DP rank | 115,264 | 213,760 |
| GSM8K accuracy | E02: 94.92% | 94.62% (1248/1319) |
| GSM8K stop / truncated / errors | E02: 99.92% / 1 / 0 | 99.70% / 4 / 0 |
| Prefix-reuse probe (rank 3) | E02: 6/6 | 6/6 correct, cached 0 / 6656 / 6656 / 0 / 6656 / 6656 |

The NVIDIA references are DEP8 with trtllm and FP8 KV at 94.62% / 99.85% (Correctness E08), and the window layout with trtllm FP8 at 95.07% / 99.70% (Correctness E06). Each FP8 truncation is a generation that ran to the 32K context. The bf16 pool size is from the same leaked-memory state.

Numerics probe (`numcheck_compare.py`, 16 GSM8K prompts, 4080 teacher-forced tokens, cache flushed before every request):

| Pair | Mean \|Δlogp\| | p99 | Top-1 agreement | Identical greedy |
|---|---:|---:|---:|---:|
| fp8 against bf16, DEP8 | 0.0406 | 0.599 | 96.99% | 0/16 |
| bf16 against bf16, same TP8 server twice (E01) | 0.0310–0.0319 | 0.46–0.47 | 97.84–97.98% | 0/32 |

Parser smoke on the FP8 server passed 5/8. The thinking-on and `tool_choice=none` rows behave as in E02. `tool_choice=required` on a greeting ran to the 2048-token limit without a call. Repeated on the same server with `max_tokens=400`, it and a weather prompt each returned one `get_weather` call.

Acceptance length over the `Decode batch` lines of the first 8 minutes of GSM8K is 2.44. The bf16 run's first 11 minutes give 2.52.

### Draft logits gather under attention DP (`1d02ff8b`)

Symptom: in the first FP8 attempt, the bf16 and fp8 DEP8 servers both died a few requests into the numerics probe with `HSA_STATUS_ERROR_MEMORY_FAULT` in `memcpy_triton_kernel` ([`dp-logprob-fault/`](dp-logprob-fault/)). Each time it was the rank that served the request right after a `/flush_cache`. The E02 runs never flushed and never asked for input logprobs.

Diagnosis: a temporary bounds check on the DP-attention `memcpy` caught `offset=0 sz=257 dst=(257, 6144) src=(1, 6144)` from `DeepseekV3ForCausalLMNextN.forward → LogitsProcessor._get_logits → _gather_dp_attn_hidden_states`. In a prefill round the draft extend keeps only each request's last hidden state. Its logits DP gather was sized from the target's `global_num_tokens_for_logprob`, which for a request with input logprobs counts every logprob row (257 for the probe's teacher-forced prompt). The copy then read past its 1-row source. Normally the bytes past it are still mapped and the read goes unnoticed. After `/flush_cache` runs `empty_cache`, they are unmapped and the read faults.

Fix: the scheduler's DP sync also gathers each rank's request count. In a prefill round, keyed on the synced `is_extend_in_batch` so that idle ranks agree, the draft worker counts one logits row per request on every rank. A first attempt keyed on the local forward mode hung, because idle ranks sized the gather differently ([`dp_fix_hang_stacks/`](dp-logprob-fault/dp_fix_hang_stacks/)).

With the fix and the bounds check enabled, the probe completed 16 prompts and [`dp_flush_repro.py`](../../scripts/v3/dp_flush_repro.py) completed 40 flush-then-request cycles, with no out-of-range copy or fault. The unit test `test_draft_extend_gathers_one_logits_row_per_request` fails before the fix and passes after it.

Conclusions:

1. An fp8_e4m3 KV cache works for GLM LoopLM on MI355X with DEP8, the window layout and MTP. It holds 1.85 times the bf16 tokens per rank, and GSM8K matches the NVIDIA fp8 references (94.62% / 99.70% stop). Logprobs move 0.009 mean \|Δlogp\| and 0.9 points of top-1 agreement beyond the bf16 run-to-run floor.
2. Under attention DP with MTP, a request asking for input logprobs made the draft's logits gather read out of bounds on every platform. On ROCm the read faulted after `empty_cache`. `1d02ff8b` fixes it.

## Data and Figures

- [`fp8/`](fp8/): script status, parser smoke, prefix probe, GSM8K metrics and predictions.
- [`numcheck/`](numcheck/): both probe records and their comparison.
- [`dp-logprob-fault/`](dp-logprob-fault/): the faulting bf16 server log, the diagnostic server's out-of-range report, the hung first attempt with its rank stacks, and the verified server log.
- [`logs/dep8_fp8.log.gz`](logs/dep8_fp8.log.gz): FP8 server log without AITER's per-kernel lines.
