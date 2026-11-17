# Matched KV sweep completed

At runtime `01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb`, all four FP8/NVFP4 and BF16/FP8-KV configurations completed 48 loads with 5,120 successful, nonempty requests. All 24 aggregate points passed the frozen SLO. At C32, NVFP4 gains 21.35% with BF16 KV and 19.24% with FP8 KV over the corresponding FP8 weights.

The [round](repro.md) preserves raw evidence and independent audits. Full GSM8K stop nonregression remains unmet; runtime publication stays held. Continue paired natural-MTP and controlled-acceptance measurements as separate lanes. Tracking PR: https://github.com/radixark/sglang-zai/pull/74.
