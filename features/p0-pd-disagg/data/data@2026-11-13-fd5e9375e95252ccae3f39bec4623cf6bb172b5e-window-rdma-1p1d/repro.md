# E02 Window layout over 1P1D with RDMA transfer on one RoCE plane — data@2026-11-13-fd5e9375e95252ccae3f39bec4623cf6bb172b5e-window-rdma-1p1d

## Environment

- Machine: two nodes with 4× NVIDIA GB300 each (node A and node B), no shared disk. Each server uses the four GPUs of one node. Prefill and the router ran on node A, decode on node B.
- Network: each node has 16 RoCE rails `ibp{0-3}p{0-3}` (Ethernet link layer). Rails are reachable between the nodes only within the same port index.
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`, served from a node-local copy; the checkpoint's own NextN head is the MTP draft. The copy was not re-hashed for this round.
- Software: the image's FlashInfer (0.7.1 on node A, 0.7.2 on node B) is overridden through `PYTHONPATH` by FlashInfer 0.7.3 with its cubin and JIT cache; `sgl_flash_mla` 1.0.3; sgl-deep-gemm 0.2.2; `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.

## Setup

Deploy `git archive fd5e9375e9` to both nodes. Both servers run `--tp-size 4 --moe-runner-backend deep_gemm --mem-fraction-static 0.80 --context-length 32768 --max-running-requests 64 --cuda-graph-max-bs-decode 64 --disable-prefill-cuda-graph`, `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model>`, `--host 0.0.0.0 --disaggregation-transfer-backend mooncake --disaggregation-enable-kv-checksum --disaggregation-ib-device ibp0p0,ibp1p0,ibp2p0,ibp3p0` and `--disaggregation-mode prefill` or `decode`, with `SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1`. Mooncake keeps its default RDMA protocol.

```bash
python3 -m sglang_router.launch_router --pd-disaggregation \
  --prefill http://<prefill-node>:30000 8998 --decode http://<decode-node>:30001 \
  --request-timeout-secs 7200
```

The router listened on port 18000.

## Commit

- Code commit: `fd5e9375e95252ccae3f39bec4623cf6bb172b5e`, pull request 58 rebased onto `glm-5-lp` at `a736925063`.
- Working tree: clean archive of the commit.
- Status: non-release. The image digest is not recorded and dependencies come from `PYTHONPATH` overlays, so the environment is not locked.

## Scripts

- Version: round-specific [`lib.sh`](lib.sh), [`pd-d.sh`](pd-d.sh), [`probe.py`](probe.py) and [`stress.py`](stress.py). The prefill and client drivers embed node addresses and are not committed.
- Temporary changes: `prefill-and-client/status` records a first client pass whose three steps failed within three seconds of the router start; `status2` is the completed pass that produced the results.

## Workload

- GSM8K: full test split (1319 questions) through `sgl-eval` 0.1.3, `sgl-eval run gsm8k --base-url <server>/v1 --temperature 1.0 --top-p 0.95`, 64 client threads, server-default thinking, no `max_tokens`, one run per configuration. Requests go through the router.
- Retrieval probes ([`probe.py`](probe.py)): a document of `Record i: the code is c.` lines sized to a target length, three questions per length (records at 1/7, 1/2 and near the end), greedy, thinking off, `max_tokens=96`. A request is correct when the expected code appears in the answer. Target lengths 300, 3000, 9000 and 24000.
- Salted stress ([`stress.py`](stress.py)): uncached record documents with a per-request salt, one random record per request, greedy, thinking off, `max_tokens=64`. A request counts when it ends with `stop` and contains the expected code. 25 requests each at 600, 3000, 9000 and 20000 target tokens, 8 concurrent.

## Results

| Run | Accuracy | Stop rate | Truncated | Errors | Accept len (decode server) | Probes | Stress |
|---|---|---|---|---|---|---|---|
| 1P1D, RDMA, plane 0 | 94.77% (1250/1319) | 99.85% | 2 | 0% | 2.54 | 12/12 correct, 12/12 `stop` | 99/100 |

Accept length is the mean of the `accept len` field over the `Decode batch` lines of the server log. Truncated counts requests that ended with `finish_reason=length`. Prefill and decode logs contain 0 and 0 `transport retry counter exceeded` lines, 0 and 0 `Rail paused` lines, 0 and 0 occurrences of `mismatch`, and 0 and 0 tracebacks.

Conclusions:

1. With all Mooncake devices pinned to one RoCE plane on both servers, the window layout transfers over RDMA cleanly: GSM8K passes the stop-rate gate, the probes are all correct, and no transfer failure, checksum mismatch or traceback was logged.
2. The failures in [E01](../data@2026-11-12-3f3a3985acdae2aff39ab9d04c6b0047992dfeb2-window-tcp-1p1d/repro.md) came from the network layout, not from the transfer code: Mooncake's automatic discovery pairs rails across port indices, and such pairs carry no traffic. An `ib_send_bw` check between the nodes passed for `ibp0p0→ibp0p0`, `ibp1p0→ibp0p0` and `ibp0p1→ibp0p1` and delivered no packets for `ibp0p2→ibp0p0`; that check was read from the terminal and its output was not captured as a file.
3. The one stress miss is a 20000-token prompt that opened with reasoning and hit `max_tokens`.
4. Not covered: different attention TP sizes on the two sides, host receive, decode KV offload, HiCache under PD.

## Data and Figures

- [`prefill-and-client/`](prefill-and-client/) — prefill launch script, router-side probe, stress and GSM8K results, and the two client status files.
- [`decode/`](decode/) — decode launch script and status. The prefill, decode and router logs contain the private addresses of the two nodes and are not committed; the same applies to client scripts that embed those addresses. [`omitted-files.json`](omitted-files.json) keeps their SHA-256 and the counters taken from them: decode accept length, tracebacks, RDMA failure lines and occurrences of `mismatch`.
- [`summary.json`](summary.json) — every number in the Results section, recomputed from the committed files by [`summarize_round.py`](../../../p0-correctness/scripts/v2/summarize_round.py).
- [`omitted-files.json`](omitted-files.json) — original path, size and SHA-256 of each file left out of this round, with the counters derived from it before omission.
- [`evidence-hashes.json`](evidence-hashes.json) — original path and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
