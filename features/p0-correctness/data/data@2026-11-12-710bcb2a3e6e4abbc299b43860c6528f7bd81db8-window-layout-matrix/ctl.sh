N=$1
/scratch/cc-swa/bin/wait.sh $N 30000 120 > /scratch/cc-swa/logs/$N/wait.log 2>&1 || { echo NOT_READY; tail -5 /scratch/cc-swa/logs/$N/wait.log; exit 1; }
python3 /scratch/cc-swa/bin/stress.py http://127.0.0.1:30000/v1 /scratch/cc-swa/logs/$N/stress2.jsonl 100 8 s2 > /scratch/cc-swa/logs/$N/stress2.log 2>&1; echo STRESS_DONE >> /scratch/cc-swa/logs/$N/stress2.log
