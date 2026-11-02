# E02 GSM8K baseline and MTP with decode CUDA graph — data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-mtp-cuda-graph

## Environment

- Machine: 8× NVIDIA H200, 143.8 GiB per GPU.
- Model: `zai-org/GLM-5-1028-Provider` at revision `7e66c40540c64bbf85e2a3c6d7264fbc514b4b43`.
- Implementation: `radixark/sglang-zai` branch `glm-5-lp` at commit `a15aa7c3edefee67d557f15d640899b825c58ba6`; exact source with no local changes.
- Software: torch `2.14.1+cu130`, flashinfer `0.7.1`, transformers `5.19.0`, sgl-flash-mla `1.0.0`, sglang-kernel `0.4.10`.
- Evaluator: sgl-eval `0.1.2`; evaluator/dataset revision `645cf567ff08c0ae9cc3fc8e1edbb975b3067816`.
- Container digest and full transitive dependency lock: not recorded.
- Prerequisites: use the checkout and dependency setup in [Correctness E01](../data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md), then install `sgl-eval==0.1.2`.

## Subrun A: baseline accuracy

### Launch

Use TP8, Triton MoE, FlashMLA Sparse, and a BF16 KV cache. CUDA graph and MTP are disabled.

```bash
export HF_HUB_OFFLINE=1
python -m sglang.launch_server \
  --model-path /path/to/GLM-5-1028-Provider \
  --host 0.0.0.0 --port 30000 \
  --tp-size 8 \
  --moe-runner-backend triton \
  --mem-fraction-static 0.75 --max-total-tokens 65536 \
  --context-length 8192 --max-running-requests 32 \
  --disable-cuda-graph \
  --reasoning-parser glm45 --tool-call-parser glm47
```

### Evaluation

The workload is the vendored GSM8K test set at the evaluator revision above, using the benchmark's default selection of 200 examples. Sampling is temperature 1.0 and top_p 0.95, with 64 evaluation threads and one repeat. No explicit output-token limit or request timeout was set by the caller.

```bash
sgl-eval run gsm8k \
  --base-url http://127.0.0.1:30000/v1 \
  --num-examples 200 --temperature 1.0 --top-p 0.95
```

The evaluator writes `metrics.json` and per-example `output-rs0.jsonl`. Recompute the published aggregates with:

```bash
python ../../scripts/v1/aggregate_gsm8k.py output-rs0.jsonl.gz
```

Expected recomputation: 200 examples, 191 correct, score 0.955, 200 stop, stop rate 1.0, truncation rate 0.0, and error rate 0.0.

## Subrun B: MTP with decode CUDA graph

### Launch

Use the same base configuration with EAGLE 3/1/4, decode CUDA graph enabled, and prefill CUDA graph disabled.

```bash
export HF_HUB_OFFLINE=1
python -m sglang.launch_server \
  --model-path /path/to/GLM-5-1028-Provider \
  --host 0.0.0.0 --port 30000 \
  --tp-size 8 \
  --moe-runner-backend triton \
  --mem-fraction-static 0.75 --max-total-tokens 65536 \
  --context-length 8192 --max-running-requests 32 \
  --cuda-graph-max-bs-decode 4 --disable-prefill-cuda-graph \
  --speculative-algorithm EAGLE \
  --speculative-num-steps 3 --speculative-eagle-topk 1 \
  --speculative-num-draft-tokens 4 \
  --speculative-draft-model-path /path/to/GLM-5-1028-Provider \
  --reasoning-parser glm45 --tool-call-parser glm47
```

The first MTP launch failed with CUDA OOM because baseline worker processes remained active. Those processes were stopped before the successful launch; no model or source settings were changed to bypass the failure.

### Request

```bash
cat > mtp-request.json <<'JSON'
{
  "model": "/path/to/GLM-5-1028-Provider",
  "messages": [{"role": "user", "content": "Explain quantum computing in three sentences."}],
  "max_tokens": 256,
  "temperature": 0,
  "top_p": 1
}
JSON
curl -sS --max-time 120 http://127.0.0.1:30000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  --data-binary @mtp-request.json \
  -o mtp-smoke.json
```

The acceptance criterion is a coherent response with `finish_reason=stop`, a nonzero NextN/MTP acceptance length, and decode execution with `cuda graph: True`. The single logged interval is not a workload-wide acceptance average or a speedup measurement.

## Results

| Subrun | Metric | Result | Evidence |
|---|---|---|---|
| A: baseline, no MTP or CUDA graph | Accuracy | 95.50% (191/200) | [`metrics.json`](metrics.json), [`output-rs0.jsonl.gz`](output-rs0.jsonl.gz) |
| A | Stop rate | 100.00% | [`output-rs0.jsonl.gz`](output-rs0.jsonl.gz) |
| A | Truncation and request error rates | 0.00% / 0.00% | [`metrics.json`](metrics.json) |
| B: MTP with decode CUDA graph | Response | Coherent three-sentence explanation with `finish_reason=stop` | [`mtp-smoke.json`](mtp-smoke.json) |
| B | NextN/MTP acceptance length | 2.27 | [`mtp-evidence.log`](mtp-evidence.log) |
| B | Ordinary decode CUDA graph | `cuda graph: True` | [`mtp-evidence.log`](mtp-evidence.log) |

Subrun A establishes the baseline accuracy only; it does not establish accuracy for the MTP configuration. Subrun B establishes one ordinary decode-graph/MTP smoke, not breakable-graph boundary validation, performance, or a release gate.

## Data and Figures

- [`metrics.json`](metrics.json) — aggregate evaluator metrics.
- [`output-rs0.jsonl.gz`](output-rs0.jsonl.gz) — all 200 per-example responses, symbolic correctness, finish reasons, and stable example IDs, sufficient to recompute every aggregate.
- [`mtp-smoke.json`](mtp-smoke.json) — MTP chat response.
- [`mtp-evidence.log`](mtp-evidence.log) — readiness, acceptance length/rate, and `cuda graph: True` log lines.
- [`evidence-hashes.json`](evidence-hashes.json) — captured and redacted SHA-256 values.
- [Aggregation script](../../scripts/v1/aggregate_gsm8k.py) and [version notes](../../scripts/v1/CHANGES.md).
- [E01 test and startup logs](../data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md#test-and-startup-logs).

The top-level `model` fields in `metrics.json` and `mtp-smoke.json` were replaced with `/path/to/GLM-5-1028-Provider` after capture to remove the serve-time local path. No prediction content, scoring outcome, or finish reason was changed. The original and redacted hashes are recorded in `evidence-hashes.json`.
