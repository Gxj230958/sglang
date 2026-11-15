# usage: job.sh "NAME|TREE|CFG|STEPS"  steps: suite,gsm8k,gsm8k300,perf:<seed>,lp:<sizes+>
IFS='|' read -r NAME TREE CFG STEPS <<< "$1"
R=/scratch/cc-pr43; cd $R
L=$R/logs/$NAME; mkdir -p $L/mem
ST=$L/job.status; : > $ST
BUSY=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | awk '$1>2000' | wc -l)
if [ "$BUSY" -ne 0 ]; then echo "GPU_BUSY_FOREIGN $(date -u +%H:%M:%S)" >> $ST; exit 3; fi
echo boot > $L/mem/epoch
bash box/serve.sh $NAME $TREE $CFG > $L/serve-start.log 2>&1
T0=$(date +%s); ready=0
for i in $(seq 1 360); do
  curl -sf -m 3 localhost:31743/health >/dev/null && { ready=1; break; }
  tmux has-session -t ccpr43 2>/dev/null || break
  sleep 10
done
if [ $ready -ne 1 ]; then echo "server NOT_READY" >> $ST; bash box/stop.sh > /dev/null 2>&1; echo DONE >> $ST; exit 1; fi
echo "server READY $(date -u +%H:%M:%S) startup_s=$(( $(date +%s) - T0 ))" >> $ST
nvidia-smi --query-gpu=index,memory.used --format=csv,noheader | tr '\n' ';' > $L/gpu-after-ready.txt
export HF_HOME=$R/hf-home
PY=/opt/sglang/bin/python
for step in ${STEPS//,/ }; do
  curl -sf -m 5 localhost:31743/health >/dev/null || { echo "$step SKIPPED_SERVER_DOWN" >> $ST; continue; }
  case $step in
    suite) echo suite > $L/mem/epoch; $PY box/suite.py $L/suite.json smoke,det,cache > $L/suite.log 2>&1 ;;
    gsm8k) echo gsm8k > $L/mem/epoch; sgl-eval run gsm8k --base-url http://127.0.0.1:31743/v1 --temperature 1.0 --top-p 0.95 --out-dir $L/eval > $L/gsm8k.log 2>&1 ;;
    gsm8k300) echo gsm8k > $L/mem/epoch; sgl-eval run gsm8k --base-url http://127.0.0.1:31743/v1 --temperature 1.0 --top-p 0.95 --num-examples 300 --out-dir $L/eval > $L/gsm8k.log 2>&1 ;;
    perf:*) bash box/perf.sh $NAME ${step#perf:} > $L/perf.log 2>&1 ;;
    valdump) touch $R/val-dump; for k in 1 2 3; do $PY box/suite.py $L/valdump.json smoke > /dev/null 2>&1; done; sleep 3 ;;
    lp:*) $PY box/longprefill.py $L/longprefill.json $L/mem/epoch $(echo ${step#lp:} | tr '+' ',') > $L/longprefill.log 2>&1 ;;
  esac
  echo "$step rc=$? $(date -u +%H:%M:%S)" >> $ST
done
nvidia-smi --query-gpu=index,memory.used --format=csv,noheader | tr '\n' ';' > $L/gpu-at-end.txt
curl -sf -m 5 localhost:31743/health >/dev/null && echo "server ALIVE_AT_END" >> $ST || echo "server DOWN_AT_END" >> $ST
bash box/stop.sh > /dev/null 2>&1
echo DONE >> $ST
