set -euo pipefail
R=/scratch/codex-fi074
trap 'echo $? > "$R/start.exit"' EXIT
for i in $(seq 1 180); do test -f "$R/provider.exit" && break; sleep 10; done
test "$(cat "$R/provider.exit")" = 0
cp -a "$R/provider/." "$R/overlay/"
sha256sum "$R/source.tar" > "$R/source.sha256"
sha256sum /scratch/models/GLM-5-1028-Provider/config.json /scratch/models/GLM-5-1028-Provider/model.safetensors.index.json > "$R/checkpoint.sha256"
/opt/sglang/bin/python "$R/gate.py" h200-tp8
