# E32 Upstream main sync correctness — data@2026-11-21-710a842c5741dade3ecd7d8583ef622745dcd9f2-upstream-main-sync

## Environment

- Machine: `mobius-8gb300-share`; one 4x NVIDIA GB300 rank per arm. The baseline used rank 0 and the candidate rank 1; each rank ran its three runs in sequence.
- Container: the box's `/opt/sglang` environment (E31 records the image as `lmsysorg/sglang:latest`); no immutable image digest was captured, so this round is non-release.
- Model: `zai-org/GLM-5-1028-Provider` at tracked FP8 revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`, including its own NextN draft. [checkpoint-receipt.json](checkpoint-receipt.json): both ranks match the config, weight-index, tokenizer and tokenizer-config hashes pinned to that revision in Correctness E27; weight shards were not rehashed.
- Software, both arms: torch 2.14.1+cu130, transformers 5.19.0, flashinfer-python 0.7.4, sglang-kernel 0.4.11, sgl-flash-mla 1.0.5, sgl-deep-gemm 0.2.9 built from DeepGEMM v0.2.9 `d66c3ada7739c496c23638f93e0b3b3ec761adf0` with `docker/patches/deep_gemm/0001-mega-moe-fp8-trtllm-weight-layout.patch`, tilelang 0.1.12, apache-tvm-ffi 0.1.11, xgrammar 0.2.7, triton 3.8.0.
- Software, per arm (each side's own pins): baseline sgl-deep-ep 0.1.2.post1 and nvidia-nccl-cu13 2.30.7; candidate sgl-deep-ep 0.1.3 and nvidia-nccl-cu13 2.31.2. Loaded versions are in each run's `versions.txt` (runtime `ncclGetVersion` 23007 / 23102), `loaded_libs.txt` (per-process mapped `deep_ep`, `libnccl` and `deep_gemm` libraries) and the `NCCL version` line of each server log.
- Evaluator: sgl-eval 0.1.3; evaluator-reported NeMo Skills revision `645cf567ff08c0ae9cc3fc8e1edbb975b3067816`.

## Setup

1. Verify [SHA256SUMS](SHA256SUMS) and the local archive hashes in [EVIDENCE-STORAGE.md](EVIDENCE-STORAGE.md).
2. Check out each arm's exact commit (below) and put its `python/` first on `PYTHONPATH`, followed by the patched sgl-deep-gemm, flashinfer 0.7.4 and sglang-kernel 0.4.11 / sgl-flash-mla 1.0.5 overlays.
3. Candidate only: install its pins outside the shared environment and load them first ([scripts/ovl.sh](scripts/ovl.sh)):

```bash
pip download --only-binary=:all: --no-deps -d wheels "sgl-deep-ep==0.1.3" "nvidia-nccl-cu13==2.31.2"
pip install --no-deps --target overlay-deps wheels/sgl_deep_ep-0.1.3-*.whl wheels/nvidia_nccl_cu13-2.31.2-*.whl
export PYTHONPATH=overlay-deps:$PYTHONPATH
export LD_PRELOAD=overlay-deps/nvidia/nccl/lib/libnccl.so.2
```

4. Launch, changing only the source checkout and the overlays (`NCCL_DEBUG=VERSION` set; no `--context-length`; CUDA graphs on; `SGLANG_SIMULATE_ACC_LEN` unset):

```bash
# TP4
python -m sglang.launch_server --model-path /path/to/GLM-5-1028-Provider \
  --host 127.0.0.1 --port 31200 --dist-init-addr 127.0.0.1:31201 \
  --tp-size 4 --kv-cache-dtype fp8_e4m3 \
  --speculative-algorithm EAGLE --reasoning-parser glm45

# DEP4 + megamoe
SGLANG_OPT_DEEPGEMM_MEGA_MOE_NUM_MAX_TOKENS_PER_RANK=8192 SGLANG_DP_USE_GATHERV=1 \
python -m sglang.launch_server --model-path /path/to/GLM-5-1028-Provider \
  --host 127.0.0.1 --port 31200 --dist-init-addr 127.0.0.1:31201 \
  --tp-size 4 --ep-size 4 --attn-dp-size 4 --moe-runner-backend megamoe \
  --kv-cache-dtype fp8_e4m3 --mem-fraction-static 0.9 --chunked-prefill-size 32768 \
  --speculative-algorithm EAGLE --reasoning-parser glm45
