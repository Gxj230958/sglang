#!/usr/bin/env bash
# CPU-only checks of a built image. Usage: verify-image.sh <image> <amd64|arm64>
set -uo pipefail
IMG=$1
ARCH=$2

echo "== docker inspect"
docker inspect --format 'arch={{.Architecture}} os={{.Os}} id={{.Id}} size={{.Size}}' "$IMG"
[ "$(docker inspect --format '{{.Architecture}}' "$IMG")" = "$ARCH" ] && echo "PASS arch" || echo "FAIL arch"
docker inspect --format 'entrypoint={{json .Config.Entrypoint}} cmd={{json .Config.Cmd}} workdir={{.Config.WorkingDir}}' "$IMG"
docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' "$IMG" | grep -E '^(SGLANG_|CUDA_VERSION|VIRTUAL_ENV|FLASHINFER_VERSION|PATH)='
docker inspect --format '{{range $k, $v := .Config.Labels}}{{println $k "=" $v}}{{end}}' "$IMG" | grep -E '^(ai\.|org\.opencontainers)'

docker run --rm --entrypoint bash "$IMG" -c '
check() { local name=$1; shift; if "$@" > /tmp/check.out 2>&1; then echo "PASS $name"; else echo "FAIL $name"; tail -15 /tmp/check.out; fi; }
export PYTHONPYCACHEPREFIX=/tmp/pyc
M=/sgl-workspace/glm-loop-1118

echo "== source"
cat /sgl-workspace/sglang.commit
bash $M/verify-source.sh /sgl-workspace/sglang $M/manifest | tail -12
extra_py=$(cd /sgl-workspace/sglang && find . -name __pycache__ -prune -o -name "*.py" -printf "%P\n" | LC_ALL=C sort \
    | LC_ALL=C comm -23 - <(sed -E "s/^[0-9a-f]{64} [ *]//" $M/manifest/cutoff-files.sha256 | LC_ALL=C sort))
echo "py files outside the cutoff tree: ${extra_py:-none}"

echo "== python"
check compileall python -m compileall -q /sgl-workspace/sglang/python/sglang
check import_sglang python -c "import sglang; print(sglang.__version__, sglang.__file__)"; cat /tmp/check.out
check import_glm_loop python -c "import sglang.srt.models.glm_loop, sglang.srt.models.glm_loop_nextn"
check serve_help sglang serve --help; grep -c -- "--" /tmp/check.out
check launch_server_help python -m sglang.launch_server --help
check serve_help_has_glm_flags bash -c "sglang serve --help | grep -q -- --dsa-decode-backend"

echo "== rust extensions (SGLANG_RUST_BUILD_MODE=$SGLANG_RUST_BUILD_MODE)"
ls -la /sgl-workspace/sglang/python/sglang/srt/rust_extensions/*.so /sgl-workspace/sglang/python/sglang/srt/mem_cache/rust_tree_core/*.so
sha256sum /sgl-workspace/sglang/python/sglang/srt/rust_extensions/*.so /sgl-workspace/sglang/python/sglang/srt/mem_cache/rust_tree_core/*.so
for m in _server _grpc _multimodal _bench; do
    check "load_rust$m" python -c "from sglang.srt.rust_extensions.loader import load_rust_extension as l; print(l(\"sglang.srt.rust_extensions.$m\").__file__)"
done
check load_rust_mem_cache python -c "import torch; from sglang.srt.rust_extensions.loader import load_rust_extension as l; print(l(\"sglang.srt.mem_cache.rust_tree_core.mem_cache\").__file__)"

echo "== sgl-deep-gemm"
DG=/opt/sglang/lib/python3.12/site-packages/deep_gemm
check dg_python_patch grep -q "TRT-LLM weight layout requires NVFP4 or FP8 x FP8 MMA" $DG/mega/__init__.py
check dg_old_error_gone bash -c "! grep -rq \"TRT-LLM packed weights require NVFP4 MMA\" $DG"
check dg_header_patch grep -q kUseTrtllmFP8Weights $DG/include/deep_gemm/impls/sm100_fp8_fp4_mega_moe.cuh
check dg_binary_patch grep -q -a "use_trtllm_fp8_weights and mma_kind == MmaKind::MXFP8FP4" $DG/_C.so
ldd $DG/_C.so | grep -E "not found" | grep -v -E "libtorch|libc10" && echo "FAIL dg_ldd" || echo "PASS dg_ldd (torch libs resolve at import)"
check import_deep_gemm python -c "import deep_gemm; print(deep_gemm.__file__)"
python -c "import flash_mla" > /dev/null 2>&1 && echo "PASS import_flash_mla" || echo "INFO import_flash_mla needs libcuda.so.1 from the GPU host driver"
grep -l -E "HAS_(BF16|FP8_576)_SPARSE_DECODE" /opt/sglang/lib/python3.12/site-packages/flash_mla/*.py || echo "flash_mla: no h64 sparse-decode markers (released 1.0.5 wheel)"

echo "== versions"
pip list 2>/dev/null | grep -i -E "^(torch|flashinfer-python|flashinfer-cubin|sglang|sglang-kernel|sgl-deep-gemm|sgl-flash-mla|sgl-deep-ep|transformers|apache-tvm-ffi|triton|kernels|mooncake-transfer-engine-cuda13|sgl-nvidia-mega) "
python -c "import torch; print(\"torch\", torch.__version__, \"cuda\", torch.version.cuda)"
echo "CUDA_VERSION=$CUDA_VERSION"; nvcc --version | tail -2; python -V; rustc -V
'
