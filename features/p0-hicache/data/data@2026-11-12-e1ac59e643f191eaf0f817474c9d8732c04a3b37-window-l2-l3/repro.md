# E02 Host L2 and file L3 on the window layout — data@2026-11-12-e1ac59e643f191eaf0f817474c9d8732c04a3b37-window-l2-l3

## Environment

- Machine: two nodes with 4× NVIDIA GB300 each (node A and node B), no shared disk. Each server uses the four GPUs of one node. This round used node A.
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`, served from a node-local copy; the checkpoint's own NextN head is the MTP draft. The copy was not re-hashed for this round.
- Software: the image's FlashInfer (0.7.1 on node A, 0.7.2 on node B) is overridden through `PYTHONPATH` by FlashInfer 0.7.3 with its cubin and JIT cache; `sgl_flash_mla` 1.0.3; sgl-deep-gemm 0.2.2; `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.

## Setup

Deploy `710bcb2a3e` with `python/sglang/srt/mem_cache/hybrid_cache/hybrid_pool_assembler.py` from `e1ac59e643` and start the server with a run's `launch.sh`: `--tp-size 4 --moe-runner-backend deep_gemm --mem-fraction-static 0.80 --context-length 32768 --max-running-requests 64 --cuda-graph-max-bs-decode 64 --disable-prefill-cuda-graph`, `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model>`, `--enable-hierarchical-cache --hicache-size <32|64> --hicache-storage-backend file`, with `SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1` and `SGLANG_HICACHE_FILE_BACKEND_STORAGE_DIR` on node-local disk. [`hc-seq.sh`](hc-seq.sh) runs the sequence. Without the fix the base commit fails at launch with `AttributeError: 'str' object has no attribute 'value'`.

## Commit

- Code commit: `e1ac59e643f191eaf0f817474c9d8732c04a3b37`, the first head of radixark/sglang-zai pull request 59.
- Working tree: `710bcb2a3e` plus the one changed source file of that commit.
- Status: non-release. The image digest is not recorded and dependencies come from `PYTHONPATH` overlays, so the environment is not locked.

## Scripts

- Version: round-specific [`serve.sh`](serve.sh), [`eval.sh`](eval.sh), [`wait.sh`](wait.sh), [`hc-seq.sh`](hc-seq.sh), [`hicache.py`](hicache.py) and [`midfork.py`](midfork.py).
- Temporary changes: none.

## Workload

- GSM8K: full test split (1319 questions) through `sgl-eval` 0.1.3, `sgl-eval run gsm8k --base-url <server>/v1 --temperature 1.0 --top-p 0.95`, 64 client threads, server-default thinking, no `max_tokens`, one run per configuration.
- Prefix-reuse probe ([`midfork.py`](midfork.py)): a 6680-token record document; six greedy, thinking-off requests in order: first, identical, different question at the end, document forked in the middle (late record), the forked document again (early record), follow-up turn. `cached` lists the reported `cached_tokens` in that order.
- L2: prefix-reuse probe, then [`hicache.py`](hicache.py) `fill 70` (70 new 6.7K-token prompts, 8 concurrent, about 468K tokens through a 422K-token device pool), then the probe again. `prefetch-before-b.txt` and `prefetch-after-b.txt` hold the count of `HiCache prefetch success` lines around the second probe.
- L3: restart the server on the same storage directory and run the probe once more.

## Results

| Configuration | Accuracy | Stop rate | Truncated | Errors | Accept len |
|---|---|---|---|---|---|
| `--hicache-size 64`, window layout | 94.84% (1251/1319) | 99.77% | 3 | 0% | 2.54 |

| Step | Prefix-reuse probe | `HiCache prefetch success` lines |
|---|---|---|
| Size 64, before the fill | 6/6 correct, 6/6 `stop`; cached 0 / 6656 / 6656 / 0 / 6656 / 6656 | |
| Size 64, after the fill (host restore) | 6/6 correct, 6/6 `stop`; cached 6656 / 6656 / 6656 / 6656 / 6656 / 6656 | 280 before and 280 after the probe |
| Size 64, after a restart (storage restore) | 6/6 correct, 6/6 `stop`; cached 6656 / 6656 / 6656 / 6656 / 6656 / 6656 | 8 |

Accept length is the mean of the `accept len` field over the `Decode batch` lines of the server log. Truncated counts requests that ended with `finish_reason=length`. KV pool: full_layer_tokens=422016, swa_layer_tokens=42176.

Conclusions:

1. With the one-line fix the window layout launches with a host stack and file storage, and passes the GSM8K stop-rate gate with HiCache enabled.
2. A prefix evicted from the device pool is restored from host memory without a storage prefetch, and after a restart from file storage; every probe request over the restored prefix is correct and ends with `stop`.
3. With `--hicache-size 32` the host pool is smaller than the device pool; [`size32/`](size32/) keeps that run's launch script, server log and anchor request. It was not investigated further.
4. Bitwise comparison of restored and device-resident runs is not available in this configuration and was not attempted.

## Data and Figures

- [`size64-l2/`](size64-l2/) — launch script, server log, probes before and after the fill, prefetch counters, `gsm8k.log` and sgl-eval output.
- [`size64-l3-restart/`](size64-l3-restart/) — restart on the same storage directory and its probe.
- [`size32/`](size32/) — the `--hicache-size 32` run.
- [`summary.json`](summary.json) — every number in the Results section, recomputed from the committed files by [`summarize_round.py`](../../../p0-correctness/scripts/v2/summarize_round.py).
- [`evidence-hashes.json`](evidence-hashes.json) — original path and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
