# Default Results, Self-Draft Fix and PD Health Diagnosis

## Context

This journal adds the completed default-profile results and the PD failure diagnosis that arrived after the 2026-11-17 tracking refresh. Raw evidence archives remain local by delivery decision.

## Outcome

- [General Performance E14](../features/p0-general-performance/data/data@2026-11-17-ac08d9be93598a62dda61191dcc91bda9cd6aa8b-h200-defaults/repro.md) completes H200 default-profile measurement: 24 points and 4,352 successful responses with zero errors or empty outputs. MTP-off at C16 gives 458.6 output tok/s; natural MTP at C8 gives 364.4.
- [General Performance E15](../features/p0-general-performance/data/data@2026-11-17-ac08d9be93598a62dda61191dcc91bda9cd6aa8b-gb300-defaults/repro.md) completes GB300 default-profile measurement: 96 points and 17,408 successful responses with zero errors or empty outputs. NVFP4 FP8-KV MTP-off at C64 gives 1398.8 output tok/s.
- E15 NVFP4 natural-MTP rows used the broken self-draft path and are excluded from final selection.
- [Correctness E30](../features/p0-correctness/data/data@2026-11-18-f40ccebfe4727bfafd139b72b039272e2b31823e-nvfp4-selfdraft/repro.md) records the fused-projection root cause and #89 validation. Two full GSM8K runs complete with zero errors and mean accept lengths 2.60 and 2.56. #89 merged as `26c4816830c53d867583f3d69117e23b44608481`.
- [PD Disaggregation E04](../features/p0-pd-disagg/data/data@2026-11-18-a22079906bf873d1c888b9a0c4b7fdc70a4432f2-health-check-failures/repro.md) attributes 27 HTTP 503 responses to three consecutive decode health-check timeouts and the resulting unhealthy worker mark. The default generation-aware health path allows 20 seconds while the router waits 5 seconds. Suggested lightweight-health and 30-second controls remain unverified.
- B300 FP8-only r4 remains active with four candidates and 48 planned points; no completed result is claimed here.

## Follow-up

- [ ] Rerun GB300 NVFP4 natural-MTP performance on the #89-fixed source before selecting a natural-MTP profile (`<OWNER>`).
- [ ] Collect and independently review B300 r4 before updating B300 recommendations (`<OWNER>`).
- [ ] Repeat the PD failure point with lightweight `/health` or router health timeout 30 seconds, and separately record decode KV residency limits (`<OWNER>`).
- [ ] Refresh the delivery cookbook only after the remaining default-profile results are audited (`<OWNER>`).
