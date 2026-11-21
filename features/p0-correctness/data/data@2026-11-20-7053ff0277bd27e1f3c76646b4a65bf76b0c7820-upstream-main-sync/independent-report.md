# E31 independent review

## Scope

The coordinating review checked the candidate in `glm-next/upstream-sync/repo`; the tracking review then checked the raw evidence and model metadata without changing the candidate, benchmark allocation or evaluation outputs.

## Candidate identity

- Remote `sync/glm-5-lp-on-upstream-main` equals tested commit `7053ff0277bd27e1f3c76646b4a65bf76b0c7820`.
- Its parents are `glm-5-lp` `13fa8258d2404deedfac9c114c43c4e4069f39b5` and upstream `main` `2b248971db8c8c349586c3757663be9cba5e366d`.
- `glm-5-lp` is unchanged. `sglang-zai` `main` equals the integrated upstream revision.
- Against merge base `6de483b326c7dd4145fde06afcac9866bf491024`, GLM touched 203 files, upstream touched 3933 and both touched 75. No file changed outside that union and no conflict markers remain.
- Files changed only by GLM are byte-identical to `glm-5-lp` except the adapted `test_glm_loop_server_args.py`. Files changed only upstream are byte-identical to upstream except `test_platform_kv_cache_dtype.py` and `test_unified_memory_spec_gate.py`.
- The combined `python/` and `docker/` diff was reviewed. The merged DSA indexer, backend ordering, padded-query exclusion, MRoPE table handling and Mooncake-only speculative gate are coherent for the exercised path. Removed helper `append_dsa_tail` has no remaining caller.

## Raw-result recomputation

`python3 verify.py` reads both 1319-row JSONL files and both server logs. It confirms unique sample IDs, symbolic correctness, finish reasons, metrics consistency, launch settings, zero tracebacks, evaluation exit zero and cleanup.

| Check | Baseline | Candidate |
|---|---:|---:|
| Samples | 1319 | 1319 |
| Correct | 1249 | 1252 |
| Accuracy from samples | 94.69% | 94.92% |
| Stop / length | 1318 / 1 | 1319 / 0 |
| Errors | 0 | 0 |
| Accept samples at >=16 running requests | 113 | 128 |
| Accept mean / median at >=16 | 2.658 / 2.680 | 2.653 / 2.655 |
| Terminal | DONE, zero GPU apps | DONE, zero GPU apps |

The captured result is [verify.json](verify.json): `gate=PASS`. Candidate accuracy and stop rate both meet or exceed the matched baseline.

## Model and environment receipt

A separate read-only check on both ranks found identical config, weight-index, tokenizer and tokenizer-config hashes. All four match the metadata pinned to FP8 revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff` in Correctness E27. The config has no `_commit_hash`; this round binds the checkpoint through those hashes and does not claim that every weight shard was rehashed. See [checkpoint-receipt.json](checkpoint-receipt.json).

The candidate server imported source from `/scratch/glm5lp-upstream-sync/7053ff0277/src`; the baseline imported from `/scratch/glm5lp-upstream-sync/13fa8258d2/src`. Both ran the same model and recipe. The runtime had sgl-deep-ep 0.1.2.post1 and NCCL 2.30.7 rather than the candidate's 0.1.3 / 2.31.2 pins; this TP4 recipe does not load DeepEP.

## Conclusion and limits

The merge resolution is sound for the exercised TP4, FP8-KV, TRTLLM DSA and EAGLE path, and the accuracy/stop-rate gate passes. DEP/MegaMoE, PD, HiSparse, unified memory, DCP/CP, attention DP/EP, DeepEP 0.1.3, fused-h64 and split-K decode, hybrid-SWA layout, the cu134 image and AMD/NPU remain unexercised. Landing on `glm-5-lp` and any release claim remain separate decisions.
