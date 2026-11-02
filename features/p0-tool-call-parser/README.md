# Tool-Call Parser

## Summary

`<MODEL_NAME>` requires an SGLang tool-call detector that reproduces the model's native tool-use behavior through the OpenAI-compatible serving API. The project is `<STATUS>`; its current target is `<GOAL>`, constrained by `<CONSTRAINTS>`, and validated against raw outputs from `<MODEL_REVISION>` rendered with the pinned chat template. Related code work is tracked in `<CODE_BRANCH_OR_PR>`, with dependencies on `<DEPENDENCIES>`. Tool calls interrupting reasoning are validated jointly with `features/p0-reasoning-parser/`.

This project gates the release only when `<MODEL_NAME>` natively emits tool calls. If the model has no tool-use capability, record the not-applicable decision with its evidence in this Summary and exclude the project from `<RELEASE_SCOPE>`.

## Scope

### In Scope

- Tool-call detector implementation and registration for the model's native call format.
- Chat-template and `--tool-call-parser auto` detection rules.
- Streaming and non-streaming parse parity, end-of-stream and truncation behavior.
- `tool_choice`, `parallel_tool_calls`, and structural-tag / grammar interaction with the detector.
- Serving-layer reconstruction: call ids and indices, argument completion, and `finish_reason`.
- Regression evidence that sibling models sharing detector code or template fingerprints keep their existing behavior.

### Out of Scope

- Reasoning parser internals, thinking defaults, and reasoning levels, owned by `features/p0-reasoning-parser/`.
- Model forward, kernel, quantization, and attention changes, which belong to their owning features.
- Agentic-workload performance measurement, owned by `features/p0-agentx-performance/`.
- General model-quality evaluation beyond tool-use behavior, owned by `features/p0-correctness/`.
- Formats and API behaviors the model does not natively emit.

## Success Criteria

- [ ] The format contract is pinned: tokenizer and chat-template revision, a rendered prompt, and raw model outputs covering plain text, one call, several calls, calls interleaved with reasoning when the model also exposes reasoning, and a follow-up turn containing a tool result.
- [ ] Detection targets the latest published chat-template revision; the pinned revision and the markers and fingerprints it relies on are recorded and re-checked when the template changes.
- [ ] The vendor's official serving flags and evaluation request settings, including template kwargs, are recorded as the reference configuration and reproduced on `<CODE_SHA>`.
- [ ] Streaming reconstruction matches non-streaming output at arbitrary chunk boundaries, including cuts inside tags, names, quotes, escapes, and between calls, for text, call names and order, and decoded arguments.
- [ ] End-of-stream, incomplete-call, and length-truncation cases release held text correctly and never leak raw markers into content or `reasoning_content`.
- [ ] Argument values and types survive parsing: literal backslashes, embedded quotes and newlines, Unicode, nested JSON, and JSON-Schema unions (`anyOf` / `oneOf` / `allOf`, `type` lists, `$ref`) decode to native types in both parse modes.
- [ ] Parse errors after partial emission do not duplicate text, collide `tool_index` values, or corrupt the next call.
- [ ] `tool_choice` modes (`none`, `auto`, `required`, named) and `parallel_tool_calls` agree between grammar constraints and detector decoding.
- [ ] `finish_reason` is `tool_calls` only on a natural stop with parsed calls.
- [ ] Auto-detection resolves `<MODEL_NAME>` to the intended parser and leaves every neighboring model's resolution unchanged, verified with negative cases against sibling templates, with an architecture-based fallback when no chat template is available.
- [ ] `auto` fully applies the detected parser configuration rather than only logging suggestions, and the cookbook recommends `--tool-call-parser auto` as the standard launch setting; explicit parser names are documented only as a debugging fallback.
- [ ] Repeated multi-turn and agentic replays show a stable raw call format, with explicit flags and `auto` reaching result parity within run noise and zero marker leaks.
- [ ] Parser unit suites pass on `<CODE_SHA>`, and a served instance validates streaming and non-streaming requests with both explicit parser flags and `auto`.
- [ ] Every result is pinned to `<CODE_SHA>`, `<MODEL_REVISION>`, and a reproduction record.

## Validation Matrix

