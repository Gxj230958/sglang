# Local archive storage

Source and result archives remain local and are not committed. Their extracted result files are preserved in this round, with logs and per-sample outputs gzip-compressed. Node addresses in 48 extracted files were replaced by rank labels; [redacted-files.json](redacted-files.json) records the original hashes.

| Archive | Local path | Bytes | SHA256 |
|---|---|---:|---|
| Baseline source | `/tmp/usync/run5/src-746e19554c.tar.gz` | 47840396 | `8d1d8ea67f5c19a1d0100d16535ec69d3e1ba986d188614d60143a65e2377cc1` |
| Candidate source | `/tmp/usync/run6/src-534c27c241.tar.gz` | 48050498 | `71b05a2a2d0868384d2321cf632a3ec11968ef9391151f0f6394851bb3e465eb` |
| Baseline colocated results | `/home/ubuntu/github_projects/sglang_worksapce/glm-next/upstream-sync/reports/20261122T0435Z-artifacts/tier2/baseline-746e19554c.tar.gz` | 1787257 | `bfba3a3121e4897d7eab06837a57cf7b09b845ed4516f01328b770a17a612722` |
| Candidate TP4 results | `/home/ubuntu/github_projects/sglang_worksapce/glm-next/upstream-sync/reports/20261122T1545Z-artifacts/tier2/candidate-534c27c241-tp4.tar.gz` | 913039 | `6143f9960b9ee7881a7a3355f86ec65d4e18e6089c679c0a93a99c3749357f9c` |
| Candidate DEP4 results | `/home/ubuntu/github_projects/sglang_worksapce/glm-next/upstream-sync/reports/20261122T1545Z-artifacts/tier2/candidate-534c27c241-dep4.tar.gz` | 940650 | `1d4ca461e799d30caf06252083185d0133e885c601d89c946fb7dff1b96b8f00` |

The unredacted full-recipe evidence remains at `/home/ubuntu/github_projects/sglang_worksapce/glm-next/upstream-sync/reports/20261122T1545Z-artifacts/leg3/`, with per-run subdirectories `gate-534c27c241/` and `gate-746e19554c/`. The original result files have SHA-256 `84276c4b9ea2a54d4349127dc39eccfa2f01edce287131abfaa743b584c374bf` and `bf41646d2f2cfb3e9e6a890e7c62e2f60e95c49417898e5743690c1dff0544c5`, respectively.
