# E36 MI355X TP8 bring-up and full GSM8K — data@2026-11-16-8d5d043629dfede1abe081977bdf41d0b299ea8b-mi355x-bringup

First end-to-end bring-up of `zai-org/GLM-5-1028-Provider` on AMD Instinct MI355X: unit and attention-kernel tests, text, image, and long-context chat smokes, and full GSM8K against a TP8 server without MTP.

This round establishes AMD correctness. It is not a performance or release gate, and MTP is not covered (see [Open issues](#open-issues)).

## Environment

- Machine: single node with 8 AMD Instinct MI355X GPUs (gfx950, 288 GB HBM each), XGMI.
- Container: SGLang ROCm 10.0 development image; the image digest was not recorded.
- Hardware: AMD Instinct MI355X x 8.
- Model: `zai-org/GLM-5-1028-Provider` at revision `66c3fe71d4c4ab43efac5bb0d2be6dea3a75d089`. It differs from `7e66c405`, used by the NVIDIA rounds, only by removing `vision_config.swiglu_limit` from `config.json`; the weights are identical.
- Software: ROCm 10.0.0, torch `2.11.0+rocm10.0.0`, triton `3.8.0+rocm10.0.0`, amd-aiter `0.1.26.dev144+g285579b62`, sglang-kernel `0.4.10`, transformers `5.19.0`; `blake3`, `zstandard` and `watchfiles` were added with pip. The transformers GLM Loop patch was not applied: SGLang parses the checkpoint with its own config classes.
- Evaluator: sgl-eval `0.1.3`; evaluator-reported NeMo Skills revision `645cf567ff08c0ae9cc3fc8e1edbb975b3067816`.

## Setup

1. Check out `radixark/sglang-zai` branch `amd_support` at the code commit below and import SGLang from it.

   ```bash
   git clone https://github.com/radixark/sglang-zai.git
   cd sglang-zai
   git checkout 8d5d043629dfede1abe081977bdf41d0b299ea8b
   export PYTHONPATH=$PWD/python
   pip install blake3 zstandard watchfiles
   ```

2. Download the checkpoint at the pinned revision with a token that can read it (`HF_TOKEN`).

   ```bash
   hf download zai-org/GLM-5-1028-Provider \
     --revision 66c3fe71d4c4ab43efac5bb0d2be6dea3a75d089 \
     --local-dir /path/to/GLM-5-1028-Provider
   ```

3. Launch the server: TP8, the ROCm defaults for this model (the `triton` DSA backend for prefill and decode, which reads a later cycle's two banks with the Triton split-K, and a bf16 KV cache), AITER block-FP8 GEMMs and MoE, decode CUDA graph, no prefill graph, no MTP.

   ```bash
   export HF_HUB_OFFLINE=1 SGLANG_USE_AITER=1
   python -m sglang.launch_server \
     --model-path /path/to/GLM-5-1028-Provider \
     --served-model-name glm-loop \
     --host 0.0.0.0 --port 30000 \
     --tp-size 8 --kv-cache-dtype bfloat16 \
     --mem-fraction-static 0.80 \
     --context-length 32768 --max-running-requests 64 \
     --chunked-prefill-size 16384 --watchdog-timeout 1800 \
     --disable-prefill-cuda-graph \
     --reasoning-parser glm45 --tool-call-parser glm47
   ```

   The startup log reports `Set DSA backends for bfloat16 KV Cache: prefill=triton, decode=triton`, 88.79 GB of weights and 1,168,000 KV tokens per GPU, and decode CUDA graphs for batch sizes 1 to 64 ([`logs/server-tp8.log.gz`](logs/server-tp8.log.gz)).

4. Wait until `GET /health` returns HTTP 200, then send the requests in [Workload](#workload).

## Commit

- Code commit for the server, smokes and GSM8K: `8d5d043629dfede1abe081977bdf41d0b299ea8b` (`radixark/sglang-zai`, branch `amd_support`, on `glm-5-lp` at `59860082`).
- The smokes ran on the same tree before it was committed; GSM8K ran on the committed tree.
- Unit and attention-kernel test logs come from `bcad3f2a4a020ea83448b55a9e4abad2a5ad870f`, which adds formatting and the ROCm test routes on top of `8d5d0436` and changes no serving code.
- Working tree: clean at each commit.

### Changes on `amd_support` relative to `glm-5-lp`

1. A later cycle's dual-bank read runs on ROCm behind the `triton` and `tilelang` DSA backends through `glm_loop_sparse_decode`'s Triton split-K, which merges both banks in one fp32 softmax. CUDA graphs use calls of at most 64 rows on the workspace reserved before capture; eager prefill uses 1024-row chunks on its own workspace. ROCm defaults to `triton` with a bf16 KV cache, and the launch hook accepts `triton` or `tilelang` there.
2. On gfx950 the block-FP8 quantization postprocess preshuffles `kv_b_proj.weight` in place for AITER. GLM LoopLM runs `post_load_weights` again after that postprocess, which derived `w_kc` / `w_vc` from the permuted weight in all 78 physical layers and produced unreadable output. The derivation now unshuffles first.
3. `MLA_ROCM` returns the cycle-0 Top-K (`loop_return_topk`), and a forced-MLA loop slot takes `MLA_ROCM` on HIP for both prefill and decode.
4. GLM's interleaved MRoPE (`mrope_interleaved_glm`) keeps SGLang's `MRotaryEmbedding` on HIP; AITER's MRoPE has neither that lane layout nor `cos_sin_rows`. The gfx950 fused RoPE + KV write is skipped for MRoPE, since it applies a plain RoPE from one position per token.
5. The AOT gate router numerics, a CUDA `moe_fused_gate` path, apply on CUDA only; HIP routes the same single-group biased sigmoid Top-K.

## Scripts

- Version: none. The smoke client mirrors [Correctness E01](../data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md); its prompts are listed below.
- GSM8K aggregates were recomputed with [scripts/v1/aggregate_gsm8k.py](../../scripts/v1/aggregate_gsm8k.py).
- Temporary changes: none.

## Workload

### Tests

```bash
python -m pytest -q test/registered/unit/configs/test_glm_loop_config.py \
  test/registered/unit/models/test_glm_loop.py
HIP_VISIBLE_DEVICES=0 python -m pytest -q -rA \
  test/registered/kernels/ops/attention/test_glm_loop_attention.py
```

### Smokes

Three chat requests, one at a time, `temperature=0`, `top_p=1`; each passes when the answer matches and `finish_reason` is `stop`.

- Text: `What is 2+3? Answer briefly.` with `max_tokens=1024`; expected `5`.
- Image: a 128x128 white PNG with a red square (pixels 16 to 111) and `What color is the square? Answer with one word.`, `max_tokens=512`; expected `red`.
- Long context: 220 filler records with `The secret code is BLUE-4721.` inserted in the middle and `What is the secret code? Reply with the code only.`, 3130 prompt tokens, past the 2048-token Top-K, `max_tokens=512`; expected `BLUE-4721`.

### Full GSM8K

The evaluator's 1319-example GSM8K test set, one repeat, 64 threads, temperature 1.0, top_p 0.95, no explicit output-token limit, as in [Correctness E03](../data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-b300-mtp-evaluation/repro.md).

```bash
sgl-eval run gsm8k --base-url http://127.0.0.1:30000/v1 \
  --num-examples 1319 --temperature 1.0 --top-p 0.95 --num-threads 64 \
  --out-dir /path/to/eval-output
python ../../scripts/v1/aggregate_gsm8k.py gsm8k/output-rs0.jsonl.gz
```

Expected recomputation: 1319 examples, 1251 correct, 1315 stop, 4 length, score 0.9484457922668689, and zero request errors.

## Results

| Check | Result | Evidence |
|---|---|---|
| GLM LoopLM config and model unit tests | 59 passed, 21 subtests | [`logs/unit-tests.log`](logs/unit-tests.log) |
| Attention kernel tests on MI355X | 8 passed, 13 skipped (FlashMLA and SM100-only routes), 95 subtests | [`logs/attention-tests.log`](logs/attention-tests.log) |
| Text smoke | `5`, `stop`, 3 completion tokens | [`text-smoke.json`](text-smoke.json) |
| Image smoke (25 image tokens) | `Red`, `stop`, 3 completion tokens | [`image-smoke.json`](image-smoke.json) |
| Long-context smoke (3130 prompt tokens) | `BLUE-4721`, `stop`, 7 completion tokens | [`long-context-smoke.json`](long-context-smoke.json) |
| Full GSM8K accuracy | 94.84% (1251/1319) | [`gsm8k/metrics.json`](gsm8k/metrics.json), [`gsm8k/output-rs0.jsonl.gz`](gsm8k/output-rs0.jsonl.gz) |
| GSM8K stop / truncation / request error rates | 99.70% / 0.30% / 0.00% | Same GSM8K evidence |

The kernel tests that cover the ROCm route are `test_triton_two_banks_equal_one_softmax` (decode, extend and target verify at 8, 16, 32 and 64 local heads, including multi-chunk eager calls), `test_triton_decode_graph_replay_reads_new_queries_and_positions`, `test_split_decode_equals_one_softmax` (bf16 and fp8 caches) and `test_window_pool_reads_the_same_keys`, whose triton route reads the hybrid SWA window pool bitwise like the full-length layout.

For reference, full GSM8K with the same sampling scored 93.86% on B300 ([E03](../data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-b300-mtp-evaluation/repro.md)) and 94.31% on H200 ([E05](../data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6-h200-mtp-evaluation/repro.md)), both with MTP.

Conclusions:

1. GLM LoopLM serves correctly on 8 MI355X GPUs at TP8 with the triton DSA backend, a bf16 KV cache and decode CUDA graphs: text, image and long-context requests answer correctly and stop normally.
2. Full GSM8K accuracy and stop behavior are in line with the NVIDIA evidence; the AMD run used no MTP.
3. The preshuffled `kv_b_proj` re-derivation was the one numerical defect; before it was fixed, the same server returned unreadable text.

## Open issues

- MTP (EAGLE 3/1/4 with `--disable-custom-all-reduce`) captured target-verify graphs for batch sizes 1 to 64, then hung capturing the draft decode graph at batch size 52 with every rank waiting in a device synchronize and the GPUs idle. The GPUs then stayed degraded until reset: RCCL operations took about 150 ms each and server initialization about 7 minutes instead of 2 seconds. MTP on MI355X remains unvalidated.
- GPQA has not been run on MI355X.
- Performance has not been measured beyond the serving log: about 55 tokens per second for one request at 32K context and about 1300 tokens per second at 64 concurrent requests, without MTP.

## Data and Figures

- [`logs/server-tp8.log.gz`](logs/server-tp8.log.gz) — server log of the GSM8K run, with AITER untuned-shape notices removed.
- [`logs/unit-tests.log`](logs/unit-tests.log), [`logs/attention-tests.log`](logs/attention-tests.log) — test output.
- [`text-smoke.json`](text-smoke.json), [`image-smoke.json`](image-smoke.json), [`long-context-smoke.json`](long-context-smoke.json) — raw chat responses.
- [`gsm8k/metrics.json`](gsm8k/metrics.json), [`gsm8k/output-rs0.jsonl.gz`](gsm8k/output-rs0.jsonl.gz) — aggregate and all 1319 predictions.
