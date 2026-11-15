# E03 Window layout under CP4 after the main merge — data@2026-11-15-f02daab4df4c9ebfa854ecc7e2da3dd151496389-window-cp4-merged-dev

## Environment

- Machine: two nodes with 4× NVIDIA GB300 each (node A and node B), no shared disk. Each server uses the four GPUs of one node. This round used node A.
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`, served from a node-local copy; the checkpoint's own NextN head is the MTP draft. The copy was not re-hashed for this round.
- Software: an overlay with sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5 and kernels 0.14.1 sits ahead of FlashInfer 0.7.3 (cubin and JIT cache) on `PYTHONPATH`; `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`. The code pins FlashInfer 0.7.4, which was not installed.

## Setup

Deploy `git archive f02daab4df` to the node and start the server with [`gb300-cp4/launch.sh`](gb300-cp4/launch.sh): `--tp-size 4 --moe-runner-backend deep_gemm --mem-fraction-static 0.80 --context-length 131072 --max-running-requests 64 --cuda-graph-max-bs-decode 64 --enable-prefill-cp --cp-strategy interleave --attn-cp-size 4 --cuda-graph-backend-prefill breakable`, `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model>`, with `SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1` and `SGLANG_JIT_DEEPGEMM_PRECOMPILE=0`. [`cp.sh`](cp.sh) runs the probes, the prefix-reuse probe and GSM8K through [`lib.sh`](lib.sh).

## Commit

- Code commit: `f02daab4df4c9ebfa854ecc7e2da3dd151496389`, pull request 57 after `glm-5-lp` at `ec8bc57fde` (upstream `main` merged) was merged into it.
- Working tree: clean archive of the commit.
- The pull request was squash-merged as `5337c504eb` after this gate.
- Status: non-release. The image digest is not recorded and dependencies come from `PYTHONPATH` overlays, so the environment is not locked.

## Scripts

- Version: round-specific [`cp.sh`](cp.sh), [`lib.sh`](lib.sh), [`probe.py`](probe.py) and [`midfork.py`](midfork.py).
- Temporary changes: none.

## Workload

- GSM8K: full test split (1319 questions) through `sgl-eval` 0.1.3, `sgl-eval run gsm8k --base-url <server>/v1 --temperature 1.0 --top-p 0.95`, 64 client threads, server-default thinking, no `max_tokens`, one run per configuration.
- Retrieval probes ([`probe.py`](probe.py)): a document of `Record i: the code is c.` lines sized to a target length, three questions per length (records at 1/7, 1/2 and near the end), greedy, thinking off, `max_tokens=96`. A request is correct when the expected code appears in the answer. Prompts span 320 to 120936 tokens.
- Prefix-reuse probe ([`midfork.py`](midfork.py)): a 6680-token record document; six greedy, thinking-off requests in order: first, identical, different question at the end, document forked in the middle (late record), the forked document again (early record), follow-up turn. `cached` lists the reported `cached_tokens` in that order.

## Results

| Configuration | Accuracy | Stop rate | Truncated | Errors | Accept len | Probes | Prefix reuse | KV pool |
|---|---|---|---|---|---|---|---|---|
| GB300 CP4, window layout | 94.47% (1246/1319) | 99.92% | 1 | 0% | 3.04 | 18/18 correct, 18/18 `stop` | 6/6 correct, 6/6 `stop`; cached 0 / 6656 / 6656 / 0 / 6656 / 6656 | full_layer_tokens=305088, swa_layer_tokens=30464 |

Accept length is the mean of the `accept len` field over the `Decode batch` lines of the server log. Truncated counts requests that ended with `finish_reason=length`.

Conclusions:

1. The window sub-pool under CP4 still passes the stop-rate gate, all 18 retrieval probes and the prefix-reuse probe on the branch that contains the upstream `main` merge.
2. No traceback was logged. FlashInfer stayed at 0.7.3 although the merged code pins 0.7.4.

## Data and Figures

- [`gb300-cp4/`](gb300-cp4/) — launch script, compressed server log, status, probe and prefix-reuse results, `gsm8k.log` and sgl-eval output.
- [`summary.json`](summary.json) — every number in the Results section, recomputed from the committed files by [`summarize_round.py`](../../../../p0-correctness/scripts/v2/summarize_round.py).
- [`evidence-hashes.json`](evidence-hashes.json) — original path and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
