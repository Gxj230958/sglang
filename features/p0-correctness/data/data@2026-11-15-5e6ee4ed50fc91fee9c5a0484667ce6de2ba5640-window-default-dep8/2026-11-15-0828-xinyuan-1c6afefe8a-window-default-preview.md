# Window layout as the default: local preview

## Context

Agent workloads are multi-turn, and the window layout holds more context per GPU. The change makes it the default and keeps `--disable-hybrid-swa-memory` as the only switch.

## Outcome

A first version (`5e6ee4ed50`) passed the DEP8 GSM8K gate with no layout variable set. The current version (`1c6afefe8a`) also removes the environment variable. Both exist only locally, stacked on pull request 58; nothing is pushed. All numbers are preview, non-release.

## Evidence

- Code: `5e6ee4ed50` (gated), `1c6afefe8a` (current local commit)
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`
- Experiment: [E10](repro.md), [E11](../data@2026-11-15-1c6afefe8af05447f81d41ad8e3d353c0d81d8d3-long-context-retrieval/repro.md)

## Follow-up

- [ ] After pull request 58 merges, rebase, gate the final commit and open a pull request (`<OWNER>`).
