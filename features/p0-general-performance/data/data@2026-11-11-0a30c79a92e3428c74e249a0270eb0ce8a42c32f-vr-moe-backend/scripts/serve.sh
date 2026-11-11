#!/bin/bash
R=/nfs_home/glm5-lcd
NL=/local/cache/glm5-lcd
export PYTHONPATH=${FMPKG:-/nfs_home/vr-dep32/stack/pkg-fmla}:${DGPKG:-/nfs_home/vr-dep32/stack/pkg-dg}:${SRCDIR:-$R/src/python}
export NCCL_SOCKET_IFNAME=eth0 GLOO_SOCKET_IFNAME=eth0 NCCL_CUMEM_ENABLE=1 NCCL_MNNVL_ENABLE=1 NCCL_NVLS_ENABLE=1
export TRITON_PTXAS_PATH=/usr/local/cuda/bin/ptxas TRITON_PTXAS_BLACKWELL_PATH=/usr/local/cuda/bin/ptxas
export TORCH_DISTRIBUTED_DEFAULT_TIMEOUT=1800
export CUDA_HOME=/usr/local/cuda CUDA_PATH=/usr/local/cuda PATH=/usr/local/cuda/bin:$PATH
export SGLANG_CACHE_DIR=$NL/sglang TRITON_CACHE_DIR=$NL/triton TORCHINDUCTOR_CACHE_DIR=$NL/inductor CUDA_CACHE_PATH=$NL/nv
export FLASHINFER_WORKSPACE_BASE=$NL/flashinfer-ws SGLANG_CUTE_AOT_CACHE_DIR=$NL/cute_aot SGLANG_JIT_CACHE_DIR=$NL/jit SGLANG_DG_CACHE_DIR=$NL/deep_gemm DG_JIT_CACHE_DIR=$NL/deep_gemm
export CPATH=/nfs_home/dsv41-refresh-20261105/deps/usr/include CPLUS_INCLUDE_PATH=/nfs_home/dsv41-refresh-20261105/deps/usr/include
export SGLANG_RUST_BUILD_MODE=never HF_HUB_OFFLINE=1
export SGLANG_SIMULATE_ACC_LEN=${ACC:-2.5}
[ -n "${XENV:-}" ] && export $XENV
mkdir -p "$NL" "$RUN"
M=/local/models/GLM-5-1028-Provider; [ -f $M/config.json ] || M=/nfs_home/models/GLM-5-1028-Provider
echo MODEL=$M > "$RUN/model-$SLURM_PROCID.txt"
python3 -c "
import os, deep_gemm, sglang, flash_mla
assert sglang.__file__.startswith(os.environ.get('SRCDIR', '/nfs_home/glm5-lcd/src/python')), sglang.__file__
print('ARM', os.environ.get('ARM'), sglang.__file__, deep_gemm.__file__, flash_mla.__file__, 'xenv', os.environ.get('XENV'))
" > "$RUN/arm-$SLURM_PROCID.txt" 2>&1 || exit 1
exec python3 -m sglang.launch_server --model-path $M \
  --nnodes 2 --node-rank $SLURM_PROCID --dist-init-addr $MASTER_ADDR:5201 --host 0.0.0.0 --port 30701 \
  --tp-size 8 ${MOE---moe-runner-backend deep_gemm} \
  --mem-fraction-static ${MEMFRAC:-0.85} --context-length 140000 \
  --max-running-requests ${MRR:-32} --cuda-graph-max-bs-decode ${MRR:-32} ${CGBS:+--cuda-graph-bs-decode $CGBS} --disable-prefill-cuda-graph \
  --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 \
  --speculative-num-draft-tokens 4 --speculative-draft-model-path $M \
  --reasoning-parser glm45 --tool-call-parser glm47 \
  --weight-loader-prefetch-checkpoints --model-loader-extra-config '{"enable_multithread_load": true}' \
  --watchdog-timeout 3600 --skip-server-warmup ${EXTRA_ARGS:-} > "$RUN/server-$SLURM_PROCID.log" 2>&1
