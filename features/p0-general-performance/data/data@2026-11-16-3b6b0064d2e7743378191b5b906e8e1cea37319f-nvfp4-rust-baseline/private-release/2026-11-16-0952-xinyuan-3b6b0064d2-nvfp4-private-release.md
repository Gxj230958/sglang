# Private NVFP4 artifact verified

The performance-only checkpoint is published at [RadixArk/GLM-5-1028-Provider-NVFP4-perf](https://huggingface.co/RadixArk/GLM-5-1028-Provider-NVFP4-perf/tree/f2c64cebac62b1888c92c9d317adbb0b0aef5955), immutable revision `f2c64cebac62b1888c92c9d317adbb0b0aef5955`. Independent verification confirmed private visibility, the exact 163-file/439,756,337,764-byte inventory, 144 LFS object SHA256 values and 19 downloaded metadata hashes. See [verification](hf-independent-verification.json), [inventory](release-inventory.json) and the worker's [verification](hf-verification.json).

## Reproduce the measured inputs

Download the NVFP4 checkpoint at the immutable revision above. Its `conversion/` directory contains the converter, tensor audit, source provenance and the serving patch. [E04](../repro.md) describes the measured serving/workload contract and contains the raw outputs.

Download FP8 source weights from private `RadixArk/GLM-5-1028-Provider` revision `9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff`. For the FP8 arm, replace its `config.json` with [fp8-source-config.json](fp8-source-config.json), the exact evaluated configuration (SHA256 `99d7088de1960a51c0f1ae58553815c4c6c223fdbde44d13dc3ebca479e0c80f`). The provider's model index, tokenizer and tokenizer configuration match the measured hashes; its configuration differs. [Source metadata verification](source-metadata-verification.json) records this distinction.

On a devbox, start with a fresh SGLang checkout at `dbfef91e7d5128eeb4ce021c26ad54e409e41a3f`, then apply `conversion/runtime.patch` from the immutable NVFP4 checkpoint using `git apply --index`. The patch SHA256 is `644d3afda7709206a1c4e5e10caf4f3ce1036a7e1bc0f8d141c2337b45dd2e1a`. `git write-tree` must return `eb2a7f3befdc087c1945bdcd153ff02704ed989f`, exactly the source tree of measured commit `3b6b0064d2e7743378191b5b906e8e1cea37319f`. [Reconstruction verification](runtime-reconstruction.json) confirms this equality without relying on commit-message metadata.

Artifact publication is complete. The initial E04 capture preceded publication; this record supplies its immutable artifact handoff. Full quality parity, multimodal inference and production readiness remain unvalidated. The current development-head integration and subsequent paired performance sweeps require their own results.
