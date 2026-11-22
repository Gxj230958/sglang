# E33 independent evidence review

## Method

The review used the extracted raw evidence rather than the report's aggregate claims alone. [verify.py](verify.py) recomputes the results and writes [verify.json](verify.json).

- Counted 1319 unique GSM8K examples per arm and independently summed `symbolic_correct` and `finish_reason` for all six evaluations.
- Checked evaluator metrics for zero errors, temperature 1.0, top_p 0.95 and no output-token cap.
- Checked exact source revisions, resolved launch settings, loaded DeepEP 0.1.3 / NCCL 2.31.2, absence of tracebacks, successful evaluator exit and zero GPU processes after teardown.
- Recomputed accept length from server-log lines at the documented running-request floors.
- Compared full-recipe AgentX aggregates with `summary.json`, checked all 29 cache-truth probes per arm, and checked health counters on both ranks.
- Recomputed every accuracy, non-stop, accept-length, throughput and TTFT gate locally.

## Recomputed results

| Lane | Baseline | Candidate | Result |
|---|---|---|---|
| TP4 | 1259 correct, stop 1319, accept 2.688 | 1247 correct, stop 1317 + length 2, accept 2.680 | PASS |
| DEP4 + megamoe | 1254 correct, stop 1317 + length 2, accept 2.662 | 1265 correct, stop 1319, accept 2.693 | PASS |
| Full-recipe GSM8K | 1238 correct, stop 1319, accept 2.603 | 1247 correct, stop 1319, accept 2.559 | PASS |
| Full-recipe AgentX | 1097 requests, 85,401.7 total / 933.4 output tok/s, TTFT p50 12.093 s, accept 2.394 | 1174 requests, 92,770.8 total / 998.6 output tok/s, TTFT p50 14.608 s, accept 2.444 | PASS: 1.09x / 1.07x / 1.21x |
| Cache truth | 29 correct answers, all `stop`, maximum 6 output tokens | 29 correct answers, all `stop`, maximum 7 output tokens | PASS |
| Health | No traceback, process crash, transfer error, disaggregation timeout or Python tree-core fallback | Same | PASS |

The candidate's two TP4 non-stop finishes satisfy both the absolute cap of three and the baseline-plus-two cap. Its accuracy is 0.91 point below baseline, within the 1.0-point tolerance. All other relative gates also pass. No numeric discrepancy was found against [integration-report.md](integration-report.md).

## Metadata and integrity

- Candidate source archive SHA-256 matches the run receipt: `71b05a2a2d0868384d2321cf632a3ec11968ef9391151f0f6394851bb3e465eb`.
- The remote sync branch contains candidate `534c27c2414db7cf47038d4da5b347cb56600981`. Remote `glm-5-lp` still reads `746e19554cf257b2db34bdb8afa85077ea2fb14e`; this review does not claim that the candidate landed.
- Both full-recipe arms use harness `1e31bef84893`. Every cache-truth answer is the planted code with `finish_reason=stop` and no reasoning content.
- Node addresses in 48 committed evidence files were replaced with `rank0` and `rank1`. [redacted-files.json](redacted-files.json) records each original path, byte size and SHA-256. Original source and result archives remain local as listed in [EVIDENCE-STORAGE.md](EVIDENCE-STORAGE.md).

## Limits

This is non-release integration evidence, not deployment selection. The colocated baselines come from the preceding round, the full-recipe baseline was re-measured, and weight shards were not rehashed. The container digest is not locked. The TTFT baseline has a 32% spread across two rounds, so its 1.30x tolerance needs calibration. The earlier prefill SIGSEGV did not recur, and the Mooncake descriptor-bound split path was not observed end to end.
