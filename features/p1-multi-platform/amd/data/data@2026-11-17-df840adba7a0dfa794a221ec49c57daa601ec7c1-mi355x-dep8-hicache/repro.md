# E02 MI355X DEP8 with the window layout, HiCache L2/L3, parsers, and SPEED-Bench acceptance — data@2026-11-17-df840adba7a0dfa794a221ec49c57daa601ec7c1-mi355x-dep8-hicache

This round brings up expert plus attention data parallelism (DEP8) with the hybrid window KV layout and MTP on 8 MI355X. It fixes a decode-graph mismatch across DP ranks that produced garbage output. On that deployment it then validates host (L2) and file (L3) HiCache with NVIDIA HiCache E03's probe sequence, checks the reasoning and tool-call parsers, and measures the MTP draft's SPEED-Bench acceptance length as the local acceptance reference for AgentX.

Status: non-release; single runs on an unlocked environment.

## Environment

- Hardware and container: as [E01](../data@2026-11-16-2dff6ce96790b25cf42ef47557f99472e8e9deaf-mi355x-mtp-serving/repro.md) (8x MI355X gfx950, ROCm 10.0.0, torch 2.11.0+rocm10.0.0, triton 3.8.0, amd-aiter 0.1.26.dev144, image digest not recorded). The host was rebooted between E01 and this round.
- Model: `zai-org/GLM-5-1028-Provider` at revision `66c3fe71d4c4ab43efac5bb0d2be6dea3a75d089`; its NextN head is the MTP draft.
- Evaluator: sgl-eval `0.1.3`. SPEED-Bench client: SGLang's `bench_serving` from the same checkout.

## Code

`radixark/sglang-zai`, branch `amd_support`:

| Commit | Content | Used by |
|---|---|---|
| `7147d9686db189b04b5b43cc2d8d938fd51e2b91` | E01's last commit | `dep8_w` (invalid run, below) |
| `df840adba7a0dfa794a221ec49c57daa601ec7c1` | DSA: capture only the sparse decode graph under attention DP | `dep8_w2` (working tree equal to this commit, committed after the run), `dep8_hc`, `dep8_l3a`, `dep8_l3b` |

## Setup

Scripts: [scripts/v3/](../../scripts/v3/) ([CHANGES.md](../../scripts/v3/CHANGES.md)) on top of v2's `launch.sh` (TP8, bf16 KV, triton DSA backends, `--reasoning-parser glm45 --tool-call-parser glm47`). DEP8 with the window layout and MTP:

```bash
SGLANG_GLM_LOOP_ENABLE_HYBRID_SWA=1 scripts/v2/start_bg.sh <name> 30000 \
  --tp-size 8 --attn-dp-size 8 --ep-size 8 --moe-a2a-backend none \
  --mem-fraction-static 0.85 --context-length 262144 --chunked-prefill-size 32768 \
  --max-running-requests 256 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph \
  --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 \
  --speculative-num-draft-tokens 4 --speculative-draft-model-path <model> --enable-cache-report
```

- HiCache L2 (`dep8_hc`): plus `--enable-hierarchical-cache --hicache-size 200 --hicache-write-policy write_through`.
- HiCache L3 (`dep8_l3a`, then `dep8_l3b` after a full restart): the L2 flags plus `--hicache-storage-backend file`, with `SGLANG_HICACHE_FILE_BACKEND_STORAGE_DIR` on local disk.

