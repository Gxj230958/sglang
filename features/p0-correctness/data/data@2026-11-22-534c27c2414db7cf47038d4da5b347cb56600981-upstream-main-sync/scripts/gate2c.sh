#!/bin/bash
# usage: gate2.sh <rev-dir> <port> <leg: tp4|dep4> [extra-overlay-dir]
D=/scratch/glm5lp-upstream-sync; REV=$1; PORT=$2; LEG=$3; OVL=${4:-}
R=$D/$REV/gate-$LEG${RUN_SUFFIX:-}; mkdir -p $R; ST=$R/status
SRC=$D/$REV/src; M=/scratch/models/GLM-5-1028-Provider; PY=/opt/sglang/bin/python
FI=/scratch/codex-glm5lp-nvfp4-perf/fi074; [ -d $FI ] || FI=/scratch/shuwen-glm-hisparse-20261117/fi074
log() { echo "$(date -u +%FT%TZ) $*" | tee -a $ST; }
for p in $FI /scratch/cc-regate2/overlay $D/overlay-dg $SRC/python $OVL; do [ -d $p ] || { log "FAIL missing $p"; exit 1; }; done
for p in $(seq $PORT $((PORT+8))); do (echo > /dev/tcp/127.0.0.1/$p) 2>/dev/null && { log "FAIL port $p in use"; exit 1; }; done
[ "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l)" = 0 ] || { log "FAIL GPUs busy"; nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader >> $ST; exit 1; }
export PYTHONPATH=${OVL:+$OVL:}$SRC/python:$D/overlay-dg:$FI:/scratch/cc-regate2/overlay PYTHONNOUSERSITE=1 SGLANG_RUST_BUILD_MODE=auto CARGO_BUILD_JOBS=8
[ -n "$OVL" ] && [ -f $OVL/nvidia/nccl/lib/libnccl.so.2 ] && export LD_PRELOAD=$OVL/nvidia/nccl/lib/libnccl.so.2
export NCCL_DEBUG=VERSION SPT_NOENV=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export HF_HOME=$D/hf-home HF_HUB_CACHE=$D/hf-home/hub SGLANG_CACHE_DIR=$D/cache/$REV/sglang TRITON_CACHE_DIR=$D/cache/$REV/triton FLASHINFER_WORKSPACE_BASE=$D/cache/$REV/flashinfer TORCH_EXTENSIONS_DIR=$D/cache/$REV/torch
unset SGLANG_SIMULATE_ACC_LEN
mkdir -p $HF_HUB_CACHE
ARGS="--model-path $M --host 127.0.0.1 --port $PORT --dist-init-addr 127.0.0.1:$((PORT+1)) --tp-size 4 --kv-cache-dtype fp8_e4m3 --speculative-algorithm EAGLE --reasoning-parser glm45"
case $LEG in
  tp4) ;;
  dep4)
    export SGLANG_OPT_DEEPGEMM_MEGA_MOE_NUM_MAX_TOKENS_PER_RANK=8192 SGLANG_DP_USE_GATHERV=1
    ARGS="$ARGS --ep-size 4 --attn-dp-size 4 --moe-runner-backend megamoe --mem-fraction-static 0.9 --chunked-prefill-size 32768" ;;
  *) log "FAIL unknown leg $LEG"; exit 1 ;;
esac
$PY - > $R/versions.txt 2>&1 <<'PYV'
import importlib.metadata as m, importlib.util, os, sglang, torch
for p in ["torch","flashinfer-python","sglang-kernel","sgl-deep-gemm","sgl-flash-mla","transformers","sgl-deep-ep","tilelang","apache-tvm-ffi","xgrammar","triton","nvidia-nccl-cu13"]:
    try: print(p, m.version(p), m.distribution(p).locate_file(""))
    except Exception as e: print(p, "MISSING")
for mod in ["deep_gemm","deep_ep","flashinfer","sgl_kernel"]:
    s=importlib.util.find_spec(mod); print("module", mod, s.origin if s else None)
print("torch.cuda.nccl.version (compile-time)", torch.cuda.nccl.version())
import ctypes
lib=ctypes.CDLL("libnccl.so.2"); v=ctypes.c_int(); lib.ncclGetVersion(ctypes.byref(v)); print("nccl runtime ncclGetVersion", v.value)
print("libnccl mapped", sorted({l.split()[-1] for l in open("/proc/self/maps") if "libnccl.so" in l}))
print("LD_PRELOAD", os.environ.get("LD_PRELOAD"))
print("sglang from", sglang.__file__)
PYV
cd $SRC
log "leg=$LEG env: MEGA_MOE_NUM_MAX_TOKENS_PER_RANK=${SGLANG_OPT_DEEPGEMM_MEGA_MOE_NUM_MAX_TOKENS_PER_RANK:-unset} DP_USE_GATHERV=${SGLANG_DP_USE_GATHERV:-unset} overlay=${OVL:-none}"
log "launch: $ARGS"
setsid $PY -m sglang.launch_server $ARGS > $R/server.log 2>&1 &
SERVER=$!; echo $SERVER > $R/server.pid
ready=0
for i in $(seq 240); do
  curl -sf -m 5 http://127.0.0.1:$PORT/health_generate > /dev/null && { ready=1; break; }
  kill -0 $SERVER 2> /dev/null || break
  sleep 10
done
if [ $ready = 1 ]; then
  log "ready"; curl -s -m 10 http://127.0.0.1:$PORT/get_server_info > $R/server_info.json
  for pid in $(pgrep -s $SERVER); do echo "pid=$pid comm=$(cat /proc/$pid/comm 2>/dev/null) preload=$(tr '\0' '\n' < /proc/$pid/environ 2>/dev/null | grep -c '^LD_PRELOAD=') libs=$(grep -oE '/[^ ]*(libnccl\.so[^ ]*|deep_ep[^ ]*\.so|deep_gemm[^ ]*\.so)' /proc/$pid/maps 2>/dev/null | sort -u | tr '\n' ' ')"; done > $R/loaded_libs.txt
  log "eval start"
  env -u HF_HUB_OFFLINE -u TRANSFORMERS_OFFLINE -u LD_PRELOAD HF_HOME=$D/eval-hf $D/eval-venv/bin/sgl-eval run gsm8k --base-url http://127.0.0.1:$PORT/v1 --temperature 1.0 --top-p 0.95 --out-dir $R/eval > $R/eval.log 2>&1
  log "eval rc=$?"
  kill -0 $SERVER 2> /dev/null && log "server alive after eval" || log "server DIED during eval"
else
  log "FAIL not ready (alive=$(kill -0 $SERVER 2>/dev/null && echo 1 || echo 0))"
  tail -40 $R/server.log >> $ST
fi
kill -TERM -- -$SERVER 2> /dev/null
for i in $(seq 30); do kill -0 $SERVER 2> /dev/null || break; sleep 5; done
kill -KILL -- -$SERVER 2> /dev/null; sleep 10
log "stopped; gpu apps: $(nvidia-smi --query-compute-apps=pid --format=csv,noheader | wc -l)"
log "DONE"
