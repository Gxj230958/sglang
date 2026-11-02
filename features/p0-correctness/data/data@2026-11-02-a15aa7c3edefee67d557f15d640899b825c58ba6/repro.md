# E01 H200 TP8 bring-up — data@2026-11-02-a15aa7c3edefee67d557f15d640899b825c58ba6

First end-to-end bring-up of `zai-org/GLM-5-1028-Provider` on NVIDIA H200: configuration, model, attention, and checkpoint-map tests, followed by one text, one image, and one long-context chat request against a TP8 server.

This round is a bring-up smoke. It is not an accuracy, performance, or release gate.

## Environment

- Machine: single node with 8 NVIDIA H200 GPUs (143771 MiB each).
- Container: none; a Python virtual environment was used and no container image is pinned.
- Hardware: NVIDIA H200 x 8.
- Model: `zai-org/GLM-5-1028-Provider` at revision `7e66c40540c64bbf85e2a3c6d7264fbc514b4b43`.
- Software: torch `2.14.1+cu130`, flashinfer `0.7.1`, transformers `5.19.0`, sgl-flash-mla `1.0.0`, sglang-kernel `0.4.10`.
- DeepEP was not installed, so no DeepEP route was exercised.

### Model

- Architecture: `GlmLoopForConditionalGeneration`, multimodal, FP8 weights, approximately 754B parameters.
- Layers: 78 physical decoder layers expanded to 106 effective slots (26 prelude + 28 loop layers x 2 cycles + 24 coda).
- One physical NextN/MTP draft layer follows the decoder layers and is not unrolled.
- Attention: MLA with DSA sparse attention, Top-K 2048, and cross-layer IndexCache.
- Later loop cycles reuse the Top-K of the paired cycle-0 slot and merge that prefix bank with a 128-token current-cycle bank by log-sum-exp.
- MoE: the first 3 layers are dense; the remaining 75 layers use 256 routed experts with top-8 routing and 1 shared expert.
- Checkpoint download: 151 repository files, including 142 weight shards, approximately 705 GiB on disk.

## Setup

1. Check out `radixark/sglang-zai` at the code commit below.

   ```bash
   git clone https://github.com/radixark/sglang-zai.git
   cd sglang-zai
   git checkout a15aa7c3edefee67d557f15d640899b825c58ba6
   ```

2. Prepare a Python 3.12 environment with the software versions listed above. `transformers==5.19.0` is the version pinned by `python/pyproject.toml` at this commit. Install the recorded Python packages and the matching CUDA 13.0 PyTorch build, then import SGLang from the checkout instead of installing it:

   ```bash
   python3 -m venv /path/to/venv
   source /path/to/venv/bin/activate
   pip install transformers==5.19.0 flashinfer==0.7.1 \
     sgl-flash-mla==1.0.0 sglang-kernel==0.4.10
   export PYTHONPATH=$PWD/python
   ```

   The complete transitive dependency lock and the PyTorch wheel index used for the `2.14.1+cu130` build are not retained; they must be selected for the target CUDA environment rather than inferred from this document.

3. Download the checkpoint at the pinned revision. The repository requires read access; supply a token through the standard `HF_TOKEN` environment variable.

   ```bash
   hf download zai-org/GLM-5-1028-Provider \
     --revision 7e66c40540c64bbf85e2a3c6d7264fbc514b4b43 \
     --local-dir /path/to/GLM-5-1028-Provider
   ```

4. Run the regression tests documented in the implementation's GLM LoopLM guide:

   ```bash
   python test/registered/unit/configs/test_glm_loop_config.py
   python test/registered/unit/models/test_glm_loop.py
   python test/registered/kernels/ops/attention/test_glm_loop_attention.py
   GLM_LOOP_CKPT=/path/to/GLM-5-1028-Provider \
     python test/manual/models/test_glm_loop_checkpoint_map.py
   ```

   The attention test requires `sgl-flash-mla`. The checkpoint-map test reads only `config.json` and `model.safetensors.index.json`, and skips when they are absent.

5. Launch the server: TP8, Triton MoE, default DSA backends (FlashMLA Sparse) with a BF16 KV cache, CUDA graph disabled, and MTP disabled.

   ```bash
   export HF_HUB_OFFLINE=1
   python -m sglang.launch_server \
     --model-path /path/to/GLM-5-1028-Provider \
     --host 0.0.0.0 --port 30000 \
     --tp-size 8 \
     --moe-runner-backend triton \
     --mem-fraction-static 0.75 --max-total-tokens 65536 \
     --context-length 8192 --max-running-requests 32 \
     --disable-cuda-graph \
     --reasoning-parser glm45 --tool-call-parser glm47
   ```

