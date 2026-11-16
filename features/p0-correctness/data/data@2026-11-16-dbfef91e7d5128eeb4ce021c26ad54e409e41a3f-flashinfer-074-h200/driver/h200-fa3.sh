set -euo pipefail
R=/scratch/codex-fi074
trap 'echo $? > "$R/h200-fa3.exit"' EXIT
/opt/sglang/bin/python -m pip install --no-deps --target "$R/overlay" sgl-fa3==0.1.0
PYTHONPATH="$R/overlay:$R/src/python" /opt/sglang/bin/python -c 'import sgl_fa3,importlib.metadata as m; print(m.version("sgl-fa3"),sgl_fa3.__file__)'
for i in $(seq 1 120); do grep -q ' DONE$' "$R/h200-tp8/status" && break; sleep 10; done
grep -q ' DONE$' "$R/h200-tp8/status"
/opt/sglang/bin/python "$R/gate-h200-retry.py" h200-tp8-fa3
