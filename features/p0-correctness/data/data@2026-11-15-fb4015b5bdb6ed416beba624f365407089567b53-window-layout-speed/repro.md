# E14 Window layout against full-length layout: serving speed — data@2026-11-15-fb4015b5bdb6ed416beba624f365407089567b53-window-layout-speed

## Environment

- Machine: one node with 8× NVIDIA B300. The node is shared; see "Discarded data" for one arm that overlapped another job.
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`, served from a node-local copy; the checkpoint's own NextN head is the MTP draft. The copy was not re-hashed for this round.
- Software: image torch 2.14.1+cu130 and transformers 5.19.0; a first overlay adds sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5 and kernels 0.14.1; a second adds flashinfer-python / cubin / jit-cache 0.7.3. The code pins FlashInfer 0.7.4, which was not installed. `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.

## Setup

Deploy `git archive fb4015b5bd` (the tree used by [E13](../data@2026-11-15-fb4015b5bdb6ed416beba624f365407089567b53-window-default-tp8/repro.md)). Each arm is a fresh server; the only difference inside a configuration is `--disable-hybrid-swa-memory` on the full-length arm.

- DEP8, [`speed.sh`](speed.sh), arms `window1`, `full`, `window2` in that order: `--tp-size 8 --ep-size 8 --attn-dp-size 8 --moe-runner-backend flashinfer_trtllm --moe-a2a-backend none --dsa-prefill-backend trtllm --dsa-decode-backend trtllm --kv-cache-dtype fp8_e4m3 --context-length 147456 --mem-fraction-static 0.88 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --chunked-prefill-size 65536 --enable-fp32-lm-head`.
- TP8, [`speed-tp8.sh`](speed-tp8.sh), arms `tp8-window`, `tp8-full`, then `tp8-window-r2`: `--tp-size 8 --mem-fraction-static 0.75 --context-length 65536 --chunked-prefill-size 32768 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph`.
- Both: `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model>`, `--enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47`.

Each arm's exact command is its `launch.sh`.

## Commit

- Code commit: `fb4015b5bdb6ed416beba624f365407089567b53`, the head of radixark/sglang-zai pull request 67 on top of `glm-5-lp` at `59860082`.
- Working tree: clean archive of the commit.
- Status: non-release. The pull request is open and not merged. The image digest is not recorded.

## Scripts

- Version: round-specific [`speed.sh`](speed.sh), [`speed-tp8.sh`](speed-tp8.sh) and the multi-turn client [`mt.py`](mt.py). `sum.py`, `sum2.py` and `sum3.py` are the ad-hoc console summaries used during the run; [`summary.json`](summary.json) supersedes them.
- Temporary changes: `speed-tp8.sh` is captured as it was for the last launch, with the arm loop edited to `for ARM in tp8-window-r2`; the first launch ran the same file with `for ARM in tp8-window tp8-full`. `mt.py` is the version used by the TP8 arms, which takes the first `content` or `reasoning_content` delta as the first token. The DEP8 arms ran an earlier version that timed only `content` deltas; that version was overwritten and is not captured. `sum3.py` is captured with its arm list edited to `tp8-window-r2`.

## Workload

- `python -m sglang.bench_serving --backend sglang --dataset-name random-ids --random-range-ratio 1 --flush-cache --warmup-requests 2`, seeds 1 and 2, EOS ignored (benchmark default), on every arm:
  - `short-c1`: 2000 input / 500 output tokens, 16 requests, concurrency 1.
  - `short-c32`: 2000 / 500, 128 requests, concurrency 32.
  - `long-c4`: 30000 / 300, 16 requests, concurrency 4.
- Multi-turn chat ([`mt.py`](mt.py), TP8 arms): 8 conversations of 8 turns; each turn resends the history and appends a user message of 150 generated records (about 3.3K prompt tokens per turn), streaming, greedy, thinking off, `max_tokens` 200; one conversation at a time (`mt-t1-*`) and four at a time (`mt-t4-*`), two prompt sets (`s1`, `s2`) that are identical across arms. The cache is flushed before each run.

## Results

Means over the runs of a layout. On DEP8 the window layout has four runs per workload (two launches × two seeds) and the full-length layout two; on TP8 each layout has two.

