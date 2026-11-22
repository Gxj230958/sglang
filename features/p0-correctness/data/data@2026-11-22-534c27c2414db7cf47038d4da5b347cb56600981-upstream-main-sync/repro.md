# E33 Upstream main sync correctness and full serving recipe — data@2026-11-22-534c27c2414db7cf47038d4da5b347cb56600981-upstream-main-sync

## Environment

- Machine: `mobius-8gb300-share`, two ranks with 4x NVIDIA GB300 each. Tier 2 used one rank per arm; the full serving recipe used both ranks, with prefill, store and router on rank 0 and decode on rank 1.
- Container: the box's `/opt/sglang` environment; no immutable image digest was captured, so this round is non-release.
- Model: `zai-org/GLM-5-1028-Provider` at tracked FP8 revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`, including its own NextN draft. The launch path is unchanged from Correctness E32. [checkpoint-receipt.json](checkpoint-receipt.json) carries that round's matching config, weight-index, tokenizer and tokenizer-config hashes; the weight shards were not rehashed for this round.
- Software: torch 2.14.1+cu130, transformers 5.19.0, flashinfer-python 0.7.4, sglang-kernel 0.4.11, sgl-flash-mla 1.0.5, sgl-deep-gemm 0.2.9 with the GLM patch, sgl-deep-ep 0.1.3, nvidia-nccl-cu13 2.31.2, mooncake-transfer-engine-cuda13 0.3.14 and sglang-router 0.3.2. Loaded NCCL runtime is 23102.
- Evaluator: sgl-eval 0.1.3. Full recipe harness: `1e31bef84893`, byte-identical on both arms.

## Setup

1. Verify [SHA256SUMS](SHA256SUMS) and the local archive hashes in [EVIDENCE-STORAGE.md](EVIDENCE-STORAGE.md).
2. Check out the exact arm commit and put its `python/` first on `PYTHONPATH`, followed by the dependency, patched DeepGEMM, FlashInfer and kernel overlays. Preload the overlay `libnccl.so.2`.
3. Launch the two colocated configurations without `--context-length` and with CUDA graphs enabled:

```bash
# TP4
python -m sglang.launch_server --model-path /path/to/GLM-5-1028-Provider \
  --host 127.0.0.1 --port 31200 --dist-init-addr 127.0.0.1:31201 \
  --tp-size 4 --kv-cache-dtype fp8_e4m3 \
  --speculative-algorithm EAGLE --reasoning-parser glm45

# DEP4 + megamoe
SGLANG_OPT_DEEPGEMM_MEGA_MOE_NUM_MAX_TOKENS_PER_RANK=8192 SGLANG_DP_USE_GATHERV=1 \
python -m sglang.launch_server --model-path /path/to/GLM-5-1028-Provider \
  --host 127.0.0.1 --port 31200 --dist-init-addr 127.0.0.1:31201 \
  --tp-size 4 --ep-size 4 --attn-dp-size 4 --moe-runner-backend megamoe \
  --kv-cache-dtype fp8_e4m3 --mem-fraction-static 0.9 --chunked-prefill-size 32768 \
  --speculative-algorithm EAGLE --reasoning-parser glm45
```

4. Evaluate each colocated server with `sgl-eval run gsm8k --base-url http://127.0.0.1:31200/v1 --temperature 1.0 --top-p 0.95`.
5. For the full serving recipe, run `qa/run_full_recipe.sh --src <exact-source> --ovl <dependency-overlays> --tag gate-<revision> --variant full --conc 64` on both ranks. The recipe uses DEP4 + megamoe with FP8 KV and EAGLE on both roles, prefill host L2 plus standalone Mooncake store L3, prefill memory fraction 0.90 and decode memory fraction 0.96. Launch commands and resolved versions are preserved in each leg's `result.json`.
6. Run `python3 verify.py` to recompute every gate from the raw samples, result files, versions and logs. The captured output is [verify.json](verify.json).

## Commit

- Candidate: `534c27c2414db7cf47038d4da5b347cb56600981`, tree `fbe85615b3c05c40609d30f50672ee901e8eb1e8`, clean, on `radixark/sglang-zai` branch `sync/glm-5-lp-on-upstream-main`. One commit, `Merge branch 'main' into glm-5-lp`, with parents `746e19554cf257b2db34bdb8afa85077ea2fb14e` and upstream `main` `b34a52fcb87a0d1c1190d16e0b5b3c4f867f591f`.
- Baseline: `glm-5-lp` `746e19554cf257b2db34bdb8afa85077ea2fb14e`. TP4 and DEP4 baselines were measured in the preceding round and reused from cache; the full-recipe baseline was measured in this round.
- Merge base: `8171e9a4f5418ddad2dda911b66605b9982cce7b`.
- Candidate source archive SHA-256: `71b05a2a2d0868384d2321cf632a3ec11968ef9391151f0f6394851bb3e465eb`.
- Remote readback during this review: `sync/glm-5-lp-on-upstream-main` is `534c27c2414db7cf47038d4da5b347cb56600981`; `glm-5-lp` remains `746e19554cf257b2db34bdb8afa85077ea2fb14e`. The candidate has not landed on `glm-5-lp` as of this record.

## Scripts

