# E04 Optional vision SwiGLU fix validation — data@2026-11-03-8451a1bf9d6156a8ff76f8d603abe9a89c1b1002-swiglu-fix

## Environment

- Machine: 8× NVIDIA B300 SXM6 AC, 275040 MiB per GPU.
- Model: `zai-org/GLM-5-1028-Provider` at revision `7e66c40540c64bbf85e2a3c6d7264fbc514b4b43`.
- Implementation: commit `8451a1bf9d6156a8ff76f8d603abe9a89c1b1002` on `radixark/sglang-zai` branch `fix/glm5-lp-implementation`, based on `a15aa7c3edefee67d557f15d640899b825c58ba6`.
- Software: torch `2.14.1+cu130`, transformers `5.19.0`, sglang-kernel `0.4.10`, and sgl-eval `0.1.3`. The serving configuration used DeepGEMM MoE and EAGLE 3/1/4 built-in NextN/MTP.
- Evaluator-reported NeMo Skills revision: `645cf567ff08c0ae9cc3fc8e1edbb975b3067816`.
- Container digest and complete transitive dependency lock: not recorded.

The fix makes omitted or null `vision_config.swiglu_limit` select ordinary SwiGLU. Explicit values preserve the clamp. The deployed checkpoint omitted the vision limit, so the real image requests exercised the unclamped path; the explicit-limit path is covered by unit tests.

## Setup

Apply the exact commit to the source used in [Correctness E03](../data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-b300-mtp-evaluation/repro.md):

```bash
git diff --binary \
  a15aa7c3edefee67d557f15d640899b825c58ba6..8451a1bf9d6156a8ff76f8d603abe9a89c1b1002 \
  > swiglu-fix.patch
tar -xzf /path/to/source-a15aa7c3.tar.gz
cd /path/to/extracted-source
git apply /path/to/swiglu-fix.patch
```

The deployed tree was checked with `git hash-object --no-filters` over every regular file. Its sorted 11586-entry manifest was byte-identical to the regular-file blob manifest from `git ls-tree -r 8451a1bf9d6156a8ff76f8d603abe9a89c1b1002`. Nine symlink/submodule entries were excluded from both manifests.

Run pre-commit on the four changed files and the pinned-environment regression tests:

```bash
pre-commit run --files \
  python/sglang/srt/configs/glm5_next.py \
  python/sglang/srt/models/glm5_next.py \
  test/registered/unit/configs/test_glm_loop_config.py \
  test/registered/unit/models/test_glm_loop.py

PYTHONPATH=/path/to/sglang/python /opt/sglang/bin/python -m pytest -q \
  test/registered/unit/configs/test_glm_loop_config.py \
  test/registered/unit/models/test_glm_loop.py
```

Launch the server with the same command and configuration as E03, but set `PYTHONPATH` and the working directory to this patched source tree. Wait for HTTP 200 from `/health`.

## Commit

- Code commit: `8451a1bf9d6156a8ff76f8d603abe9a89c1b1002`.
- Working tree: clean. The deployed regular-file blobs match this commit.
- Base drift: `glm-5-lp` subsequently advanced to `6fed795944fc9c2df9f02c4937ffac9e28a4c2d7`; this round does not claim validation on that later commit.

## Scripts

- Version: none. Round-specific request generation is retained as [`requests.py`](requests.py).
- Temporary changes: only the metrics and request-script model-path redactions recorded in `evidence-hashes.json`.

## Workload

1. Configuration and model regression tests, including omitted, null, and explicit SwiGLU limits. The three new cases were also run against the pre-fix implementation with only the new test files added.
2. Two text and two synthetic-image chat requests at temperature 1.0, top_p 0.95, and max_tokens 4096. The image cases cover shapes/colors and exact text recognition. Each case requires its expected content and `finish_reason=stop`.
3. Full 1319-example GSM8K with one repeat, 64 evaluation threads, temperature 1.0, and top_p 0.95:

   ```bash
   sgl-eval run gsm8k \
     --base-url http://127.0.0.1:30000/v1 \
     --num-examples 1319 --temperature 1.0 --top-p 0.95 \
     --out-dir /path/to/eval-output
   ```

The full-run acceptance criteria were fixed before execution: accuracy at least 92.86%, stop rate at least 99.00%, and zero request errors. Recompute the aggregates with:

```bash
python ../../scripts/v1/aggregate_gsm8k.py output-rs0.jsonl.gz
```

## Results

| Check | Result | Evidence |
|---|---|---|
| Pre-commit | Passed on all four changed files | Command above |
| Config/model tests at `8451a1bf` | 42 passed | [`unit.log.gz`](unit.log.gz) |
| Three new cases on pre-fix code | 2 failed, 1 passed, confirming the regression cases distinguish the fix | [`unit-prefix.log.gz`](unit-prefix.log.gz) |
| Text arithmetic | `391`, `finish_reason=stop` | [`requests.json`](requests.json) |
| Text factual request | `Paris`, `finish_reason=stop` | [`requests.json`](requests.json) |
| Shapes image, 190 image tokens | Correct red square and blue circle, `finish_reason=stop` | [`requests.json`](requests.json) |
| OCR image, 184 image tokens | `PURPLE ELEPHANT 734`, `finish_reason=stop` | [`requests.json`](requests.json) |
| Full GSM8K accuracy | 95.22% (1256/1319) | [`metrics.json`](metrics.json), [`output-rs0.jsonl.gz`](output-rs0.jsonl.gz) |
| Full GSM8K stop rate | 99.32% (1310/1319) | [`output-rs0.jsonl.gz`](output-rs0.jsonl.gz) |
| Full GSM8K truncation / request error rates | 0.68% / 0.00% | [`metrics.json`](metrics.json) |

Conclusions:

1. The optional vision SwiGLU configuration loads and executes correctly for omitted and explicit limits in the covered tests.
2. Real text and image requests completed with the expected content and normal stop behavior.
3. The single full GSM8K run met all predeclared accuracy, stop-rate, and request-error gates. Independent aggregation reproduces 1256 correct, 1310 stop, and 9 length outcomes.
4. This round does not establish performance, image-benchmark quality, or correctness after rebasing onto later `glm-5-lp` commits.

## Data and Figures

- [`unit.log.gz`](unit.log.gz) and [`unit-prefix.log.gz`](unit-prefix.log.gz) — fixed and pre-fix regression-test output.
- [`requests.py`](requests.py), [`requests.json`](requests.json), and [`requests.log`](requests.log) — real request generation and summarized results.
- [`metrics.json`](metrics.json) and [`output-rs0.jsonl.gz`](output-rs0.jsonl.gz) — aggregate and all 1319 GSM8K predictions.
- [`deployed-manifest.txt.gz`](deployed-manifest.txt.gz) — deployed regular-file blob manifest.
- [`evidence-hashes.json`](evidence-hashes.json) — SHA-256 of uncompressed evidence as captured and after redaction.
- [GSM8K aggregation script](../../scripts/v1/aggregate_gsm8k.py) and [version notes](../../scripts/v1/CHANGES.md).

The top-level model path in `metrics.json` and the checkpoint path in `requests.py` were replaced with `/path/to/GLM-5-1028-Provider`. No prediction, answer, score, or finish reason was changed.
