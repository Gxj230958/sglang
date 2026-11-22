# glm-5-lp on upstream main: run 20261122T1545Z

Result: candidate `534c27c2414db7cf47038d4da5b347cb56600981` (tree
`fbe85615b3c05c40609d30f50672ee901e8eb1e8`, glm-5-lp `746e19554c` + upstream main `b34a52fcb8`) passes
Tier 1 and all three Tier 2 legs: (i) TP4, (ii) DEP4 + megamoe, and (iii) the full serving recipe
(`qa/lib/gate.py`: LEG PASS).

Pushed to radixark/sglang-zai `sync/glm-5-lp-on-upstream-main` (`710a842c57..534c27c241`); `glm-5-lp`
fast-forwards to it. `reports/READY_FOR_REVIEW.md` written. Evidence:
`reports/20261122T1545Z-artifacts/`. Evidence record: Correctness E33, radixark/sglang-zai#119
(`track/upstream-sync-20261122` -> `glm-5-lp-track`, head `148bf43ce69410ccf0919f000efdc7b5ebe9abcb`, open).

## Revisions

| | revision |
|---|---|
| sgl-project/sglang `main` integrated | `b34a52fcb87a0d1c1190d16e0b5b3c4f867f591f` (+100 commits since `8171e9a4f5`, +38 since run 20261122T0435Z's `4e7a4ff3c8`). Upstream `main` was `cb337923d5` at 15:43 UTC. |
| radixark/sglang-zai `main` | `b34a52fcb8`: `git push zai upstream/main:main` at 12:47 UTC reported up to date (the 6-hourly mains sync had already pushed it); `git ls-remote` readback equal at 12:47 and 15:43 UTC |
| radixark/sglang-zai `glm-5-lp` | `746e19554cf257b2db34bdb8afa85077ea2fb14e`, unchanged at 12:47, 15:38 and 15:43 UTC |
| merge base | `8171e9a4f5418ddad2dda911b66605b9982cce7b`; upstream +464 files, glm-5-lp +204 files, both 23 |
| candidate | `534c27c2414db7cf47038d4da5b347cb56600981`: one commit, parents `746e19554c` then `b34a52fcb8`, message `Merge branch 'main' into glm-5-lp`, no body, author/committer Xinyuan Tong |
| tested tree | `fbe85615b3c05c40609d30f50672ee901e8eb1e8`; Tier 1 on the candidate checkout, Tier 2 on `git archive 534c27c241` (sha256 `71b05a2a2d0868384d2321cf632a3ec11968ef9391151f0f6394851bb3e465eb`) |
| `sync/glm-5-lp-on-upstream-main` | pushed `710a842c57..534c27c241` with `--force-with-lease` pinned to `710a842c57`; `git ls-remote` readback `534c27c241` at 15:38 and 15:43 UTC |

How the tree was built: `git merge b34a52fcb8` on top of `746e19554c` (three conflicts, below), the
adaptations below, then
`git commit-tree fbe85615 -p 746e19554c -p b34a52fcb8 -m "Merge branch 'main' into glm-5-lp"`.

File-level check against the merge base `8171e9a4f5`:
- Files only glm-5-lp touched equal `746e19554c`.
- Files only upstream touched equal `b34a52fcb8`, except three tests (the adaptations).
- No file outside the union changed.

## Conflicts

| file | resolution |
|---|---|
| `python/sglang/srt/disaggregation/mooncake/conn.py` | Upstream #46460 moves every transfer onto `MooncakeTransport` (`_transfer_copies` -> `write_all` + `status_all`). glm-5-lp bounds each synchronous batch to its share of the peer's Mooncake TCP admission queue. Upstream's transport form is kept. glm-5-lp's bound is re-applied inside `_transfer_copies`: `_bounded_copy_batches` splits the copies into batches of at most `max_transfer_batch_descriptors` ranges, each drained before the next is submitted. `_sync_batch_descriptor_bound` and the prefill-side bound are glm-5-lp's. `process_layer_tp_aware` takes upstream's form. |
| `python/sglang/srt/models/glm5_next.py` | glm-5-lp's `_build_layer` and upstream #47047's `_captures_attn_tp_slices(layer, forward_batch)` staticmethod are both kept. |
| `test/registered/unit/disaggregation/test_mooncake_transfer_batching.py` | Upstream's transport harness (`attach_mooncake_transport`, `MooncakeKVManager.__new__`), with glm-5-lp's descriptor-bound parameters and its descriptor-bound and TCP admission tests. 26 passed. |

Adaptations:
- `test_pp_hybrid_kv_transfer.py` and `test_minimax_m31_cache_transfer.py`: upstream #46460's stand-in managers borrow `MooncakeKVManager._transfer_copies`, which now reads `max_transfer_batch_descriptors`. Each stand-in sets it to 0, next to its `max_transfer_batch_indices = 0`. 12/12 and 35/35 pass, as on both sides.
- Carried from earlier rounds: `arch.py` and `test_jit_cache.py` use glm-5-lp #55's public `jit_cuda_version`; `flashinfer_trtllm.py` imports both `deployment_attn_dp_size` (upstream #51995) and `route_quant_handoff`.

## Post-merge identifier audit

Over the Python files glm-5-lp touched, in the merged tree (`sigdiff.out`, `8171e9a4f5..b34a52fcb8`:
142 removed, 68 re-signatured):
- Removed names still referenced: 0. New removals include `SamplingBatchInfo.filter_batch`, `merge_batch` and their `adjusted_*` variants; no glm-5-lp file calls them.
- `sampling_allows_vocab_shards` gains `adjusts_logits`. Both callers in the merged tree pass it (`logits_processor.py:649`, `eagle_utils.py:739`).
- `MooncakeKVManager._send_slot_state` now takes `src_keys`/`dst_keys` instead of pointer lists. glm-5-lp's `DSA_TAIL` branch calls it that way in the merged `conn.py`.
- The required-parameter changes found in earlier rounds (`RequestRetirer` `penalty_status_pool`, `validate_dflash_request` `bound_runtime`) are still passed.

## Dependency pins

No pin changed in `4e7a4ff3c8..b34a52fcb8` (`python/pyproject*.toml`, `docker/`, requirements). Both
sides load sgl-deep-ep 0.1.3 and NCCL 2.31.2 (runtime 23102) from `overlay-deps-710a842c57` and
patched sgl-deep-gemm 0.2.9 from `overlay-dg`. Also loaded: torch 2.14.1+cu130, flashinfer 0.7.4,
sglang-kernel 0.4.11, sgl-flash-mla 1.0.5, transformers 5.19.0.

## Verification

### Tier 1 (host, CPU): PASS

- Conflict markers: 0.
- pre-commit: `SKIP=clippy-rust-workspace,rustfmt-rust-workspace,rustfmt-sgl-router,mint-broken-links,lychee,export-cookbook-commands pre-commit run --files <26 files: the 23 changed on both sides + the three adapted tests>`: pass, no changes.
- Byte-compile: all 9514 tracked `.py` files, 0 failures.
- CPU unit tests: 287 files, each run as `PYTHONPATH=python /home/ubuntu/cpu-venv/bin/python -m pytest -q -p no:cacheprovider -o addopts="" <file>`. The list is run 20261122T0435Z's 268 plus 19 unit tests touched in `4e7a4ff3c8..b34a52fcb8`.
  - Result: 266 files clean; 4010 passed, 160 failed, 4 errors, 116 skipped.
  - GLM LoopLM with transformers 5.19.0 and the vllm import stub: 13/13, 15/15, 48/48.
- 21 failing files. None comes from the merge: each was re-run on `git archive` of both sides in the same venv (`tier1/failure-classification.md`).
  - 11 known: same files and counts as earlier runs.
  - 3 glm-5-lp test-stub debt: `test_lora_pp` (2) and `test_scheduler_held_row_admission` (19), `enable_hisparse` (glm-5-lp #87); `test_schedule_batch_req_pool_indices` (1), its `SimpleNamespace` request lacks `multimodal_inputs` (fails on glm-5-lp, passes on upstream).
  - 1 failing on upstream `b34a52fcb8` and glm-5-lp alike: `test_graph_pool_borrow` (1).
  - 6 environment, failing identically on upstream: no `flashinfer`, no `nixl`, no `ninja`, no CUDA (`test_cuda_vmm_utils`), the venv's transformers (`test_hf_transformers`, 9), `test_serving_deepseek_recipe` (15 on upstream, 13 on glm-5-lp).

### Tier 2 (GPU): PASS

- Box `mobius-8gb300-share`, `devbox-lock` held 12:54-15:38 UTC and released after teardown. GPUs were idle and no store, server or router remained.
  - 12:54-13:46: leg (iii) baseline side, both ranks.
  - 14:01-14:45: candidate legs (i) on rank 0 and (ii) on rank 1.
  - 14:47-15:38: leg (iii) candidate side, both ranks.
- Legs (i) and (ii): `scripts/gate2c.sh` and `scripts/analyze.py`, unchanged since run 20261121T0550Z. Eval: `sgl-eval run gsm8k --base-url http://127.0.0.1:31200/v1 --temperature 1.0 --top-p 0.95`, full 1319, CUDA graphs on, no `--context-length`.
- The gate is the GSM8K rows of `qa/gate.md`, one run per side:
  - at most 3 non-`stop` finishes and at most baseline + 2, no `error`;
  - accuracy at least baseline - 1.0 point;
  - accept length at least baseline - 0.2. Accept length is the mean over decode lines with at least 16 running requests (TP4) or DP0 lines with at least 8 (DEP4).
- Baselines for `746e19554c`: measured in run 20261122T0435Z, cached in `state.json`.

| leg | baseline `746e19554c` | candidate `534c27c241` | gate |
|---|---|---|---|
| (i) TP4: accuracy | 95.45% (1259) | 94.54% (1247) | -0.91 pt: PASS |
| (i) TP4: finish_reason | stop 1319 | stop 1317 + length 2 | 2 <= 3 and <= 0 + 2: PASS |
| (i) TP4: accept length | 2.688 | 2.680 | PASS |
| (ii) DEP4 + megamoe: accuracy | 95.07% (1254) | 95.91% (1265) | +0.84 pt: PASS |
| (ii) DEP4 + megamoe: finish_reason | stop 1317 + length 2 | stop 1319 | PASS |
| (ii) DEP4 + megamoe: accept length | 2.662 | 2.693 | PASS |
| errors / tracebacks, both legs | 0 / 0 | 0 / 0 | |

Leg (i) passes with no margin on two rows: accuracy is 0.09 point above its floor, and the two
`length` finishes are exactly the baseline + 2 limit. Both are reasoning loops that run to the
262144-token context: gsm8k-1303 (262043 tokens) and gsm8k-255 (262060 tokens). gsm8k-255 also looped
on the baseline's DEP4 leg in run 20261122T0435Z. Leg (ii), with the same weights and the same merged
code outside the MoE path, has 1319 `stop` and the higher accuracy.

Leg (i) resolved MoE `flashinfer_trtllm`, DSA, MTP 3/1/4, 48 running. Leg (ii) resolved
`moe_a2a_backend` megamoe, attention DP 4, EP 4, 48 running.

Leg (iii) ran `qa/run_full_recipe.sh --src /scratch/glm5lp-upstream-sync/<rev>/src --ovl
/scratch/glm5lp-upstream-sync/overlay-deps-710a842c57:/scratch/glm5lp-upstream-sync/overlay-dg
--tag gate-<rev> --variant full --conc 64` with harness `1e31bef84893` on both sides. Then
`qa/lib/gate.py` (`leg3/gate.txt`, LEG PASS):

| check | baseline `746e19554c` (12:54-13:46) | candidate `534c27c241` (14:47-15:38) | gate |
|---|---|---|---|
| GSM8K accuracy / finish_reason / accept | 93.86% / stop 1319 / 2.603 | 94.54% / stop 1319 / 2.559 | PASS |
| AgentX c64, 900 s: requests / errors | 1097 / 0 | 1174 / 0 | PASS |
| AgentX total / output tok/s | 85,402 / 933.4 | 92,771 / 998.6 | 1.09x / 1.07x: PASS |
| AgentX TTFT p50 / ITL / accept | 12.1 s / 18.8 ms / 2.39 | 14.6 s / 18.9 ms / 2.44 | 1.21x: PASS |
| cache truth: tiers | host 6208, storage 6208 across a prefill restart, 0 after a fresh store | the same | PASS |
| cache truth: answers | all probes `stop` with the planted code, 6 tokens each, no reasoning | all probes `stop` with the planted code, 7 tokens each, no reasoning | PASS |
| log health | clean; 11 client aborts | clean; 14 client aborts | PASS |

- Cache truth's immediate repeat probe hit the device tier on the baseline (6208 tokens) and not on the candidate (0). That probe is not one of the five sub-checks. The round 5 baseline run on the same `746e19554c` also got 0 there, so the miss happens on glm-5-lp as well.
- This is the first live run of harness `1e31bef84893` (2048-token probe budget). Every probe finished within 7 tokens, so the earlier 32-token budget would have given the same outcome on both sides.
- The recipe, the scripts and `gate.md` are in step: `qa/recipe.md`, `qa/run_full_recipe.sh`, `qa/lib/*` and `qa/gate.md` are byte-identical to the `harness-1e31bef84893/` snapshot in `reports/20261122T0435Z-artifacts/`. No feature left the recipe.

## Not verified

- glm-5-lp #115's EP block-FP8 decode MoE kernels: neither leg (ii) (megamoe) nor leg (iii) selects that backend.
- Upstream #52054's per-row penalties in EAGLE verify: no request in these evals sets a penalty.
- The split path of the re-applied transfer bound (`_bounded_copy_batches` yielding more than one batch). Leg (iii) runs every request through `_transfer_copies` with the bound set and logs no transfer error, but does not record whether any transfer exceeded the bound. The unit tests cover the split.
- Also not exercised:
  - glm-5-lp #110's fused FlashMLA extra-KV prefill;
  - HiSparse;
  - unified memory, DCP/CP;
  - the Marlin MXFP8 and trtllm-gen MXFP4 MoE paths;
  - the cu134 image build, AMD/NPU.

## Open questions

1. **Cache-truth probe change** (harness `1e31bef84893`, from run 20261122T0435Z): it now has a live run on both sides, both passing. Confirm it is acceptable for the gate.
2. **AgentX TTFT tolerance.** The same glm-5-lp `746e19554c` measured TTFT p50 16.0 s in run 20261122T0435Z and 12.1 s in this run, with total throughput 84,850 and 85,402 tok/s. A 32% same-revision spread is wider than the 1.30x row allows: this candidate's 14.6 s passes against 12.1 s and would pass against 16.0 s, but a future round could fail or pass on noise. Should the TTFT row use the larger of the two cached baseline measurements, or be widened, now that two measurements exist?
3. **Prefill SIGSEGV** (run 20261121T2020Z): `cudaGraphLaunch` during prefill breakable CUDA graph replay, concurrent with a Mooncake zero-copy L3 prefetch. It has not recurred in the five full-recipe runs since, and it has no reproduction.
4. **Test-stub debt**: glm-5-lp Scheduler stubs lack `enable_hisparse` (`test_lora_pp`, `test_scheduler_held_row_admission`), and `test_schedule_batch_req_pool_indices`'s request stub lacks `multimodal_inputs`. The DSA stub debt is carried from run 20261120T1944Z.
