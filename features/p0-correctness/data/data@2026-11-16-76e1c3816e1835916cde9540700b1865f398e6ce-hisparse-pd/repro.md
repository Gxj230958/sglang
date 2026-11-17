# E29 HiSparse decode under PD: GSM8K, GPQA and RULER2 against a plain decode — data@2026-11-16-76e1c3816e1835916cde9540700b1865f398e6ce-hisparse-pd

## Environment

- Machines: two nodes with 4× NVIDIA GB300 each (Grace CPUs, aarch64, 955 GiB host memory per node), connected by four 200 Gb/s InfiniBand NICs per node. Node A runs the prefill server, the Mooncake master and the PD router; node B runs the decode server and the clients of the AgentX round.
- Containers: the nodes' stock SGLang images, `lmsysorg/sglang:v0.5.22` on node A and `lmsysorg/sglang:v0.5.23` on node B; image digests were not recorded. The served source tree and the kernel packages below are put in front of the image by `PYTHONPATH` ([`scripts/pd_env.sh`](scripts/pd_env.sh)), so both nodes import the same code and kernels.
- Model: `zai-org/GLM-5-1028-Provider` at revision `66c3fe71d4c4ab43efac5bb0d2be6dea3a75d089` (all 150 files of the node-local copy carry this revision in their Hugging Face download metadata). This is not the `7e66c405` revision of earlier rounds. The checkpoint's own NextN head is the MTP draft.
- Software, as imported with the round's `PYTHONPATH` on both nodes: flashinfer-python / flashinfer-cubin / flashinfer-jit-cache 0.7.4 (+cu130), sglang-kernel 0.4.11, sgl-deep-gemm 0.2.8, sgl-flash-mla 1.0.5, kernels 0.14.1, torch 2.14.1+cu130, mooncake-transfer-engine-cuda13 0.3.13.post1 (master `0.3.13.post1`, git `7197358`), sglang-router 0.3.2, NVIDIA driver 580.178.04, CUDA 13.0. Evaluation: sgl-eval 0.1.3 in its own virtual environment (`ns_commit_sha` `645cf567` in every `metrics.json`).

## Setup

All five scripts source [`scripts/pd_env.sh`](scripts/pd_env.sh), which holds the flags both servers share: `--moe-runner-backend flashinfer_trtllm --disable-shared-experts-fusion --kv-cache-dtype bf16 --dsa-prefill-backend flashmla_sparse --dsa-decode-backend flashmla_sparse`, MTP (`--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4`, draft quantization fp8), `--mem-fraction-static 0.80 --context-length 147456 --chunked-prefill-size 8192 --disable-prefill-cuda-graph --enable-fp32-lm-head --reasoning-parser glm45 --tool-call-parser glm47 --random-seed 1`, and the Mooncake transfer backend over the four RDMA NICs. Both servers use the default window KV layout.

1. [`scripts/pd_master.sh`](scripts/pd_master.sh) starts the Mooncake master on node A.
2. [`scripts/pd_prefill.sh`](scripts/pd_prefill.sh) starts the prefill server on node A: TP4, `--max-running-requests 64`, the unified-cache external linker with the Mooncake store backend over RDMA (`enable_group_semantics: true`, 140 GB global segment).
3. [`scripts/pd_decode.sh`](scripts/pd_decode.sh) starts the decode server on node B: TP4 with DP attention 4 and EP4 (`--tp-size 4 --dp-size 4 --enable-dp-attention --ep-size 4`), `--max-running-requests 256 --cuda-graph-max-bs-decode 32`.
   - Baseline arm: no further flags.
   - HiSparse arm (`HS=1 RATIO=6 DBS=4096`): `--enable-hisparse --hisparse-config '{"top_k":2048,"device_buffer_size":4096,"host_to_device_ratio":6}'`.
4. [`scripts/pd_router.sh`](scripts/pd_router.sh) starts the PD router on node A in front of the two servers.
5. [`scripts/pd_acc.sh`](scripts/pd_acc.sh) runs the three evaluations through the router.

Per-rank decode KV pools, from the decode logs:

| Arm | Full-attention device rows | Window rows | Host-backed logical ids | Scheduler token capacity in this round |
|---|---:|---:|---:|---:|
| Baseline | 208,256 | 45,568 | — | 208,256 |
| HiSparse, ratio 6 | 122,752 | 45,568 | 736,512 | 122,752 |

Timeline (UTC, from the logs): prefill server up from 2026-11-16 19:20 to 2026-11-17 07:42 for both arms. Baseline decode 19:20:57–23:09:58 on 2026-11-16; HiSparse decode 00:21:04–04:49:44 on 2026-11-17.

## Commit

- Code commit: `76e1c3816e1835916cde9540700b1865f398e6ce`, published as branch `hisparse-window-subpool-eval` of `radixark/sglang-zai`. It is the HiSparse change on `glm-5-lp` at `dd452d24`. Pull request 84 carries the same change rebased onto `58dc6ec3` (head `9193094c`).
- Working tree: `76e1c381` plus [`without-request-capacity.patch`](without-request-capacity.patch), which leaves out the request-capacity part of `kv_cache_configurator.py`.
  - The served Python tree was compared file by file with `76e1c381` after the AgentX round; all 5,281 files match.
  - During this round, `kv_cache_configurator.py` did not yet have the request-capacity change. It was synced in at 2026-11-17 06:14, after both arms finished.
  - The patch reconstructs that earlier state. No hash of the earlier file was kept.
  - Without HiSparse, `logical_ids_per_full_row()` is 1, so the change does nothing to the baseline arm.
  - On the HiSparse arm, its absence is visible as the 122,752-token scheduler capacity in the log. Every evaluation prompt is far shorter than the device rows, so no request was refused or truncated by it.