| Configuration | Workload | Layout | Output tokens/s | Median TTFT (ms) | Mean TPOT (ms) | Accept len |
|---|---|---|---|---|---|---|
| DEP8 `trtllm` FP8 | `short-c1` | window | 134.6 | 387 | 6.63 | 3.24 |
| | | full-length | 128.5 | 382 | 7.01 | 2.97 |
| | `short-c32` | window | 1061 | 1274 | 25.5 | 2.87 |
| | | full-length | 1077 | 1296 | 25.1 | 2.85 |
| | `long-c4` | window | 129.6 | 2613 | 20.8 | 2.69 |
| | | full-length | 125.6 | 2503 | 22.3 | 2.32 |
| TP8 BF16 | `short-c1` | window | 224.6 | 326 | 3.81 | 2.95 |
| | | full-length | 236.1 | 311 | 3.62 | 3.09 |
| | `short-c32` | window | 1171 | 519 | 23.4 | 2.92 |
| | | full-length | 1175 | 501 | 23.1 | 2.90 |
| | `long-c4` | window | 127.7 | 3546 | 18.2 | 2.70 |
| | | full-length | 126.6 | 2805 | 19.2 | 2.59 |

Spread between the two DEP8 launches of the window layout (mean of two seeds each): `short-c1` 133.8 and 135.4 tokens/s, `short-c32` 1060 and 1062, `long-c4` 126.1 and 133.0.

Every run completed all its requests; no server logged a traceback.

Multi-turn on TP8 (median TTFT of turns 2 to 8, per prompt set):

| Layout | One conversation at a time | Four at a time | Cached / prompt tokens at turn 8 (median) |
|---|---|---|---|
| window (`tp8-window-r2`) | 334 ms, 336 ms | 352 ms, 353 ms | about 23.5K / 26.7K |
| full-length (`tp8-full`) | 328 ms, 326 ms | 350 ms, 354 ms | about 23.4K / 26.7K |

KV pool per rank at the same memory budget: DEP8 `full_layer_tokens=2656064, swa_layer_tokens=265600` against `max_total_num_tokens=2058688` (+29%); TP8 `full_layer_tokens=1195520, swa_layer_tokens=119552` against `max_total_num_tokens=920448` (+30%).

Conclusions:

1. No speed difference attributable to the layout is visible: every difference between layouts is within the spread between seeds and between two launches of the same layout.
2. Where mean TPOT differs, it follows the MTP accept length of the run. On TP8 `short-c1`, TPOT × accept length is 11.1 to 11.2 ms on all four runs.
3. Median TTFT of `long-c4` is bimodal because requests queue behind each other's prefill (one full-length TP8 seed has a median of 1910 ms, the other three TP8 runs 3482 to 3700 ms); p99 TTFT is 7.3 to 7.4 s on every TP8 run and 3.8 to 3.9 s on every DEP8 run.
4. In a conversation that resends its history, every turn after the first reuses the cached prefix on both layouts, with the same cached-token counts and TTFT within 10 ms.

### Discarded data

Kept for the record; not usable for comparing layouts.

- `window1/`, `full/`, `window2/` `mt-s*.jsonl` (DEP8 multi-turn): each arm used a different salt in its prompts, so the prompts differ between arms, and DP8 spreads the turns of a conversation over eight attention workers, so cache hits are a matter of routing. These rows also come from the earlier client, which recorded no TTFT for a response without `content` (11 to 14 of 48 requests on the window arms, 2 to 4 on the full-length arm, on different prompts); the cause of the empty `content` was not examined.
- `tp8-window/` (first TP8 window arm): while it launched, another job on the shared node held about 111 GB on GPU 0 (free memory at weight load 154.5 GB instead of 265.6 GB), and the server sized its pool to `full_layer_tokens=247168`. It was rerun on idle GPUs as `tp8-window-r2`. `window2` overlapped the same job in wall-clock time but launched with full free memory and the full pool, and agrees with `window1`.

## Data and Figures

- `window1/`, `full/`, `window2/`, `tp8-window-r2/`, `tp8-full/`, `tp8-window/` — per arm: `launch.sh`, compressed server log, `bench_serving` result (`*.jsonl`) and console (`*.log`) per workload and seed, multi-turn rows.
- `status`, `status-tp8-run1`, `status-tp8` — driver status of the DEP8 run, the first TP8 run and the TP8 rerun; the `*.out` driver consoles are empty.
- [`summary.json`](summary.json) — per-file numbers behind the Results section, recomputed from the committed files by [`summarize_round.py`](../../scripts/v2/summarize_round.py).
- [`evidence-hashes.json`](evidence-hashes.json) — original path and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
