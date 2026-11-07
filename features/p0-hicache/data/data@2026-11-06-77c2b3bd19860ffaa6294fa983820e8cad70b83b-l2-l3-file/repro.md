# E01 HiCache L2 host and L3 file validation — data@2026-11-06-77c2b3bd19860ffaa6294fa983820e8cad70b83b-l2-l3-file

## Environment

- Machine: 8× NVIDIA B300, TP8 / CP1 / attention DP1; FP8 weights and BF16 KV cache.
- Model and bundled tokenizer: `zai-org/GLM-5-1028-Provider` at revision `7e66c40540c64bbf85e2a3c6d7264fbc514b4b43`.
- Implementation: `glm-5-lp` at `77c2b3bd19860ffaa6294fa983820e8cad70b83b`.
- Software: torch `2.14.1+cu130`, transformers `5.19.0`, sglang-kernel `0.4.10`, and `sgl-flash-mla==1.0.3`; FlashMLA sparse prefill, TRT-LLM decode, DeepGEMM MoE, kernel IO, and page-first host layout.
- The installed transformers package lacked `glm_loop`. The compatibility configuration had SHA-256 `700b5d32efd4cebf618924c83edf586250c5d32d52b30db53f2bded9d22f9f7a`. It has no immutable source-commit pin, so this is a non-release experiment.

## Setup

Deploy the complete `77c2b3bd` source and the shared compatibility configuration. The probe starts and stops its own servers and uses these behavior-changing settings:

- `--enable-hierarchical-cache --hicache-ratio 2 --hicache-write-policy write_through`
- `--enable-cache-report --hicache-storage-prefetch-policy wait_complete`
- `--max-total-tokens 65536 --context-length 32768 --page-size 64`
- L3 rounds additionally use `--hicache-storage-backend file` and `SGLANG_HICACHE_FILE_BACKEND_STORAGE_DIR` under the experiment directory.
- Both rounds use TP8, BF16 KV, prefill chunk 16384, `--disable-prefill-cuda-graph`, and no speculative decoding.

Run the full positive and negative sequence:

```bash
export HICACHE_EXPERIMENT_DIR=/path/to/experiment
export GLM_SOURCE_DIR=/path/to/source-77c2b3bd
export FLASHMLA_SITE=/path/to/flashmla-1.0.3
export PYTHON=/path/to/python
export GLM_MODEL=/path/to/GLM-5-1028-Provider
python probe.py
```

`HICACHE_NEGATIVE_ONLY=1 python probe.py` resumes only the clear-and-recompute phase after a completed positive run. The final probe waits up to 300 seconds for asynchronous physical file deletion before asserting an empty store.

## Commit

- Code commit: `77c2b3bd19860ffaa6294fa983820e8cad70b83b`.
- Working tree: the compatibility configuration listed above; all other runtime source comes from the complete commit tarball.
- Status: non-release because the compatibility file and container are not locked. No product-source change was made for this experiment.

## Scripts

- Version: round-specific [`probe.py`](probe.py).
- Temporary changes: machine-specific paths are environment variables. The final clear operation waits for asynchronous file deletion; this affects probe timing, not cache behavior.

## Workload

- N1 and N2 use distinct questions over the same 4482-token ledger; N2 is asked only during restore phases. S1 uses an unrelated 1470-token ledger.
- Semantic requests use temperature 0 and at most 512 new tokens. Every case requires its exact numeric answer and `finish_reason=stop`.
- L2-only runs cold and device-warm requests, then 24 unrelated 4096-token filler requests (98304 tokens) to exceed the device pool while remaining within host capacity. N1 and S1 must restore from host; N2 may hit device after N1 restores their shared prefix.
- L3 population writes N1 and S1 with write-through. A flush must preserve both KV and indexer files.
- A complete process restart with the same store must restore N1, S1, and N2 from storage after flushing local tiers.
- The negative control flushes local tiers and clears L3 before each request, then requires `cached_tokens=0` and correct recomputation.
- The 4482-token prompts exercise later-cycle dual-bank attention.

## Results

| Check | Result | Evidence |
|---|---|---|
| L2 N1 host restore | 4480 tokens; device=0, storage=0; correct answer 64 | [`results.json`](results.json) |
| L2 S1 host restore | 1408 tokens; device=0, storage=0; correct answer 56 | [`results.json`](results.json) |
| L2 shared-prefix N2 | 4416 device tokens after N1 restored the prefix; correct answer 18 | [`results.json`](results.json) |
| L3 files after flush | 93 KV + 93 indexer files, 743309568 bytes | [`validation-summary.json`](validation-summary.json) |
| L3 N1 after full restart | 4480 storage tokens; device=0, host=0; correct answer 64 | [`results.json`](results.json) |
| L3 S1 after full restart | 1408 storage tokens; device=0, host=0; correct answer 56 | [`results.json`](results.json) |
| L3 N2 after full restart | 4416 storage tokens; device=0, host=0; correct answer 18 | [`results.json`](results.json) |
| L3 clear-and-recompute | 3/3 requests with cached_tokens=0 and correct answers | [`results.json`](results.json) |
| Semantic correctness | 18/18 correct and 18/18 `finish_reason=stop` | [`validation-summary.json`](validation-summary.json) |
| Server health | No Traceback in L2, L3-populate, L3-restart, or L3-negative server logs | Server-log checks recorded in the round conclusion |

Conclusions:

1. Host L2 restores both short and later-cycle long prefixes after device eviction.
2. File L3 preserves KV and DSA indexer state across `/flush_cache` and a full process restart.
3. Clearing L3 forces correct recomputation; a later request may populate the store again.
4. This validates only host L2 and file L3 with BF16 KV, write-through, kernel IO, and page-first layout. Mooncake, direct external linker, FP8 KV, MTP, and other IO/layout combinations remain unvalidated.

## Data and Figures

- [`results.json`](results.json) — append-only raw semantic results, cache-source details, answers, finish reasons, output IDs, and store events. The final `L3_C_recompute` rows and last three clear events are the negative-control evidence.
- [`validation-summary.json`](validation-summary.json) — independently recomputed request counts, cache hits, file counts, and correctness summary.
- [`probe.py`](probe.py) — round-specific server lifecycle, workload generation, tier checks, and negative control.
