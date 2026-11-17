# Current integration Rust correctness

The exact integration `01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb` completed full FP8 GSM8K on four GB300 GPUs: 95.22% accuracy, 99.77% stop, three output-limit truncations and zero errors. All four ranks selected the default Rust tree core. NVFP4 GSM8K 100 sanity scored 95%, with 99% stop and zero errors. Source, prediction and artifact hashes were independently checked.

[E18 reproduction and raw evidence](repro.md) own these results. Full NVFP4 natural-MTP validation and the remaining platform/feature gates are pending. Performance claims continue to require matched FP8/NVFP4 measurements on one exact source and environment.
