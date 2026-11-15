# E06 Window layout validation matrix after the window-slot KV fix — data@2026-11-12-710bcb2a3e6e4abbc299b43860c6528f7bd81db8-window-layout-matrix

## Environment

- Machine: two nodes with 4× NVIDIA GB300 each (node A and node B), no shared disk. Each server uses the four GPUs of one node.
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`, served from a node-local copy; the checkpoint's own NextN head is the MTP draft. The copy was not re-hashed for this round.
- Software: the image's FlashInfer (0.7.1 on node A, 0.7.2 on node B) is overridden through `PYTHONPATH` by FlashInfer 0.7.3 with its cubin and JIT cache; `sgl_flash_mla` 1.0.3; sgl-deep-gemm 0.2.2; `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.

## Setup

Deploy `710bcb2a3e` and start each server with the `launch.sh` of its run directory. Common flags: `--tp-size 4 --moe-runner-backend deep_gemm --mem-fraction-static 0.80 --context-length 32768 --max-running-requests 64 --cuda-graph-max-bs-decode 64 --disable-prefill-cuda-graph`, `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model>`, `--reasoning-parser glm45 --tool-call-parser glm47 --enable-cache-report`. Window-layout servers set `SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1`; full-length servers leave it unset.

| Run directory | Layout | Additional flags |
|---|---|---|
| `gate` | window | `--chunked-prefill-size 8192` |
| `trtllm-bf16` | window | `--dsa-prefill-backend trtllm --dsa-decode-backend trtllm` |
| `trtllm-fp8`, `trtllm-fp8-window-stress` | window | the same plus `--kv-cache-dtype fp8_e4m3` |
| `trtllm-fp8-full-length-stress` | full-length | the same as the FP8 window runs |
| `prefix-window`, `prefix-full-length` | window, full-length | none |

## Commit

- Code commit: `710bcb2a3e6e4abbc299b43860c6528f7bd81db8`, `glm-5-lp` after radixark/sglang-zai pull request 42.
- Working tree: `gate` ran the exact commit. The `trtllm-*` runs used a tree that also carried the prefill-CP patch of `0c95a2b1d2`, and the `prefix-*` runs one that also carried the PD patch of `3f3a3985ac`; neither code path is reached by these launches.
- Status: non-release. The image digest is not recorded and dependencies come from `PYTHONPATH` overlays, so the environment is not locked.

## Scripts

- Version: round-specific [`serve.sh`](serve.sh), [`eval.sh`](eval.sh), [`wait.sh`](wait.sh), [`ctl.sh`](ctl.sh), [`fp8ctl.sh`](fp8ctl.sh), [`probe.py`](probe.py), [`midfork.py`](midfork.py) and [`stress.py`](stress.py).
- Temporary changes: `gate-void-flashinfer-0.7.1/` is a first gate attempt on the image's FlashInfer 0.7.1; the server died mid-evaluation when the JIT `speculative_sampling` module failed to build, and it produced no result.

## Workload

- GSM8K: full test split (1319 questions) through `sgl-eval` 0.1.3, `sgl-eval run gsm8k --base-url <server>/v1 --temperature 1.0 --top-p 0.95`, 64 client threads, server-default thinking, no `max_tokens`, one run per configuration.
- Retrieval probes ([`probe.py`](probe.py)): a document of `Record i: the code is c.` lines sized to a target length, three questions per length (records at 1/7, 1/2 and near the end), greedy, thinking off, `max_tokens=96`. A request is correct when the expected code appears in the answer. Target lengths 300, 3000, 9000 and 24000.
- Prefix-reuse probe ([`midfork.py`](midfork.py)): a 6680-token record document; six greedy, thinking-off requests in order: first, identical, different question at the end, document forked in the middle (late record), the forked document again (early record), follow-up turn. `cached` lists the reported `cached_tokens` in that order.
- Salted stress ([`stress.py`](stress.py)): uncached record documents with a per-request salt, one random record per request, greedy, thinking off, `max_tokens=64`. A request counts when it ends with `stop` and contains the expected code. The file names give the concurrency (`c1` serial, otherwise 8).

## Results

