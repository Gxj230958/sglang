# E32 summary

Candidate `710a842c5741dade3ecd7d8583ef622745dcd9f2` (tree `9ab79bb1b50b67bbc9a1e7d75fbdc8ebddf33aff`) is one `Merge branch 'main' into glm-5-lp` commit integrating `glm-5-lp` `45bff30acfb5ec97673046ea7b8d36b822bbc520` with upstream `main` `8171e9a4f5418ddad2dda911b66605b9982cce7b`. After review, `glm-5-lp` was fast-forwarded to it.

Both Tier 2 legs pass against baselines of `45bff30acf` measured in the same round on 4x GB300, full GSM8K, temperature 1.0 / top_p 0.95:

| Leg | Arm | Correct | Accuracy | Stop | Length | Errors |
|---|---|---:|---:|---:|---:|---:|
| TP4 | Baseline | 1251/1319 | 94.84% | 1319/1319 | 0 | 0 |
| TP4 | Candidate | 1254/1319 | 95.07% | 1319/1319 | 0 | 0 |
| DEP4 + megamoe run 1 | Baseline | 1256/1319 | 95.22% | 1319/1319 | 0 | 0 |
| DEP4 + megamoe run 2 | Baseline | 1249/1319 | 94.69% | 1316/1319 | 3 | 0 |
| DEP4 + megamoe run 1 | Candidate | 1272/1319 | 96.44% | 1319/1319 | 0 | 0 |
| DEP4 + megamoe run 2 | Candidate | 1257/1319 | 95.30% | 1318/1319 | 1 | 0 |

Each side ran with its own dependency pins: the baseline with sgl-deep-ep 0.1.2.post1 / NCCL 2.30.7, the candidate with sgl-deep-ep 0.1.3 / NCCL 2.31.2, confirmed from the loaded libraries. Independent recomputation from the raw samples returns `PASS` in [verify.json](verify.json).

This is non-release integration evidence. It does not validate glm-5-lp #110's fused FlashMLA prefill, HiSparse, PD, unified memory or the locked image, and it does not select a deployment profile.
