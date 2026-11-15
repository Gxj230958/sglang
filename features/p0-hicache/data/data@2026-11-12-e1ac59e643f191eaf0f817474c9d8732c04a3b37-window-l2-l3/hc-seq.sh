L=/scratch/cc-swa/logs/hc-swa; B=http://127.0.0.1:30000/v1
python3 /scratch/cc-swa/bin/midfork.py $B $L/midfork-a.json m2 > $L/midfork-a.log 2>&1
python3 /scratch/cc-swa/bin/hicache.py $B $L/anchor.json fill 70 l2fill2 > $L/fill2.log 2>&1
grep -c 'HiCache prefetch success' $L/serve.log > $L/prefetch-before-b.txt
python3 /scratch/cc-swa/bin/midfork.py $B $L/midfork-b.json m2 > $L/midfork-b.log 2>&1
grep -c 'HiCache prefetch success' $L/serve.log > $L/prefetch-after-b.txt
/scratch/cc-swa/evalenv/bin/sgl-eval run gsm8k --base-url $B --temperature 1.0 --top-p 0.95 --num-threads 64 --out-dir $L/eval > $L/gsm8k.log 2>&1
echo "EVAL_DONE rc=$?" > $L/eval.status
