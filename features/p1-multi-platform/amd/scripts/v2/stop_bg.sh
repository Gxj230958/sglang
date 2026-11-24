#!/bin/bash
# stop_bg.sh <logname>: kill the server process group started by start_bg.sh
P=$(cat /persistent/work/glm_loop_amd/logs/$1.pid)
kill -TERM -- -$P 2>/dev/null; for i in $(seq 1 30); do kill -0 $P 2>/dev/null || break; sleep 1; done
kill -KILL -- -$P 2>/dev/null; sleep 3
for g in $(seq 0 7); do :; done
rocm-smi --showmemuse 2>/dev/null | grep "VRAM%" | awk '{print $NF}' | tr '\n' ' '; echo
