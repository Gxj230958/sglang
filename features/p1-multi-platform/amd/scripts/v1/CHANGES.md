# Changes

## v1

- `launch.sh`: TP8 MI355X server launch used by Correctness E36 (bf16 KV, ROCm DSA defaults, `ulimit -c 0` so an aborted rank does not stream a core through the host's apport).
- `smoke.py`: text, image and long-context chat smokes; each passes on the expected answer with `finish_reason=stop`.
- `probe.py`: first-token top-5 logprobs for three raw prompts; flat distributions flag broken weights or attention.
- `bench_dual_bank.py`: one-GPU microbenchmark of the later-cycle dual-bank split-K against the single-bank ROCm Triton decode, under CUDA graph replay.
- `stress_dummy.py`: decode, 6K-token sparse prefill and 16-request batching against a dummy-weight server to find crashes before real weights load.
