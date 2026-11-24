#!/bin/bash
# stop_bg.sh <logname>: stop the server process group started by start_bg.sh (TERM, KILL after 30 s),
# then wait up to 10 min until no process holds a GPU (pinned HiCache pools free slowly), so the next
# launch does not start on top of it. Prints the VRAM% per GPU (memory the driver keeps after a crashed
# process is not a live process and does not hold this up).
P=$(cat /persistent/work/glm_loop_amd/logs/$1.pid)
kill -TERM -- -$P 2>/dev/null; for i in $(seq 1 30); do kill -0 $P 2>/dev/null || break; sleep 1; done
kill -KILL -- -$P 2>/dev/null; sleep 3
for i in $(seq 1 60); do
  rocm-smi --showpids 2>/dev/null | grep -q "No KFD PIDs currently running" && break
  sleep 10
done
# The driver keeps freeing for a minute or two after the processes exit: wait until VRAM stops dropping.
vram() { awk "{s+=\$1} END {printf \"%d\", s/1048576}" /sys/class/drm/card*/device/mem_info_vram_used; }
prev=$(vram); for i in $(seq 1 40); do sleep 15; cur=$(vram); [ "$cur" -ge "$prev" ] && break; prev=$cur; done
rocm-smi --showmemuse 2>/dev/null | grep "VRAM%" | awk '{print $NF}' | tr '\n' ' '; echo
