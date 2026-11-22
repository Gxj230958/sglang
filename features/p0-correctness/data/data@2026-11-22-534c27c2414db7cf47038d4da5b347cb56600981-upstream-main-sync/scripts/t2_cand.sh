D=/scratch/glm5lp-upstream-sync; REV=e06a13406b; OVL=$D/overlay-deps-710a842c57; L=$D/$REV/legs.status
echo "$(date -u +%FT%TZ) rank1 legs start rev=$REV overlay=$OVL" >> $L
RUN_SUFFIX= bash $D/gate2c.sh $REV 31200 tp4 $OVL; echo "$(date -u +%FT%TZ) tp4 exit=$?" >> $L
RUN_SUFFIX= bash $D/gate2c.sh $REV 31200 dep4 $OVL; echo "$(date -u +%FT%TZ) dep4 exit=$?" >> $L
for g in gate-tp4 gate-dep4; do /opt/sglang/bin/python $D/analyze.py $D/$REV/$g > $D/$REV/$g/analysis.json 2>&1; done
echo "$(date -u +%FT%TZ) LEGS_DONE" >> $L
