# glm-5-lp on upstream main: run 20261121T0550Z

Result: candidate `710a842c5741dade3ecd7d8583ef622745dcd9f2` (tree
`9ab79bb1b50b67bbc9a1e7d75fbdc8ebddf33aff`) passes Tier 1 and both Tier 2 legs (TP4; DEP4 +
megamoe) against re-measured baselines of glm-5-lp `45bff30acf`, and is pushed to radixark/sglang-zai
`sync/glm-5-lp-on-upstream-main`. Landed: the coordinating agent reviewed it and fast-forwarded
radixark/sglang-zai `glm-5-lp` to `710a842c5741dade3ecd7d8583ef622745dcd9f2` (`git ls-remote`
readback 05:50 UTC). Evidence: `reports/20261121T0550Z-artifacts/` (including the archived
`READY_FOR_REVIEW.md`).

Started on the user's request ahead of the 12-hour schedule, after run 20261121T0310Z could not
push because `glm-5-lp` moved during its Tier 2.

## Revisions

| | revision |
|---|---|
| sgl-project/sglang `main` integrated | `8171e9a4f5418ddad2dda911b66605b9982cce7b` (+12 commits since run 20261121T0310Z) |
| radixark/sglang-zai `main` | fast-forwarded `c95fb12bb8c2dbe318ddba9bbcc80db561798dfa` -> `8171e9a4f5418ddad2dda911b66605b9982cce7b` with a plain `git push zai upstream/main:main`; `git ls-remote` readback equal at 03:08 UTC and again at push time |
| radixark/sglang-zai `glm-5-lp` | `45bff30acfb5ec97673046ea7b8d36b822bbc520` (#110 on top of `13fa8258d2`); re-checked with `git ls-remote` immediately before the candidate push (05:46 UTC): unchanged |
| merge base | `6de483b326c7dd4145fde06afcac9866bf491024`; upstream +4192 files, glm-5-lp +203 files, both 81 |
| candidate | `710a842c5741dade3ecd7d8583ef622745dcd9f2`: one commit, parents `45bff30acf` then `8171e9a4f5`, message `Merge branch 'main' into glm-5-lp`, no body, author/committer Xinyuan Tong |
| tested tree | `9ab79bb1b50b67bbc9a1e7d75fbdc8ebddf33aff`; Tier 1 ran on the candidate checkout, Tier 2 on `git archive 710a842c57` (sha256 `1fda25bc...`) |
| `sync/glm-5-lp-on-upstream-main` | `7053ff0277bd27e1f3c76646b4a65bf76b0c7820` -> `710a842c5741dade3ecd7d8583ef622745dcd9f2` (`--force-with-lease` pinned to `7053ff0277`); readback equal |

How the tree was built: run 20261121T0310Z's tested tree (`ff776255fc`), then `git merge 45bff30acf`
(clean), then `git merge 8171e9a4f5` (one conflict, below), then
`git commit-tree 9ab79bb1 -p 45bff30acf -p 8171e9a4f5 -m "Merge branch 'main' into glm-5-lp"`.
The intermediate merges are local only.

File-level check of the tree against both sides (merge base `6de483b326`): files only glm-5-lp
touched equal `45bff30acf` except `test_glm_loop_server_args.py`; files only upstream touched equal
`8171e9a4f5` except `test_platform_kv_cache_dtype.py` and `test_unified_memory_spec_gate.py` (the
three test adaptations from run 20261120T1944Z); no file outside the union changed.

## Conflicts

| file | resolution |
|---|---|
| `python/sglang/srt/mem_cache/allocator/hisparse.py` | Upstream #51252 moves the shared HiSparse allocator methods into `HiSparseAllocatorBase` and routes every free (including `free_full`) through `_free_rows`, which releases the HiSparse mapping. Taken as the form. glm-5-lp's additions ride on it unchanged: optional caller-built `logical_attn_allocator`, `get_hisparse_kvcache()` resolving an `SWAKVPool`'s full sub-pool (used for `register_mapping`, `get_last_loc_hisparse_device`, `free_hisparse`), and `HiSparseSWATokenToKVPoolAllocator`. That class's own `free_full` is dropped: the base `free_full` does the same (logical free, then `free_hisparse`) because this allocator never defers frees. |

Every other file merged cleanly. glm-5-lp #110 (`dsa_loop.py` fused FlashMLA extra-KV prefill,
`test_glm_loop_attention.py`) touches no file upstream changed.

