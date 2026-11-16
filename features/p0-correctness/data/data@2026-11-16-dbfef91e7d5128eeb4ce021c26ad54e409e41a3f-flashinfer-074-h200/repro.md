# E15 FlashInfer 0.7.4 and H200 gates on the merged window-default head — data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-flashinfer-074-h200

## Environment

- Machines: one node with 8× NVIDIA B300 ([`b300/`](b300/)) and one node with 8× NVIDIA H200, 143771 MiB each ([`h200/`](h200/)).
- Container: each node's stock SGLang development image; the image digests were not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, served from a node-local copy on each node; the checkpoint's own NextN head is the MTP draft. `checkpoint.sha256` on both nodes records the same `config.json` (`99d7088d…`) and `model.safetensors.index.json` (`55979a94…`) digests; the weight shards were not re-hashed.
- Software: a round-owned overlay installed with `pip install --no-deps --target` ([`b300/setup.sh`](b300/setup.sh), [`b300/provider.sh`](b300/provider.sh)): flashinfer-python 0.7.4, flashinfer-cubin 0.7.4, flashinfer-jit-cache 0.7.4+cu130 with the matching architecture provider (`sm103a` on B300, `sm90a` on H200), sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1; image transformers 5.19.0 and torch 2.14.1; sgl-eval 0.1.3 on B300 and 0.1.2 on H200. H200 additionally needs `sgl-fa3==0.1.0` ([`h200/h200-fa3.sh`](h200/h200-fa3.sh)). The `SERVER_IMPORTS` line at the top of each server log records the versions and module paths the server process imported. `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.

## Setup

Deploy `git archive dbfef91e7d` (`source.sha256`, `source-verify.json`: 12,571 files, no mismatch on either node), build the overlay, then run `gate.py <leg>` (`start.sh`, [`b300/dep8.sh`](b300/dep8.sh), [`h200/h200-fa3.sh`](h200/h200-fa3.sh)). `gate.py` launches [`server.py`](b300/server.py), which prints `SERVER_IMPORTS` and then runs the unchanged `sglang.launch_server` module; the full argument list of each leg is in its `launch.json`.

- Common: `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model> --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47 --enable-metrics`. No layout flag: the window layout is the default at this commit.
- `b300-tp8` and `h200-tp8-fa3`: `--tp-size 8 --mem-fraction-static 0.75 --context-length 65536 --chunked-prefill-size 32768`, default `flashmla_sparse` DSA routes, BF16 KV. H200 uses the same flags as B300.
- `b300-dep8`: `--tp-size 8 --ep-size 8 --attn-dp-size 8 --moe-runner-backend flashinfer_trtllm --moe-a2a-backend none --dsa-prefill-backend trtllm --dsa-decode-backend trtllm --kv-cache-dtype fp8_e4m3 --context-length 147456 --mem-fraction-static 0.88 --chunked-prefill-size 65536 --enable-fp32-lm-head`.

`gpu-before.csv` of every leg shows idle GPUs before launch.

## Commit

- Code commit: `dbfef91e7d5128eeb4ce021c26ad54e409e41a3f`, the tip of `glm-5-lp` after radixark/sglang-zai pull request 67 merged (window sub-pool as the default layout, `SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA` removed).
- Working tree: clean archive of the commit.
- Status: non-release. One unseeded run per leg; image digests not recorded.

## Scripts

- Version: round-specific `gate.py`, `server.py`, `suite.py`, `setup.sh`, `provider.sh`, `start.sh` per node, plus the copies kept on the coordinating host in [`driver/`](driver/). Numbers are recomputed by [`summarize_round.py`](../../scripts/v2/summarize_round.py).
- Temporary changes: none to the served code.

## Workload

- GSM8K: full test split (1319 questions) through `sgl-eval run gsm8k --base-url <server>/v1 --temperature 1.0 --top-p 0.95`, 64 client threads, server-default thinking, no `max_tokens`, one run per leg.
- Smoke suite (`suite.py` `smoke`): text, thinking, 3.4K / 10.0K / 19.9K-token needle and image requests.

## Results

| Leg | Accuracy | Stop rate | Truncated | Errors | Accept len (counters) | Accept len (log lines) | Smoke | KV pool | Tracebacks |
|---|---|---|---|---|---|---|---|---|---|
| `b300-tp8`: 8× B300, TP8, BF16 KV | 96.06% (1267/1319) | 100% (1319/1319) | 0 | 0 | 2.6577 | 2.54 | 6/6 `stop` | full_layer_tokens=1195520, swa_layer_tokens=119552 | 0 |
| `b300-dep8`: 8× B300, DEP8 `trtllm`, FP8 KV | 95.07% (1254/1319) | 100% (1319/1319) | 0 | 0 | 2.6053 | 2.57 | 6/6 `stop` | full_layer_tokens=2656064, swa_layer_tokens=265600 | 0 |
| `h200-tp8-fa3`: 8× H200, TP8, BF16 KV | 94.77% (1250/1319) | 99.85% (1317/1319) | 2 | 0 | 2.6158 | 2.50 | 6/6 `stop` | full_layer_tokens=139136, swa_layer_tokens=13888 | 0 |

- Accept len (counters) is the eval-only ratio of the `sglang:generation_tokens_total` delta to the `sglang:spec_verify_calls_total` delta between `before-eval-metrics.txt` and `after-eval-metrics.txt`: 675404 / 254135, 786948 / 302053 and 830568 / 317522. The generation-token deltas equal `total_completion_tokens` in each `metrics.json`.
- Accept len (log lines) is the unweighted mean of the `accept len` field over the `Decode batch` lines logged during the eval, the definition used by the earlier rounds ([E13](../data@2026-11-15-fb4015b5bdb6ed416beba624f365407089567b53-window-default-tp8/repro.md): 2.76 at TP8; [E10](../data@2026-11-15-5e6ee4ed50fc91fee9c5a0484667ce6de2ba5640-window-default-dep8/repro.md): 2.54 at DEP8, both with FlashInfer 0.7.3). The two definitions are not interchangeable.
- Truncated counts requests that ended with `finish_reason=length`.

H200 capacity: the same TP8 flags that give 1,195,520 full-length tokens on B300 give 139,136 on H200 (about 89 GB of weights per rank out of 143.8 GB, 31.94 GB reported available after the pool and the CUDA graphs). During the eval the first rank logged three `KV cache pool is full. Retract requests` events (each retracting one request; every rank logs the same event, 24 lines in total). The retracted requests resumed and the eval completed. B300 logged no retraction.

Failed first H200 attempt ([`h200/h200-tp8/`](h200/h200-tp8/), kept as captured, no eval): the server exited during the multimodal warmup with `ModuleNotFoundError: No module named 'sgl_fa3'` on all eight ranks (8 tracebacks) because the image lacks the package the tree pins. Installing `sgl-fa3==0.1.0` into the overlay was the only change before `h200-tp8-fa3`.

Conclusions:

1. With FlashInfer 0.7.4 (python, cubin and JIT cache), the version the code pins, the merged head launches and passes the full GSM8K gate at TP8 and DEP8 on B300 with MTP and the default window layout.
2. On 8× H200 the same head passes with the default `flashmla_sparse` routes and BF16 KV: 94.77% accuracy, 99.85% stop rate, 2 truncated. The `trtllm` routes are the Blackwell configuration and were not run on H200.
3. H200 fits the checkpoint at TP8 but with about 12% of the B300 KV capacity under the same flags; GSM8K at 64 client threads already triggers request retraction.
4. These are single unseeded runs. The differences against the FlashInfer 0.7.3 rounds (TP8 94.92% / 99.77% stop in E13, DEP8 95.45% / 100% in E10, log-line accept length 2.76 against 2.54 at TP8) are not attributed to FlashInfer. The same-day control [E16](../data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-flashinfer-073-074-accept-length/repro.md) runs 0.7.3 and 0.7.4 back to back at TP8: the counter-based accept lengths are within 0.9% of each other and the 0.7.3 arm does not reproduce the 2.76 log-line value; the cause of the gap is unresolved.

Not covered: FP8 KV, EP / DP layouts, PD, HiCache and serving speed on H200; more seeds.

## Data and Figures

- [`b300/`](b300/), [`h200/`](h200/) — per node: overlay setup scripts and logs, `checkpoint.sha256`, `source.sha256`, `source-verify.json`, the nodes' own `evidence-sha256.json`, and one directory per leg with `launch.json`, compressed server log, `status`, `gpu-before.csv` / `gpu-after.csv`, smoke results, metric and server-info snapshots before and after the eval, `gsm8k.log` and sgl-eval output.
- [`driver/`](driver/) — driver scripts and `results.json` as kept on the coordinating host. In `results.json` the node names are replaced by the labels `8x-b300-node` and `8x-h200-node`.
- [`summary.json`](summary.json) — sgl-eval aggregates, finish reasons, log-line accept length, pool sizes and traceback counts recomputed from the committed files.
- [`evidence-hashes.json`](evidence-hashes.json) — original location and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
