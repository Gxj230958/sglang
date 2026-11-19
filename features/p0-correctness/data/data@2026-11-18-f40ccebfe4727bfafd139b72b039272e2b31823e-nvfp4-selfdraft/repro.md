# E30 NVFP4 self-draft fused-projection fix — data@2026-11-18-f40ccebfe-nvfp4-selfdraft

## Environment

- Machine: 4x GB300 GPUs, TP4.
- Runtime: development container; no immutable image digest was locked, so this round is non-release.
- Model: NVFP4 GLM LoopLM at revision `f2c64cebac62b1888c92c9d317adbb0b0aef5955`.
- Evaluation: sgl-eval full GSM8K 1319, temperature 1.0, top_p 0.95, max_tokens 32768, seeds 1 and 2.

## Setup

Launch the NVFP4 target with `--tp-size 4 --speculative-algorithm EAGLE --max-running-requests 64` and no draft path or draft quantization flags. Before the fix, the same default loaded the draft but accepted almost no draft tokens. The complete diagnosis is summarized below and `resolve2.py` preserves the CPU reproduction.

## Commit

- Validated head: `f40ccebfe4727bfafd139b72b039272e2b31823e`.
- Merged as: `26c4816830c53d867583f3d69117e23b44608481` in [#89](https://github.com/radixark/sglang-zai/pull/89).
- Working tree: clean; raw GPU gate logs remain on the benchmark allocation and are not imported into this branch.

## Root Cause

The draft class used an empty `packed_modules_mapping`. Under ModelOpt MIXED_PRECISION, `fused_qkv_a_proj_with_mqa` and `shared_experts.gate_up_proj` therefore resolved to no quantization algorithm and became unquantized BF16 linears. Their FP8 weights were cast to BF16 and their scale tensors were skipped. FP8 checkpoints are unaffected because `Fp8Config` quantizes every non-ignored linear.

## Results

| Run | GSM8K accuracy | Stop rate | Truncated | Errors | Mean accept len |
|---|---:|---:|---:|---:|---:|
| Seed 1 | 94.77% | 99.55% | 6 | 0 | 2.60 |
| Seed 2 | 94.09% | 99.62% | 5 | 0 | 2.56 |

Conclusions:

1. Declaring the target's `packed_modules_mapping` on the NextN class restores fused-projection resolution to `FP8_PB_WO`.
2. The regression test fails without the mapping with `[None, None]` and passes with it.
3. Accept length recovers from 1.00–1.02 to 2.56–2.60, while both full evaluations complete with zero request errors.
4. GB300 E15 NVFP4 natural-MTP performance rows predate this fix and must be rerun before final profile selection.

## Data and Figures

- `resolve2.py` — CPU quantization-resolution reproduction.
- [PR #89](https://github.com/radixark/sglang-zai/pull/89) — exact launch, modifications and full evaluation table.
- Raw GPU gate artifacts are retained on the benchmark allocation; this is PR validation and remains non-release.
