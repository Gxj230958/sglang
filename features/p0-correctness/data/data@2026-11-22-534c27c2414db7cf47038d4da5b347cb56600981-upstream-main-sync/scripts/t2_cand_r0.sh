D=/scratch/glm5lp-upstream-sync; REV=534c27c241; OVL=$D/overlay-deps-710a842c57; L=$D/$REV/legs.status
echo "$(date -u +%FT%TZ) rank0 leg tp4 start rev=$REV overlay=$OVL" >> $L
RUN_SUFFIX= bash $D/gate2c.sh $REV 31200 tp4 $OVL; echo "$(date -u +%FT%TZ) tp4 exit=$?" >> $L
/opt/sglang/bin/python $D/analyze.py $D/$REV/gate-tp4 > $D/$REV/gate-tp4/analysis.json 2>&1
echo "$(date -u +%FT%TZ) tp4 LEG_DONE" >> $L
