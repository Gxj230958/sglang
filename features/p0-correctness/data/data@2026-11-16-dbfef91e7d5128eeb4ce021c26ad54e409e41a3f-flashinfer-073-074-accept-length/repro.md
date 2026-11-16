# E16 FlashInfer 0.7.3 against 0.7.4: MTP accept length at TP8 — data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-flashinfer-073-074-accept-length

## Environment

- Machine: one node with 8× NVIDIA B300, the B300 node of [E15](../data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-flashinfer-074-h200/repro.md).
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, served from the node-local copy hashed in E15 (`b300/checkpoint.sha256` there); the checkpoint's own NextN head is the MTP draft.
- Software: two `PYTHONPATH` overlays in front of the same source tree and image. Arm `fi073`: flashinfer-python 0.7.3, flashinfer-cubin 0.7.3, flashinfer-jit-cache 0.7.3+cu130. Arm `fi074`: the E15 overlay with flashinfer-python 0.7.4, flashinfer-cubin 0.7.4, flashinfer-jit-cache 0.7.4+cu130. Both arms: sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1, sgl-eval 0.1.3. [`fi073/imports.txt`](fi073/imports.txt) and [`fi074/imports.txt`](fi074/imports.txt) record the FlashInfer module path and the package versions each arm resolves; in `fi073` no JIT-cache architecture provider module loads, in `fi074` the `sm103a` provider loads. `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.

## Setup

[`ab.sh`](ab.sh) runs the two arms one after the other on the same node. Per arm it checks that every GPU is idle, writes `imports.txt` and `launch.sh`, starts the server, waits for `/health`, runs GSM8K twice against the same server process (`t1`, then `t0`), and stops the server. Before and after each GSM8K run it stores the `sglang:generation_tokens_total` and `sglang:spec_verify_calls_total` lines of `/metrics`.

- Launch flags, identical in both arms ([`fi073/launch.sh`](fi073/launch.sh), [`fi074/launch.sh`](fi074/launch.sh)): `--tp-size 8 --mem-fraction-static 0.75 --context-length 65536 --chunked-prefill-size 32768 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model> --enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47 --enable-metrics`. These are the `b300-tp8` flags of E15: default `flashmla_sparse` DSA routes, BF16 KV, default window layout.
- The arms differ only in the overlay entries of `PYTHONPATH`.
- Timeline (UTC, [`status`](status) and the server logs): `fi073` server 01:01:34–01:38:35, `fi074` server 01:39:28–02:19:02.

## Commit

- Code commit: `dbfef91e7d5128eeb4ce021c26ad54e409e41a3f`, the tip of `glm-5-lp`.
- Working tree: the `git archive` tree deployed and verified file by file in E15 (`b300/source-verify.json` there). It was not re-verified before this round.
- Status: non-release. One unseeded run per arm and sampling setting; image digest not recorded.

## Scripts

- Version: round-specific [`ab.sh`](ab.sh). Numbers are recomputed by [`summarize_round.py`](../../scripts/v2/summarize_round.py); the counter ratios are computed from the `*.metrics` files as described under Results.
- Temporary changes: none to the served code.

## Workload

- GSM8K: full test split (1319 questions) through `sgl-eval run gsm8k --base-url <server>/v1`, 64 client threads, server-default thinking, no `max_tokens`, no seed.
- `t1`: `--temperature 1.0 --top-p 0.95`, the gate setting of the earlier rounds.
- `t0`: `--temperature 0`.

## Results

| Sampling | Arm | Accuracy | Stop rate | Truncated | Accept len (counters) | Accept len (log lines) | Completion tokens |
|---|---|---|---|---|---|---|---|
| temperature 1.0, top_p 0.95 | `fi073` | 95.60% (1261/1319) | 100% (1319/1319) | 0 | 2.6480 | 2.5916 (445 lines) | 718,322 |
| temperature 1.0, top_p 0.95 | `fi074` | 95.07% (1254/1319) | 99.92% (1318/1319) | 1 | 2.6423 | 2.6302 (724 lines) | 881,311 |
| temperature 0 | `fi073` | 96.51% (1273/1319) | 99.32% (1310/1319) | 9 | 2.8231 | 2.8297 (734 lines) | 1,294,159 |
| temperature 0 | `fi074` | 96.82% (1277/1319) | 99.55% (1313/1319) | 6 | 2.8463 | 2.8707 (725 lines) | 1,171,655 |

- Accept len (counters) is the ratio of the `sglang:generation_tokens_total` delta to the `sglang:spec_verify_calls_total` delta between `before-<run>.metrics` and `after-<run>.metrics`: 718322 / 271269, 881311 / 333544, 1294159 / 458410 and 1171655 / 411636. Each generation-token delta equals `total_completion_tokens` in the run's `metrics.json`.
- Accept len (log lines) is the unweighted mean of the `accept len` field over the `Decode batch` lines logged while the run was in flight (`accept_len_during_run` in [`summary.json`](summary.json)), the definition used by the rounds before E15.
- Truncated counts requests that ended with `finish_reason=length`. Every truncated request generated between 65,391 and 65,462 tokens, that is, it ran until the 65,536-token context was full.
- Truncated questions at temperature 0: `fi073` 12, 87, 119, 255, 380, 675, 690, 1089, 1119; `fi074` 93, 119, 255, 675, 690, 1119. Five are common to both arms (119, 255, 675, 690, 1119). At temperature 1.0: `fi074` 1074.
- Both arms: KV pool `full_layer_tokens=1195520, swa_layer_tokens=119552`, every `Decode batch` line with `cuda graph: True`, no traceback, no KV retraction, server healthy after the second run.

Conclusions:

1. In these runs the counter-based MTP accept length of the two FlashInfer versions is within 0.9%: 0.7.4 is 0.2% lower at temperature 1.0 (2.6480 against 2.6423) and 0.8% higher at temperature 0 (2.8231 against 2.8463). By log lines 0.7.4 is 1.5% higher in both settings. One unseeded run per arm and setting does not establish equivalence.
2. The same-day 0.7.3 arm does not reproduce the log-line gap between [E13](../data@2026-11-15-fb4015b5bdb6ed416beba624f365407089567b53-window-default-tp8/repro.md) (2.76, FlashInfer 0.7.3) and E15 (2.54, FlashInfer 0.7.4) at TP8: it gives 2.59 and the 0.7.4 arm 2.63. The cause of that gap is unresolved. The log-line value is an unweighted mean over a few hundred periodic lines; the counter ratio weights every verify call equally.
3. Greedy decoding drives a small set of questions into reasoning that fills the context on both FlashInfer versions (9 and 6 of 1319, 5 shared). At temperature 1.0 one request of the 0.7.4 arm did the same and none of the 0.7.3 arm; with one unseeded run per arm this is not attributed to FlashInfer.
4. Accuracy is within 0.6 points between the arms in both settings.

Not covered: DEP8, FP8 KV and the `trtllm` DSA routes; H200; more seeds; alternating the order of the arms; re-verifying the source tree for this round; the same JIT-cache provider state on both arms (see Environment).

## Data and Figures

- [`ab.sh`](ab.sh), [`status`](status) — the driver and its progress log (times in UTC).
- [`fi073/`](fi073/), [`fi074/`](fi074/) — per arm: `launch.sh`, `imports.txt`, compressed `serve.log`, compressed `gsm8k-t1.log` / `gsm8k-t0.log`, the four `*.metrics` counter snapshots, and the sgl-eval output of both runs under `eval-t1/` and `eval-t0/` (`metrics.json`, compressed `output-rs0.jsonl`).
- [`summary.json`](summary.json) — sgl-eval aggregates, finish reasons, log-line accept length per run, pool sizes and traceback counts recomputed from the committed files.
- [`evidence-hashes.json`](evidence-hashes.json) — original location and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
