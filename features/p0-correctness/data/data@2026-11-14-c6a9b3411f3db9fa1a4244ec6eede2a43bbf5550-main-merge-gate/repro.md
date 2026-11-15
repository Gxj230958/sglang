# E08 Upstream main merged into the model branch: TP8 and DEP8 gate — data@2026-11-14-c6a9b3411f3db9fa1a4244ec6eede2a43bbf5550-main-merge-gate

## Environment

- Machine: one node with 8× NVIDIA B300.
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`, served from a node-local copy; the checkpoint's own NextN head is the MTP draft. The copy was not re-hashed for this round.
- Software: image torch 2.14.1+cu130 and transformers 5.19.0; a first overlay adds sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5 and kernels 0.14.1; a second adds flashinfer-python / cubin / jit-cache 0.7.3. The code pins FlashInfer 0.7.4, which was not installed. `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.

## Setup

Deploy `git archive c6a9b3411f` and run [`gate.sh`](gate.sh) (TP8) and [`gate-dep8.sh`](gate-dep8.sh) (DEP8). The first launch fails on the kernel version check until the dependency overlay with sglang-kernel 0.4.11 is ahead of the image packages. All servers use `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model>` and `--enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47`; no layout variable is set, so these runs use the full-length layout.

- TP8: `--tp-size 8 --mem-fraction-static 0.75 --context-length 65536 --chunked-prefill-size 32768 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph`.
- DEP8: `--tp-size 8 --ep-size 8 --attn-dp-size 8 --moe-runner-backend flashinfer_trtllm --moe-a2a-backend none --dsa-prefill-backend trtllm --dsa-decode-backend trtllm --kv-cache-dtype fp8_e4m3 --context-length 147456 --mem-fraction-static 0.88 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --chunked-prefill-size 65536 --enable-fp32-lm-head`.

## Commit

- Code commit: `c6a9b3411f3db9fa1a4244ec6eede2a43bbf5550`, a local merge of upstream `main` at `6de483b326` (131 commits) into `glm-5-lp` at `4922ea6eab`.
- Working tree: clean archive of the commit.
- This commit was not pushed. The pushed merge is `ec8bc57fde`, recorded in [E09](../data@2026-11-15-ec8bc57fde48466d602529752d428b466efc54cf-main-merge-dep8/repro.md).
- Status: non-release. The image digest is not recorded and dependencies come from `PYTHONPATH` overlays, so the environment is not locked.

## Scripts

- Version: round-specific [`gate.sh`](gate.sh), [`gate-dep8.sh`](gate-dep8.sh) and [`suite.py`](suite.py).
- Temporary changes: none.

## Workload

- GSM8K: full test split (1319 questions) through `sgl-eval` 0.1.3, `sgl-eval run gsm8k --base-url <server>/v1 --temperature 1.0 --top-p 0.95`, 64 client threads, server-default thinking, no `max_tokens`, one run per configuration.
- Smoke suite ([`suite.py`](suite.py) `smoke`): text, thinking, 4K / 12K / 24K long-context needle and image requests.

## Results

| Configuration | Accuracy | Stop rate | Truncated | Errors | Accept len | Smoke | KV pool |
|---|---|---|---|---|---|---|---|
| TP8, `flashmla_sparse`, BF16 KV | 94.69% (1249/1319) | 99.92% | 1 | 0% | 2.64 | 6/6 `stop` | 920448 tokens |
| DEP8, `trtllm`, FP8 KV | 95.07% (1254/1319) | 100.00% | 0 | 0% | 2.66 | 6/6 `stop` | 2058688 tokens per DP rank |

Accept length is the mean of the `accept len` field over the `Decode batch` lines of the server log. Truncated counts requests that ended with `finish_reason=length`.

Conclusions:

1. The merge passes the GSM8K stop-rate gate and the smoke suite on both B300 configurations, with no traceback.
2. Not covered by this gate: the window layout, prefill CP, PD, HiCache, GB300, FlashInfer 0.7.4, and the image build. The window, CP, PD and HiCache combinations were re-gated on the merged branch in [Prefill CP E03](../../../p0-parallelism/prefill-cp/data/data@2026-11-15-f02daab4df4c9ebfa854ecc7e2da3dd151496389-window-cp4-merged-dev/repro.md) and [PD Disaggregation E03](../../../p0-pd-disagg/data/data@2026-11-15-bdbebf62fca4af4e628e26f9e55d139bb7794047-rdma-window-full-hicache/repro.md).

## Data and Figures

- [`tp8/`](tp8/), [`dep8/`](dep8/) — launch script, compressed server log, smoke results, `gsm8k.log` and sgl-eval output.
- `status-tp8`, `status-dep8-c6a9`, `gate.out`, `gate-dep8.out` — driver status and console.
- [`summary.json`](summary.json) — every number in the Results section, recomputed from the committed files by [`summarize_round.py`](../../scripts/v2/summarize_round.py).
- [`evidence-hashes.json`](evidence-hashes.json) — original path and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
