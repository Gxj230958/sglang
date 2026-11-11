# E02 MoE runner backend for long-context decode on Vera Rubin — data@2026-11-11-0a30c79a92e3428c74e249a0270eb0ce8a42c32f-vr-moe-backend

## Environment

- Machine: 2 nodes × 4 NVIDIA Vera Rubin GPUs (compute capability 10.7, 212 SMs, 286524 MiB each, driver 620.47), one NVLink domain, Slurm with an enroot container per node.
- Layout: TP8 across the two nodes; FP8 weights, BF16 KV cache, `flashmla_sparse` DSA prefill and decode (the model defaults), FlashInfer all-reduce fusion (auto-enabled).
- Model: `zai-org/GLM-5-1028-Provider` at revision `66c3fe71d4c4ab43efac5bb0d2be6dea3a75d089` (from the download metadata of the local copy).
- Container: `lmsysorg/sglang` nightly `cu134-20261105-732d34b` imported as a squashfs image; the image digest was not recorded.
- Software in the image: torch `2.15.0+cu134`, transformers `5.19.0`, triton `3.9.0`, flashinfer-python `0.7.2` with `flashinfer-jit-cache-sm107a 0.7.2+cu134`, sglang-kernel `0.4.10`, CUDA 13.4. Full list in [`environment.log`](environment.log).
- Overlays on `PYTHONPATH`, ahead of the image's packages: SGLang source at the code commit below; DeepGEMM built from `sgl-project/DeepGEMM` `398a2ac`; FlashMLA built from the `sgl` branch at `46b6727`.

This is a non-release experiment: the container digest and the two kernel-library builds are not locked artifacts, and Subrun C ran a working tree that is not a single commit.

## Setup

Deploy the SGLang source of the code commit and put it first on `PYTHONPATH` together with the DeepGEMM and FlashMLA builds. On each of the two nodes (node rank 0 and 1):

```bash
export NCCL_SOCKET_IFNAME=eth0 GLOO_SOCKET_IFNAME=eth0 \
  NCCL_CUMEM_ENABLE=1 NCCL_MNNVL_ENABLE=1 NCCL_NVLS_ENABLE=1
export SGLANG_RUST_BUILD_MODE=never HF_HUB_OFFLINE=1
export SGLANG_SIMULATE_ACC_LEN=2.5        # Subruns A and B only
python3 -m sglang.launch_server --model-path /path/to/GLM-5-1028-Provider \
  --nnodes 2 --node-rank <RANK> --dist-init-addr <NODE0>:5201 --host 0.0.0.0 --port 30701 \
  --tp-size 8 <MOE_FLAG> \
  --mem-fraction-static 0.85 --context-length 140000 \
  --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph \
  --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 \
  --speculative-num-draft-tokens 4 --speculative-draft-model-path /path/to/GLM-5-1028-Provider \
  --reasoning-parser glm45 --tool-call-parser glm47 \
  --weight-loader-prefetch-checkpoints --model-loader-extra-config '{"enable_multithread_load": true}' \
  --watchdog-timeout 3600 --skip-server-warmup
```

`<MOE_FLAG>` per arm: `--moe-runner-backend deep_gemm`, `--moe-runner-backend triton`, `--moe-runner-backend flashinfer_trtllm`, or nothing (Subrun C, "unset").

Wait for HTTP 200 from `/health`, then run the workload from node 0.

The scripts in [`scripts/`](scripts/) are the ones used, as they stood at the end of the day. `serve.sh` gained three options after Subrun A, none of which changes Subrun A's command: a node-local model path when present, an optional decode graph batch-size list (unused), and `MOE` (empty omits the MoE flag; unset keeps `--moe-runner-backend deep_gemm`).

## Commit

