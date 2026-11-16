# GB300 serving-configuration sweep: TP4 without MTP scores highest at concurrency 8 on a short multi-turn workload

## Context

No serving configuration had been compared on GB300. Eight candidates on one four-GPU node cover TP4 against DEP4, BF16 against FP8 KV, the `flashmla_sparse` against the `trtllm` DSA routes, MTP on against off and the window against the full-length KV layout, under one closed-loop four-turn chat workload and an SLO of P90 TTFT ≤ 3 s and P90 interactivity ≥ 30 tokens/s.

## Outcome

At `dbfef91e` on 4× GB300, all 8 candidates completed concurrency 1 / 2 / 4 / 8 with two repeats each (4,096 requests, none failed). The highest passing score is TP4 with BF16 KV and MTP off at concurrency 8: 2060.1 total tokens/s per GPU, 283.7 output tokens/s, P90 TTFT 0.913 s, P90 interactivity 43.1 tokens/s; DEP4 with FP8 KV and MTP off is next at 1735.4. With MTP, output throughput is higher at concurrency 1 (93.8 against 55.9 tokens/s at TP4) and lower at concurrency 8 (248.1 against 283.7), where every MTP candidate fails the interactivity gate; the MTP candidates pass up to concurrency 4. TP4 with FP8 KV on the `trtllm` routes scores within 3% of the BF16 candidates at concurrency 4 and holds 820,352 against 422,400 full-length KV tokens. The window and full-length layouts score within 4.4% at every passing level. The workload is narrow (inputs up to about 4.7K tokens, 128 output tokens per turn, thinking off, `ignore_eos`, concurrency up to 8); the sweep ran on FlashInfer 0.7.3 while the code pins 0.7.4, with one server launch per candidate, no accuracy evaluation, and no verification that the GPUs were used exclusively during the measurements.

## Evidence

- Code: `dbfef91e7d5128eeb4ce021c26ad54e409e41a3f`
- Model: `zai-org/GLM-5-1028-Provider`
- Experiment: [E03](repro.md)

## Follow-up

- [ ] Repeat the MTP on / off comparison above concurrency 4 on B300 and with longer outputs and thinking enabled (`<OWNER>`).
- [ ] Extend the grid above concurrency 8 for the MTP-off candidates and rerun the leading candidates on FlashInfer 0.7.4 (`<OWNER>`).
- [ ] Measure TP4 with the default MoE runner instead of `deep_gemm` (`<OWNER>`).
