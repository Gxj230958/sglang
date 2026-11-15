# Analysis and Design

## Summary

`zai-org/GLM-5-1028-Provider` tracking for establishing the design that must be completed before any concrete parallelism feature is implemented. Status: In progress. Related code work: `radixark/sglang-zai` branch `glm-5-lp` at `a15aa7c3`. The current layout constraints of the implementation are recorded below; candidate layouts have not been compared and no design has been reviewed. Target workload and hardware: `<WORKLOAD>` on `<HARDWARE>`; acceptance thresholds remain to be defined.

This is the prerequisite for every implementation subproject in [Parallelism](../README.md). Mark this work Complete and link the design decision from the parent README before implementation begins.

## Scope

### In Scope

- Map attention, dense layers, experts, KV state, and pipeline boundaries to ranks.
- Compare candidate strategies against model structure, memory limits, interconnect, and workloads.
- Specify valid feature combinations, communication interfaces, implementation order, and validation gates.

### Out of Scope

- Unselected configurations and unsupported feature combinations.
- Performance or support claims without reproducible evidence.

## Success Criteria

- [ ] A reviewed design records selected and deferred strategies with their rationale.
- [ ] Rank groups, tensor layouts, state ownership, and collective ordering are explicit.
- [ ] The design has an owner, resolved blocking questions, and a concrete correctness and performance plan.

## Assignees

- `<OWNER>` — Design, implementation coordination, and validation evidence.

## Stages

### Stage 1: Define requirements and design — In progress

- Model structure: 78 physical decoder layers expand to 106 effective slots (26 prelude + 28 loop layers x 2 cycles + 24 coda); every slot owns its own KV cache layer while later cycles share the cycle-0 weights.
- Attention: MLA with DSA sparse attention (Top-K 2048); a later-cycle slot reads the paired cycle-0 Top-K prefix bank and a 128-token current-cycle bank and merges them by log-sum-exp.
- MoE: the first 3 layers are dense; the remaining 75 layers use 256 routed experts, top-8 routing, and 1 shared expert.
- Validated baseline: plain TP8 on 8 H200 GPUs ([Correctness E01](../../p0-correctness/data/data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6/repro.md)).
- Constraint: `--pipeline-parallel-size > 1` is rejected at launch because a stage boundary inside the loop region would split the damp blend from the cycle it commits.
- Constraint: `--attn-cp-size > 1` and `--enable-prefill-cp` are rejected at launch because the current-cycle window is built over the whole packed query range.
- Constraint: `--dcp-size > 1` is rejected at launch because both KV banks must be available on the same attention rank.
- Constraint: `--enable-two-batch-overlap` and `--enable-eplb` are also rejected at launch.
- Source: launch checks in `python/sglang/srt/arg_groups/glm_loop_hook.py` and the GLM LoopLM guide at `a15aa7c3`; the rejections themselves were not exercised in E01.
- Not yet validated on H200: expert parallelism, attention data parallelism, and DeepEP; DeepEP was not installed in the E01 environment.
- Update 2026-11-15: at `710bcb2a` prefill CP runs on the full-length KV layout, and `radixark/sglang-zai` pull request 57 (merged as `5337c504`) enables it for the hybrid window sub-pool; expert parallelism with attention DP is validated on GB300 (DEP4, DeepEP) and B300 (DEP8). Evidence: [Prefill CP](../prefill-cp/README.md) E01–E03 and [DP Attention](../dp-attention/README.md) E01–E02. The pipeline-parallel and decode-CP rejections above were not revisited.
- [ ] Record the target workloads, dependencies, configuration boundaries, and acceptance thresholds.
- [ ] Compare candidate layouts and document the selected topology and interfaces.
- Next action: define the target workload and topology, then compare TP8 with expert parallelism and attention data parallelism within these constraints.

### Stage 2: Review and complete the design — Not started

- [ ] Resolve blocking questions and record the reviewed design in this README.
- [ ] Link the decision from the parent README and mark Analysis and Design Complete.

## Experiments

No experiments recorded yet.
