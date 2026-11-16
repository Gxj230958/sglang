# TP8 with FP8 KV passes GSM8K on B300 and holds 1.94× the KV tokens of BF16

## Context

On the merged head the TP8 gates all used BF16 KV with the `flashmla_sparse` DSA routes, and FP8 KV had only been gated under DEP8 with the `trtllm` routes. TP8 with FP8 KV is the plain-TP configuration with the larger KV capacity, so it needed its own gate and a speed comparison against BF16 on the same day.

## Outcome

On 8× B300 at `dbfef91e` with FlashInfer 0.7.4 and MTP, TP8 with `--kv-cache-dtype fp8_e4m3` and the `trtllm` DSA routes completes full GSM8K at 95.07% accuracy and 99.77% stop rate (3 of 1319 requests ran until the context was full), with a counter-based accept length of 2.6320. The KV pool holds 2,321,664 full-length tokens against 1,195,520 for BF16 under the same memory fraction. Against a BF16 `flashmla_sparse` server launched right after it, output throughput was 211.3 / 220.3 against 231.8 / 234.7 tokens/s at concurrency 1, 1203.8 / 1215.2 against 1125.4 / 1193.5 at concurrency 32, and 145.2 / 144.2 against 128.9 / 127.6 on 30K-token inputs at concurrency 4. One launch per arm in a fixed order and one unseeded GSM8K run; the arms differ in both KV dtype and DSA backend; the source tree was not re-verified for this round.

## Evidence

- Code: `dbfef91e7d5128eeb4ce021c26ad54e409e41a3f`
- Model: `zai-org/GLM-5-1028-Provider`
- Experiment: [E17](repro.md)

## Follow-up

- [ ] Repeat the concurrency-1 comparison with more launches and separate the KV dtype from the DSA backend (`<OWNER>`).
- [ ] Measure how often a GSM8K request at temperature 1.0 runs until the context is full, across seeds and KV dtypes (`<OWNER>`).