| Configuration | Accuracy | Stop rate | Truncated | Errors | Accept len | Probes | Prefix reuse | KV pool |
|---|---|---|---|---|---|---|---|---|
| MTP + decode CUDA graphs (`gate`) | 95.68% (1262/1319) | 99.47% | 7 | 0% | 2.60 | not run | not run | full_layer_tokens=422016, swa_layer_tokens=42176 |
| `trtllm`, BF16 KV | 94.01% (1240/1319) | 99.62% | 5 | 0% | 2.63 | 12/12 correct, 12/12 `stop` | 6/6 correct, 6/6 `stop`; cached 0 / 6656 / 6656 / 0 / 6656 / 6656 | full_layer_tokens=422016, swa_layer_tokens=42176 |
| `trtllm`, FP8 KV | 95.07% (1254/1319) | 99.70% | 4 | 0% | 2.63 | 10/12 correct, 10/12 `stop` | 6/6 correct, 6/6 `stop`; cached 0 / 6656 / 6656 / 0 / 6656 / 6656 | full_layer_tokens=819520, swa_layer_tokens=81920 |

Accept length is the mean of the `accept len` field over the `Decode batch` lines of the server log. Truncated counts requests that ended with `finish_reason=length`.

Prefix reuse on a single TP4 server:

| Layout | Prefix-reuse probe |
|---|---|
| Window | 6/6 correct, 6/6 `stop`; cached 0 / 6656 / 6656 / 0 / 6656 / 6656 |
| Full-length | 6/6 correct, 6/6 `stop`; cached 0 / 6656 / 6656 / 3200 / 6656 / 6656 |

Salted stress, stop-and-correct / wrong code with `stop` / not `stop`:

| Server | Probes | Serial, 3000 | Serial, 9000 | 8 concurrent, 3000 | 8 concurrent, 9000 | 8 concurrent, 20000 |
|---|---|---|---|---|---|---|
| `trtllm` FP8, window (second start) | 12/12 correct, 12/12 `stop` | 30 / 0 / 0 | 28 / 0 / 2 | 99 / 1 / 0 | 99 / 0 / 1 | 95 / 0 / 5 |
| `trtllm` FP8, full-length | 12/12 correct, 12/12 `stop` | 30 / 0 / 0 | 30 / 0 / 0 | 98 / 1 / 1 | 100 / 0 / 0 | 92 / 0 / 8 |

| Server, BF16 KV, prompts of 9000 tokens and more | Requests | Stop and correct |
|---|---|---|
| Window, 8 concurrent (`stress2`, `stress4`) | 800 | 796 |
| Window, serial (`stress3-c1`) | 120 | 120 |
| Full-length, 8 concurrent (`stress2`, `stress3-c8`, `stress4`) | 1100 | 1096 |

Conclusions:

1. After the window-slot KV fix the window layout passes the full GSM8K stop-rate gate with MTP and decode CUDA graphs: 99.47% stop, equal to the full-length reference at `f8f3fd9253`. All seven truncated requests ran to the 32768-token context.
2. The `trtllm` DSA backend serves the window layout with BF16 and with FP8 KV and passes the same gate.
3. A fork in the middle of a cached document reuses nothing on the window layout and 3200 tokens on the full-length layout; every other case reuses 6656 tokens on both, and all answers are correct.
4. Greedy thinking-off long prompts occasionally open with reasoning instead of the answer and hit `max_tokens`, or return a wrong code with `stop`. On BF16 KV this affects 4 of 800 window requests and 4 of 1100 full-length requests under concurrency and none of 120 serial window requests. With FP8 KV the rate is higher on both layouts (window 7 of 300, full-length 10 of 300 at 8 concurrent).
5. The stock image's FlashInfer 0.7.1 cannot build the MTP sampling module at this commit; 0.7.3 is required.

## Data and Figures

- [`gate/`](gate/), [`trtllm-bf16/`](trtllm-bf16/), [`trtllm-fp8/`](trtllm-fp8/) — launch script, compressed server log, status, probes, `gsm8k.log` and sgl-eval output of each GSM8K run.
- [`trtllm-fp8-window-stress/`](trtllm-fp8-window-stress/), [`trtllm-fp8-full-length-stress/`](trtllm-fp8-full-length-stress/) — probes and stress rows on both FP8 layouts.
- [`prefix-window/`](prefix-window/), [`prefix-full-length/`](prefix-full-length/) — prefix-reuse probes and BF16 stress rows on single servers.
- [`gate-void-flashinfer-0.7.1/`](gate-void-flashinfer-0.7.1/) — the void first attempt.
- [`summary.json`](summary.json) — every number in the Results section, recomputed from the committed files by [`summarize_round.py`](../../scripts/v2/summarize_round.py).
- [`evidence-hashes.json`](evidence-hashes.json) — original path and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
