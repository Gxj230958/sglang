#!/bin/bash
# final_gate.sh: GPU GLM loop attention unit test, then TP8+MTP smoke + capped GSM8K on the cleanup head.
cd /scratch/mobius/mi350x; source <(sed -n 4,15p scripts/matrix2.sh); export SGL_SRC=/scratch/mobius/cleanup-wt
T=$(cd $SGL_SRC && find test -name test_glm_loop_attention.py | head -1)
echo "=== FINAL start $(date +%T) src=$(git -C $SGL_SRC rev-parse --short HEAD)" >> $ST
(cd $SGL_SRC && PYTHONPATH=python timeout 3600 /opt/venv/bin/python -m pytest -q $T 2>&1 | tail -15) > logs/glm_loop_attention_test.txt
tail -1 logs/glm_loop_attention_test.txt | sed 's/^/glm_loop_attention test: /' >> $ST
run final-tp8-mtp $TP8 --disable-prefill-cuda-graph $MTP; stop final-tp8-mtp
echo "=== FINAL DONE $(date +%T)" >> $ST
