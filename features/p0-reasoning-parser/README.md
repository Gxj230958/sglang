# Reasoning Parser

## Summary

`<MODEL_NAME>` requires an SGLang reasoning parser that reproduces the model's thinking behavior, including its supported reasoning levels, through the OpenAI-compatible serving API. Status: Not started. Its current target is `<GOAL>`, constrained by `<CONSTRAINTS>`, and validated against raw outputs from `<MODEL_REVISION>` rendered with the pinned chat template. Related code work is tracked in `<CODE_BRANCH_OR_PR>`, with dependencies on `<DEPENDENCIES>`. Tool calls interrupting reasoning are validated jointly with `features/p0-tool-call-parser/`.

This project gates the release only when `<MODEL_NAME>` exposes thinking or reasoning output. If the model has no reasoning capability, record the not-applicable decision with its evidence in this Summary and exclude the project from `<RELEASE_SCOPE>`. If the model supports thinking but no reasoning levels, reduce the level-specific criteria and matrix rows to thinking on/off and record that reduction here.

## Scope

### In Scope

- Reasoning parser implementation and registration, including thinking-marker handling and `stream_reasoning`.
- Thinking on/off defaults, `chat_template_kwargs` handling, and `--reasoning-parser auto` / reasoning-mode detection rules.
- Reasoning levels: the supported `<REASONING_LEVEL_SET>` (for example the model's `reasoning_effort` values), the default when the level is omitted, per-level template and generation behavior, and rejection or mapping of unsupported levels.
- The contract for a reasoning level requested while thinking is disabled.
- Content vs `reasoning_content` routing, tool calls interrupting reasoning, and grammar ownership of the reasoning prefix.
- Regression evidence that sibling models sharing parser code or template fingerprints keep their existing behavior.

### Out of Scope

- Tool-call detector internals and tool schema handling, owned by `features/p0-tool-call-parser/`.
- Model forward, kernel, quantization, and attention changes, which belong to their owning features.
- General model-quality evaluation beyond reasoning behavior, owned by `features/p0-correctness/`.
- Performance tuning of reasoning workloads.

## Success Criteria

- [ ] The format contract is pinned: tokenizer and chat-template revision, rendered prompts, and raw outputs covering thinking on/off and every level in `<REASONING_LEVEL_SET>`, including content absent, whitespace-only content, and text ending exactly at the closing marker.
- [ ] Detection targets the latest published chat-template revision; the pinned revision and the markers and fingerprints it relies on are recorded and re-checked when the template changes.
- [ ] The vendor's official evaluation settings for reasoning, including the levels and template kwargs used by official scorecards, are recorded as the reference configuration and reproduced on `<CODE_SHA>`.
- [ ] The layer consuming each reasoning level is identified (chat-template passthrough vs serving-layer normalization), and rendered prompts prove the level takes effect; a silently ignored level is a blocking defect.
- [ ] Every supported reasoning level produces its contracted template rendering and serving behavior, and the default level applies when the request omits it.
- [ ] Unsupported or invalid levels follow the pinned contract, whether that is rejection, mapping, or documented no-validation passthrough, and a level requested while thinking is disabled follows the pinned effort-over-disabled contract.
- [ ] Precedence among the request field, `chat_template_kwargs`, and server defaults is pinned, and conflicting values follow the pinned rejection or resolution contract.
- [ ] Explicit request values are never overridden by template defaults (including an explicit `false` for thinking toggles).
- [ ] When thinking markers are special tokens, parser-on and parser-off behavior is pinned against `<REFERENCE_IMPLEMENTATION>`, including the `skip_special_tokens` interaction.
- [ ] Streaming and non-streaming responses agree on content routing and marker stripping, with no opening or closing marker leaked into content or `reasoning_content` at any chunk boundary, at end of stream, or under truncation.
- [ ] When the model also emits tool calls, tool calls interrupting reasoning produce correct content routing and complete calls; exactly one layer owns the reasoning prefix when grammar constraints are active, and think-end markers resolve to real token ids wherever grammar deferral depends on them.
- [ ] Responses API and Anthropic adapter level defaults and mappings agree with the chat-completions contract.
- [ ] Auto-detection resolves `<MODEL_NAME>` to the intended parser and thinking defaults and leaves every neighboring model's resolution unchanged, verified with negative cases against sibling templates.
- [ ] Parser unit suites pass on `<CODE_SHA>`, and a served instance validates every reasoning level with both explicit parser flags and `auto`.
- [ ] A `<QUALITY_GATE>` evaluation shows no stop-rate or empty-content regression from reasoning defaults or level handling.
- [ ] Every result is pinned to `<CODE_SHA>`, `<MODEL_REVISION>`, and a reproduction record.

## Validation Matrix

| Capability | Mode | Configuration | Gate | Status | Evidence | Owner |
|---|---|---|---|---|---|---|
| Thinking on/off | Stream and non-stream | `<PARSER_FLAGS>` | Correct routing and marker stripping | `<STATUS>` | `<ROUND_PATH>` | `<OWNER>` |
| Reasoning level behavior | Each level in `<REASONING_LEVEL_SET>` | `<LEVEL_SETTINGS>` | Every level matches its contracted behavior | `<STATUS>` | `<ROUND_PATH>` | `<OWNER>` |
| Default and invalid levels | Omitted, unsupported, malformed | `<LEVEL_SETTINGS>` | Pinned default and rejection/mapping contract | `<STATUS>` | `<ROUND_PATH>` | `<OWNER>` |
| Level precedence and conflicts | Field vs kwargs vs server default | `<LEVEL_SETTINGS>` | Pinned precedence; conflicts rejected or resolved per contract | `<STATUS>` | `<ROUND_PATH>` | `<OWNER>` |
| Level over disabled thinking | `<LEVEL_SETTINGS>` | Thinking disabled | Pinned effort-over-disabled contract | `<STATUS>` | `<ROUND_PATH>` | `<OWNER>` |
| `stream_reasoning` and EOS | `<CASES>` | `<PARSER_FLAGS>` | No marker leakage; held text released | `<STATUS>` | `<ROUND_PATH>` | `<OWNER>` |
| Tool calls interrupting reasoning (when tool use is supported) | Stream and non-stream | `<TOOL_CASES>` | Correct routing; calls complete | `<STATUS>` | `<ROUND_PATH>` | `<OWNER>` |
| Auto-detection | Explicit flags vs `auto` | `<TEMPLATE_SET>` | Intended resolution; sibling models unchanged | `<STATUS>` | `<ROUND_PATH>` | `<OWNER>` |
| Serving end-to-end | Stream and non-stream; Responses and Anthropic surfaces | `<SERVER_CONFIG>` | Correct content fields, level mappings, and stop behavior | `<STATUS>` | `<ROUND_PATH>` | `<OWNER>` |

## Assignees

- `<OWNER>` — `<RESPONSIBILITY>`

## Stages

### Stage 1: Pin the reasoning contract — Not started

- [ ] Pin `<MODEL_REVISION>`, tokenizer revision, and chat-template revision; record rendered prompts and raw outputs for thinking on/off and every reasoning level (`<OWNER>`).
- [ ] Enumerate `<REASONING_LEVEL_SET>` and record the per-level template mapping, the omitted-level default, the unsupported-level contract, and the effort-over-disabled contract, with reference behavior from `<REFERENCE_IMPLEMENTATION>` where one exists.
- [ ] Record the vendor's official evaluation settings for reasoning and identify which layer consumes each level; verify by inspecting rendered prompts.
- [ ] Record whether thinking markers are special tokens and how `skip_special_tokens` changes parser-on and parser-off output.
- [ ] Pin the latest published chat-template revision and record the markers and fingerprints detection relies on.
- [ ] Identify the nearest existing reasoning parser and list every shared-code consumer that the implementation may affect, including grammar backends that consume reasoning state.

### Stage 2: Implement and unit-validate the parser — Not started

- [ ] Implement the reasoning parser and level handling, including field/kwargs/default precedence and conflict behavior; register names in the parser registry and the dependency-free name list, and add reasoning-mode and auto-detection rules with sibling negative cases (`<OWNER>`).
- [ ] Add regression cases for marker stripping, EOS and truncation, per-level behavior, precedence and conflicts, explicit-`false` toggles, and auto-detection to the registered parser unit suites; verify cases for newly supported behavior fail on the pre-implementation base, while preservation cases (sibling negative cases and existing behavior) pass on both base and implementation.
- [ ] Run the full parser unit selection plus every sibling parser suite that shares modified code on `<CODE_SHA>`.

### Stage 3: Validate serving and certify for release — Not started

- [ ] Serve the pinned model on `<HARDWARE>` with the vendor's reference configuration and exercise streaming and non-streaming requests at every reasoning level with explicit parser flags and with `auto`; record content routing and stop behavior for every matrix row.
- [ ] Probe Responses API and Anthropic adapter level handling against the chat-completions contract.
- [ ] Run a `<QUALITY_GATE>` evaluation to confirm no stop-rate or empty-content regression from reasoning defaults or level handling.
- [ ] Open the upstream SGLang pull request `<PR_URL>` with the validation evidence linked, and record final results in the Experiments table.
- [ ] Link release-facing reasoning behavior, supported levels, and official evaluation settings from `day0-delivery/cookbook/`, documenting `--reasoning-parser auto` as the standard launch setting and explicit parser names only as a debugging fallback.

## Experiments

| ID | Date | Topic | Basic Setting | Result | Round |
|---|---|---|---|---|---|
| E01 | `<YYYY-MM-DD>` | `<TOPIC>` | `<HARDWARE>; <WORKLOAD>` | `<RESULT>` | [round](data/data@<YYYY-MM-DD>-<CODE_SHA>/repro.md) |
