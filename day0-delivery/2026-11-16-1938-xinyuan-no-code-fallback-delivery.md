# November 18 fallback delivery

## Decision

Deliver a fallback Docker image and cutoff commit to Z.ai by Wednesday, November 18, 2026. Finish the basic-feature GPU matrix and required evaluation first, then select the best usable performance configuration. Freeze the accepted source, image, checkpoint revisions and launch configuration after Z.ai benchmarks accuracy.

## Execution order

1. Complete GPU coverage for the required serving, MTP, Rust cache, KV, parallelism, HiCache/HiSparse and PD paths. Reuse existing evidence only where the source and configuration match. Resolve delivery blockers and record unsupported cells explicitly.
2. Review full accuracy and finish-reason results on the intended cutoff. The current integration's stopping nonregression remains unresolved; measured performance alone does not qualify it for delivery.
3. Run bounded, matched FP8/NVFP4 sweeps to fill the gaps needed to choose the best usable configuration. Reuse compatible completed measurements. Select using throughput, latency, stability and quality together. Keep simulated acceptance separate from natural MTP deployment measurements.
4. Build the fallback image remotely from the selected source and pinned dependencies. Verify its source, native Rust artifacts and image-level serving/evaluation behavior; record the registry digest.
5. Hand off the image digest, full cutoff commit, checkpoint revisions, exact commands, feature/evaluation matrix, performance choice and evidence links. Record Z.ai's accuracy result against that candidate, then freeze it.

Basic-feature validation precedes additional MoE/performance sweeps. Broader backend exploration and extra optimization matrices follow this delivery unless needed to resolve a delivery blocker. AgentX performance and further HumanX diagnostics remain deferred.

## Current status

The [current validation and performance index](../README.md) contains the verified rounds. Current runtime `01d0a662d14a2b64d6a53fb48182fa79b5ddcbeb` is an integration under evaluation. The cutoff commit, fallback image digest and final performance profile have not been selected. NVFP4 remains a performance-only checkpoint; its measurements do not establish accuracy parity.

## Handoff gates

- [ ] Required basic features have source-bound GPU evidence.
- [ ] Accuracy, stop/length/error counts and unresolved limits are reviewed for the cutoff.
- [ ] The selected profile has matched FP8/NVFP4 measurements on the candidate environment.
- [ ] The Docker digest and native artifacts match the tested source and dependency pins.
- [ ] Exact launch and evaluation commands reproduce the selected configuration.
- [ ] Z.ai accuracy results identify the same image, source and model revisions.
- [ ] Accepted artifacts are frozen after that benchmark.

See [artifact locks and validation gates](README.md) and [Docker provenance](docker/README.md).
