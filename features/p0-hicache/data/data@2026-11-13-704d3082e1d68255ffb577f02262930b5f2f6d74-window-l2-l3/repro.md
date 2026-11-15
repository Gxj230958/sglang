# E03 Host L2 and file L3 on the window layout after the rebase — data@2026-11-13-704d3082e1d68255ffb577f02262930b5f2f6d74-window-l2-l3

## Environment

- Machine: two nodes with 4× NVIDIA GB300 each (node A and node B), no shared disk. Each server uses the four GPUs of one node. This round used node B.
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`, served from a node-local copy; the checkpoint's own NextN head is the MTP draft. The copy was not re-hashed for this round.
- Software: the image's FlashInfer (0.7.1 on node A, 0.7.2 on node B) is overridden through `PYTHONPATH` by FlashInfer 0.7.3 with its cubin and JIT cache; `sgl_flash_mla` 1.0.3; sgl-deep-gemm 0.2.2; `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.

## Setup

Deploy `git archive 704d3082e1` and start the server with [`l2/launch.sh`](l2/launch.sh): `--tp-size 4 --moe-runner-backend deep_gemm --mem-fraction-static 0.80 --context-length 32768 --max-running-requests 64 --cuda-graph-max-bs-decode 64 --disable-prefill-cuda-graph --enable-hierarchical-cache --hicache-size 64 --hicache-storage-backend file`, `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model>`, with `SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1` and `SGLANG_HICACHE_FILE_BACKEND_STORAGE_DIR` on node-local disk. [`hc.sh`](hc.sh) runs the L2 sequence, GSM8K, then the restart for L3.

## Commit

- Code commit: `704d3082e1d68255ffb577f02262930b5f2f6d74`, pull request 59 rebased onto `glm-5-lp` at `a736925063`.
- Working tree: clean archive of the commit.
- The pull request was closed on 2026-11-14; the same fix and its regression test are on `glm-5-lp` as `8d9f8c2134`.
- Status: non-release. The image digest is not recorded and dependencies come from `PYTHONPATH` overlays, so the environment is not locked.

## Scripts

- Version: round-specific [`hc.sh`](hc.sh), [`lib.sh`](lib.sh), [`hicache.py`](hicache.py) and [`midfork.py`](midfork.py).
- Temporary changes: none.

## Workload

- GSM8K: full test split (1319 questions) through `sgl-eval` 0.1.3, `sgl-eval run gsm8k --base-url <server>/v1 --temperature 1.0 --top-p 0.95`, 64 client threads, server-default thinking, no `max_tokens`, one run per configuration.
- Prefix-reuse probe ([`midfork.py`](midfork.py)): a 6680-token record document; six greedy, thinking-off requests in order: first, identical, different question at the end, document forked in the middle (late record), the forked document again (early record), follow-up turn. `cached` lists the reported `cached_tokens` in that order.
- L2: probe, `hicache.py fill 70`, probe again; L3: restart on the same storage directory, probe.

## Results

| Configuration | Accuracy | Stop rate | Truncated | Errors | Accept len |
|---|---|---|---|---|---|
| `--hicache-size 64`, window layout | 95.22% (1256/1319) | 99.62% | 5 | 0% | 2.72 |

| Step | Prefix-reuse probe | `HiCache prefetch success` lines |
|---|---|---|
| Before the fill | 6/6 correct, 6/6 `stop`; cached 0 / 6656 / 6656 / 0 / 6656 / 6656 | |
| After the fill (host restore) | 6/6 correct, 6/6 `stop`; cached 6656 / 6656 / 6656 / 6656 / 6656 / 6656 | 0 before and 0 after the probe |
| After a restart (storage restore) | 6/6 correct, 6/6 `stop`; cached 6656 / 6656 / 6656 / 6656 / 6656 / 6656 | 8 |

Accept length is the mean of the `accept len` field over the `Decode batch` lines of the server log. Truncated counts requests that ended with `finish_reason=length`. KV pool: full_layer_tokens=422016, swa_layer_tokens=42176.

Conclusions:

1. The fix holds after the rebase: GSM8K passes the stop-rate gate, and host and storage restores return 6656 cached tokens with all probe answers correct.
2. HiCache on a PD prefill server is recorded in [PD Disaggregation E03](../../../p0-pd-disagg/data/data@2026-11-15-bdbebf62fca4af4e628e26f9e55d139bb7794047-rdma-window-full-hicache/repro.md).

## Data and Figures

- [`l2/`](l2/) — launch script, server log, probes, prefetch counters, `gsm8k.log`, sgl-eval output and status.
- [`l3-restart/`](l3-restart/) — restart on the same storage directory and its probe.
- [`summary.json`](summary.json) — every number in the Results section, recomputed from the committed files by [`summarize_round.py`](../../../p0-correctness/scripts/v2/summarize_round.py).
- [`evidence-hashes.json`](evidence-hashes.json) — original path and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