6. Wait until `GET /health` returns HTTP 200, then send the requests in [Workload](#workload).

## Commit

- Code commit: `a15aa7c3edefee67d557f15d640899b825c58ba6` (`radixark/sglang-zai`, branch `glm-5-lp`).
- Working tree: clean; the source was deployed from the archive of this exact commit with no local changes.

## Scripts

- Version: none. The round-specific requests are defined inline below.
- Temporary changes: none.

## Workload

- Dataset or request source: three synthetic chat requests defined in this file.
- Input and output lengths: 22, 54 (25 image tokens), and 2747 prompt tokens; outputs of 3, 3, and 9 completion tokens.
- Concurrency or batch size: one request at a time.
- Sampling and evaluation settings: `temperature=0`, `top_p=1`; `max_tokens` 1024 for the text request and 512 for the others. Each request passes when the answer matches exactly and `finish_reason` is `stop`.

Text request:

```bash
cat > text-request.json <<'JSON'
{
  "model": "/path/to/GLM-5-1028-Provider",
  "messages": [{"role": "user", "content": "What is 2+3? Answer briefly."}],
  "max_tokens": 1024,
  "temperature": 0,
  "top_p": 1
}
JSON
curl -sS --max-time 300 http://127.0.0.1:30000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  --data-binary @text-request.json \
  -o text-smoke.json
```

Image and long-context requests (requires Pillow):

```python
import base64, io, json, urllib.request
from PIL import Image, ImageDraw

URL = "http://127.0.0.1:30000/v1/chat/completions"
MODEL = "/path/to/GLM-5-1028-Provider"


def post(name, content, max_tokens=512):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": content}],
        "max_tokens": max_tokens,
        "temperature": 0,
        "top_p": 1,
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as response:
        d = json.load(response)
    with open(f"{name}-smoke.json", "w") as handle:
        json.dump(d, handle, ensure_ascii=False, indent=2)


image = Image.new("RGB", (128, 128), "white")
ImageDraw.Draw(image).rectangle((16, 16, 111, 111), fill=(220, 0, 0))
buffer = io.BytesIO()
image.save(buffer, format="PNG")
data_url = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()
post("image", [
    {"type": "text", "text": "What color is the large square in this image? Answer with one color."},
    {"type": "image_url", "image_url": {"url": data_url}},
])

codeword = "ZEBRA-7419"
filler = " ".join(["alpha beta gamma"] * 900)
post("long-context", (
    f"Remember this exact codeword: {codeword}.\n"
    + filler
    + "\nWhat is the exact codeword at the beginning? Answer with the codeword only."
))
```

## Results

| Check | Gate | Result | Status |
|---|---|---|---|
| `test_glm_loop_config.py` | all tests pass | 12/12 passed | Complete |
| `test_glm_loop.py` (loop and model, CPU) | all tests pass | 27/27 passed | Complete |
| `test_glm_loop_attention.py` (dual-bank attention, H200) | all applicable tests pass | 4 passed, 2 platform-dependent skipped | Complete |
| `test_glm_loop_checkpoint_map.py` | all tests pass | 6/6 passed | Complete |
| Server startup at TP8 | `/health` returns 200 | 200; about 101 GiB used per GPU | Complete |
| Text request | content `5`, `finish_reason=stop` | `5`, `stop`, 3 completion tokens | Complete |
| Image request | content `Red`, `finish_reason=stop` | `Red`, `stop`, 25 image tokens | Complete |
| Long-context request | content `ZEBRA-7419`, `finish_reason=stop` | `ZEBRA-7419`, `stop`, 2747 prompt tokens | Complete |

Conclusions:

1. At `a15aa7c3` and model revision `7e66c405`, the checkpoint loads and serves on 8 H200 GPUs with TP8, Triton MoE, FlashMLA Sparse, and a BF16 KV cache.
2. Text, image, and long-context requests return the expected answer and stop on an end-of-sequence token.
3. The long-context request exceeds the 2048-token DSA Top-K width, so the Top-K performs a real selection, and the codeword at the start of the prompt is still retrieved.

Limitations:

- Each request is a single greedy sample; this round gives no accuracy estimate.
- MTP, GSM8K or any other accuracy evaluation, CUDA graph replay, performance benchmarking, and disaggregated deployment were not run.
- Expert parallelism, attention data parallelism, DeepEP, FP8 KV cache, and the `trtllm` DSA backend were not run on H200.
- Reasoning and tool-call parsing were enabled at launch but not exercised: every response has a null `reasoning_content` and no tool calls.
- The two skipped attention tests are platform-dependent and were skipped on H200.

## Data and Figures

The files below are the server responses with one post-capture redaction. In each file, the top-level `model` field echoed the server's local `--model-path`; that value was replaced with `/path/to/GLM-5-1028-Provider` after capture. Each file contained exactly one occurrence. No other field, value, key order, or whitespace was changed.

- [`text-smoke.json`](text-smoke.json) — raw response to the text request.
- [`image-smoke.json`](image-smoke.json) — raw response to the image request.
- [`long-context-smoke.json`](long-context-smoke.json) — raw response to the long-context request.

| File | SHA-256 as captured | SHA-256 after redaction |
|---|---|---|
| `text-smoke.json` | `57c3453de43a6e7dedd6f77e629fb993c199d81d5bffc74e8256cd844bbbddff` | `e27b8c7e5ba23f263a50c3c701d7e9531ce19017cd7c31645e107eccaf58a3cd` |
| `image-smoke.json` | `ad9dfef533326d67c463bb09c640c0255fc078c73e3e07de765634dd471c59b2` | `6fab439603172f6f34df0ac348869ec13009f442e5cb72ab6a4cd1182a61c21a` |
| `long-context-smoke.json` | `ebff1ae32d1cae95aaadf759c7c1052143d04086758861c9a7f03f832593e445` | `0915c3eb0c198ab6bf0bc11806e94ffc80e6ffc69575020b2dd584a2088c2d64` |

### Test and startup logs

- [`logs/config-tests.log.gz`](logs/config-tests.log.gz) — configuration expansion and 12 config tests.
- [`logs/model-tests.log.gz`](logs/model-tests.log.gz) — 27 loop/model tests.
- [`logs/attention-tests.log.gz`](logs/attention-tests.log.gz) — 4 passed and 2 platform-dependent skipped attention tests.
- [`logs/checkpoint-map-tests.log.gz`](logs/checkpoint-map-tests.log.gz) — 6 checkpoint-map tests.
- [`logs/server-baseline.log.gz`](logs/server-baseline.log.gz) — baseline startup and serving log.
- [`evidence-hashes.json`](evidence-hashes.json) — captured and redacted SHA-256 values for the log files.

The log files replace local model, source, and virtual-environment paths with generic `/path/to/...` placeholders. Their original and redacted hashes are recorded so the redaction is auditable.
