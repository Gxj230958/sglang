# E13 Window layout as the default: TP8 gate on the pull-request head — data@2026-11-15-fb4015b5bdb6ed416beba624f365407089567b53-window-default-tp8

## Environment

- Machine: one node with 8× NVIDIA B300.
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`, served from a node-local copy; the checkpoint's own NextN head is the MTP draft. The copy was not re-hashed for this round.
- Software: image torch 2.14.1+cu130 and transformers 5.19.0; a first overlay adds sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5 and kernels 0.14.1; a second adds flashinfer-python / cubin / jit-cache 0.7.3. The code pins FlashInfer 0.7.4, which was not installed. `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.

## Setup

Deploy `git archive fb4015b5bd` and run [`gate.sh`](gate.sh): `--tp-size 8 --mem-fraction-static 0.75 --context-length 65536 --chunked-prefill-size 32768 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph`, `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model>`, `--enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47`. No layout flag is passed; the server selects the window layout by default.

## Commit

- Code commit: `fb4015b5bdb6ed416beba624f365407089567b53`, the head of radixark/sglang-zai pull request 67 on top of `glm-5-lp` at `59860082`. It makes the window sub-pool the default layout and removes the `SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA` variable; `--disable-hybrid-swa-memory` selects the full-length layout.
- Working tree: clean archive of the commit.
- Status: non-release. The pull request is open and not merged. The image digest is not recorded.

## Scripts

- Version: round-specific [`gate.sh`](gate.sh) and [`suite.py`](suite.py).
- Temporary changes: none.

## Workload

- GSM8K: full test split (1319 questions) through `sgl-eval` 0.1.3, `sgl-eval run gsm8k --base-url <server>/v1 --temperature 1.0 --top-p 0.95`, 64 client threads, server-default thinking, no `max_tokens`, one run.
- Smoke suite ([`suite.py`](suite.py) `smoke`): text, thinking, 4K / 12K / 24K long-context needle and image requests.

## Results

| Configuration | Accuracy | Stop rate | Truncated | Errors | Accept len | Smoke | KV pool |
|---|---|---|---|---|---|---|---|
| TP8, default layout | 94.92% (1252/1319) | 99.77% | 3 | 0% | 2.76 | 6/6 `stop` | full_layer_tokens=1195520, swa_layer_tokens=119552 |

Accept length is the mean of the `accept len` field over the `Decode batch` lines of the server log. Truncated counts requests that ended with `finish_reason=length`. No traceback was logged.

Conclusions:

1. On the pull-request head, without any layout flag, the server builds the window pool and passes the full GSM8K gate at TP8.
2. Three truncated requests of 1319 match the rate seen on `glm-5-lp` before the change ([E07](../data@2026-11-13-802d8157b74564997e350ffa981b5e567e391920-topk-by-reference-gate/repro.md): 3 of 2638 on each arm).
3. The DEP8 gate of the same change ran on its first revision `5e6ee4ed` ([E10](../data@2026-11-15-5e6ee4ed50fc91fee9c5a0484667ce6de2ba5640-window-default-dep8/repro.md)); DEP8 was not rerun on this head.

## Data and Figures

- [`tp8/`](tp8/) — launch script, compressed server log, smoke results, `gsm8k.log` and sgl-eval output.
- `status`, `gate-final.out` — driver status and console.
- [`summary.json`](summary.json) — every number in the Results section, recomputed from the committed files by [`summarize_round.py`](../../scripts/v2/summarize_round.py).
- [`evidence-hashes.json`](evidence-hashes.json) — original path and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
