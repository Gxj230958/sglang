#!/bin/bash
# wait_bg.sh <logname>: block until ready/failed; print key lines
L=/persistent/work/glm_loop_amd/logs/$1.log; P=$(cat /persistent/work/glm_loop_amd/logs/$1.pid)
until grep -qE "The server is fired up|Traceback" $L || ! kill -0 $P 2>/dev/null; do sleep 3; done
sleep 2
grep -v "^\[aiter\]\|server_args=" $L | grep -E "fired up|Error|KV Cache is allocated|Load weight end|Capture cuda graph end" | head -12 | cut -c1-300
if grep -q Traceback $L; then echo "--- traceback:"; grep -v "^\[aiter\]" $L | grep -m1 -A60 Traceback | grep -E "File \"/persistent|Error|error" | tail -12 | cut -c1-300; fi
kill -0 $P 2>/dev/null && echo ALIVE || echo DEAD
