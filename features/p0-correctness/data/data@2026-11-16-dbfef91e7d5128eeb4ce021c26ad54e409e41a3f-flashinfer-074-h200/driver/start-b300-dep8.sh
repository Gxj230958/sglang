set -euo pipefail
R=/scratch/codex-fi074
trap 'echo $? > "$R/dep8.exit"' EXIT
for i in $(seq 1 1800); do grep -q ' DONE$' "$R/b300-tp8/status" && break; sleep 10; done
grep -q ' DONE$' "$R/b300-tp8/status"
/opt/sglang/bin/python "$R/gate.py" b300-dep8
