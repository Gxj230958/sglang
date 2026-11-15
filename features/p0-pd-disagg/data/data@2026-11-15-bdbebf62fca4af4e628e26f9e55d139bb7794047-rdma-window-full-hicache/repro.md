# E03 Window, full-length and prefill-HiCache legs over 1P1D with RDMA — data@2026-11-15-bdbebf62fca4af4e628e26f9e55d139bb7794047-rdma-window-full-hicache

## Environment

- Machine: two nodes with 4× NVIDIA GB300 each (node A and node B), no shared disk. Each server uses the four GPUs of one node. Prefill and the router ran on node A, decode on node B.
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`, served from a node-local copy; the checkpoint's own NextN head is the MTP draft. The copy was not re-hashed for this round.
- Software: an overlay with sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5 and kernels 0.14.1 sits ahead of FlashInfer 0.7.3 (cubin and JIT cache) on `PYTHONPATH`; `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`. The code pins FlashInfer 0.7.4, which was not installed.

## Setup

Deploy `git archive bdbebf62fc` to both nodes. [`lib.sh`](lib.sh) starts every server with `--tp-size 4 --moe-runner-backend deep_gemm --mem-fraction-static 0.80 --context-length 32768 --max-running-requests 64 --cuda-graph-max-bs-decode 64 --disable-prefill-cuda-graph`, `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model>`, `--host 0.0.0.0 --disaggregation-transfer-backend mooncake --disaggregation-enable-kv-checksum --disaggregation-ib-device ibp0p0,ibp1p0,ibp2p0,ibp3p0` and `--disaggregation-mode prefill` or `decode`. Each leg is a cold start of both servers.

| Leg | Layout | Extra prefill flags |
|---|---|---|
| `pdswa` | window (`SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1` on both servers) | none |
| `pdfull` | full-length (variable unset) | none |
| `pdhc` | window | `--enable-hierarchical-cache --hicache-size 64 --hicache-storage-backend file` |
| `pdhc3` | window, both servers restarted on the storage directory left by `pdhc` | same as `pdhc` |

```bash
python3 -m sglang_router.launch_router --pd-disaggregation \
  --prefill http://<prefill-node>:30000 8998 --decode http://<decode-node>:30001 \
  --request-timeout-secs 7200
