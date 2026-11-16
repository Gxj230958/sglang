# FlashInfer 0.7.4 and H200 validated on the merged window-default head

## Context

radixark/sglang-zai pull request 67 merged into `glm-5-lp` as `dbfef91e` on 2026-11-15, making the window sub-pool the default layout. Every earlier gate of this line ran with FlashInfer 0.7.3 on Blackwell although the code pins 0.7.4, and H200 had not been run since `a15aa7c3`.

## Outcome

On `dbfef91e` with FlashInfer 0.7.4, MTP and the default layout, full GSM8K passed on 8× B300 at TP8 (96.06%, 100% stop) and DEP8 `trtllm` FP8 (95.07%, 100% stop), and on 8× H200 at TP8 with `flashmla_sparse` and BF16 KV (94.77%, 99.85% stop, 2 truncated). H200 needs `sgl-fa3==0.1.0`, which the image lacks, and holds 139,136 full-length KV tokens under the B300 TP8 flags against 1,195,520 on B300; the eval triggered three request retractions there. Single unseeded runs; no claim about a FlashInfer effect on accuracy or accept length.

## Evidence

- Code: `dbfef91e7d5128eeb4ce021c26ad54e409e41a3f`
- Model: `zai-org/GLM-5-1028-Provider`
- Experiment: [E15](repro.md)
- Pull request: radixark/sglang-zai pull request 67 (merged)

## Follow-up

- [ ] Decide the H200 serving configuration (context length, concurrency, KV dtype) given the KV capacity (`<OWNER>`).
- [ ] Add `sgl-fa3` to the H200 image or document the install step (`<OWNER>`).