```

Resolved settings: TP4 uses `flashinfer_trtllm` MoE; DEP4 uses `moe_a2a_backend` megamoe, attention DP 4 and a per-rank chunked prefill of 8192. Both use TRTLLM DSA prefill/decode, EAGLE steps/top-k/draft tokens 3/1/4 and 48 running requests.

5. Evaluate each server:

```bash
sgl-eval run gsm8k --base-url http://127.0.0.1:31200/v1 --temperature 1.0 --top-p 0.95
```

6. Run `python3 verify.py` to recompute the gate from the raw samples, server information, versions and logs. The captured output is [verify.json](verify.json).

## Commit

- Candidate: `710a842c5741dade3ecd7d8583ef622745dcd9f2`, tree `9ab79bb1b50b67bbc9a1e7d75fbdc8ebddf33aff`, clean, pushed to `radixark/sglang-zai` branch `sync/glm-5-lp-on-upstream-main`. One commit, `Merge branch 'main' into glm-5-lp`, parents `glm-5-lp` `45bff30acfb5ec97673046ea7b8d36b822bbc520` and upstream `main` `8171e9a4f5418ddad2dda911b66605b9982cce7b`; `glm-5-lp` fast-forwards to it.
- Baseline: `glm-5-lp` `45bff30acfb5ec97673046ea7b8d36b822bbc520`, measured in this round.
- Merge base: `6de483b326c7dd4145fde06afcac9866bf491024`.
- `glm-5-lp` was re-checked unchanged immediately before the candidate push. After review, `glm-5-lp` was fast-forwarded to the candidate (`git ls-remote` readback `710a842c5741dade3ecd7d8583ef622745dcd9f2` at 2026-11-21T05:50Z). `sglang-zai` `main` was fast-forwarded to `8171e9a4f5418ddad2dda911b66605b9982cce7b`.

## Scripts

- [integration-report.md](integration-report.md) — merge, conflict, audit, dependency and Tier 1/Tier 2 report.
- [ready-for-review.md](ready-for-review.md) — the review hand-off written at push time.
- [verify.py](verify.py) — recomputes accuracy, finish reasons, launch settings, loaded NCCL/DeepEP versions, terminal status and both gates.
- [scripts/](scripts/) — `legs.sh` and `gate2c.sh` (launch, evaluate, capture), `ovl.sh` (candidate pins), `analyze.py`, the audit scripts and the CPU test runners.
- [tier1/](tier1/) — CPU test summaries and pre-commit logs.
- Temporary changes: none; both arms ran their exact commits.

## Workload

- Dataset: full GSM8K test split through sgl-eval 0.1.3 (1319 unique examples per run); the dataset checkout revision was not captured separately.
- Shape: one zero-shot chat request per example, 64 evaluator threads, no explicit output-token limit (the 262144-token context bounds generation).
- Sampling: temperature 1.0, top_p 0.95, no caller seed.
- Runs: TP4 once per arm; DEP4 twice per arm.

## Results

| Metric | Baseline `45bff30acf` | Candidate `710a842c57` | Delta |
|---|---:|---:|---:|
| TP4 correct / 1319 | 1251 | 1254 | +3 |
| TP4 accuracy | 94.84% | 95.07% | +0.23 pt |
| TP4 stop rate | 100.00% | 100.00% | 0 |
| DEP4 run 1 / run 2 correct | 1256 / 1249 | 1272 / 1257 | +16 / +8 |
| DEP4 two-run mean accuracy | 94.96% | 95.87% | +0.91 pt |
| DEP4 run 1 / run 2 stop rate | 100.00% / 99.77% | 100.00% / 99.92% | 0 / +0.15 pt |
| DEP4 length finishes (run 1 / run 2) | 0 / 3 | 0 / 1 | |
| Request errors / tracebacks, all runs | 0 / 0 | 0 / 0 | |
| Accept length, TP4 at >= 16 running (mean) | 2.692 | 2.694 | |
| Accept length, DEP4 DP0 at >= 8 running (mean, run 1 / run 2) | 2.667 / 2.652 | 2.679 / 2.663 | |

Conclusions:

1. TP4 gate (stop rate and accuracy at or above the baseline): PASS.
2. DEP4 + megamoe gate (every candidate run's stop rate at or above its paired baseline run; two-run mean accuracy at least the baseline mean minus 1.0 point): PASS.
3. Every `length` finish is a sample decoded to the context limit; they occur on both arms.
4. Wall times are descriptive only; the arms ran on different ranks with different long-sample mixes.

## Limits and release status

Candidate-integration correctness evidence, not a release selection. Exercised: TP4 and DEP4 attention DP, FP8 KV, TRTLLM DSA, EAGLE MTP, `flashinfer_trtllm` MoE and DeepGEMM MegaMoE with DeepEP 0.1.3 / NCCL 2.31.2 loaded. Not exercised: glm-5-lp #110's fused FlashMLA extra-KV prefill (bf16 KV with `flashmla_sparse` and a FlashMLA wheel exposing the API), HiSparse, PD disaggregation, unified memory, DCP/CP, the EP block-FP8 / MXFP8 decode MoE backends, fused-h64 and split-K decode, the hybrid-SWA layout, the cu134 image build and AMD/NPU. The image digest is unpinned and weight shards were not rehashed.

## Data and Figures

- [summary.md](summary.md) — concise result and gates.
- [terminal-snapshot.json](terminal-snapshot.json) — launch, readiness, evaluation and cleanup times for all six runs.
- `baseline-tp4/`, `baseline-dep4-r1/`, `baseline-dep4-r2/`, `candidate-tp4/`, `candidate-dep4-r1/`, `candidate-dep4-r2/` — per run: `status`, `versions.txt`, `loaded_libs.txt`, `analysis.json`, `server_info.json`, `eval/*/metrics.json`, 1319 per-sample outputs (`output-rs0.jsonl.gz`), server and evaluator logs (`*.log.gz`).
- [verify.json](verify.json) — recomputation output; gate `PASS`.
- [EVIDENCE-STORAGE.md](EVIDENCE-STORAGE.md) — local archive paths, sizes and hashes.
- No figures were generated.
