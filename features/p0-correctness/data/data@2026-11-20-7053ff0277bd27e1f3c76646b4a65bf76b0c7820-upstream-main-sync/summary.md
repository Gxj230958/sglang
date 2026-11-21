# E31 summary

Candidate `7053ff0277bd27e1f3c76646b4a65bf76b0c7820` integrates `glm-5-lp` `13fa8258d2404deedfac9c114c43c4e4069f39b5` with upstream `main` `2b248971db8c8c349586c3757663be9cba5e366d`. It is pushed to `sync/glm-5-lp-on-upstream-main` and has not landed on `glm-5-lp`.

The matched GB300 TP4 FP8-KV EAGLE gate passes:

| Arm | Correct | Accuracy | Stop | Length | Errors | Accept length >=16, mean / median |
|---|---:|---:|---:|---:|---:|---:|
| Baseline | 1249/1319 | 94.69% | 1318/1319 | 1 | 0 | 2.658 / 2.680 |
| Candidate | 1252/1319 | 94.92% | 1319/1319 | 0 | 0 | 2.653 / 2.655 |

Both ranks use model revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`, bound by matching config, weight-index and tokenizer metadata hashes. Tier 1 and Tier 2 pass. Independent raw-sample and log recomputation returns `PASS` in [verify.json](verify.json).

This is non-release integration evidence. It does not validate DEP/MegaMoE, PD, HiSparse, unified memory, DeepEP 0.1.3 or the locked image, and it does not select a performance profile.
