#!/bin/bash
# usage: legs.sh <rev-dir> [extra-overlay-dir]   runs tp4, dep4-r1, dep4-r2 in sequence on this rank
D=/scratch/glm5lp-upstream-sync; REV=$1; OVL=${2:-}
L=$D/$REV/legs.status
echo "$(date -u +%FT%TZ) legs start rev=$REV overlay=${OVL:-none}" >> $L
RUN_SUFFIX= bash $D/gate2c.sh $REV 31200 tp4 $OVL; echo "$(date -u +%FT%TZ) tp4 exit=$?" >> $L
RUN_SUFFIX=-r1 bash $D/gate2c.sh $REV 31200 dep4 $OVL; echo "$(date -u +%FT%TZ) dep4-r1 exit=$?" >> $L
RUN_SUFFIX=-r2 bash $D/gate2c.sh $REV 31200 dep4 $OVL; echo "$(date -u +%FT%TZ) dep4-r2 exit=$?" >> $L
for g in gate-tp4 gate-dep4-r1 gate-dep4-r2; do /opt/sglang/bin/python $D/analyze.py $D/$REV/$g > $D/$REV/$g/analysis.json 2>&1; done
echo "$(date -u +%FT%TZ) LEGS_DONE" >> $L
