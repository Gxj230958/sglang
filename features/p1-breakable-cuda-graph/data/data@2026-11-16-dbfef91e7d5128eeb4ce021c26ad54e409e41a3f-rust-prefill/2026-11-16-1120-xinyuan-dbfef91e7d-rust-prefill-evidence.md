# Rust breakable-prefill evidence

## Outcome

The FP8 MTP-off grid completed 12 loads and 1280 successful, nonempty requests. Independent accounting confirms C32 throughput 5242.682 total tok/s/GPU, 2.84% above the matched eager BF16 configuration. All 524 observed prefill forwards in sampled load windows replayed graphs.

Natural-MTP BCG stopped at a 1024-token sanity limit with an empty final answer; the 2048-cap candidate did not launch. GSM8K200 on the completed arm has 182 correct, 198 stop and two truncated empty final answers. These observations leave full correctness and deployment selection open.

## Evidence and follow-up

- Code: `dbfef91e7d5128eeb4ce021c26ad54e409e41a3f`, four verified Rust ranks.
- [Reproduction and immutable evidence](repro.md).
- [Independent raw-data audit](audit.json).
- Review the stopping finding and complete matched FP8/NVFP4 BCG measurements on common code before selecting deployment profiles.
