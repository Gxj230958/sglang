# NVFP4 priority and paired performance sweeps

## Decision

NVFP4 is the highest-priority performance workstream. Complete its Rust sanity, matched FP8/NVFP4 performance baseline and private artifact publication first. Every subsequent performance sweep includes NVFP4-version data.

## Scope

The requirement covers MoE/backend selection, MTP and concurrency, KV dtype and parallelism, breakable prefill CUDA graphs, and AgentX/HumanX serving optimization. Preserve completed FP8 measurements and add matched NVFP4 arms before closing a sweep. Unsupported hardware/backend combinations need an explicit unsupported or failed cell with evidence.

## Measurement contract

- Pin the same exact serving revision with support for both weight formats, dependency versions, hardware, workload, seeds and cache policy.
- Record weight quantization and KV-cache dtype independently.
- Keep controlled simulated-MTP comparisons at acceptance 3.5 for both formats and include MTP-off controls. Report natural-acceptance runs separately.
- Identify the converted checkpoint by immutable revision and tensor manifest. Its performance-only status and non-gating sanity scope remain explicit.
- Treat Rust backend verification as a prerequisite in every serving arm.

## Follow-up

- [ ] Complete NVFP4 baseline and publish the private checkpoint with conversion provenance.
- [ ] Make the pinned artifact and launch recipe available to each performance sweep.
- [ ] Extend the MoE, BCG and AgentX/HumanX matrices with NVFP4 cells.
- [ ] Update the deployment recommendation from paired results.

Historical baseline: `dbfef91e7d5128eeb4ce021c26ad54e409e41a3f`. NVFP4 serving support is being evaluated at `3b6b0064d2e7743378191b5b906e8e1cea37319f`; a new comparison must use one common revision for both formats. [Feature priorities](../../README.md#execution-priorities).
