# E01 Window layout under prefill CP4 — data@2026-11-12-0c95a2b1d2f1cfcaa6bcc503acfe868cd8a6083e-window-cp4

## Environment

- Machine: two nodes with 4× NVIDIA GB300 each (node A and node B), no shared disk. Each server uses the four GPUs of one node. The window-layout server ran on node A, the full-length reference on node B.
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`, served from a node-local copy; the checkpoint's own NextN head is the MTP draft. The copy was not re-hashed for this round.
- Software: the image's FlashInfer (0.7.1 on node A, 0.7.2 on node B) is overridden through `PYTHONPATH` by FlashInfer 0.7.3 with its cubin and JIT cache; `sgl_flash_mla` 1.0.3; sgl-deep-gemm 0.2.2; `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.

## Setup

Deploy `710bcb2a3e` plus the code diff of `0c95a2b1d2` (`git diff 710bcb2a3e 0c95a2b1d2 -- python test`) to both nodes, put the FlashInfer 0.7.3 overlay ahead of the image packages, and start each server with its `launch.sh`:

```bash
python3 -m sglang.launch_server --model-path <model> --tp-size 4 --moe-runner-backend deep_gemm \
  --mem-fraction-static 0.80 --context-length 131072 --max-running-requests 64 --cuda-graph-max-bs-decode 64 \
  --enable-prefill-cp --cp-strategy interleave --attn-cp-size 4 --cuda-graph-backend-prefill breakable \
  --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 \
  --speculative-num-draft-tokens 4 --speculative-draft-model-path <model> \
  --reasoning-parser glm45 --tool-call-parser glm47 --enable-cache-report
```

Both servers set `SGLANG_JIT_DEEPGEMM_PRECOMPILE=0`. The window server additionally sets `SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1`; the reference runs the same tree without it.

## Commit

- Code commit: `0c95a2b1d2f1cfcaa6bcc503acfe868cd8a6083e`, the first head of radixark/sglang-zai pull request 57.
- Working tree: `710bcb2a3e` with the `python` and `test` paths of that commit applied as a patch; the documentation change of the commit was not deployed.
- Status: non-release. The image digest is not recorded and dependencies come from `PYTHONPATH` overlays, so the environment is not locked.

## Scripts

- Version: round-specific [`serve.sh`](serve.sh), [`eval.sh`](eval.sh), [`wait.sh`](wait.sh) and [`probe.py`](probe.py).
- Temporary changes: none.

## Workload

- GSM8K: full test split (1319 questions) through `sgl-eval` 0.1.3, `sgl-eval run gsm8k --base-url <server>/v1 --temperature 1.0 --top-p 0.95`, 64 client threads, server-default thinking, no `max_tokens`, one run per configuration.
- Retrieval probes ([`probe.py`](probe.py)): a document of `Record i: the code is c.` lines sized to a target length, three questions per length (records at 1/7, 1/2 and near the end), greedy, thinking off, `max_tokens=96`. A request is correct when the expected code appears in the answer. Target lengths 300, 3000, 9000, 24000, 60000 and 110000 give prompts of 320 to 120936 tokens.

## Results

| Configuration | Accuracy | Stop rate | Truncated | Errors | Accept len | Probes | KV pool |
|---|---|---|---|---|---|---|---|
| CP4, window layout | 95.30% (1257/1319) | 99.92% | 1 | 0% | 2.80 | 18/18 correct, 18/18 `stop` | full_layer_tokens=304640, swa_layer_tokens=30464 |
| CP4, full-length layout | 94.16% (1242/1319) | 99.92% | 1 | 0% | 2.79 | 18/18 correct, 18/18 `stop` | 234560 tokens |

Accept length is the mean of the `accept len` field over the `Decode batch` lines of the server log. Truncated counts requests that ended with `finish_reason=length`.

Conclusions:

1. The window sub-pool serves under interleaved prefill CP4 with MTP and decode CUDA graphs. Its stop rate equals the full-length reference in the same configuration, and neither server logged a traceback.
2. Retrieval is correct at every probed length up to 120936 prompt tokens on both layouts.
3. At the same memory fraction the window layout holds 304640 full-layer tokens against 234560 for the full-length layout (+29.9%).
4. Each configuration has one GSM8K run; the 1.1-point accuracy difference is within the spread of single runs recorded in the other rounds of this date.
5. Not covered: CP8, the `trtllm` DSA backend under CP, and HiCache under CP.

## Data and Figures

- [`window/`](window/) and [`full-length/`](full-length/) — launch script, compressed server log, readiness and eval status, `gsm8k.log`, probe results, and the sgl-eval output directory (`metrics.json`, compressed `output-rs0.jsonl`).
- [`summary.json`](summary.json) — every number in the Results section, recomputed from the committed files by [`summarize_round.py`](../../../../p0-correctness/scripts/v2/summarize_round.py).
- [`evidence-hashes.json`](evidence-hashes.json) — original path and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
