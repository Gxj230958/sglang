# E05 MI350X weight-free validation — data@2026-11-24-747c80ac250e5db44e4b242135da4bc9dbe76e86-mi350x-weight-free

First run of the `amd_support` tree on AMD Instinct MI350X: the GLM LoopLM unit tests, the ROCm attention-kernel tests, and an 8-GPU all-reduce check.
The checkpoint was not available on the machine, so this round loads no weights and serves no requests.
It establishes that the MI355X code runs on MI350X without changes up to the point where weights are needed; it is not a correctness or performance gate.

## Environment

- Machine: single-node AMD devbox with 8 AMD Instinct MI350X GPUs (SR-IOV virtual functions, gfx950), all GPU pairs linked by XGMI.
- Container: SGLang ROCm 10.0 development image; the image digest was not recorded.
- Hardware: AMD Instinct MI350X VF x 8.
- Model: none loaded.
- Software: ROCm 10.0.0, torch `2.11.0+rocm10.0.0`, triton `3.8.0`, amd-aiter `0.1.29.dev156+g581579ab5`, sglang-kernel `0.4.11`, transformers `5.19.0` ([environment.txt](environment.txt)). The MI355X rounds used amd-aiter `0.1.26.dev144+g285579b62` and sglang-kernel `0.4.10`.

## Setup

1. Check out `radixark/sglang-zai` branch `amd_support` at the code commit below and import SGLang from it.

   ```bash
   git clone https://github.com/radixark/sglang-zai.git
   cd sglang-zai
   git checkout 747c80ac250e5db44e4b242135da4bc9dbe76e86
   export PYTHONPATH=$PWD/python
   pip install blake3 zstandard watchfiles
   ```

2. Run the unit tests.

   ```bash
   python -m pytest -v -p no:cacheprovider \
     test/registered/unit/configs/test_glm_loop_config.py \
     test/registered/unit/cli/test_glm_loop_server_args.py \
     test/registered/unit/models/test_glm_loop.py
   ```

3. Run the attention-kernel tests on one GPU.

   ```bash
   HIP_VISIBLE_DEVICES=0 python -m pytest -v -rs -p no:cacheprovider \
     test/registered/kernels/ops/attention/test_glm_loop_attention.py \
     test/registered/kernels/ops/attention/test_glm_loop_fp8_sparse_decode.py
   ```

4. Run the all-reduce check on 8 GPUs.

   ```bash
   torchrun --nproc-per-node 8 allreduce_check.py
   ```

## Commit

- Code commit: `747c80ac250e5db44e4b242135da4bc9dbe76e86` (`radixark/sglang-zai`, branch `amd_support`, on `glm-5-lp` at `59860082`), the commit of AMD E04.
- Working tree: clean.

## Scripts

- [allreduce_check.py](allreduce_check.py) — round-specific: RCCL all-reduce of bf16 tensors of 4096, 1M and 64M elements across 8 ranks; checks the sum, then times 20 repetitions.
- Temporary changes: none.

## Workload

- Dataset or request source: none; repository tests and a synthetic all-reduce.
- Input and output lengths: not applicable.
- Concurrency or batch size: not applicable.
- Sampling and evaluation settings: not applicable.

## Results

| Check | Result |
|---|---|
| GLM LoopLM unit tests (config, server arguments, model) | 75 passed, 43 subtests passed |
| GLM LoopLM attention-kernel tests | 9 passed, 105 subtests passed, 35 skipped |
| 8-GPU all-reduce sum | correct at all three sizes |
| 8-GPU all-reduce bus bandwidth, 64M bf16 elements | 360.1 GB/s in this run (298 GB/s in an earlier run the same day) |

The 35 skipped kernel tests need FlashMLA, SM100/SM103 trtllm-gen sparse MLA, sgl-kernel's SM100+ `merge_state_v2`, or the CUDA fused FP8 sparse decode; each skip reason is in [attention-kernel-tests.log](attention-kernel-tests.log).

Conclusions:

1. The ROCm GLM LoopLM paths on `amd_support` (dual-bank Triton split-K, hybrid window pool through the triton route) pass their kernel tests on MI350X with the newer amd-aiter and sglang-kernel; no code change was needed.
2. All 8 GPUs communicate correctly over XGMI.
3. Serving on real weights is blocked: the checkpoint could not be downloaded. The supplied token was rejected by Hugging Face (HTTP 401), and the machine's own account has no read access to `zai-org/GLM-5-1028-Provider` or `zai-org/GLM-5.4-1122-Provider` (HTTP 404).

## Data and Figures

- [unit-tests.log](unit-tests.log) — pytest output of step 2.
- [attention-kernel-tests.log](attention-kernel-tests.log) — pytest output of step 3, with skip reasons.
- [allreduce-8gpu.txt](allreduce-8gpu.txt) — rank-0 output of step 4.
- [environment.txt](environment.txt) — ROCm, Python package versions, GPU product names and XGMI link count.
