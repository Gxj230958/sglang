#!/bin/bash
# Accuracy suite through the PD router. Usage: pd_acc.sh <tag>
TAG=${1:?}
cd $WORK
export HF_HOME=$PWD/eval-hf
export PATH=$PWD/sgl-eval-venv/bin:$PATH
GPQA=$PWD/sgl-eval-venv/lib/python3.12/site-packages/sgl_eval/_vendored/nemo_skills/dataset/gpqa/diamond.jsonl
ONLY=${2:-gsm8k,gpqa,ruler2}
EV=sgl-eval-venv/bin/sgl-eval
URL=http://127.0.0.1:32022/v1
mkdir -p evals/$TAG
[[ $ONLY == *gsm8k* ]] && $EV run gsm8k --base-url $URL --model glm-loop --num-examples 200 --temperature 1.0 --top-p 0.95 --max-tokens 16384 --num-threads 128 --out-dir evals/$TAG > logs/${TAG}_gsm8k.log 2>&1
[[ $ONLY == *gpqa* ]] && $EV run gpqa --from-dataset $GPQA --base-url $URL --model glm-loop --temperature 1.0 --top-p 0.95 --max-tokens 32768 --n-repeats 2 --num-threads ${GPQA_THREADS:-32} --out-dir evals/$TAG > logs/${TAG}_gpqa.log 2>&1
[[ $ONLY == *ruler2* ]] && $EV run ruler2 --base-url $URL --model glm-loop --ruler2-seq-len 32768 --ruler2-tokenizer $MODEL_PATH --temperature 1.0 --top-p 0.95 --max-tokens 8192 --num-threads 64 --out-dir evals/$TAG > logs/${TAG}_ruler2.log 2>&1
for f in gsm8k gpqa ruler2; do echo "## $f"; grep -A12 "^== " logs/${TAG}_$f.log | grep -v "it/s"; tail -2 logs/${TAG}_$f.log | grep -i error; done
echo PD_ACC_DONE
