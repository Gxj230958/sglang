# Changes

## v2

- Add `summarize_round.py`, which walks an experiment round and recomputes its headline numbers from the committed raw files: sgl-eval GSM8K aggregates and finish-reason counts, MTP accept length and failure-line counters from server logs, retrieval-probe, prefix-reuse and salted-stress tallies.
- `aggregate_gsm8k.py` from v1 is unchanged and stays in `v1/`.
