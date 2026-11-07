# E01 Small-head FlashMLA sparse prefill — data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-prefill

## Environment

- Machine: 1× NVIDIA B300 from an 8× B300 TP8 host; the kernel benchmark used only GPU 0 and ran after all model processes had stopped.
- Model: `zai-org/GLM-5-1028-Provider` at revision `7e66c40540c64bbf85e2a3c6d7264fbc514b4b43`; shapes represent 8 and 32 local query heads with BF16 Q/KV.
- Implementation: small-head SGLang change at `aabfddd8214bee95b6b526af5f77c81398bda133`; the benchmark calls FlashMLA directly and does not load model weights.
- Software: torch `2.14.1+cu130`, transformers `5.19.0`, sglang-kernel `0.4.10`, and `sgl-flash-mla==1.0.3`. The wheel contains the merged [FlashMLA companion change](https://github.com/sgl-project/FlashMLA/pull/27).
- Container digest and complete transitive dependency lock: not recorded. This is not a release-artifact result.

## Setup

Install the public capability wheel and run the round-specific benchmark on an otherwise idle GPU:

```bash
python -m pip install --target /path/to/flashmla-1.0.3 sgl-flash-mla==1.0.3
FLASHMLA_BENCH_OUT=/path/to/output \
PYTHONPATH=/path/to/flashmla-1.0.3 \
CUDA_VISIBLE_DEVICES=0 python bench.py
```

`bench.py` differs from the executed probe only by taking its output directory from `FLASHMLA_BENCH_OUT`; random generation, numerical comparison, CUDA Graph capture, and timing are unchanged.

## Commit

- Code commit: `aabfddd8214bee95b6b526af5f77c81398bda133` for the SGLang integration design; FlashMLA public wheel `1.0.3` supplies the measured kernel.
- Working tree: no product-source edit in this round. The rebase to `f86559388173b8abc3c6db80e3ec78e797dd85f0` leaves the small-head patch unchanged, but was not separately benchmarked here.
- An earlier timing set overlapped another model process and was excluded. Only the final idle-GPU run is reported.

## Scripts

- Version: round-specific [`bench.py`](bench.py).
- Temporary changes: output-directory parameterization only.

## Workload

- Seeds: 4101, 4102, and 4103.
- Local head counts: 8 and 32; Q/KV dimensions: 512 and 576.
- Context lengths: 8192, 16384, and 102400.
- Each case uses 8192 query rows and top-k 2048. The compact output is compared with active heads from native head64.
- Each case captures both implementations in CUDA Graphs, then measures 15 samples of five replays and uses the median. There are 36 cases in total.

## Results

| Dimension and context | Median latency reduction across 8/32 heads | Numerical result |
|---|---:|---|
| D512, 8192 and 16384 context | 13.449–13.516% | Maximum absolute difference 0 |
| D512, 102400 context | 7.345–7.347% | Maximum absolute difference 0 |
| D576, 8192 context | 15.459–16.262% | Maximum absolute difference 0 |
| D576, 16384 context | 15.601–15.943% | Maximum absolute difference 0 |
| D576, 102400 context | 6.628–7.010% | Maximum absolute difference 0 |

All 36 cases were faster than native head64. Across per-configuration medians, the reduction range was 6.63–16.26%; at 100K context it was 6.63–7.35%. Exact values and all timing samples are in [`kernel-results.json`](kernel-results.json); independent medians are in [`aggregate.json`](aggregate.json).

Conclusions:

1. The small-head kernel reproduces native active-head outputs exactly for every measured shape.
2. The kernel improvement is positive across the entire measured matrix, including 100K context.
3. These are kernel-only measurements. End-to-end attribution is recorded separately in [General Performance E01](../../../p0-general-performance/data/data@2026-11-06-aabfddd8214bee95b6b526af5f77c81398bda133-small-head-serving/repro.md).

## Data and Figures

- [`kernel-results.json`](kernel-results.json) — raw outputs and 15 timing samples for each of 36 cases.
- [`aggregate.json`](aggregate.json) — independently calculated medians and summary bounds.
- [`bench.py`](bench.py) — reproduction probe with output-path parameterization.
