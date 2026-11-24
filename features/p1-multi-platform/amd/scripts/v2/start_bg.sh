#!/bin/bash
# start_bg.sh <logname> <port> [launch.sh args...]; writes logs/<logname>.pid with the server PID
# and starts scripts/doctor.py (non-destructive stall/eviction monitor) next to it.
cd /persistent/work/glm_loop_amd
NAME=$1; shift
setsid nohup scripts/launch.sh "$@" > logs/$NAME.log 2>&1 < /dev/null &
echo $! > logs/$NAME.pid
sleep 1
setsid nohup /opt/venv/bin/python scripts/doctor.py $NAME > logs/$NAME.doctor.out 2>&1 < /dev/null &
echo "pid $(cat logs/$NAME.pid) log logs/$NAME.log doctor logs/$NAME.doctor.log"
