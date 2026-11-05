# E03 B300 MTP full GSM8K and GPQA-4096 — data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-b300-mtp-evaluation

## Environment

- Machine: 8× NVIDIA B300 SXM6 AC, 275040 MiB per GPU.
- Model: `zai-org/GLM-5-1028-Provider` at revision `7e66c40540c64bbf85e2a3c6d7264fbc514b4b43`.
- Implementation: `radixark/sglang-zai` branch `glm-5-lp` at commit `a15aa7c3edefee67d557f15d640899b825c58ba6`; exact source with no local changes.
- Software: torch `2.14.1+cu130`, transformers `5.19.0`, sglang-kernel `0.4.10`; flashinfer was not installed. The MoE runner was DeepGEMM.
- Evaluator: sgl-eval `0.1.3`; evaluator-reported NeMo Skills revision `645cf567ff08c0ae9cc3fc8e1edbb975b3067816`.
- Container digest and complete transitive dependency lock: not recorded.

Both subruns used the same serving configuration: TP8, DeepGEMM MoE, EAGLE 3/1/4 built-in NextN/MTP, decode CUDA graph, and prefill CUDA graph disabled. These are MTP results, not non-speculative baseline results.

## Setup

Use the checkout and model acquisition steps in [Correctness E01](../data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md), then install `sgl-eval==0.1.3` in the B300 serving environment.

```bash
export HF_HUB_OFFLINE=1
export SGLANG_RUST_BUILD_MODE=auto
python -m sglang.launch_server \
  --model-path /path/to/GLM-5-1028-Provider \
  --host 0.0.0.0 --port 30000 \
  --tp-size 8 \
  --moe-runner-backend deep_gemm \
  --mem-fraction-static 0.75 --max-total-tokens 131072 \
  --context-length 8192 --max-running-requests 64 \
  --cuda-graph-max-bs-decode 64 --disable-prefill-cuda-graph \
  --speculative-algorithm EAGLE \
  --speculative-num-steps 3 --speculative-eagle-topk 1 \
  --speculative-num-draft-tokens 4 \
  --speculative-draft-model-path /path/to/GLM-5-1028-Provider \
  --reasoning-parser glm45 --tool-call-parser glm47
```

Wait until `GET /health` returns HTTP 200 before starting either subrun.

## Commit

- Code commit: `a15aa7c3edefee67d557f15d640899b825c58ba6`.
- Working tree: clean; the source was deployed from the archive of this exact commit with no local changes.

## Scripts

- Version: none. Evaluation commands are defined inline below.
- Temporary changes: none.

## Workload

### Subrun A: full GSM8K

The workload is the evaluator's full 1319-example GSM8K test set, with one repeat, 64 evaluation threads, temperature 1.0, and top_p 0.95. No explicit output-token limit was set by the caller.

```bash
sgl-eval run gsm8k \
  --base-url http://127.0.0.1:30000/v1 \
  --num-examples 1319 --temperature 1.0 --top-p 0.95 \
  --out-dir /path/to/eval-output
```

Recompute accuracy and finish-reason aggregates from this round's directory:

```bash
python ../../scripts/v1/aggregate_gsm8k.py gsm8k/output-rs0.jsonl.gz
```

Expected recomputation: 1319 examples, 1238 correct, 1309 stop, 10 length, score 0.9385898407884761, and zero request errors.

### Subrun B: GPQA-Diamond with 4096 output tokens

The workload is GPQA-Diamond: 198 questions with 8 repeats, 64 evaluation threads, temperature 1.0, top_p 0.95, chat template thinking enabled, and `max_tokens=4096`.

```bash
sgl-eval run gpqa \
  --base-url http://127.0.0.1:30000/v1 \
  --temperature 1.0 --top-p 0.95 --max-tokens 4096 \
  --out-dir /path/to/eval-output
```

The evaluator reports pass@1 as the mean over all repeats, pass@8 over the eight samples per question, and majority@8 using its pinned scoring implementation. The 4096-token budget is part of this result; the high truncation rate means this is not an unconstrained reasoning-quality measurement.

## Results

| Subrun | Metric | Result | Evidence |
|---|---|---:|---|
| A: full GSM8K with MTP | Accuracy | 93.86% (1238/1319) | [`gsm8k/metrics.json`](gsm8k/metrics.json), [`gsm8k/output-rs0.jsonl.gz`](gsm8k/output-rs0.jsonl.gz) |
| A | Stop rate | 99.24% (1309/1319) | [`gsm8k/output-rs0.jsonl.gz`](gsm8k/output-rs0.jsonl.gz) |
| A | Truncation / request error rates | 0.76% / 0.00% | [`gsm8k/metrics.json`](gsm8k/metrics.json) |
| B: GPQA-4096 with MTP | pass@1 | 45.52% | [`gpqa-4096/metrics.json`](gpqa-4096/metrics.json), `output-rs0.jsonl.gz` through `output-rs7.jsonl.gz` |
| B | pass@8 | 69.19% | Same GPQA evidence |
| B | majority@8 | 68.69% | [`gpqa-4096/metrics.json`](gpqa-4096/metrics.json) |
| B | Stop rate | 48.67% | Same GPQA evidence |
| B | Truncation / no-answer / request error rates | 51.33% / 51.70% / 0.00% | Same GPQA evidence |

Conclusions:

1. The B300 MTP configuration completed both evaluation workloads without request errors.
2. Full GSM8K accuracy and normal-stop behavior are recorded for this exact configuration.
3. GPQA pass@1, pass@8, stop, truncation, and no-answer rates recompute from the retained predictions. More than half of GPQA generations reached the 4096-token limit, so these values must remain tied to that budget and must not be presented as a release quality gate.

## Data and Figures

- [`gsm8k/metrics.json`](gsm8k/metrics.json) and [`gsm8k/output-rs0.jsonl.gz`](gsm8k/output-rs0.jsonl.gz) — aggregate and all 1319 GSM8K predictions.
- [`gpqa-4096/metrics.json`](gpqa-4096/metrics.json) and `gpqa-4096/output-rs0.jsonl.gz` through `gpqa-4096/output-rs7.jsonl.gz` — aggregate and all 1584 GPQA predictions.
- [`evidence-hashes.json`](evidence-hashes.json) — SHA-256 of uncompressed evidence as captured and after redaction.
- [GSM8K aggregation script](../../scripts/v1/aggregate_gsm8k.py) and [version notes](../../scripts/v1/CHANGES.md).

The top-level `model` fields in the two metrics files were replaced with `/path/to/GLM-5-1028-Provider` after capture to remove the serve-time local path. Prediction files were not redacted. No prediction content, scoring outcome, or finish reason was changed.
