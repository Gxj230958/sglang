# Window layout against full-length layout: serving speed compared

## Context

Pull request 67 makes the window layout the default. Its accuracy gates had passed ([E10](../data@2026-11-15-5e6ee4ed50fc91fee9c5a0484667ce6de2ba5640-window-default-dep8/repro.md), [E13](../data@2026-11-15-fb4015b5bdb6ed416beba624f365407089567b53-window-default-tp8/repro.md)); the serving speed of the two layouts had not been compared.

## Outcome

On 8x B300 at `fb4015b5`, with MTP on, the default layout and `--disable-hybrid-swa-memory` were benchmarked on the DEP8 `trtllm` FP8 and TP8 BF16 configurations with `bench_serving` random-ID workloads (2000 / 500 tokens at concurrency 1 and 32, 30000 / 300 at concurrency 4, two seeds) and, on TP8, an 8-turn chat that resends its history. No speed difference attributable to the layout is visible: output throughput, TTFT and TPOT differ within the spread between seeds and between two launches of the same layout, and multi-turn prefix reuse and TTFT are the same on both. The window layout holds 29% (DEP8) and 30% (TP8) more full-length tokens in the same memory. The pull-request description carries the same numbers. The first TP8 window arm overlapped another job on the shared node and was rerun; the DEP8 multi-turn rows used arm-specific prompts and are not comparable.

## Evidence

- Code: `fb4015b5bd` (pull-request head)
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`
- Experiment: [E14](repro.md)
- Pull request: radixark/sglang-zai pull request 67

## Follow-up

- [ ] Merge decision for pull request 67 (`<OWNER>`).
