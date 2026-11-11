# E02 Split-K sparse decode config on Vera Rubin — data@2026-11-11-b04b763b055e1a04358f03f6666280e00c54389c-vr-split-decode

## Environment

- Machine: NVIDIA Vera Rubin GPU (compute capability 10.7, 212 SMs, 286524 MiB, driver 620.47); one GPU per kernel job, 2 nodes × 4 GPUs for the serving subrun.
- Model: none for the kernel subruns (synthetic tensors at the model's shapes); `zai-org/GLM-5-1028-Provider` at revision `66c3fe71d4c4ab43efac5bb0d2be6dea3a75d089` for the serving subrun.
- Container and software: as in [General Performance E02](../../../p0-general-performance/data/data@2026-11-11-0a30c79a92e3428c74e249a0270eb0ce8a42c32f-vr-moe-backend/repro.md); versions in [`environment.log`](environment.log).

Non-release: the container digest is not recorded and the serving subrun ran a working tree that is not a single commit.

## Setup

Put the SGLang source on `PYTHONPATH` inside the container and run one GPU job per sweep:

```bash
# Config sweep: rows, then "block_h,num_warps,target_programs,block_k;..." candidates
HEADS=8 DUAL=1 python3 scripts/split_rig.py 4,8,16,32,64 "8,4,512,64;16,4,296,64"
# Selected rule and the registered GPU test, on the candidate source
bash scripts/verify3.sh
```

`split_rig.py` asserts that it imports SGLang from the expected source directory; adjust that path and the paths in `rig.sbatch`, `sweep.sh` and `verify3.sh` to the local layout.

## Commit

- Code commit: `b04b763b055e1a04358f03f6666280e00c54389c`, the head of [the split-K decode config change (PR #44)](https://github.com/radixark/sglang-zai/pull/44) on `radixark/sglang-zai`, based on `glm-5-lp` at `0a30c79a92e3428c74e249a0270eb0ce8a42c32f`.
- Config sweeps `rig-5038` to `rig-5042`: source at `0a30c79a92`, clean.
- `rig-5044`, and config sweeps `rig-5073` to `rig-5081` and `rig-5085` to `rig-5087`: `0a30c79a92` plus the 8-head rule of `f98e456fbb`. The rig sets the config per call and the kernel code is the base commit's; at 16, 32 and 64 heads that rule does not apply, so the module default there is still `(16, 4, 296)`.
- `rig-5088`: a tar of the working tree whose only difference from `b04b763b05` is one blank line.
- Serving subrun: `0a30c79a92` plus cherry-picks of PR #42 and PR #43 plus the 8-head rule of `f98e456fbb`; the 16/32/64-head part of `b04b763b05` did not run in a server.

## Scripts

- Version: none; stored in this round under [`scripts/`](scripts/).
- `split_rig.py` builds 4 layers of `[1048576, 1, 576]` BF16 KV (and a second bank), 8 requests of 131072 context, random Top-K 2048 indices per row and a 128-token window for the second bank; captures the 4 calls in one CUDA graph; reports the best of 5 × 300 replays per call; and checks every arm against a dense FP32 softmax over the selected keys.
- Its first config, printed as `(0,0,0,64)`, removes the table entry of the shape and calls the module default. On `0a30c79a92`, and above 8 heads with the 8-head rule, that is the `(16, 4, 296)` fallback; on the candidate source it is the new rule.
- Temporary changes: none.

## Workload

- Kernel: `sparse_mla_decode` of `python/sglang/kernels/ops/attention/glm_loop_sparse_decode.py`, single bank and dual bank.
- Shapes: 8, 16, 32 and 64 local heads; 2 to 64 rows; Top-K 2048; BF16 query and KV.
- Baseline: the config the base commit runs on this device, which is the B300 table entry where one exists for `(rows, heads)` and `(16, 4, 296)` otherwise.
- Candidate: 4 warps; `(8, 4, 512)` up to 8 local heads; `(16, 4, 296)` up to 16 heads and for 32 heads below 4 rows; `(32, 4, 296)` otherwise.
- Serving subrun: the Subrun A workload of General Performance E02 (131072 input tokens, 512 output tokens, batch 1 and 8, simulated acceptance 2.5) with the FlashInfer TRT-LLM MoE runner.

## Results

Time per call, candidate / baseline, single bank. Dual-bank ratios are within 0.03 of these.

| Rows | 8 heads | 16 heads | 32 heads | 64 heads |
|---|---:|---:|---:|---:|
| 2 | not compared | 1.00 | 1.00 | 0.93 |
| 3 | not compared | 1.00 | 0.79 | 0.75 |
| 4 | 0.96 | 1.00 | 0.94 | 1.00 |
| 8 | 0.90 | 1.00 | 1.00 | 0.89 |
| 12 | 0.91 | 1.00 | 0.71 | 1.00 |
| 16 | 0.93 | 1.00 | 0.89 | 1.00 |
| 32 | 0.83 | 1.00 | 0.93 | 0.90 |
| 64 | 0.76 | 1.00 | 0.91 | 0.87 |

Cells at 1.00 run the same config before and after. Candidate time per call, single bank, from `rig-5088`:

| Rows | 8 heads | 16 heads | 32 heads | 64 heads |
|---|---:|---:|---:|---:|
| 4 | 5.93 µs | 6.56 µs | 7.98 µs | 11.18 µs |
| 8 | 7.81 µs | 9.30 µs | 11.49 µs | 16.70 µs |
| 16 | 11.38 µs | 12.62 µs | 17.65 µs | 26.90 µs |
| 32 | 15.10 µs | 19.93 µs | 28.17 µs | 45.60 µs |
| 64 | 22.72 µs | 32.13 µs | 48.39 µs | 81.48 µs |

Serving subrun (8 local heads):

| Metric | Baseline | Candidate | Delta |
|---|---:|---:|---:|
| `_split_kernel` average per call, batch 8 (32 verify rows), rank-0 decode trace | 15.9 µs | 12.2 µs | −23% |
| `_split_kernel` average per call, batch 1 (4 verify rows) | 5.3 µs | 5.3 µs | 0% |
| Batch 8 output tokens/s, three runs | 1151.62, 1138.07, 1147.03 | 1181.95, 1154.79, 1206.32 | +3.1% raw, about +1.6% per verify step |
| Batch 1 output tokens/s, three runs | 257.73, 259.26, 260.49 | 257.7, 261.5, 255.94 | flat |

The serving baseline is the `flashinfer_trtllm` arm of General Performance E02, which ran on a different node pair and without PR #42 and PR #43; the throughput difference is within node-to-node variance and is not a claim of this round. The trace average is the supporting observation.

Conclusions:

1. On Vera Rubin the 8-local-head shape of TP8 is 4–24% faster per call with an 8-head block and a 512-program target, with the gain growing with the row count.
2. Eight warps lose at every head block and row count measured (1.0–1.9× the 4-warp time), including the B300 table's 8-warp entries; the table is therefore not read on compute capability 10.7.
3. At 32 and 64 local heads a 32-head block with 4 warps is the best or tied config from 4 rows up (from 2 rows at 64 heads). At 16 local heads no config beat `(16, 4, 296)` across the row range.
4. Losing variants: more than about 512 programs of 8-head blocks; 1-tile splits of 16-head blocks; `BLOCK_K = 128`; 2 warps.
5. Every arm matches the dense reference with a relative error of 2–3e-3, the same as the base config, and `test/registered/kernels/ops/attention/test_glm_loop_attention.py` of the base commit passes on the candidate source (17 passed, 135 subtests).

Not covered: B300 or any other device (their behaviour is unchanged by the PR); 32- and 64-head serving; an end-to-end accuracy evaluation of this change.

## Data and Figures

- `rig/rig-5038.log` to `rig-5042.log` — 8 local heads, config sweeps.
- `rig/rig-5044.log` — 8 local heads, the 8-head rule as module default against `(16, 4, 296)`.
- `rig/rig-5073.log` to `rig-5081.log` — 16, 32 and 64 local heads, single bank, config sweeps.
- `rig/rig-5085.log` to `rig-5087.log` — rows 2, 3, 12 (and 24, 48 at 16 heads), both banks.
- `rig/rig-5088.log` — the final rule as module default at 8, 16, 32 and 64 heads, and the GPU test result.
- `serving/` — the candidate serving run: `results.jsonl`, logs, `server_args.json`, rank-0 decode traces and the `kernels-bs*.txt` / `layer-bs*.txt` listings produced by `ktab.py` and `seq.py` of General Performance E02.
- `scripts/` — `split_rig.py`, `rig.sbatch`, `sweep.sh`, `verify.sh`, `verify3.sh`.
- `environment.log` — GPU, compute capability, package versions and compiler of the container.
- `evidence-hashes.json` — SHA-256 of every file in this round.