- Code commit: `0a30c79a92e3428c74e249a0270eb0ce8a42c32f` (`radixark/sglang-zai`, branch `glm-5-lp`).
- Working tree, Subruns A and B: clean; deployed from `git archive` of this commit.
- Working tree, Subrun C: this commit plus cherry-picks of [the hybrid-SWA window write fix (PR #42)](https://github.com/radixark/sglang-zai/pull/42) and [the loop memory change (PR #43)](https://github.com/radixark/sglang-zai/pull/43), plus the 8-local-head split-K decode rule that later became `f98e456fbb` in [the split-K decode config change (PR #44)](https://github.com/radixark/sglang-zai/pull/44). Deployed as a tar of the working tree. Non-release.

## Scripts

- Version: none; the scripts are stored in this round under [`scripts/`](scripts/).
- `job.sbatch` starts the server on both nodes and runs `bench.sh` (Subrun A) or `eval.sh` (Subrun C). `ktab.py` and `seq.py` produce the per-kernel and per-layer listings from a decode trace. `argcheck.sh` is Subrun B.
- Temporary changes: none beyond the `serve.sh` options listed under Setup.

## Workload

### Subrun A: one-batch long-context decode

- Request source: `python3 -m sglang.benchmark.one_batch_server` of the code commit, random prompts, one warmup batch of 1024 tokens.
- Input and output lengths: 131072 input tokens, 512 output tokens.
- Batch sizes: 1 and 8. Two plain runs per batch size, then one profiled invocation (`--profile --profile-by-stage --profile-steps 5`), which records one plain and one profiled result line.
- Sampling: the benchmark's defaults. `SGLANG_SIMULATE_ACC_LEN=2.5` fixes the accepted tokens per verify step so that arms compare at equal acceptance.
- Metric: `output_throughput` of `results.jsonl` (tokens per second over the decode phase), and decode time per verify step as `acc_length / output_throughput × batch_size`.

### Subrun B: default backend resolution

`scripts/argcheck.sh` resolves the server arguments inside the container on one GPU, without loading weights, for `--tp-size 8` alone and for `--tp-size 8 --ep-size 8 --attn-dp-size 8 --moe-a2a-backend deepep`.

### Subrun C: GSM8K with the MoE flag unset and with DeepGEMM

- Request source: `python3 -m sglang.test.few_shot_gsm8k` of the working tree, the 1319-question GSM8K test split, 5-shot completion prompts, `--parallel 32`, 512 new tokens, temperature 0.
- No simulated acceptance (`SGLANG_SIMULATE_ACC_LEN=-1`); MTP runs with its real acceptance.
- This is a paired sanity check between backends, not the chat-format evaluation of the correctness project.

## Results

### Subrun A

Output tokens per second at 131072 input tokens, plain runs in order (the third value is the plain line of the profiled invocation):

| MoE runner backend | Batch 1 | Batch 8 | MoE kernels per layer, batch 1 | MoE kernels per layer, batch 8 |
|---|---|---|---|---|
| `deep_gemm` | 191.95, 65.39, 189.17 | 925.11, 961.49, 934.42 | 28.5 + 26.5 µs | 51.0 + 51.2 µs |
| `triton` | 206.11, 204.19, 211.26 | 892.13, 901.34, 892.18 | 29.3 + 18.5 µs | 61.2 + 72.0 µs |
| `flashinfer_trtllm` | 257.73, 259.26, 260.49 | 1151.62, 1138.07, 1147.03 | 12.6 + 9.6 µs | 43.6 + 22.8 µs |

The MoE columns are the two expert GEMM kernels of one mid-stack layer in the rank-0 decode trace (`arms/<backend>/layer-bs*.txt`); the TRT-LLM arm adds about 4.5 µs of activation and finalize kernels, and runs the shared expert as separate dense kernels.

| Metric | Baseline (`deep_gemm`) | Candidate (`flashinfer_trtllm`) | Delta |
|---|---:|---:|---:|
| Batch 1 output tokens/s, mean of plain runs excluding the 65.39 outlier | 190.6 | 259.2 | +36% |
| Batch 8 output tokens/s, mean of plain runs | 940.3 | 1145.6 | +22% |
| Whole-layer kernel time, batch 1 | 115 µs | 84 µs | −27% |
| Whole-layer kernel time, batch 8 | 196 µs | 157 µs | −20% |

### Subrun B

| Arguments | Resolved `moe_runner_backend` | Shared-expert fusion disabled |
|---|---|---|
| `--tp-size 8` | `flashinfer_trtllm` | yes |
| `--tp-size 8 --ep-size 8 --attn-dp-size 8 --moe-a2a-backend deepep` | `auto` | no |

### Subrun C

| Arm | Nodes | Accuracy | Invalid | Mean MTP accept length | Eval output tokens/s | Eval latency |
|---|---|---:|---:|---:|---:|---:|
| `--moe-runner-backend deep_gemm` | pair A | 92.6% | 0.0% | 2.854 | 917.3 | 144.2 s |
| `--moe-runner-backend deep_gemm` | pair B | 92.3% | 0.0% | 2.855 | 897.5 | 147.4 s |
| flag unset (`flashinfer_trtllm`) | pair A | 93.1% | 0.0% | 2.853 | 867.8 | 153.9 s |

Conclusions:

1. On Vera Rubin at TP8, the DeepGEMM MoE runner takes about half of each decode layer at 4 and 32 verify rows. The FlashInfer TRT-LLM runner raises long-context decode throughput by 36% at batch 1 and 22% at batch 8 at equal simulated acceptance.
2. The Triton runner is 9% faster than DeepGEMM at batch 1 and 5% slower at batch 8.
3. With `--moe-runner-backend` unset, plain TP already resolves to `flashinfer_trtllm` on this platform; the slower result comes only from passing `--moe-runner-backend deep_gemm` explicitly. With DeepEP the backend stays `auto`.
4. GSM8K accuracy and MTP acceptance are equal between the two backends within the sampling error of 1319 questions (about 0.7 points).
5. On the short-prompt, 32-concurrent GSM8K run the TRT-LLM arm finished 4–7% later than the DeepGEMM arms. This is one run per arm, includes prefill, and was not profiled, so the backend comparison above 8 concurrent requests remains open.
6. The decode step depends weakly on context length: per verify step only the indexer logits and Top-K kernels (24 calls each) scale with it; the sparse attention reads its Top-K 2048 keys at any length.

Known limits: one `deep_gemm` batch-1 run returned 65.39 tokens/s with no identified cause and is excluded from the mean; the batch-1 `deep_gemm` profile is distorted by profiler overhead (5 steps span 3.9 s), so its per-layer times come from kernel durations only; arms ran on different node pairs except where the table says otherwise; no B300 or Hopper measurement is part of this round.

## Data and Figures

- `arms/<backend>/results.jsonl` — one line per benchmark run, as written by the benchmark.
- `arms/<backend>/bench.log.gz`, `server-rank0.log.gz`, `job.log`, `arm-0.txt`, `server_args.json` — client log, rank-0 server log, job markers, the imported package paths, and the server arguments recorded by the profiler.
- `arms/<backend>/decode-trace-bs{1,8}-rank0.json.gz` — rank-0 decode-stage profiler traces (5 steps).
- `arms/<backend>/kernels-bs{1,8}.txt` — `python3 scripts/ktab.py <trace> 60`: GPU kernel time by kernel name.
- `arms/<backend>/layer-bs{1,8}.txt` — `python3 scripts/seq.py <trace> 40`: the kernel sequence of one layer and the DeepGEMM GEMM duration histogram.
- `default-backend-resolution.log` — Subrun B output.
- `accuracy/<arm>/eval.log`, `server-rank0.log.gz`, `job.log`, `arm-0.txt` — Subrun C. The backend of each arm is the `moe_runner_backend` value in the `server_args=` line of its server log; the arm directory named `deep_gemm-nodes-a` was launched under the job label `acc-default`.
- `environment.log` — GPU, compute capability, package versions and compiler of the container.
- `evidence-hashes.json` — SHA-256 of every file in this round.