Per DP rank the KV pool holds 1,477,248 full-layer and 147,712 window tokens (127.44 GB plus 4.44 GB, bf16). With `--hicache-size 200` each rank allocates a 2,123,648-token host pool (193.27 GB, packed with the MTP draft's layer) plus 6.17 GB for the DSA indexer.

## Workload

- GSM8K: full test split through `sgl-eval run gsm8k --temperature 1.0 --top-p 0.95 --num-threads 64`, server-default thinking, no `max_tokens`. These servers run with a 262,144-token context, so a non-terminating generation runs to about 262K tokens. NVIDIA's comparison rounds ran at 32,768 tokens, which ends such a generation at 32K.
- Prefix-reuse probe ([`midfork.py`](../../scripts/v3/midfork.py), HiCache E03's): a 6680-token record document, then six greedy, thinking-off requests. They are, in order: first; identical; a different question at the end; the document forked in the middle (late record); the forked document again (early record); and a follow-up turn. All probe and fill requests are pinned to DP rank 3 with `X-Data-Parallel-Rank`.
- L2 sequence ([`hc_dep8.sh`](../../scripts/v3/hc_dep8.sh)): probe, then `hicache.py fill 260` on rank 3, then probe again, then full GSM8K. The fill is 260 documents of about 6.7K tokens, about 1.74M tokens in total, more than the rank's 1.477M-token GPU pool, so LRU evicts the first probe's prefix from the GPU. L3: probe, restart on the same storage directory, probe.
- Parser smoke ([`parser_smoke.py`](../../scripts/v3/parser_smoke.py)): greedy requests through `/v1/chat/completions` on `dep8_hc`.
- SPEED-Bench acceptance: InferenceX's collector settings (`benchmarks/single_node/speedbench/glm5.3_fp4_b300_sglang.sh` at InferenceX `67c3ed26`). The 80 `qualitative`/`coding` prompts are built with [`speedbench_prep_coding.py`](../../scripts/v3/speedbench_prep_coding.py), with chat-template default thinking (on), temperature 1.0, top_p 0.95, 4096 output tokens without ignore-EOS, and 32 concurrent requests:

```bash
python -m sglang.bench_serving --backend sglang --port 30000 --model <model> \
  --dataset-name speed-bench --dataset-path qualitative_coding.jsonl \
  --speed-bench-output-len 4096 --num-prompts 80 --max-concurrency 32 \
  --temperature 1.0 --top-p 0.95 --disable-ignore-eos --output-details
```

  It ran on `dep8_hc` (MTP 3/1/4) alongside that server's GSM8K. Acceptance length is a per-request property, so the concurrent load does not change it.

## Results

### DEP8 decode-graph fix

`dep8_w` (at `7147d968`) answered short single requests with `!!!!`, and its GSM8K showed low acceptance and runaway generations; the run was stopped and is not scored. On ROCm, `create_attention_graph_variants` captures a dense decode graph (no indexer, KV length ≤ Top-K) and a sparse one, and each forward selects one from the batch's longest request. Under attention DP each rank selected from its own batch: an idle rank took the sparse graph and a rank with short requests the dense one. The ranks then replayed different graphs around the shared MoE collectives. `df840adb` captures only the sparse graph, which serves every length, under attention DP, with a unit test (`test_dsa_graph_variants.py`). Target-verify capture time fell from 103 s to 30 s.

### Correctness

| Run | Configuration | Accuracy | Stop | Truncated | Errors |
|---|---|---:|---:|---:|---:|
| `dep8_w2` | DEP8 + window + MTP | 94.92% (1252/1319) | 99.92% | 1 | 0 |
| `dep8_hc` | the same plus HiCache L2 | 95.45% (1259/1319) | 99.85% | 2 | 0 |

The NVIDIA references range from 94.01% to 96.06% accuracy and from 99.24% to 100% stop rate. Each truncation is a generation that ran to the 262K-token context. The one in `dep8_w2` answered `\boxed{168}` and then looped on a tool-call-like string; at a 32K context it would have ended at 32K. For `dep8_w2`, acceptance length over the `Decode batch` lines of its first 11 minutes, while most requests were active, is 2.52. The NVIDIA GSM8K rounds range from 2.54 to 2.86, and their means include the tails. The `dep8_hc` window also contains the SPEED-Bench requests, so its acceptance length is not reported.

### HiCache on DEP8 + window + MTP

| Step | Prefix-reuse probe | `cached_tokens` in request order |
|---|---|---|
| L2, before the fill | 6/6 correct, 6/6 `stop` | 0 / 6656 / 6656 / 0 / 6656 / 6656 |
| L2, after the fill (host restore) | 6/6 correct, 6/6 `stop` | 6656 / 6656 / 6656 / 6656 / 6656 / 6656 |
| L3, first server | 6/6 correct, 6/6 `stop` | 0 / 6656 / 6656 / 0 / 6656 / 6656 |
| L3, after a full restart (storage restore) | 6/6 correct, 6/6 `stop` | 6656 / 6656 / 6656 / 6656 / 6656 / 6656 |

After the first L3 probe the storage directory held 328 files (932 MB). The restarted server logged 2 `HiCache prefetch success` lines. The pattern matches NVIDIA HiCache E03 on 4x GB300 TP4. The servers ran without metrics, so the host load-back is inferred from the pool sizes rather than counted.

### Parsers (`glm45` reasoning, `glm47` tool calls)

| Check | Result |
|---|---|
| One tool call: `finish_reason=tool_calls`, name and arguments parsed, no markers in content | Pass |
| Streaming reconstruction equals the non-streaming call | Pass |
| Two parallel calls with distinct ids | Pass |
| `tool_choice=required` | Pass |
| Follow-up turn with a tool result | Pass |
| Thinking off: no `reasoning_content` | Pass |
| Thinking on, trivial prompt: the model itself emits `</think>` first, so `reasoning_content` is empty; a harder prompt returns 956 characters of reasoning routed to `reasoning_content` | Model behavior |
| `tool_choice=none`: the model emitted a raw tool call, which lands in `content` | Serving behavior shared with CUDA: SGLang keeps the tools in the prompt and skips parsing |

### SPEED-Bench acceptance length (MTP 3/1/4)

| Prompts | Completed | Output tokens | Acceptance length |
|---:|---:|---:|---:|
| 80 | 80 | 246,103 | 2.49 |

InferenceX has no golden acceptance curve for this model. Its curves for the sibling models at three draft tokens are GLM-5.2-FP8 2.99, GLM-5.3-NVFP4 2.94 and GLM-5.3-Flash 3.00.

Conclusions:

1. DEP8 with the window layout and MTP runs correctly on MI355X once every DP rank replays the same decode graph: GSM8K 94.92% with 99.92% stop. It holds about 11.8M full-layer tokens over the node, against 1.02M for TP8 without the window layout.
2. HiCache L2 and L3 work on that deployment. After eviction to host, and after a restart from file storage, the full 6656-token prefix is reused and all probe answers stay correct. GSM8K with HiCache scores 95.45% with 99.85% stop.
3. The parsers behave as specified for tool calls and reasoning routing. The two non-passing rows are model and shared serving behavior, not AMD differences.
4. The draft accepts 2.49 tokens per verify at three draft tokens on SPEED-Bench coding. This is a local calibration on MI355X, not a reference-platform golden value. Local AgentX runs use it with SGLang's acceptance simulation.

## Data and Figures

- [`dep8-gsm8k/`](dep8-gsm8k/): `dep8_w2` sgl-eval metrics and predictions.
- [`hicache/`](hicache/): script status, the four probe records, the fill log, and GSM8K metrics and predictions.
- [`parsers/parser_smoke.json`](parsers/parser_smoke.json): every parser check with its response.
- [`speedbench/`](speedbench/): `bench_serving` log and per-request output.
- [`logs/`](logs/): server logs without AITER's per-kernel lines (`dep8_w`, `dep8_w2`, `dep8_hc`, `dep8_l3a`, `dep8_l3b`).
