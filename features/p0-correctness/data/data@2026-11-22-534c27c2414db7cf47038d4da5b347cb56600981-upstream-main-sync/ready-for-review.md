# Ready for review: glm-5-lp on upstream main

- Candidate: `534c27c2414db7cf47038d4da5b347cb56600981`, radixark/sglang-zai branch `sync/glm-5-lp-on-upstream-main`; one commit `Merge branch 'main' into glm-5-lp`, parents `glm-5-lp` then `main`. `glm-5-lp` fast-forwards to it.
- Tested tree: `fbe85615b3c05c40609d30f50672ee901e8eb1e8` (identical to the candidate's tree).
- Sources: radixark/sglang-zai `glm-5-lp` `746e19554cf257b2db34bdb8afa85077ea2fb14e` (unchanged at 15:43 UTC) + sgl-project/sglang `main` `b34a52fcb87a0d1c1190d16e0b5b3c4f867f591f` (= radixark/sglang-zai `main`).
- Tier 1 PASS. Tier 2 PASS on mobius-8gb300-share, one run per side against glm-5-lp `746e19554c`:
  - (i) TP4 FP8 KV + EAGLE, full GSM8K 1319: 94.54% / stop 1317 + length 2 / accept 2.680 vs 95.45% / 1319 / 2.688 (passes at the limit on accuracy and non-stop count).
  - (ii) DEP4 + megamoe, full GSM8K 1319: 95.91% / stop 1319 / accept 2.693 vs 95.07% / 1317 + 2 / 2.662.
  - (iii) full serving recipe, harness `1e31bef84893`: `gate.py` LEG PASS; AgentX c64 1.09x total / 1.07x output tok/s, TTFT p50 1.21x; cache truth all five pass.
- Conflicts: `mooncake/conn.py` (upstream transport refactor #46460; glm-5-lp's per-batch descriptor bound re-applied inside `_transfer_copies`), `glm5_next.py`, `test_mooncake_transfer_batching.py`.
- Report: `reports/20261122T1545Z.md` (open questions at the end).
- Evidence record: Correctness E33, radixark/sglang-zai#119 into `glm-5-lp-track` (open).
