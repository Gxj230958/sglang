# E07 Top-K anchors by reference: merge gate — data@2026-11-13-802d8157b74564997e350ffa981b5e567e391920-topk-by-reference-gate

## Environment

- Machine: one node with 8× NVIDIA B300.
- Container: the node's stock SGLang development image; the image digest was not recorded.
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`, served from a node-local copy; the checkpoint's own NextN head is the MTP draft. The copy was not re-hashed for this round.
- Software: image torch 2.14.1+cu130, transformers 5.19.0, sglang-kernel 0.4.10; an overlay on `PYTHONPATH` adds flashinfer-python / cubin / jit-cache 0.7.3, sgl-deep-gemm 0.2.7 and sgl-flash-mla 1.0.4; `SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND=python`.

## Setup

Deploy `git archive 802d8157b7` (candidate) and `git archive a736925063` (base) and start one server at a time with [`launch.sh`](launch.sh) or [`launch-base.sh`](launch-base.sh): `--tp-size 8 --mem-fraction-static 0.75 --context-length 65536 --chunked-prefill-size 32768 --max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph`, `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path <model>`, `--enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47`. [`gate.sh`](gate.sh) runs the smoke suite and the first candidate evaluation; [`chain.sh`](chain.sh) runs the second candidate evaluation and both base evaluations.

## Commit

- Code commit: `802d8157b74564997e350ffa981b5e567e391920`, radixark/sglang-zai pull request 43 reduced to the Top-K change and rebased onto `a736925063`.
- Baseline: `a736925063e7d0da812b8632f3c0683953fb96e5`.
- Working tree: clean archives.
- The pull request was squash-merged as `8f5dff0f45` after this gate.
- Status: non-release. The image digest is not recorded and dependencies come from `PYTHONPATH` overlays, so the environment is not locked.

## Scripts

- Version: round-specific [`gate.sh`](gate.sh), [`chain.sh`](chain.sh) and the two launch scripts.
- Temporary changes: none.

## Workload

- GSM8K: full test split (1319 questions) through `sgl-eval` 0.1.3, `sgl-eval run gsm8k --base-url <server>/v1 --temperature 1.0 --top-p 0.95`, 64 client threads, server-default thinking, no `max_tokens`, one run per configuration. Two runs per arm on one server start each.
- Smoke suite on the candidate ([`suite.json`](suite.json)): text, thinking, 4K / 12K / 24K long-context needle and image requests.

## Results

| Arm | Run | Accuracy | Stop rate | Truncated | Errors |
|---|---|---|---|---|---|
| Base `a736925063` | 1 | 95.38% (1258/1319) | 100.00% | 0 | 0% |
| Base `a736925063` | 2 | 94.09% (1241/1319) | 99.77% | 3 | 0% |
| Candidate `802d8157b7` | 1 | 94.24% (1243/1319) | 99.85% | 2 | 0% |
| Candidate `802d8157b7` | 2 | 94.77% (1250/1319) | 99.92% | 1 | 0% |

Mean accept length over each server log: base 2.68, candidate 2.64. All six smoke requests on the candidate ended with `stop`. Neither server logged a traceback.

Conclusions:

1. Both arms truncate 3 of 2638 requests; the candidate's stop rate matches the base within sampling variation, and accuracy overlaps (base 95.38% and 94.09%, candidate 94.24% and 94.77%).
2. The change is a code simplification with no measured speed or memory effect; the equivalence and performance evidence is in [Kernel Optimization E03](../../../p0-kernel-opt/data/data@2026-11-12-6ed895fa2678d8c4d52576e7ae5e3707ee4180e7-topk-by-reference-b300/repro.md).

## Data and Figures

- [`eval/`](eval/), [`eval-cand2/`](eval-cand2/) — candidate sgl-eval outputs; [`eval-base1/`](eval-base1/), [`eval-base2/`](eval-base2/) — base outputs.
- `serve.log.gz`, `serve-base.log.gz` — candidate and base server logs; `gsm8k.log`, `eval-*.log` — evaluation consoles; `suite.json`, `suite.log` — smoke results; `gate.status`, `chain.status`, `*.out` — driver status and console.
- [`summary.json`](summary.json) — every number in the Results section, recomputed from the committed files by [`summarize_round.py`](../../scripts/v2/summarize_round.py).
- [`evidence-hashes.json`](evidence-hashes.json) — original path and SHA-256 of every captured file, taken before compression; generated files are hashed as committed.