## Post-merge identifier audit

Over every file glm-5-lp touched, in the merged tree (`audit2.out`, `audit3.out`, `sigdiff.out`):
- unresolved `sglang.*` imports 0; names removed in `c95fb12bb8..8171e9a4f5` still referenced 0; calls passing a removed keyword 0.
- Env vars / flags referenced from GLM files: same output as run 20261121T0310Z.
- Re-signatured: `MooncakeKVManager.send_kvcache` gains `dst_num_draft_entries` (#47840: the receiver's draft-entry count now travels as register-message field 22). glm-5-lp's Mooncake changes (batched sync transfer, MLA attention-TP check) add no register fields, so the field indices do not collide. `Scheduler.save_remote_model` / `save_sharded_model` and two PP mixin helpers were removed upstream; no GLM file uses them.

## Dependency pins

No pin changed in `c95fb12bb8..8171e9a4f5`. Candidate: torch 2.14.1, flashinfer 0.7.4, sglang-kernel
0.4.11, sgl-deep-gemm 0.2.9 (glm patch unchanged, sha256 prefix `d1b8ac39dd66375c`), sgl-flash-mla
1.0.5 (Docker source build 1.0.4 @ `46b6727a` from glm-5-lp), transformers 5.19.0, and upstream's
sgl-deep-ep 0.1.3 / NCCL 2.31.2 (glm-5-lp pins 0.1.2.post1 / 2.30.7; the candidate takes upstream's,
as in the previous rounds). #110's fused prefill needs a FlashMLA wheel with
`has_sparse_prefill_extra_kv()`, which sgl-flash-mla 1.0.5 lacks, so it keeps the two-launch path.

## Verification

### Tier 1 (host, CPU): PASS

- Conflict markers: 0.
- pre-commit: `SKIP=clippy-rust-workspace,rustfmt-rust-workspace,rustfmt-sgl-router,mint-broken-links,lychee,export-cookbook-commands pre-commit run --files <81 files changed on both sides + test_glm_loop_server_args.py>`: pass, no changes (`tier1/precommit.log`). A first invocation over all 204 files that differ from upstream reported glm-5-lp's own files (trailing whitespace in three `docker/patches/*.patch`, clang-format on four `kernels/jit/csrc/*.cuh`, isort on `test_sigmoid_topk_fp8_quant.py`); those files are byte-identical to `glm-5-lp`, the hook edits were reverted, and the log is kept as `tier1/precommit-glm-only-files-info.log` (open question 3).
- Byte-compile: all 9473 tracked `.py` files, 0 failures.
- CPU unit tests: 223 files (the previous list without `test/registered/cpu/`, plus 12 CPU-registered tests the new upstream range touched), `PYTHONPATH=python /home/ubuntu/cpu-venv/bin/python -m pytest -q -p no:cacheprovider -o addopts="" <file>` each: 212 files clean; 3084 passed, 108 failed, 2 errors, 74 skipped. GLM LoopLM with transformers 5.19.0 and the vllm import stub: 13/13, 15/15, 48/48.
  - Resolution-relevant: `test_hisparse_allocator` 18 passed; Mooncake / PD `test_disaggregation_wire` 98, `test_mooncake_transfer_batching` 25, `test_pp_hybrid_kv_transfer` 12, `test_receiver_connection_pool` 11 passed.
  - `test_dsa_flashmla_head_padding` passes again (upstream #51978 fixed its stub).
  - The 11 failing files are the same set, with the same counts, as runs 20261120T1944Z and 20261121T0310Z: venv transformers/vllm (GLM config and model tests, pass with the overlay), glm-5-lp DSA test-stub debt (3 files), HiCache native extension needs OpenSSL/ninja (4 files), missing `tilelang` / `parameterized` (2 collect errors).

### Tier 2 (GPU): PASS on both legs

- Box: `mobius-8gb300-share`, `devbox-lock` held 04:04-05:46 UTC and released. Rank 0 ran the glm-5-lp `45bff30acf` baselines, rank 1 the candidate; each rank ran TP4, then DEP4 twice, sequentially (`scripts/legs.sh`, `scripts/gate2c.sh`). GPUs idle before each launch and after each stop.
- Common environment: `/opt/sglang` (torch 2.14.1+cu130, transformers 5.19.0, tilelang 0.1.12, tvm-ffi 0.1.11, xgrammar 0.2.7, triton 3.8.0) with PYTHONPATH overlays: source tree, patched sgl-deep-gemm 0.2.9 (DeepGEMM v0.2.9 `d66c3ada7739c496c23638f93e0b3b3ec761adf0` + the glm patch, built on each rank), flashinfer 0.7.4, sglang-kernel 0.4.11 / sgl-flash-mla 1.0.5. `NCCL_DEBUG=VERSION`; `SGLANG_SIMULATE_ACC_LEN` unset; CUDA graphs on; no `--context-length`.
- Per-side pins, as loaded (`versions.txt`, `loaded_libs.txt`, server log):
  - baseline: sgl-deep-ep 0.1.2.post1 and NCCL 2.30.7 from the image (its tree's pins); `ncclGetVersion` 23007; `NCCL version 2.30.7+cuda13.3`.
  - candidate: sgl-deep-ep 0.1.3 and nvidia-nccl-cu13 2.31.2 from `/scratch/glm5lp-upstream-sync/overlay-deps-ff776255fc` (released wheels, `--no-deps --target`, PYTHONPATH plus `LD_PRELOAD` of its `libnccl.so.2`); `ncclGetVersion` 23102; `NCCL version 2.31.2+cuda13.3`; all four `sglang::scheduler` processes map only the overlay `deep_ep/_C` and `libnccl.so.2`.
- Eval: `sgl-eval run gsm8k --base-url http://127.0.0.1:31200/v1 --temperature 1.0 --top-p 0.95` (sgl-eval 0.1.3, full 1319, 64 threads, no max_tokens).

Leg (i) TP4: `python -m sglang.launch_server --model-path /scratch/models/GLM-5-1028-Provider --tp-size 4 --kv-cache-dtype fp8_e4m3 --speculative-algorithm EAGLE --reasoning-parser glm45`. Resolved: MoE `flashinfer_trtllm`, DSA prefill/decode `trtllm`, MTP 3/1/4, 48 running requests.

| TP4 | baseline `45bff30acf` | candidate `710a842c57` |
|---|---|---|
| correct / accuracy | 1251 / 94.84% | 1254 / 95.07% |
| finish_reason / stop rate | stop 1319 / 100% | stop 1319 / 100% |
| errors / tracebacks | 0 / 0 | 0 / 0 |
| accept length, >= 16 running (mean) | 2.692 | 2.694 |

Leg (ii) DEP4 + megamoe: `SGLANG_OPT_DEEPGEMM_MEGA_MOE_NUM_MAX_TOKENS_PER_RANK=8192 SGLANG_DP_USE_GATHERV=1` with the TP4 flags plus `--ep-size 4 --attn-dp-size 4 --moe-runner-backend megamoe --mem-fraction-static 0.9 --chunked-prefill-size 32768`. Resolved: `moe_a2a_backend` megamoe, attention DP 4, per-rank chunked prefill 8192, DSA `trtllm`/`trtllm`, MTP 3/1/4, 48 running requests.

| DEP4 + megamoe | baseline `45bff30acf` run 1 / run 2 | candidate `710a842c57` run 1 / run 2 |
|---|---|---|
| correct / accuracy | 1256 / 95.22%, 1249 / 94.69% | 1272 / 96.44%, 1257 / 95.30% |
| two-run mean accuracy | 94.96% | 95.87% |
| finish_reason | stop 1319; stop 1316 + length 3 | stop 1319; stop 1318 + length 1 |
| stop rate | 100.00%, 99.77% | 100.00%, 99.92% |
| errors / tracebacks | 0 / 0 both | 0 / 0 both |
| accept length, DP0 lines with >= 8 running (mean) | 2.667, 2.652 | 2.679, 2.663 |

Every `length` finish is a sample decoded to the 262144-token context limit (baseline run 2: three;
candidate run 2: one; candidate run 1 also has one sample that stopped normally at 260139 tokens).
Run 20261121T0310Z's `13fa8258d2` baseline had one such sample as well.

Gates (the rule from run 20261121T0310Z, unchanged): TP4 stop rate and accuracy at or above the
baseline: PASS. DEP4 every candidate run's stop rate at or above its paired baseline run (100% vs
100%, 99.92% vs 99.77%) and two-run mean accuracy at least the baseline mean minus 1.0 point
(+0.91 points): PASS.

Artifacts: `tier2/baseline-45bff30acf.tar.gz`, `tier2/candidate-710a842c57.tar.gz` (status,
versions, loaded libraries, analysis, server info, metrics, per-sample JSONL, server and eval logs
for all six runs), hashes in `SHA256SUMS`. Baselines cached in `state.json` under `45bff30acf`.

## Not verified

The two legs exercise TP4 and DEP4 attention-DP with FP8 KV, trtllm DSA, EAGLE MTP, `flashinfer_trtllm`
MoE (TP4) and DeepGEMM MegaMoE with DeepEP 0.1.3 / NCCL 2.31.2 (DEP4). Not exercised: glm-5-lp #110's
fused FlashMLA extra-KV prefill (needs `--dsa-prefill-backend flashmla_sparse`, bf16 KV and a newer
FlashMLA wheel), the HiSparse allocators touched by the conflict (unit-tested only), PD
disaggregation (Mooncake/NIXL, the unified-memory spec gate, the new draft-entry register field),
unified memory, DCP/CP, the EP block-FP8 / MXFP8 decode MoE backends, the glm fused-h64 and split-K
decode kernels, the hybrid-SWA window layout, the cu134 image build, AMD/NPU.

## Open questions

1. DEP4 gate rule (carried from run 20261121T0310Z): stop rate at or above the paired baseline on every run plus two-run mean accuracy within 1.0 point. Keep it?
2. Carried from run 20261120T1944Z: the DSA test-stub fix for glm-5-lp's 13 failing cases; EAGLE/EAGLE3 over Mooncake under unified-memory PD versus upstream #50767; `libdw-dev`/`libelf-dev` installed on both mobius ranks.
3. glm-5-lp files fail the merged pre-commit config: trailing whitespace / missing final newline in `docker/patches/deep_gemm/0001-...patch` and `docker/patches/flash_mla/000{1,2}-...patch` (where the hook's edit would break the patches; an exclude for `docker/patches/` fits better), clang-format in four `python/sglang/kernels/jit/csrc/*.cuh`, isort in `test/registered/kernels/ops/moe/test_sigmoid_topk_fp8_quant.py`. Left as glm-5-lp has them.
4. Evidence record: E32 is opened as a pull request into `glm-5-lp-track` from `track/upstream-sync-20261121`. radixark/sglang-zai#116 (another branch) still holds E31 for run 20261120T1944Z; the two add lines at the same index locations.
