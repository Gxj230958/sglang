# scripts/v2

Changes from v1, for the MI355X MTP serving round (AMD E01):

- `launch.sh`: puts `pyhooks/` first on `PYTHONPATH` and sets `ulimit -c 0`. A core dump of a ROCm rank streams hundreds of GB of mappings to the host's crash handler.
- `pyhooks/sitecustomize.py` (new): every server process calls `prctl(PR_SET_PTRACER, ANY)`, so `py-spy dump` can attach under yama `ptrace_scope=1`. `SIGUSR1` produces a faulthandler stack dump and the process keeps running. It chains to the distribution's `sitecustomize`.
- `doctor.py` (new; started by `start_bg.sh`): a monitor that never stops a rank. Every 15 s it logs, per rank, the KFD `evicted_time` and CUDA graph capture progress. Rank stacks (`py-spy dump --native`) are taken in three cases:
  - before the server is up, when the log is silent or one capture shape stalls for 90 s;
  - after the server is up, when the log is silent while requests are in flight;
  - on a queue-eviction storm.
- `start_bg.sh` / `wait_bg.sh` / `stop_bg.sh`: background launch with a recorded PID and the doctor attached; graceful stop (TERM, then KILL after 30 s).
- `bench_parity.sh` (new): Correctness E14's B300 TP8 workloads (short-c1, short-c32, long-c4; random IDs; two seeds).
- `numcheck.py` / `numcheck_compare.py` (new): a numerics probe for kernel-path A/B. It runs GSM8K prompts, collects greedy continuations and teacher-forced logprobs on shared reference tokens, and flushes the cache before every request.
- `trace_summary.py` / `decode_breakdown.py` (new): per-kernel time over decode cycles of a torch-profiler trace.
- `ar.py` / `ar_events.py` / `kfd_events.py` (new): 2 KB all-reduce health check. `ar_events.py` adds an in-process KFD SMI event listener; without CAP_SYS_ADMIN, KFD delivers queue-eviction events only to the process itself.
- `symm_stress.py` (new): repeats SGLang's symmetric-memory multimem probe across 8 ranks and stops at the first onset of the eviction state.
- `smoke.py` unchanged; `probe.py`, `stress_dummy.py` and `bench_dual_bank.py` remain in v1.