- [integration-report.md](integration-report.md) — merge, conflict, dependency and Tier 1/Tier 2 report from the run.
- [independent-report.md](independent-report.md) — independent recomputation and evidence review.
- [ready-for-review.md](ready-for-review.md) — review hand-off written after the run.
- [verify.py](verify.py) — recomputes sample counts, finish reasons, launch settings, accept lengths, full-recipe gates and terminal status.
- [scripts/](scripts/) — launch, evaluation, capture, audit and CPU test scripts.
- [tier1/](tier1/) — CPU test summaries, failure classification and pre-commit logs.
- Temporary changes: none; each arm ran its exact commit.

## Workload

- Colocated GSM8K: full test split, 1319 unique examples per run, 64 evaluator threads, temperature 1.0, top_p 0.95, no explicit output-token limit. One TP4 run and one DEP4 run per arm; baseline runs are from the immediately preceding candidate round.
- Full-recipe GSM8K: the same 1319-question protocol through the PD router, one run per arm.
- AgentX: `semianalysis_cc_traces_weka_062126`, concurrency 64, five-minute warmup followed by a 900-second measured window. Client cancellations at window close are reported separately from errors.
- Cache truth: 29 probes per arm covering device, host and standalone-store restores, a prefill restart with the store retained, and a fresh-store negative control. The harness allows 2048 tokens per probe and checks the planted seven-digit answer in the returned content.
- Health: server, router, store and client logs are checked for tracebacks, process crashes, transfer errors, disaggregation timeouts and Python tree-core fallback.

## Results

| Metric | Baseline `746e19554c` | Candidate `534c27c241` | Delta |
|---|---:|---:|---:|
| TP4 correct / 1319 | 1259 | 1247 | -12 |
| TP4 accuracy | 95.45% | 94.54% | -0.91 pt |
| TP4 stop / length | 1319 / 0 | 1317 / 2 | -2 / +2 |
| TP4 accept length at >= 16 running | 2.688 | 2.680 | -0.008 |
| DEP4 + megamoe correct / 1319 | 1254 | 1265 | +11 |
| DEP4 + megamoe accuracy | 95.07% | 95.91% | +0.84 pt |
| DEP4 + megamoe stop / length | 1317 / 2 | 1319 / 0 | +2 / -2 |
| DEP4 + megamoe accept length at >= 8 running | 2.662 | 2.693 | +0.031 |
| Full-recipe GSM8K accuracy | 93.86% | 94.54% | +0.68 pt |
| Full-recipe GSM8K stop | 1319 | 1319 | 0 |
| Full-recipe accept length | 2.603 | 2.559 | -0.044 |
| AgentX requests / errors | 1097 / 0 | 1174 / 0 | +77 / 0 |
| AgentX total tok/s | 85,401.7 | 92,770.8 | 1.09x |
| AgentX output tok/s | 933.4 | 998.6 | 1.07x |
| AgentX TTFT p50 | 12.1 s | 14.6 s | 1.21x |
| AgentX ITL p50 | 18.8 ms | 18.9 ms | +0.1 ms |
| AgentX accept length | 2.394 | 2.444 | +0.050 |
| Cache-truth probes | 29/29 correct, all `stop` | 29/29 correct, all `stop` | PASS |

Conclusions:

1. TP4 passes: candidate has two non-stop finishes, within the absolute cap of three and the baseline-plus-two cap; accuracy is within 1.0 point and accept length is within 0.2 of baseline.
2. DEP4 + megamoe passes the same accuracy, stop and accept-length criteria.
3. The full serving recipe passes every absolute and relative gate: AgentX total and output throughput are at least 90% of baseline, TTFT p50 is at most 130% of baseline, and all cache-truth and health checks pass.
4. The two TP4 `length` finishes are reasoning loops to the 262144-token context limit, not evaluator errors.

## Limits and release status

This is candidate-integration evidence, not a release selection. The image digest is unpinned, weight shards were not rehashed, and the colocated baseline measurements are reused from the preceding round. Not exercised: #115 EP block-FP8 decode MoE kernels, #110 fused FlashMLA extra-KV prefill, HiSparse, unified memory, DCP/CP, Marlin MXFP8 and trtllm-gen MXFP4 paths, cu134 image build, and AMD/NPU. The re-applied Mooncake descriptor-bound split path is unit-tested but was not observed end to end. AgentX TTFT tolerance needs calibration: the same baseline measured 16.0 s in the preceding round and 12.1 s here. The prefill SIGSEGV seen in an earlier round did not recur.

## Data and Figures

- [summary.md](summary.md) — concise result and gates.
- [verify.json](verify.json) — independent recomputation output; all gates `PASS`.
- [terminal-snapshot.json](terminal-snapshot.json) — launch, readiness, evaluation and cleanup status.
- `baseline-tp4/`, `baseline-dep4/`, `candidate-tp4/`, `candidate-dep4/` — raw per-sample outputs, metrics, launch information, dependency versions and compressed logs for the colocated legs.
- `leg3/` — full-recipe result files, launch commands, per-sample GSM8K outputs, AgentX aggregate exports, cache-truth results, health summaries and compressed logs.
- [redacted-files.json](redacted-files.json) — original sizes and SHA-256 hashes of 48 files in which node addresses were replaced with `rank0` and `rank1`; unredacted evidence remains local.
- [EVIDENCE-STORAGE.md](EVIDENCE-STORAGE.md) — local source and result archive paths, sizes and hashes.
- No figures were generated.
