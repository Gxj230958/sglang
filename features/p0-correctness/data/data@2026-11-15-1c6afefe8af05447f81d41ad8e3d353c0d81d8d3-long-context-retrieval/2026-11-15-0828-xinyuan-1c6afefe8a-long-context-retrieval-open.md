# Open observation: random-record retrieval degrades from 60K tokens on DEP8 with FP8 KV

## Context

A 120.9K-token probe returned a wrong code during the default-layout gate. An A/B over three arms checked whether the layout or the merge caused it.

## Outcome

All three arms (default window, full-length, pre-merge window) answer 6 to 8 of 12 random-record prompts (50–67%) at 60K and at 120.9K tokens. The layout and the merge are ruled out as causes. The cause itself is not identified.

## Evidence

- Code: `1c6afefe8a`, `e941d571f3`
- Model: `zai-org/GLM-5-1028-Provider`, tracked revision `7e66c405`
- Experiment: [E11](repro.md)

## Follow-up

- [ ] Attribute the misses: BF16 against FP8 KV, TP8 against DEP8, thinking on against off, on the same prompt set (`<OWNER>`).
