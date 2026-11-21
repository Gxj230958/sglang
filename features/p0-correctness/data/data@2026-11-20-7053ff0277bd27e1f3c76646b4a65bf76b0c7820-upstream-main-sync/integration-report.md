# glm-5-lp on upstream main: run 20261120T1944Z

Result: candidate `7053ff0277bd27e1f3c76646b4a65bf76b0c7820` passes Tier 1 and Tier 2 and is pushed to
radixark/sglang-zai `sync/glm-5-lp-on-upstream-main`. Ready for review (`READY_FOR_REVIEW.md`).
Evidence: `reports/20261120T1944Z-artifacts/`.

## Revisions

| | revision |
|---|---|
| sgl-project/sglang `main` integrated | `2b248971db8c8c349586c3757663be9cba5e366d` |
| radixark/sglang-zai `main` | fast-forwarded `7d82bda66c79f14eaf6fb4664425792558e78478` -> `2b248971db8c8c349586c3757663be9cba5e366d` (plain push; `git ls-remote` readback equals upstream/main) |
| radixark/sglang-zai `glm-5-lp` | `13fa8258d2404deedfac9c114c43c4e4069f39b5` (unchanged) |
| merge base | `6de483b326c7dd4145fde06afcac9866bf491024`; upstream +495 commits / 3933 files, glm-5-lp +120 commits / 203 files |
| candidate | `7053ff0277bd27e1f3c76646b4a65bf76b0c7820`, one merge commit, parents glm-5-lp then upstream/main; branch `sync/glm-5-lp-on-upstream-main` in `glm-next/upstream-sync/repo` and on sglang-zai |

## Conflicts (16 files)

