# E33 summary

Candidate `534c27c2414db7cf47038d4da5b347cb56600981` (tree `fbe85615b3c05c40609d30f50672ee901e8eb1e8`) integrates `glm-5-lp` `746e19554cf257b2db34bdb8afa85077ea2fb14e` with upstream `main` `b34a52fcb87a0d1c1190d16e0b5b3c4f867f591f`. It is on `sync/glm-5-lp-on-upstream-main`; `glm-5-lp` remains `746e19554c` at the review readback.

All three verification legs pass on 2 x 4 GB300, using full GSM8K at temperature 1.0 / top_p 0.95 and the full serving recipe:

| Leg | Baseline | Candidate | Gate |
|---|---|---|---|
| TP4 | 95.45%, stop 1319, accept 2.688 | 94.54%, stop 1317 + length 2, accept 2.680 | PASS within all three tolerances |
| DEP4 + megamoe | 95.07%, stop 1317 + length 2, accept 2.662 | 95.91%, stop 1319, accept 2.693 | PASS |
| Full recipe GSM8K | 93.86%, stop 1319, accept 2.603 | 94.54%, stop 1319, accept 2.559 | PASS |
| Full recipe AgentX c64 | 1097 requests, 85,401.7 total / 933.4 output tok/s, TTFT p50 12.1 s | 1174 requests, 92,770.8 total / 998.6 output tok/s, TTFT p50 14.6 s | PASS: 1.09x / 1.07x / 1.21x |
| Cache truth and health | 29/29 probes correct, no errors | 29/29 probes correct, no errors | PASS |

[verify.json](verify.json) independently recomputes every result from raw samples and reports `PASS` for TP4, DEP4 + megamoe and the full recipe. Node addresses in 48 evidence files are replaced by rank labels; original hashes are in [redacted-files.json](redacted-files.json).

This is non-release integration evidence. The candidate has not landed on `glm-5-lp`; the image is not locked and this round does not select a deployment profile.
