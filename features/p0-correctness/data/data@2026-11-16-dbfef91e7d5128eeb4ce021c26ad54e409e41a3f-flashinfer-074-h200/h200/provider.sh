set -euo pipefail
R=/scratch/codex-fi074
trap 'echo $? > "$R/provider.exit"' EXIT
while [ ! -f "$R/setup.exit" ]; do sleep 10; done
test "$(cat "$R/setup.exit")" = 0
/opt/sglang/bin/python -m pip install --no-deps --target "$R/provider" flashinfer-jit-cache-sm90a==0.7.4 --index-url https://flashinfer.ai/whl/cu130
