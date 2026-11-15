# E02 Window layout under CP4 on GB300 and CP8 on B300 — data@2026-11-13-e941d571f3877797b383d616e957f30c8936c52d-window-cp4-cp8

## Environment

- Machine: two nodes with 4× NVIDIA GB300 each (node A and node B), no shared disk. Each server uses the four GPUs of one node. The CP4 runs used node A.
- Machine: one node with 8× NVIDIA B300. It ran CP8.
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`, served from a node-local copy; the checkpoint's own NextN head is the MTP draft. The copy was not re-hashed for this round.
- Software: the image's FlashInfer (0.7.1 on node A, 0.7.2 on node B) is overridden through `PYTHONPATH` by FlashInfer 0.7.3 with its cubin and JIT cache; `sgl_flash_mla` 1.0.3; sgl-deep-gemm 0.2.2; `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.
- Software on B300: image torch 2.14.1+cu130, transformers 5.19.0, sglang-kernel 0.4.10; an overlay on `PYTHONPATH` adds flashinfer-python / cubin / jit-cache 0.7.3, sgl-deep-gemm 0.2.7 and sgl-flash-mla 1.0.4; `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.

## Setup

Deploy `git archive e941d571f3` to each node and start the servers with their `launch.sh`. All servers use `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model>`, `--reasoning-parser glm45 --tool-call-parser glm47 --enable-cache-report`, `SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1` and `SGLANG_JIT_DEEPGEMM_PRECOMPILE=0`.

- GB300 CP4: `--tp-size 4 --moe-runner-backend deep_gemm --mem-fraction-static 0.80 --context-length 131072 --max-running-requests 64 --cuda-graph-max-bs-decode 64 --enable-prefill-cp --cp-strategy interleave --attn-cp-size 4 --cuda-graph-backend-prefill breakable`.
- B300 CP8: `--tp-size 8 --mem-fraction-static 0.75 --context-length 131072 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --enable-prefill-cp --cp-strategy interleave --attn-cp-size 8 --cuda-graph-backend-prefill breakable`.

[`gb300-cp.sh`](gb300-cp.sh) and [`gb300-cplong.sh`](gb300-cplong.sh) drive the GB300 runs through [`gb300-lib.sh`](gb300-lib.sh); [`b300-combo.sh`](b300-combo.sh) drives the B300 run (its second job is recorded under DP Attention E02).

## Commit

- Code commit: `e941d571f3877797b383d616e957f30c8936c52d`, pull request 57 rebased onto `glm-5-lp` at `a736925063`.
- Working tree: clean archive of the commit.
- Status: non-release. The image digest is not recorded and dependencies come from `PYTHONPATH` overlays, so the environment is not locked.

## Scripts

- Version: round-specific driver scripts listed above, [`probe.py`](probe.py) and [`midfork.py`](midfork.py).
- Temporary changes: the first GB300 probe pass asked for a 120000-token target, which exceeds the 131072-token context after templating; the server rejected it with HTTP 400 and the 110000-token tier was rerun on a second start of the same tree (`gb300-cp4-long`).

## Workload

- GSM8K: full test split (1319 questions) through `sgl-eval` 0.1.3, `sgl-eval run gsm8k --base-url <server>/v1 --temperature 1.0 --top-p 0.95`, 64 client threads, server-default thinking, no `max_tokens`, one run per configuration.
- Retrieval probes ([`probe.py`](probe.py)): a document of `Record i: the code is c.` lines sized to a target length, three questions per length (records at 1/7, 1/2 and near the end), greedy, thinking off, `max_tokens=96`. A request is correct when the expected code appears in the answer.
- Prefix-reuse probe ([`midfork.py`](midfork.py)): a 6680-token record document; six greedy, thinking-off requests in order: first, identical, different question at the end, document forked in the middle (late record), the forked document again (early record), follow-up turn. `cached` lists the reported `cached_tokens` in that order.

## Results

| Configuration | Accuracy | Stop rate | Truncated | Errors | Accept len | Probes | Prefix reuse | KV pool |
|---|---|---|---|---|---|---|---|---|
| GB300 CP4 | 94.69% (1249/1319) | 100.00% | 0 | 0% | 2.56 | 15/15 correct with `stop` up to 64738 tokens ([`gb300-cp4/probe.log`](gb300-cp4/probe.log)); 3/3 correct, 3/3 `stop` at 120935–120936 tokens | not run | full_layer_tokens=304640, swa_layer_tokens=30464 |
| B300 CP8 | 95.68% (1262/1319) | 99.92% | 1 | 0% | 2.75 | 17/18 correct, 18/18 `stop` | 6/6 correct, 6/6 `stop`; cached 0 / 6656 / 6656 / 0 / 6656 / 6656 | full_layer_tokens=1065792, swa_layer_tokens=106560 |

Accept length is the mean of the `accept len` field over the `Decode batch` lines of the server log. Truncated counts requests that ended with `finish_reason=length`.

Conclusions:

1. The window sub-pool passes the stop-rate gate under CP4 on GB300 and CP8 on B300 at this commit; no server logged a traceback.
2. On B300 CP8 one of the three 120936-token probes (record 4230) returned a wrong code with `stop`; the other 17 probes are correct. The GB300 CP4 probes are all correct, including the three at 120935–120936 tokens.
3. Mid-document forks reuse no cached tokens on the window layout and answer correctly.
4. Not covered: the `trtllm` DSA backend under CP and HiCache under CP.

## Data and Figures

- [`gb300-cp4/`](gb300-cp4/) — CP4 server log, launch script, status, `gsm8k.log`, probe log and sgl-eval output.
- [`gb300-cp4-long/`](gb300-cp4-long/) — second start of the same tree for the 110000-token probe tier.
- [`b300-cp8/`](b300-cp8/) — CP8 server log, launch script, probe and prefix-reuse results, `gsm8k.log` and sgl-eval output. The driver's status file was not retained.
- [`summary.json`](summary.json) — every number in the Results section, recomputed from the committed files by [`summarize_round.py`](../../../../p0-correctness/scripts/v2/summarize_round.py).
- [`evidence-hashes.json`](evidence-hashes.json) — original path and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
