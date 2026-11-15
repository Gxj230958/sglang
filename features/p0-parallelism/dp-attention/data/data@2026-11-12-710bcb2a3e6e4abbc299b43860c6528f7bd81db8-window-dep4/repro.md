# E01 Window layout under DEP4 — data@2026-11-12-710bcb2a3e6e4abbc299b43860c6528f7bd81db8-window-dep4

## Environment

- Machine: two nodes with 4× NVIDIA GB300 each (node A and node B), no shared disk. Each server uses the four GPUs of one node. This round used node A.
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`, served from a node-local copy; the checkpoint's own NextN head is the MTP draft. The copy was not re-hashed for this round.
- Software: the image's FlashInfer (0.7.1 on node A, 0.7.2 on node B) is overridden through `PYTHONPATH` by FlashInfer 0.7.3 with its cubin and JIT cache; `sgl_flash_mla` 1.0.3; sgl-deep-gemm 0.2.2; `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.

## Setup

Deploy `710bcb2a3e` and start the server with [`dep4/launch.sh`](dep4/launch.sh): `--tp-size 4 --ep-size 4 --attn-dp-size 4 --moe-a2a-backend deepep --deepep-mode auto --moe-runner-backend deep_gemm --mem-fraction-static 0.80 --context-length 32768 --max-running-requests 64 --cuda-graph-max-bs-decode 16 --disable-prefill-cuda-graph`, `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model>`, with `SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1` and `SGLANG_DP_USE_GATHERV=1`.

## Commit

- Code commit: `710bcb2a3e6e4abbc299b43860c6528f7bd81db8`, `glm-5-lp` after pull request 42.
- Working tree: the deployed tree also carried the prefill-CP patch of `0c95a2b1d2`; its code path is not reached without the CP flags.
- Status: non-release. The image digest is not recorded and dependencies come from `PYTHONPATH` overlays, so the environment is not locked.

## Scripts

- Version: round-specific [`serve.sh`](serve.sh), [`eval.sh`](eval.sh), [`wait.sh`](wait.sh), [`probe.py`](probe.py) and [`midfork.py`](midfork.py).
- Temporary changes: none.

## Workload

- GSM8K: full test split (1319 questions) through `sgl-eval` 0.1.3, `sgl-eval run gsm8k --base-url <server>/v1 --temperature 1.0 --top-p 0.95`, 64 client threads, server-default thinking, no `max_tokens`, one run per configuration.
- Retrieval probes ([`probe.py`](probe.py)): a document of `Record i: the code is c.` lines sized to a target length, three questions per length (records at 1/7, 1/2 and near the end), greedy, thinking off, `max_tokens=96`. A request is correct when the expected code appears in the answer. Target lengths 300, 3000, 9000 and 24000.
- Prefix-reuse probe ([`midfork.py`](midfork.py)): a 6680-token record document; six greedy, thinking-off requests in order: first, identical, different question at the end, document forked in the middle (late record), the forked document again (early record), follow-up turn. `cached` lists the reported `cached_tokens` in that order.

## Results

| Configuration | Accuracy | Stop rate | Truncated | Errors | Accept len | Probes | Prefix reuse | KV pool per DP rank |
|---|---|---|---|---|---|---|---|---|
| DEP4, window layout | 94.16% (1242/1319) | 99.47% | 7 | 0% | 2.67 | 12/12 correct, 12/12 `stop` | 6/6 correct, 6/6 `stop`; cached 0 / 0 / 0 / 0 / 0 / 6656 | full_layer_tokens=246784, swa_layer_tokens=24640 |

Accept length is the mean of the `accept len` field over the `Decode batch` lines of the server log. Truncated counts requests that ended with `finish_reason=length`.

Conclusions:

1. The window layout serves under TP4 + EP4 + attention DP4 with MTP and decode CUDA graphs; the stop rate equals the 99.47% reference of the full-length layout at `f8f3fd9253`, and no traceback was logged.
2. Requests land on different DP ranks, so only the follow-up turn of the prefix-reuse probe reports cached tokens; all answers are correct.
3. Not covered here: eight GPUs on one node; see [E02](../data@2026-11-13-e941d571f3877797b383d616e957f30c8936c52d-window-dep8/repro.md).

## Data and Figures

- [`dep4/`](dep4/) — launch script, compressed server log, status, probe and prefix-reuse results, `gsm8k.log` and sgl-eval output.
- [`summary.json`](summary.json) — every number in the Results section, recomputed from the committed files by [`summarize_round.py`](../../../../p0-correctness/scripts/v2/summarize_round.py).
- [`evidence-hashes.json`](evidence-hashes.json) — original path and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