- Status: non-release. One launch per arm, unseeded sampling, image digests not recorded, model revision differs from earlier rounds, and the working tree differs from the published commit as described.

## Scripts

- Version: round-specific scripts under [`scripts/`](scripts/). IP addresses, host names and local paths were replaced by placeholders (`<PREFILL_NODE_IP>`, `<DECODE_NODE_IP>`, `$WORK`, `$MODEL_PATH`, `$FLASHINFER_074`, `$KERNEL_OVERLAY`, `$FLASH_MLA_103`) in every committed file, logs included.
- Temporary changes: the working-tree difference above.

## Workload

All requests go through the PD router with sgl-eval 0.1.3 at the model's recommended sampling, temperature 1.0 and top_p 0.95, and server-default thinking.

- GSM8K: 200 questions, `--max-tokens 16384`, 128 threads.
- GPQA diamond: 198 questions × 2 repeats from the copy vendored in sgl-eval (`--from-dataset .../nemo_skills/dataset/gpqa/diamond.jsonl`), `--max-tokens 32768`, 32 threads.
- RULER2: 1200 examples at `--ruler2-seq-len 32768` with the model's tokenizer, `--max-tokens 8192`, 64 threads.

## Results

| Eval | Baseline decode | HiSparse decode | Stop rate (baseline / HiSparse) | Errors |
|---|---:|---:|---|---|
| GSM8K (200) | 96.00% | 94.00% | 99.00% / 99.50% | 0 / 0 |
| GPQA diamond, pass@1 avg of 2 | 69.95% ± 0.36% | 72.47% ± 3.21% | 76.26% / 78.03% | 0 / 0 |
| RULER2 32K (1200) | 91.14% | 90.58% | 98.25% / 98.83% | 0 / 0 |

- GPQA truncates about 22–24% of samples in both arms at 32,768 tokens; pass@2 is 76.26% / 80.81%.

RULER2 sub-tasks (100 examples each, from `aggregate.task` in each `metrics.json`):

| Task | Baseline | HiSparse | Task | Baseline | HiSparse |
|---|---:|---:|---|---:|---:|
| mk_niah_basic | 98.00% | 98.00% | mv_niah_easy | 93.25% | 90.58% |
| mk_niah_easy | 99.73% | 99.69% | mv_niah_medium | 78.09% | 84.87% |
| mk_niah_medium | 89.00% | 90.00% | mv_niah_hard | 74.15% | **64.07%** |
| mk_niah_hard | 89.00% | 91.00% | qa_basic | 100.00% | 100.00% |
| mv_niah_basic | 95.50% | 96.25% | qa_easy | 95.00% | 91.00% |
| qa_medium | 89.00% | 89.00% | qa_hard | 93.00% | 92.50% |
- Excluded run, kept in the round as evidence: the first baseline GPQA attempt used 128 client threads (`evals/pd_base/sgl_eval_gpqa_20261116-193908`, [`logs/pd_base_gpqa.t128.log.gz`](logs/pd_base_gpqa.t128.log.gz)).
  - It scored 62.12% with an 8.84% request error rate.
  - The decode server was full, prefill bootstrap waits passed the 300 s default, and the router answered 503.
  - Both arms were then run at 32 threads.
- An earlier baseline invocation could not fetch GPQA from the gated Hub dataset ([`logs/pd_acc_base.out`](logs/pd_acc_base.out)); the vendored copy was used from then on.

Conclusions:

1. Under PD with a DPA4 + EP4 + MTP decode, HiSparse at `top_k` 2048, device buffer 4096 and host ratio 6 gives aggregate GSM8K, GPQA diamond and RULER2 32K scores within 2.5 points of the baseline, in both directions. Every request completed without error.
2. Open observation: RULER2 `mv_niah_hard` is 10.1 points lower with HiSparse (74.15% → 64.07%), while `mv_niah_medium` is 6.8 points higher.
   - At 100 examples per task, the standard error of a difference near 70% is about 6.5 points, so one run per arm neither confirms nor rules out a regression on multi-value retrieval.
   - The task needs repeated seeds per arm before HiSparse is called accuracy-neutral on long-context retrieval.

## Data and Figures

- `evals/pd_base/`, `evals/pd_hs/` — sgl-eval `metrics.json` and per-sample outputs (`output-rs*.jsonl.gz`) of each run; the run directories named in Results are the scored ones.
- `logs/pd_acc_*.out` — the evaluation summaries printed by `pd_acc.sh`; `pd_acc_base3.out` and `pd_acc_hs.out` hold the scored set.
- `logs/pd_{base,hs}_{gsm8k,gpqa,ruler2}.log*` — sgl-eval console logs.
- `logs/pd_decode_base.acc.log.gz`, `logs/pd_decode_hs.lenbug.log.gz` — decode server logs of the baseline and HiSparse arms. The HiSparse log also covers the first AgentX attempts of the [AgentX round](../../../p0-agentx-performance/data/data@2026-11-17-76e1c3816e1835916cde9540700b1865f398e6ce-hisparse-pd/repro.md), which found the request-capacity defect.
- `logs/pd_prefill.r1.log.gz`, `logs/pd_master.r1.log.gz`, `logs/pd_router.r1.log` — prefill server, Mooncake master and router startup logs over the same window.
- [`evidence-hashes.json`](evidence-hashes.json) — SHA-256 of every file in the round.
