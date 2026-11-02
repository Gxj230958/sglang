# AgentX Performance

## Summary

`zai-org/GLM-5-1028-Provider` AgentX performance tracking replays representative agentic workloads to measure user-visible latency, throughput, concurrency scaling, prefix reuse, and cache behavior. Status: Not started. No agentic workload has been run. The target envelope is `<TARGET_ENVELOPE>` under `<SERVICE_LEVEL_OBJECTIVE>`. Related code work is `<CODE_BRANCH_OR_PR>`, with dependencies on `<TRACE_SOURCE>`, `<CACHE_CONFIGURATION>`, and `<GENERAL_PERFORMANCE_BASELINE>`.

## Scope

### In Scope

- Versioned agentic traces or a reproducible synthetic equivalent.
- Single-user latency and multi-user concurrency sweeps.
- Time to first token, inter-token latency, request duration, and throughput.
- Prefix-cache hit behavior, reuse distance, and memory pressure.
- Failure, timeout, cancellation, and retry behavior.

### Out of Scope

- Generic one-batch or serving workloads owned by `p0-general-performance`.
- Agent quality evaluation unrelated to serving behavior.
- Tool-call format correctness and parser validation, owned by `features/p0-tool-call-parser/`; agentic results here assume its serving gates have passed.
- Private trace payloads that cannot be safely committed or reproduced.

## Success Criteria

- [ ] The trace source is pinned, sanitized, and reproducible.
- [ ] The release profile satisfies `<LATENCY_GATE>` across `<CONCURRENCY_RANGE>`.
- [ ] Throughput and cache behavior meet `<THROUGHPUT_GATE>` and `<CACHE_GATE>`.
- [ ] Failure and timeout rates stay below `<RELIABILITY_GATE>`.
- [ ] The recommended operating envelope includes capacity boundaries.
- [ ] Every result is pinned to code, model, hardware, and trace revisions.

## Workload Profile

| Trace ID | Source Revision | Requests | Input Distribution | Output Distribution | Prefix Reuse | Tool Pattern | Status |
|---|---|---:|---|---|---|---|---|
| `<TRACE_ID>` | `<TRACE_REVISION>` | `<REQUEST_COUNT>` | `<INPUT_DISTRIBUTION>` | `<OUTPUT_DISTRIBUTION>` | `<REUSE_PROFILE>` | `<TOOL_PATTERN>` | `<STATUS>` |

## Concurrency Envelope

No concurrency results recorded yet.

## Recommended Operating Envelope

| Profile | Concurrency Range | Hardware | Configuration | SLO | Capacity Boundary | Evidence | Status |
|---|---|---|---|---|---|---|---|
| `<PROFILE>` | `<MIN>-<MAX>` | `<HARDWARE>` | `<CONFIGURATION>` | `<SLO>` | `<BOUNDARY>` | `<ROUND_PATH>` | `<STATUS>` |

## Assignees

- `<OWNER>` — `<RESPONSIBILITY>`

## Stages

### Stage 1: Establish trace and baseline — Not started

- [ ] Pin and sanitize `<TRACE_SOURCE>`.
- [ ] Define latency, throughput, cache, and reliability metrics.
- [ ] Run the baseline concurrency sweep.
- Next action: select and pin a sanitized agentic trace source; start the baseline sweep after the general-performance baseline exists.

### Stage 2: Map the operating envelope — Not started

- [ ] Sweep `<CONFIGURATION_SET>` across `<CONCURRENCY_RANGE>`.
- [ ] Attribute cache, scheduler, and memory-pressure transitions.
- [ ] Identify recommended and unsafe operating bands.

### Stage 3: Certify release behavior — Not started

- [ ] Rerun the selected envelope on locked artifacts.
- [ ] Confirm trace privacy and reproducibility requirements.
- [ ] Publish reviewed guidance to the delivery cookbook.

## Experiments

No experiments recorded yet.
