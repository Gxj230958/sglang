# Delivery Status Refresh After the Default-Behavior Fixes

## Context

The November 18 fallback delivery needs a current implementation head, reproducible deployment defaults and a complete performance matrix. This journal records the implementation merges and the transition from the completed eager-prefill measurements to the integrated default-BCG sweeps.

## Outcome

- Pull requests [#85](https://github.com/radixark/sglang-zai/pull/85), [#86](https://github.com/radixark/sglang-zai/pull/86) and [#87](https://github.com/radixark/sglang-zai/pull/87) merged into `glm-5-lp` on 2026-11-17. The resulting branch head is `4ef2500d29ca90bc415247d5e476fe25ddd47f29`.
- #85 enables multimodal breakable prefill by default and resolves the built-in MTP draft path to the target checkpoint. Its H200 minimal-command run completed full GSM8K with 1249/1319 correct, 1316 normal stops, three length truncations and zero errors. Image/tool checks were 11/14, identical to the eager control; the three solid-colour image failures remain open.
- #86 maps ModelOpt mixed-precision configuration onto effective loop slots. #87 preserves HiSparse device-buffer reservations while prefills await host copies. Their existing GPU evidence remains pinned to `e9a0a0287215c18b08ecb120f9d00db52986052b`; #84 is still required for hybrid-SWA HiSparse on the current branch.
- The delivery recipe now uses breakable prefill by default, leaves prefill chunk and context length unset, sets max-running-requests 64 explicitly and does not enable the FP32 LM head. NVFP4 keeps the FP8 draft path until its self-draft result is reviewed.
- The local cookbook draft is `a62b1db914357ed5430191f005471c7c30d05f0d` on `docs/glm5lp-cookbook`. It remains unpublished and its performance cells must be refreshed after the default sweeps.

## Completed Performance Evidence

- [E10](../features/p0-general-performance/data/data@2026-11-17-e9a0a0287215c18b08ecb120f9d00db52986052b-h200-delivery/repro.md): H200 FP8, 48 points and 8,704 successful responses.
- [E11](../features/p0-general-performance/data/data@2026-11-17-e9a0a0287215c18b08ecb120f9d00db52986052b-gb300-delivery/repro.md): GB300 matched FP8/NVFP4, 96 points and 17,408 successful responses.
- [E12](../features/p0-general-performance/data/data@2026-11-17-e9a0a0287215c18b08ecb120f9d00db52986052b-b300-delivery/repro.md): B300 TP8/DEP8 matched FP8/NVFP4, 96 points and 17,408 successful responses.
- [E13](../features/p0-general-performance/data/data@2026-11-17-e9a0a0287215c18b08ecb120f9d00db52986052b-gb300-fp8kv-breakable/repro.md): GB300 FP8-KV breakable follow-up, 48 points and 8,704 successful responses.

E12 is an eager-prefill historical baseline, not the final B300 deployment recommendation. E13 shows that the earlier FP8-KV natural-MTP deficit was caused by eager prefill rather than the KV dtype.

## Active Queue at 2026-11-17T16:46Z

- B300: 12 integrated default-BCG candidates on test head `ac08d9be93598a62dda61191dcc91bda9cd6aa8b`; no auditable measured points yet.
- GB300: eight minimal/default-flag candidates on the same test head; the first candidate is running with no recorded candidate failure.
- H200: two FP8 minimal-command candidates on the same test head; no auditable measured points yet.
- The test head predates the final log-only warning adjustment and the squash-merge identities. Final release claims still require validation on the locked delivery commit and image.

## Follow-up

- [ ] Collect and independently audit the B300, GB300 and H200 default sweep results before selecting final profiles (`<OWNER>`).
- [ ] Review NVFP4 self-draft behavior and preserve the FP8-draft fallback if needed (`<OWNER>`).
- [ ] Resolve or explicitly scope #84's aggregated-mode capacity validation before merging hybrid-SWA HiSparse (`<OWNER>`).
- [ ] Refresh cookbook commands and performance cells from the integrated default results (`<OWNER>`).
- [ ] Bind the accepted profiles to an exact delivery source and GPU-qualified image (`<OWNER>`).
