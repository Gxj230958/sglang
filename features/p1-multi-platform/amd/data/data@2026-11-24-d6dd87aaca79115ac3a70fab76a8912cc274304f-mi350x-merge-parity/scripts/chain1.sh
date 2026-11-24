#!/bin/bash
D=/scratch/mobius/mi350x; cd $D
mv acc/merge-mtp/ruler2 acc/merge-mtp/ruler2-failed-python-path 2>/dev/null; mv acc/merge-mtp/ruler2.log acc/merge-mtp/ruler2-failed-python-path.log 2>/dev/null
mv acc/merge-mtp/gpqa acc/merge-mtp/gpqa-gated-403 2>/dev/null; mv acc/merge-mtp/gpqa.log acc/merge-mtp/gpqa-gated-403.log 2>/dev/null
scripts/acc_suite.sh merge-mtp 30000 ruler2
P=$(cat logs/merge-mtp.pid); kill -TERM -- -$P 2>/dev/null; while pgrep -g $P >/dev/null; do sleep 2; done
until [ "$(rocm-smi --showmemuse | grep -c 'VRAM%): 0$')" = 8 ]; do sleep 3; done
scripts/matrix.sh
