set -euo pipefail
R=/scratch/codex-fi074
trap 'echo $? > "$R/setup.exit"' EXIT
P=/opt/sglang/bin/python
$P -m pip install --no-deps --target "$R/overlay" sglang-kernel==0.4.11 sgl-deep-gemm==0.2.8 sgl-flash-mla==1.0.5 kernels==0.14.1 flashinfer-python==0.7.4
$P -m pip install --no-deps --target "$R/overlay" flashinfer-cubin==0.7.4 --index-url https://flashinfer.ai/whl
$P -m pip install --no-deps --target "$R/overlay" flashinfer-jit-cache==0.7.4 --index-url https://flashinfer.ai/whl/cu130
PYTHONPATH="$R/overlay:$R/src/python" $P -c 'import importlib.metadata as m; print("JIT_REQUIRES",m.requires("flashinfer-jit-cache")); import flashinfer,torch; print("IMPORT",flashinfer.__version__,flashinfer.__file__,torch.__version__,torch.version.cuda)'