```

The router listened on port 18000.

## Commit

- Code commit: `bdbebf62fca4af4e628e26f9e55d139bb7794047`, pull request 58 after `glm-5-lp` at `5337c504eb` was merged into it.
- Working tree: clean archive of the commit.
- The pull request head `c7c93b3fd0` is this tree plus a documentation-only commit. The pull request is open.
- Status: non-release. The image digest is not recorded and dependencies come from `PYTHONPATH` overlays, so the environment is not locked.

## Scripts

- Version: round-specific [`lib.sh`](lib.sh), [`probe.py`](probe.py), [`stress.py`](stress.py), [`midfork.py`](midfork.py) and [`hicache.py`](hicache.py). The client driver embeds node addresses and is not committed; its steps are the commands listed under Workload.
- Temporary changes: none. In `pdhc-client/status`, `fill rc=1` and `mfb rc=1` are the exit status of the trailing `grep -c` that counted zero prefetch lines, not of the probes.

## Workload

- GSM8K: full test split (1319 questions) through `sgl-eval` 0.1.3, `sgl-eval run gsm8k --base-url <server>/v1 --temperature 1.0 --top-p 0.95`, 64 client threads, server-default thinking, no `max_tokens`, one run per configuration. Requests go through the router.
- Retrieval probes ([`probe.py`](probe.py)): a document of `Record i: the code is c.` lines sized to a target length, three questions per length (records at 1/7, 1/2 and near the end), greedy, thinking off, `max_tokens=96`. A request is correct when the expected code appears in the answer. Target lengths 300, 3000, 9000 and 24000.
- Salted stress ([`stress.py`](stress.py)): uncached record documents with a per-request salt, one random record per request, greedy, thinking off, `max_tokens=64`. A request counts when it ends with `stop` and contains the expected code. 25 requests each at 600, 3000, 9000 and 20000 target tokens, 8 concurrent.
- Prefix-reuse probe ([`midfork.py`](midfork.py)): a 6680-token record document; six greedy, thinking-off requests in order: first, identical, different question at the end, document forked in the middle (late record), the forked document again (early record), follow-up turn. `cached` lists the reported `cached_tokens` in that order.
- HiCache fill ([`hicache.py`](hicache.py) `fill 70`): 70 new 6.7K-token prompts, 8 concurrent, pushed through the prefill device pool between two prefix-reuse probes; `prefetch-after-*.txt` holds the number of `HiCache prefetch success` lines in the prefill log at that point.

## Results

| Leg | Accuracy | Stop rate | Truncated | Errors | Accept len (decode server) | Probes | Stress |
|---|---|---|---|---|---|---|---|
| `pdswa` | 95.07% (1254/1319) | 99.55% | 6 | 0% | 2.72 | 12/12 correct, 12/12 `stop` | 100/100 |
| `pdfull` | 94.69% (1249/1319) | 99.70% | 4 | 0% | 2.61 | 12/12 correct, 12/12 `stop` | 100/100 |
| `pdhc` | 94.84% (1251/1319) | 99.55% | 6 | 0% | 2.59 | not run | not run |

| HiCache step | Prefix-reuse probe | `HiCache prefetch success` lines in the prefill log |
|---|---|---|
| `pdhc`, before the fill | 6/6 correct, 6/6 `stop`; cached 0 / 6656 / 6656 / 0 / 6656 / 6656 | 0 |
| `pdhc`, after the 70-prompt fill | 6/6 correct, 6/6 `stop`; cached 6656 / 6656 / 6656 / 6656 / 6656 / 6656 | 0 |
| `pdhc3`, after restarting both servers | 6/6 correct, 6/6 `stop`; cached 6656 / 6656 / 6656 / 6656 / 6656 / 6656 | 8 |

| Leg (prefill / decode) | `transport retry counter exceeded` | `Rail paused` | `mismatch` | Traceback |
|---|---|---|---|---|
| `pdswa` | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| `pdfull` | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| `pdhc` | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| `pdhc3` | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |

Accept length is the mean of the `accept len` field over the `Decode batch` lines of the server log. Truncated counts requests that ended with `finish_reason=length`.

Conclusions:

1. On the branch that contains the upstream `main` merge, PD over RDMA passes the stop-rate gate, the probes and the stress on both the window and the full-length layout, with no transfer failure, checksum mismatch or traceback.
2. A prefill server with HiCache restores an evicted prefix from host memory (no storage prefetch line) and, after a restart of both servers, from file storage (8 prefetch lines); the restored prefix transfers to the decode server and all probe answers are correct.
3. The window legs stop at 99.55% in one run each, above the 99.47% reference of the full-length layout at `f8f3fd9253` and below the 99.85% of [E02](../data@2026-11-13-fd5e9375e95252ccae3f39bec4623cf6bb172b5e-window-rdma-1p1d/repro.md). All truncations are requests that ran to the 32768-token context.
4. Open review finding, not addressed by this commit: the KV checksum addresses the DSA tail buffers with full-KV page ids. It is reachable only with a compressed index pool (`index_kpool > 1`); this checkpoint uses 1.
5. Not covered: decode-side HiCache, host receive, decode KV offload, different attention TP sizes on the two sides, CP prefill under PD.

## Data and Figures

- `pdswa-client/`, `pdfull-client/`, `pdhc-client/`, `pdhc3-client/` — router-side results of each leg: probes, stress, prefix-reuse probes, prefetch counters, `gsm8k.log`, sgl-eval output and status.
- `*-prefill/`, `*-decode/` — launch scripts; `*.ready` and `*-client.out` are the driver's readiness and console files. The prefill, decode and router logs contain the private addresses of the two nodes and are not committed; the same applies to client scripts that embed those addresses. [`omitted-files.json`](omitted-files.json) keeps their SHA-256 and the counters taken from them: decode accept length, tracebacks, RDMA failure lines and occurrences of `mismatch`.
- [`summary.json`](summary.json) — every number in the Results section, recomputed from the committed files by [`summarize_round.py`](../../../p0-correctness/scripts/v2/summarize_round.py).
- [`omitted-files.json`](omitted-files.json) — original path, size and SHA-256 of each file left out of this round, with the counters derived from it before omission.
- [`evidence-hashes.json`](evidence-hashes.json) — original path and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
