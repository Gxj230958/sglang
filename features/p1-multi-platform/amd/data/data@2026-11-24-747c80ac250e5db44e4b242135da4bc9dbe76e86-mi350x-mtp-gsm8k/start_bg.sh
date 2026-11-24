#!/bin/bash
# start_bg.sh <logname> <port> [launch.sh args...]; pid file holds the server's process-group id.
cd /scratch/mobius/mi350x
NAME=$1; shift
setsid nohup scripts/launch.sh "$@" > logs/$NAME.log 2>&1 < /dev/null &
echo $! > logs/$NAME.pid
sleep 1
setsid nohup /opt/venv/bin/python scripts/doctor.py $NAME > logs/$NAME.doctor.out 2>&1 < /dev/null &
echo "pid $(cat logs/$NAME.pid) log logs/$NAME.log"
