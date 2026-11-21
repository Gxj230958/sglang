# Ready for review: glm-5-lp on upstream main

- Candidate: `710a842c5741dade3ecd7d8583ef622745dcd9f2`, radixark/sglang-zai branch `sync/glm-5-lp-on-upstream-main`; one commit `Merge branch 'main' into glm-5-lp`, parents `glm-5-lp` then `main`. `glm-5-lp` fast-forwards to it.
- Tested tree: `9ab79bb1b50b67bbc9a1e7d75fbdc8ebddf33aff` (identical to the candidate's tree).
- Sources: radixark/sglang-zai `glm-5-lp` `45bff30acfb5ec97673046ea7b8d36b822bbc520` (re-checked unchanged right before the push) + sgl-project/sglang `main` `8171e9a4f5418ddad2dda911b66605b9982cce7b` (sglang-zai `main` fast-forwarded to it).
- Tier 1 PASS. Tier 2 PASS on 4x GB300, full GSM8K 1319, baselines re-measured on `45bff30acf`:
  - TP4 FP8 KV + EAGLE: candidate 95.07% / stop 100% vs baseline 94.84% / 100%.
  - DEP4 + megamoe (DeepEP 0.1.3 / NCCL 2.31.2 loaded on the candidate): two-run mean 95.87% vs 94.96%; stop 100% / 99.92% vs 100% / 99.77%.
- Report: `reports/20261121T0550Z.md` (one conflict, `mem_cache/allocator/hisparse.py`; open questions at the end).
