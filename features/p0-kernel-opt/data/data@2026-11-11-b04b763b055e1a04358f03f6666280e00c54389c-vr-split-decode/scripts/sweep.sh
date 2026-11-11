cd /tmp && python3 -u /nfs_home/glm5-lcd/split_rig.py $ROWS "$CFGS" 2>&1 | grep -E "rows=|RIG_DONE|Error"