| file | resolution |
|---|---|
| `docker/Dockerfile.cu134` | Adjacent ARG lines: glm FlashMLA source-build ARGs kept beside upstream DeepEP 0.1.3 and `SGL_NCCL_VERSION=2.31.2`. |
| `python/pyproject.toml` | `sgl-deep-ep==0.1.3` (upstream; glm-5-lp never changed this pin). |
| `python/sglang/kernels/ops/attention/__init__.py` | Union of registrations: glm `mla_fp8_cast` and `glm_loop_sparse_mla_decode` (Triton + JIT), upstream `beam_shared_context`, `indexer_head_gate`, DSv4 FP4-indexer ops. |
| `python/sglang/srt/arg_groups/kv_cache_hook.py` | Unified-memory PD spec gate: upstream adds NIXL and rejects speculative decoding for every backend; glm-5-lp allows EAGLE/EAGLE3 over Mooncake. Merged: spec allowed only for Mooncake + EAGLE/EAGLE3. |
| `python/sglang/srt/arg_groups/mega_moe_hook.py` | Error text carries both glm "FP8 experts" and upstream gfx1250 note. |
| `python/sglang/srt/arg_groups/pd_disaggregation_hook.py` | Supported-architecture message lists both GLM LoopLM and Inkling2. |
| `python/sglang/srt/disaggregation/decode.py` | glm `pd_kv_is_mla(pool, storage)` plus upstream `host_pool_blocked` flag. |
| `python/sglang/srt/environ.py` | Upstream retires the `SGLANG_K31_DECODE_MOE` alias (plain `EnvBool`); glm env vars kept next to upstream `SGLANG_TRTLLM_MLA_WORKSPACE_MB`. |
| `python/sglang/srt/layers/attention/dsa/dsa_indexer.py` | Upstream refactor (`_fused_k_weights`, `_fused_q_quant`, `prepare_merged_k_gate`) is the form; glm MRoPE table (`_fused_rope_args`, now `(None, positions)` for the NoPE head-gate indexer) and the merged `wk_weights_proj` tiny-GEMM ride inside it; `_fused_q_quant` takes `cos_sin_cache`. |
| `python/sglang/srt/layers/attention/dsa_backend.py` | trtllm decode: glm fused-h64 prep, then upstream prebuilt FP8 q (Kimi-K3.1 only), then the FP8 cast; glm split-K decode returns before upstream's DCP-partial (`dcp_topk_length`) / replicated-DCP slot handling. |
| `python/sglang/srt/layers/moe/mega_moe.py` | glm localization predicate kept (SM100/103/107 plus `deep_gemm.is_localization_available()`, present since DeepGEMM v0.2.8); upstream's SM list is a subset. |
| `python/sglang/srt/mem_cache/kv_cache_configurator.py` | Hybrid-SWA logical capacity keeps the glm HiSparse ratio; window geometry keeps glm `window_layer_ids` and gains upstream `is_mxfp8`. |
| `python/sglang/srt/mem_cache/static_kv_storage.py` | Upstream inlined and removed `append_dsa_tail`; glm `add_dsa_index_state` kept for the SWA and plain DSA branches. |
| `python/sglang/srt/models/deepseek_common/attention_forward_methods/forward_mla.py` | Both new per-forward flags kept; upstream alt-stream absorbed q (`q_nope_out_alt`) takes precedence and disables the glm padded query; `"nsa"` alias dropped (upstream #51074 removed it) with the glm MRoPE no-fuse check kept. |
| `python/sglang/srt/models/glm5_next.py` | Union: glm `precompile_kernels_after_loading` / encoder media config, upstream `register_modelslim_projection_aliases`. |
| `test/registered/kernels/ops/speculative/test_speculative_sampling.py` | glm `est_time=90` (its fallback-tile case) plus upstream AMD registration. |

Folded into the merge commit as well:
- `python/sglang/srt/layers/rotary_embedding/mrope.py`: ruff-format line wrap required by the merged pre-commit config.
- `test/registered/unit/cli/test_glm_loop_server_args.py`: encoder-disaggregation stub gains `enable_token_space_processor` (read by upstream since #46412).
- `test/registered/unit/mem_cache/test_platform_kv_cache_dtype.py`: the hybrid DSA+SWA case passes a request pool and mocks the draft-token / index-K elision reads the glm pool builder makes.
- `test/registered/unit/server_args/test_unified_memory_spec_gate.py`: NIXL rejects EAGLE, Mooncake accepts it (see open question 2).

## Post-merge identifier audit

Over every file glm-5-lp touched, in the merged tree (scripts in `reports/20261120T1944Z-artifacts/`):
- every `sglang.*` import resolves to an existing module and name: 0 unresolved;
- names upstream removed in 6de483b326..2b248971db with no remaining definition, referenced from glm-touched files: 0 real hits (false positives: a module name, upstream's own removed-options map, a docs URL anchor);
- calls passing a keyword upstream removed from the callee: 0;
- `SGLANG_*` env vars and `--flags` in glm docs/scripts/code: none references a removed option;
- 170 kernel-registry string targets resolve.

## Dependency pins

| pin | merge base | glm-5-lp | upstream | candidate | note |
|---|---|---|---|---|---|
| torch | 2.14.1 | 2.14.1 | 2.14.1 | 2.14.1 | same |
| flashinfer-python | 0.7.4 | 0.7.4 | 0.7.4 | 0.7.4 | same |
| sglang-kernel | 0.4.11 | 0.4.11 | 0.4.11 | 0.4.11 | same |
| sgl-deep-gemm | 0.2.8 | 0.2.9 | 0.2.9 | 0.2.9 | same; glm docker patch `0001-mega-moe-fp8-trtllm-weight-layout.patch` unchanged |
| sgl-flash-mla (pyproject) | 1.0.5 | 1.0.5 | 1.0.5 | 1.0.5 | same |
| sgl-flash-mla (Dockerfile source build) | - | 1.0.4 @ 46b6727a + glm patches | - | glm kept | glm-only build stage |
| transformers | 5.19.0 | 5.19.0 | 5.19.0 | 5.19.0 | same |
| sgl-deep-ep | 0.1.2.post1 | 0.1.2.post1 | 0.1.3 | 0.1.3 | upstream bump, paired with NCCL 2.31.2 at runtime; glm never changed it |
| NCCL / Mooncake (Dockerfile) | 2.30.7 / 0.3.13.post1 | same as base | 2.31.2 / 0.3.14 | upstream | glm never changed them |

## Verification

### Tier 1 (host, CPU): PASS

- Conflict markers: `git grep -nE '^(<<<<<<<|>>>>>>>) '` 0 hits; pre-commit `check-merge-conflict` passed.
- pre-commit: `SKIP=clippy-rust-workspace,rustfmt-rust-workspace,rustfmt-sgl-router,mint-broken-links,lychee,export-cookbook-commands pre-commit run --files <75 files changed on both sides>`: pass after ruff-format rewrapped `mrope.py` (folded in); the three adapted tests pass too. Skipped hooks build Rust or reach the network.
- Byte-compile: `compile()` over the 2730 .py files that differ from either parent: 0 failures.
- CPU unit tests: 193 CPU-registered files under `test/registered/unit/` covering GLM LoopLM, server-args hooks, PD/state entries, KV configurator/pools, DSA, MegaMoE, environ. `PYTHONPATH=python /home/ubuntu/cpu-venv/bin/python -m pytest -q -p no:cacheprovider -o addopts="" <file>` per file (venv: Python 3.12.3, torch 2.13.0+cpu, transformers 5.12.1, outlines 0.1.11). Totals: 179 files clean; 2539 passed, 111 failed, 2 errors, 58 skipped. Each failing file was rerun on both parents (worktrees at 13fa8258d2 and 2b248971db):

| file | candidate | glm-5-lp | upstream | cause |
|---|---|---|---|---|
| cli/test_glm_loop_server_args | 1 fail | pass | absent | merge: stub lacked upstream field; adapted, 13 pass |
| mem_cache/test_platform_kv_cache_dtype | 1 fail | absent | pass | merge: upstream test x glm pool builder; adapted, 6 pass |
| server_args/test_unified_memory_spec_gate | 1 fail | pass | pass | merge: design intersection; adapted, 9 pass |
| configs/test_glm_loop_config | 15 fail | 15 fail | absent | venv transformers 5.12.1; 15/15 pass on both with transformers 5.19.0 |
| models/test_glm_loop | 33 fail | same | absent | transformers + no vllm; 48/48 pass on both with transformers 5.19.0 and a vllm import stub |
| layers/attention/test_dsa_backend_dp_padding | 8 fail | 7 fail | pass | glm-5-lp test debt: upstream stubs lack glm backend/layer attributes; 11/11 pass with them added (scratch, not committed) |
| layers/attention/test_dsa_eager_metadata_no_host_sync | 2 fail | 2 fail | pass | same; 3/3 with stub attributes |
| layers/attention/test_dsa_unified_pool | 4 fail | 4 fail | pass | same; 6/6 with stub attributes |
| disaggregation/test_decode_hicache_tree_core, test_specv2_kvcache_offloading; mem_cache/test_hicache_unified_key_scheme, test_unified_cache_linker | fail | same set where present | same set | HiCache native hash extension needs OpenSSL headers and ninja |
| layers/attention/test_tilelang_dsa_decode_split | collect error | absent | collect error | no `tilelang` in the venv |
| managers/test_disagg_idle_step_counters | collect error | collect error | collect error | no `parameterized` in the venv |

The scratch stub diff for the three DSA files is `reports/20261120T1944Z-artifacts/dsa_test_stub_glm_attrs.diff`; the new upstream DCP case (`test_trtllm_sharded_dcp_decode_attends_the_indexer_local_slots`) is among the 11 that pass with it, exercising the merged split-K / DCP ordering.

### Tier 2 (GPU): PASS

- Box: `mobius-8gb300-share` (`devbox-lock` held 18:28-19:45 UTC, released), one 4x GB300 rank per run: rank 0 baseline, rank 1 candidate.
- Environment: `/opt/sglang` (torch 2.14.1+cu130, transformers 5.19.0, tilelang 0.1.12, tvm-ffi 0.1.11, xgrammar 0.2.7) plus PYTHONPATH overlays: source tree, own patched sgl-deep-gemm 0.2.9 (DeepGEMM v0.2.9 `d66c3ada7739c496c23638f93e0b3b3ec761adf0` + glm patch, built on each rank), flashinfer 0.7.4 (`/scratch/shuwen-glm-hisparse-20261117/fi074`), sglang-kernel 0.4.11 / sgl-flash-mla 1.0.5 (`/scratch/cc-regate2/overlay`). sgl-deep-ep 0.1.2.post1 and NCCL 2.30.7 from the image (DeepEP unused by this recipe). Rust radix-tree core built by cargo at startup on both. `SGLANG_SIMULATE_ACC_LEN` unset.
- Serve: `python -m sglang.launch_server --model-path /scratch/models/GLM-5-1028-Provider --tp-size 4 --kv-cache-dtype fp8_e4m3 --speculative-algorithm EAGLE --reasoning-parser glm45` (no `--context-length`, CUDA graphs on). `--reasoning-parser glm45` is added because `docs/docs/basic_usage/glm_loop.mdx` measures this reasoning model through chat with it. Resolved: MoE `flashinfer_trtllm`, DSA prefill/decode `trtllm`, MTP steps 3 / topk 1 / draft tokens 4, max running requests 48.
- Eval: `sgl-eval run gsm8k --base-url http://127.0.0.1:31200/v1 --temperature 1.0 --top-p 0.95` (sgl-eval 0.1.3, own venv, full 1319, 64 threads, no max_tokens).

| | glm-5-lp `13fa8258d2` (baseline) | candidate `7053ff0277` |
|---|---|---|
| GSM8K accuracy | 94.69% | 94.92% |
| finish_reason | stop 1318, length 1 | stop 1319 |
| stop rate | 99.92% | 100.00% |
| errors / tracebacks | 0 / 0 | 0 / 0 |
| accept length at >= 16 running requests (mean / median) | 2.658 / 2.680 | 2.653 / 2.655 |
| eval wall time | 1901 s (one sample decoded to the 262144 context limit) | 915 s |

Gate: stop rate >= baseline and accuracy >= baseline: PASS. Artifacts: `tier2/*.tar.gz` (status, versions, analysis, metrics, per-sample JSONL, server/eval logs).

## Not verified

The recipe exercises TP4 with an FP8 KV cache, trtllm DSA, EAGLE MTP and flashinfer_trtllm MoE. Not exercised on GPU: PD disaggregation (Mooncake/NIXL, including the merged unified-memory spec gate), unified memory, HiSparse, DCP/CP, attention DP / EP / DeepEP 0.1.3 / MegaMoE (`megamoe` was not selected), the glm fused-h64 and split-K decode kernels, the hybrid-SWA window layout, the cu134 image build, AMD/NPU.

## Open questions

1. glm-5-lp carries 13 failing cases in three upstream DSA unit-test files (stubs lack glm attributes; reproducible on glm-5-lp itself). A stub-only fix is verified in scratch. Fold it into this sync, land it separately on glm-5-lp, or leave it?
2. Unified-memory PD speculative gate: the candidate keeps glm-5-lp's EAGLE/EAGLE3-over-Mooncake (from `1093927e5d`) while upstream #50767 rejects speculative decoding on both NIXL and Mooncake; upstream's test was adapted accordingly. Confirm this is the intended behavior.
3. sgl-deep-ep moves to 0.1.3 with NCCL 2.31.2 at runtime: any glm deployment using DeepEP needs the new wheel; not exercised here.
4. Environment change on `mobius-8gb300-share`: `libdw-dev` / `libelf-dev` were apt-installed on both ranks to build DeepGEMM v0.2.9 (DeepJIT needs elfutils headers, as `Dockerfile.cu134` installs).
5. The sglang-zai `glm-5-lp-track` record for this round needs a PR to that branch, which this task does not open.
