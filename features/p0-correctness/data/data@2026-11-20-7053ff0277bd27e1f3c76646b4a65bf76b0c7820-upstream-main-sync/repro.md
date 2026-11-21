# E31 Upstream main sync correctness — data@2026-11-20-7053ff0277bd27e1f3c76646b4a65bf76b0c7820-upstream-main-sync

## Environment

- Machine: `mobius-8gb300-share`; one 4x NVIDIA GB300 rank per arm. Baseline used rank 0 and the candidate used rank 1.
- Container: `lmsysorg/sglang:latest`; no immutable image digest was captured, so this round is non-release.
- Model: `zai-org/GLM-5-1028-Provider` at tracked FP8 revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`, including its own NextN draft.
- Checkpoint receipt: [checkpoint-receipt.json](checkpoint-receipt.json). Both ranks match the config, weight-index, tokenizer and tokenizer-config hashes pinned to that revision in Correctness E27. `config.json` has no `_commit_hash`; weight shards were not rehashed.
- Software: torch 2.14.1+cu130, transformers 5.19.0, flashinfer-python 0.7.4, sglang-kernel 0.4.11, patched sgl-deep-gemm 0.2.9, sgl-flash-mla 1.0.5, tilelang 0.1.12, apache-tvm-ffi 0.1.11, xgrammar 0.2.7, triton 3.8.0, sgl-deep-ep 0.1.2.post1 and nvidia-nccl-cu13 2.30.7. The recipe does not load DeepEP.
- Evaluator: sgl-eval 0.1.3; evaluator-reported NeMo Skills revision `645cf567ff08c0ae9cc3fc8e1edbb975b3067816`.

## Setup

1. Verify [SHA256SUMS](SHA256SUMS) and the local archive hashes in [EVIDENCE-STORAGE.md](EVIDENCE-STORAGE.md). The archives themselves are not committed.
2. Obtain the exact candidate, baseline and model revisions below. Recreate the CUDA 13 environment and source/dependency overlays recorded in [integration-report.md](integration-report.md).
3. Start each arm with the same recipe, changing only the source checkout:

```bash
python -m sglang.launch_server \
  --model-path /path/to/GLM-5-1028-Provider \
  --host 127.0.0.1 --port 31200 --dist-init-addr 127.0.0.1:31201 \
  --tp-size 4 --kv-cache-dtype fp8_e4m3 \
  --speculative-algorithm EAGLE --reasoning-parser glm45
```

The launch uses no `--context-length`. Resolved settings include TRTLLM DSA prefill/decode, `flashinfer_trtllm` MoE, EAGLE steps/top-k/draft tokens 3/1/4, 48 running requests and CUDA graphs enabled. `SGLANG_SIMULATE_ACC_LEN` is unset.

4. Run the full evaluation:

```bash
sgl-eval run gsm8k --base-url http://127.0.0.1:31200/v1 \
  --temperature 1.0 --top-p 0.95
```

5. Run `python3 verify.py` to recompute the gate from the raw samples and server logs. The captured output is [verify.json](verify.json).

## Commit

- Candidate: `7053ff0277bd27e1f3c76646b4a65bf76b0c7820`, clean and pushed to `radixark/sglang-zai` branch `sync/glm-5-lp-on-upstream-main`.
- Candidate parents: `glm-5-lp` `13fa8258d2404deedfac9c114c43c4e4069f39b5` and upstream `main` `2b248971db8c8c349586c3757663be9cba5e366d`.
- Merge base: `6de483b326c7dd4145fde06afcac9866bf491024`.
- `glm-5-lp` remains unchanged at `13fa8258d2404deedfac9c114c43c4e4069f39b5`; the candidate has not landed there.
- `sglang-zai` `main` was fast-forwarded to `2b248971db8c8c349586c3757663be9cba5e366d`.

## Scripts

- [integration-report.md](integration-report.md) — original conflict, dependency and Tier 1/Tier 2 report.
- [independent-report.md](independent-report.md) — coordinating review and independent tracking verification.
- [verify.py](verify.py) — recomputes sample accuracy, finish reasons, launch invariants, terminal status and accept length at 16 or more running requests.
- [scripts/](scripts/) — original audit, gate and analysis scripts.
- [tier1/](tier1/) — CPU test and pre-commit summaries.

## Workload

Full GSM8K test split: 1319 unique examples per arm, one run, 64 evaluator threads, temperature 1.0, top_p 0.95, no explicit output-token limit and no caller-specified seed. The evaluator commit is recorded in each metrics file; the dataset checkout revision was not independently captured. The baseline ran first and the candidate second, each on a separate rank with identical model metadata and dependency overlays.

## Results

| Metric | Baseline `13fa8258d2` | Candidate `7053ff0277` |
|---|---:|---:|
| Correct / 1319 | 1249 | 1252 |
| Accuracy | 94.69% | 94.92% |
| Normal stop / 1319 | 1318 | 1319 |
| Stop rate | 99.92% | 100.00% |
| Length truncations | 1 | 0 |
| Request errors / tracebacks | 0 / 0 | 0 / 0 |
| Accept length at >=16 running requests, mean | 2.658 | 2.653 |
| Accept length at >=16 running requests, median | 2.680 | 2.655 |
| Evaluation wall time | 1901 s | 915 s |

The gate requires stop rate and accuracy to meet or exceed the matched baseline. Both pass. Wall time is descriptive, not a controlled performance comparison.

## Limits and release status

This is a candidate-integration correctness result, not a release selection. Only TP4, FP8 KV, TRTLLM DSA, EAGLE MTP and `flashinfer_trtllm` MoE were exercised on GPU. PD, unified memory, HiSparse, DCP/CP, attention DP/EP, DeepEP 0.1.3, MegaMoE, fused-h64 and split-K decode, hybrid-SWA layout, the cu134 image build and AMD/NPU remain unexercised on the candidate. The image digest is unpinned and weight shards were not rehashed.

## Data and Figures

- [summary.md](summary.md) — concise result and gate.
- [terminal-snapshot.json](terminal-snapshot.json) — launch, evaluation and cleanup status for both arms.
- [candidate/](candidate/) and [baseline/](baseline/) — raw status, versions, analysis, server information, metrics and 1319 per-sample outputs per arm.
- [candidate-logs/](candidate-logs/) and [baseline-logs/](baseline-logs/) — raw server and evaluator logs.
- [verify.json](verify.json) — independent recomputation output; gate `PASS`.
- [EVIDENCE-STORAGE.md](EVIDENCE-STORAGE.md) — local archive paths, sizes and hashes.
- No figures were generated.
