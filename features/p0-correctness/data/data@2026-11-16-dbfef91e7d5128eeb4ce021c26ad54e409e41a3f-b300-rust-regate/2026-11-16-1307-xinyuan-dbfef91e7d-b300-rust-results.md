# B300 Rust correctness suite completed

At runtime `dbfef91e7d5128eeb4ce021c26ad54e409e41a3f`, all three full GSM8K arms completed with eight mapped Rust ranks each. [E19](repro.md) records 1243/1315 correct/stop for TP8 BF16, 1251/1319 for TP8 FP8 KV, and 1245/1318 for DEP8, each out of 1319.

TP8 FP8 KV passes the observed comparison. BF16 and DEP8 stopping nonregression remains unmet. Raw records, counters, source integrity and final idle state are independently checked. H200 and current-source feature work remain open under [tracking PR74](https://github.com/radixark/sglang-zai/pull/74).
