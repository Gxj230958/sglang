# FlashInfer 0.7.3 and 0.7.4 run back to back at TP8: MTP accept length within 0.9%

## Context

[E15](../data@2026-11-16-dbfef91e7d5128eeb4ce021c26ad54e409e41a3f-flashinfer-074-h200/repro.md) passed the GSM8K gates with FlashInfer 0.7.4, but its TP8 log-line accept length (2.54) was below the 2.76 of the FlashInfer 0.7.3 round E13, and the two runs were a day apart. A lower accept length would lower decode throughput by about the same fraction, so the two versions were run back to back on the same node, source tree and flags.

## Outcome

On 8× B300 at TP8 with `dbfef91e`, full GSM8K gives a counter-based accept length of 2.6480 (0.7.3) against 2.6423 (0.7.4) at temperature 1.0 / top_p 0.95 and 2.8231 against 2.8463 at temperature 0; the log-line means are 2.59 against 2.63 and 2.83 against 2.87. The counter ratios of the two arms are within 0.9% in both settings, and the 0.7.3 arm does not reproduce E13's 2.76; the cause of the E13-to-E15 gap is unresolved and no equivalence is claimed. Accuracy is 95.60% against 95.07% at temperature 1.0. Greedy decoding leaves 9 and 6 of 1319 requests running until the context is full on the two arms, 5 of them the same questions; one request of the 0.7.4 arm did so at temperature 1.0. Single unseeded runs in a fixed arm order; the source tree was not re-verified for this round and only the 0.7.4 arm loads a JIT-cache architecture provider.

## Evidence

- Code: `dbfef91e7d5128eeb4ce021c26ad54e409e41a3f`
- Model: `zai-org/GLM-5-1028-Provider`
- Experiment: [E16](repro.md)

## Follow-up

- [ ] Report MTP accept length from the eval-only counters in later rounds (`<OWNER>`).
- [ ] Decide whether context-filling reasoning under greedy decoding needs a release note or a default `max_tokens` recommendation (`<OWNER>`).
