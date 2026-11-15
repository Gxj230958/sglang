# E01 Window layout over 1P1D with forced TCP transfer — data@2026-11-12-3f3a3985acdae2aff39ab9d04c6b0047992dfeb2-window-tcp-1p1d

## Environment

- Machine: two nodes with 4× NVIDIA GB300 each (node A and node B), no shared disk. Each server uses the four GPUs of one node. Prefill and the router ran on node A, decode on node B.
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`, served from a node-local copy; the checkpoint's own NextN head is the MTP draft. The copy was not re-hashed for this round.
- Software: the image's FlashInfer (0.7.1 on node A, 0.7.2 on node B) is overridden through `PYTHONPATH` by FlashInfer 0.7.3 with its cubin and JIT cache; `sgl_flash_mla` 1.0.3; sgl-deep-gemm 0.2.2; `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.

## Setup

Deploy `710bcb2a3e` with the seven changed `python` and `test` files of `3f3a3985ac` to both nodes. Both servers run `--tp-size 4 --moe-runner-backend deep_gemm --mem-fraction-static 0.80 --context-length 32768 --max-running-requests 64 --cuda-graph-max-bs-decode 64 --disable-prefill-cuda-graph`, `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model>`, `--host 0.0.0.0 --disaggregation-transfer-backend mooncake --disaggregation-enable-kv-checksum` and `--disaggregation-mode prefill` (with `--disaggregation-bootstrap-port 8998`) or `decode`. Environment: `SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1`, `MOONCAKE_PROTOCOL=tcp`, `MC_FORCE_TCP=1`.

```bash
python3 -m sglang_router.launch_router --pd-disaggregation \
  --prefill http://<prefill-node>:30000 8998 --decode http://<decode-node>:30001 \
  --request-timeout-secs 7200
```

The `rdma-auto-*` pair is the first attempt, started without `MC_FORCE_TCP=1`.

## Commit

- Code commit: `3f3a3985acdae2aff39ab9d04c6b0047992dfeb2`, the first head of radixark/sglang-zai pull request 58.
- Working tree: `710bcb2a3e` plus the code files of that commit; the deployed files were hash-identical to the commit.
- Status: non-release. The image digest is not recorded and dependencies come from `PYTHONPATH` overlays, so the environment is not locked.

## Scripts

- Version: round-specific [`serve.sh`](serve.sh), [`eval.sh`](eval.sh), [`wait.sh`](wait.sh), [`probe.py`](probe.py) and [`stress.py`](stress.py).
- Temporary changes: none.

## Workload

- GSM8K: full test split (1319 questions) through `sgl-eval` 0.1.3, `sgl-eval run gsm8k --base-url <server>/v1 --temperature 1.0 --top-p 0.95`, 64 client threads, server-default thinking, no `max_tokens`, one run per configuration. Requests go through the router.
- Retrieval probes ([`probe.py`](probe.py)): a document of `Record i: the code is c.` lines sized to a target length, three questions per length (records at 1/7, 1/2 and near the end), greedy, thinking off, `max_tokens=96`. A request is correct when the expected code appears in the answer. Target lengths 300, 3000, 9000 and 24000.
- Salted stress ([`stress.py`](stress.py)): uncached record documents with a per-request salt, one random record per request, greedy, thinking off, `max_tokens=64`. A request counts when it ends with `stop` and contains the expected code. Run 1: 16 requests each at 600, 3000, 9000 and 20000 target tokens, 8 concurrent. Run 2 (restarted pair): 100 requests at each length, 8 concurrent, after a cold replay of the probe sequence.

## Results

| Run | Accuracy | Stop rate | Truncated | Errors | Accept len (decode server) | Probes | Stress |
|---|---|---|---|---|---|---|---|
| Run 1, forced TCP | 94.01% (1240/1319) | 99.70% | 4 | 0% | 2.57 | 12/12 correct, 11/12 `stop` | 64/64 |
| Run 2, restarted pair | not run | | | | | 12/12 correct, 12/12 `stop` | 398/400 |

Accept length is the mean of the `accept len` field over the `Decode batch` lines of the server log. Truncated counts requests that ended with `finish_reason=length`. Over the GSM8K window alone the decode accept length is 2.58.

Transfer health, from the omitted logs:

| Pair | `transport retry counter exceeded` | `Rail paused` | `transfer failed` | `mismatch` | Traceback |
|---|---|---|---|---|---|
| Run 1, prefill / decode | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Run 2, prefill / decode | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| First attempt without `MC_FORCE_TCP=1`, prefill / decode | 2011 / 0 | 2011 / 0 | 4 / 4 | 0 / 0 | 0 / 0 |

Conclusions:

1. The window layout transfers main KV, window state and index-K (including the draft) over 1P1D with MTP; GSM8K passes the stop-rate gate and no checksum mismatch or traceback was logged.
2. The one probe that ended with `length` in run 1 (9225 tokens, correct answer text) did not recur in the cold replay on a restarted pair.
3. In run 2, 2 of 400 salted requests opened with reasoning instead of an answer and hit `max_tokens`. Single-server controls on the same prompt sets show the same rare event on both layouts ([Correctness E06](../../../p0-correctness/data/data@2026-11-12-710bcb2a3e6e4abbc299b43860c6528f7bd81db8-window-layout-matrix/repro.md)).
4. With `MOONCAKE_PROTOCOL=tcp` alone, Mooncake still selected the nodes' RDMA devices and 2011 transfer slices failed. The cause is recorded in [E02](../data@2026-11-13-fd5e9375e95252ccae3f39bec4623cf6bb172b5e-window-rdma-1p1d/repro.md).
5. Not covered: RDMA transfer, different attention TP sizes on the two sides, host receive, decode KV offload.

## Data and Figures

- [`run1-client/`](run1-client/) — router-side probe, stress and GSM8K results of run 1.
- [`run2-client/`](run2-client/) — cold probe replay and the 400-request stress on the restarted pair.
- `run1-*`, `run2-*`, `rdma-auto-*` prefill and decode directories — launch scripts. The prefill, decode and router logs contain the private addresses of the two nodes and are not committed; the same applies to client scripts that embed those addresses. [`omitted-files.json`](omitted-files.json) keeps their SHA-256 and the counters taken from them: decode accept length, tracebacks, RDMA failure lines and occurrences of `mismatch`.
- [`summary.json`](summary.json) — every number in the Results section, recomputed from the committed files by [`summarize_round.py`](../../../p0-correctness/scripts/v2/summarize_round.py).
- [`omitted-files.json`](omitted-files.json) — original path, size and SHA-256 of each file left out of this round, with the counters derived from it before omission.
- [`evidence-hashes.json`](evidence-hashes.json) — original path and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