| Capability | Mode | Configuration | Gate | Status | Evidence | Owner |
|---|---|---|---|---|---|---|
| Non-stream parse | `<CASES>` | `<PARSER_FLAGS>` | `<PASS_CRITERION>` | `<STATUS>` | `<ROUND_PATH>` | `<OWNER>` |
| Stream chunk-boundary invariance | `<CUT_PLAN>` | `<PARSER_FLAGS>` | Stream equals non-stream after `json.loads` | `<STATUS>` | `<ROUND_PATH>` | `<OWNER>` |
| EOS flush and truncation | `<CASES>` | `<PARSER_FLAGS>` | No held text lost; no marker leakage | `<STATUS>` | `<ROUND_PATH>` | `<OWNER>` |
| Argument value and type preservation | `<SCHEMA_SET>` | `<PARSER_FLAGS>` | Native decoded types match in both modes | `<STATUS>` | `<ROUND_PATH>` | `<OWNER>` |
| Error after partial emission | `<CASES>` | `<PARSER_FLAGS>` | No duplication, index collision, or corruption | `<STATUS>` | `<ROUND_PATH>` | `<OWNER>` |
| `tool_choice` and grammar | `<CHOICE_MATRIX>` | `<STRICT_LEVEL>` | Grammar and detector agree on every case | `<STATUS>` | `<ROUND_PATH>` | `<OWNER>` |
| Auto-detection | Explicit flags vs `auto` | `<TEMPLATE_SET>` | Intended resolution; sibling models unchanged | `<STATUS>` | `<ROUND_PATH>` | `<OWNER>` |
| Agentic replay stability | Repeated multi-turn traces | Explicit flags vs `auto` | Result parity within run noise; zero marker leaks; schema-failure rate within `<GATE>` | `<STATUS>` | `<ROUND_PATH>` | `<OWNER>` |
| Serving end-to-end | Stream and non-stream | `<SERVER_CONFIG>` | Correct calls, content, and `finish_reason` | `<STATUS>` | `<ROUND_PATH>` | `<OWNER>` |

## Assignees

- `<OWNER>` — `<RESPONSIBILITY>`

## Stages

### Stage 1: Pin the format contract — `<STATUS>`

- [ ] Pin `<MODEL_REVISION>`, tokenizer revision, and chat-template revision; record rendered prompts and raw outputs for every contract case (`<OWNER>`).
- [ ] Record reference behavior from `<REFERENCE_IMPLEMENTATION>` where one exists, including escaping, whitespace, and optional-opener conventions.
- [ ] Record the vendor's official serving flags and evaluation request settings, including template kwargs, as the reference configuration.
- [ ] Pin the latest published chat-template revision and record the markers and fingerprints detection relies on.
- [ ] Identify the nearest existing detector and list every shared-code consumer that the implementation may affect.

### Stage 2: Implement and unit-validate the detector — `<STATUS>`

- [ ] Implement the detector; register names in the parser registry and the dependency-free name list, and add auto-detection rules with sibling negative cases and an architecture-based fallback (`<OWNER>`).
- [ ] Add chunk-boundary, EOS, schema-union, and auto-detection regression cases to the registered parser unit suites; verify cases for newly supported behavior fail on the pre-implementation base, while preservation cases (sibling negative cases and existing behavior) pass on both base and implementation.
- [ ] Run the full parser unit selection plus every sibling detector suite that shares modified code on `<CODE_SHA>`.

### Stage 3: Validate serving and certify for release — `<STATUS>`

- [ ] Serve the pinned model on `<HARDWARE>` with the vendor's reference configuration and exercise streaming and non-streaming tool requests with explicit parser flags and with `auto`; record responses and `finish_reason` for every matrix row.
- [ ] Replay repeated multi-turn and agentic traces against both flag modes; record schema-failure rates, marker leaks, and raw-format stability.
- [ ] Run a `<QUALITY_GATE>` evaluation to confirm no stop-rate or empty-content regression from template changes.
- [ ] Open the upstream SGLang pull request `<PR_URL>` with the validation evidence linked, and record final results in the Experiments table.
- [ ] Document `--tool-call-parser auto` as the standard launch setting in `day0-delivery/cookbook/`, with explicit parser names only as a debugging fallback.

## Experiments

| ID | Date | Topic | Basic Setting | Result | Round |
|---|---|---|---|---|---|
| E01 | `<YYYY-MM-DD>` | `<TOPIC>` | `<HARDWARE>; <WORKLOAD>` | `<RESULT>` | [round](data/data@<YYYY-MM-DD>-<CODE_SHA>/repro.md) |
