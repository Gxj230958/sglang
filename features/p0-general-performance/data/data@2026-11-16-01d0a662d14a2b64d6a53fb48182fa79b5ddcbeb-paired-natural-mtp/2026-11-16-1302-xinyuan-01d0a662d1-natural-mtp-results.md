# Natural MTP paired sweep completed

The [E07 round](repro.md) records 48 loads and 5,120 successful requests at runtime 01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb. All four FP8/NVFP4 weight and BF16/FP8 KV combinations pass the frozen SLO through C4. NVFP4 C4 scores exceed their matched FP8 cases by 3.78% and 7.75%, respectively. Raw timing reconstruction, actual Rust mappings, source integrity and terminal cleanup are verified.

Server seeds differ across arms; a separate fixed-seed controlled-MTP/MTP-off round is active. Full-GSM8K stopping nonregression remains unmet. Evidence is submitted through [tracking PR74](https://github.com/radixark/sglang-zai/pull/74).
