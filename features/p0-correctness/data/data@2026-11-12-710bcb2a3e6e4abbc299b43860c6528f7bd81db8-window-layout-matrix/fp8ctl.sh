N=$1; L=/scratch/cc-swa/logs/$N
/scratch/cc-swa/bin/wait.sh $N 30000 150 > $L/wait.log 2>&1 || { echo NOT_READY > $L/ctl.status; exit 1; }
python3 /scratch/cc-swa/bin/probe.py http://127.0.0.1:30000/v1 $L/probe.json 300 3000 9000 24000 > $L/probe.log 2>&1
python3 /scratch/cc-swa/bin/stress.py http://127.0.0.1:30000/v1 $L/stress-c1.jsonl 30 1 f1 3000 9000 > $L/stress-c1.log 2>&1
python3 /scratch/cc-swa/bin/stress.py http://127.0.0.1:30000/v1 $L/stress-c8.jsonl 100 8 f2 3000 9000 20000 > $L/stress-c8.log 2>&1
echo CTL_DONE > $L/ctl.status
