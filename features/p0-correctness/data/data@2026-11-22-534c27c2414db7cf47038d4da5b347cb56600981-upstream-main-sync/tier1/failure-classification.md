Tier 1 CPU tests, candidate 534c27c241: 287 files (run 5's 268 + 19 unit tests touched in 4e7a4ff3c8..b34a52fcb8).
First pass on 9a611163b1 (same tree minus the two test adaptations below): 264 files clean; 4005 passed, 165 failed, 4 errors, 116 skipped.
GLM overlay (transformers 5.19.0 + vllm stub): test_glm_loop_server_args 13, test_glm_loop_config 15, test_glm_loop 48 passed.

Merge-induced, adapted in the candidate:
- test_pp_hybrid_kv_transfer (3 failed) and test_minimax_m31_cache_transfer (2 failed): their stand-in managers
  (upstream #46460) borrow MooncakeKVManager._transfer_copies, which now reads max_transfer_batch_descriptors (glm-5-lp's
  batching); each stand-in gets max_transfer_batch_descriptors = 0 next to max_transfer_batch_indices = 0.
  After: 12/12 and 35/35 passed (both pass on glm-5-lp 746e19554c and on upstream b34a52fcb8).

21 remaining failing files, none introduced by the merge (each re-run on git archive of both sides in the same venv):
- 11 known (same files and counts as earlier runs): glm_loop_config, decode_hicache_tree_core,
  specv2_kvcache_offloading, dsa_backend_dp_padding, dsa_eager_metadata_no_host_sync, dsa_unified_pool, tilelang_dsa_decode_split,
  disagg_idle_step_counters, hicache_unified_key_scheme, unified_cache_linker, glm_loop.
- 3 glm-5-lp test-stub debt: test_lora_pp (2), test_scheduler_held_row_admission (19) (enable_hisparse, glm-5-lp #87);
  test_schedule_batch_req_pool_indices (1, 'SimpleNamespace' has no attribute 'multimodal_inputs'; fails on glm-5-lp, passes on upstream).
- 1 failing on upstream b34a52fcb8 and glm-5-lp alike: test_graph_pool_borrow (1).
- 6 environment, failing identically on upstream: test_fp8_blockwise_linear_backends (no flashinfer), test_hicache_nixl_storage (no nixl),
  test_ngram_worker_prompt (no ninja), test_cuda_vmm_utils (CUDA), test_hf_transformers (9, venv transformers),
  test_serving_deepseek_recipe (15 on upstream, 13 on glm-5-lp).
test_prefill_cuda_graph_runner passes again.
