# Window-layout HiCache launch fix landed directly on the model branch

## Context

A static window pool with a host stack failed at launch because pool names were read as enum values. radixark/sglang-zai pull request 59 carried the one-line fix and a regression test.

## Outcome

The same fix and test were committed to `glm-5-lp` as `8d9f8c2134`, and pull request 59 was closed unmerged on 2026-11-14 as superseded.

## Evidence

- Code: `704d3082e1` (gated pull-request head), `8d9f8c2134` (commit on the branch)
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`
- Experiment: [E03](repro.md)
- Pull request: radixark/sglang-zai pull request 59

## Follow-up

- [ ] Validate HiCache with FP8 KV and under prefill CP (`<OWNER>`).
