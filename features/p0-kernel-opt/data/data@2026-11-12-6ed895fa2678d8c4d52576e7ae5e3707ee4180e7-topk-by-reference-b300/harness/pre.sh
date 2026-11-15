R=/scratch/cc-pr43; cd $R; mkdir -p logs/pre
export PYTHONPATH=$R/src-clean/python:$R/overlay CUDA_VISIBLE_DEVICES=0 HF_HOME=$R/hf-home
PY=/opt/sglang/bin/python
$PY box/micro.py logs/pre/micro.json > logs/pre/micro.log 2>&1; echo "micro rc=$?" > logs/pre/status
(cd src-clean && $PY -m pytest test/registered/kernels/ops/attention/test_glm_loop_attention.py -q -p no:cacheprovider > $R/logs/pre/kernel-clean.log 2>&1; echo "kernel-clean rc=$?" >> $R/logs/pre/status)
(cd src-clean && $PY -m pytest test/registered/unit/models/test_glm_loop.py -q -p no:cacheprovider > $R/logs/pre/unit-clean.log 2>&1; echo "unit-clean rc=$?" >> $R/logs/pre/status)
(cd src-base && PYTHONPATH=$R/src-base/python:$R/overlay $PY -m pytest test/registered/unit/models/test_glm_loop.py -q -p no:cacheprovider > $R/logs/pre/unit-base.log 2>&1; echo "unit-base rc=$?" >> $R/logs/pre/status)
timeout 1500 $PY box/topk_ownership.py logs/pre/topk_ownership.json > logs/pre/topk_ownership.log 2>&1; echo "topk_ownership rc=$?" >> logs/pre/status
echo DONE >> logs/pre/status
