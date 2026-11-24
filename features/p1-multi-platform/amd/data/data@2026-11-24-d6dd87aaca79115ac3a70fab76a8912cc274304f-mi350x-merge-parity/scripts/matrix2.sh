#!/bin/bash
# matrix2.sh: rerun CP8, HiSparse and HiCache on the cleanup branch (SGL_SRC) after the first matrix pass.
# Each: launch, smoke + capped GSM8K (acc_suite.sh), config-specific probes, stop. Status in acc/matrix.status.
cd /scratch/mobius/mi350x
ST=/scratch/mobius/mi350x/acc/matrix.status
M=/scratch/hf_home/hub/models--RadixArk--GLM-5-1028-Provider/snapshots/9c24449260e89d2d2bb6ed8f92d5f386c04ad7ff
MTP="--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4 --speculative-draft-model-path $M --enable-cache-report"
DEP8="--tp-size 8 --attn-dp-size 8 --ep-size 8 --moe-a2a-backend none --mem-fraction-static 0.85 --context-length 65536 --chunked-prefill-size 32768 --max-running-requests 256 --cuda-graph-max-bs-decode 32"
TP8="--mem-fraction-static 0.75 --context-length 65536 --chunked-prefill-size 32768 --max-running-requests 32 --cuda-graph-max-bs-decode 32"
export SGLANG_HICACHE_FILE_BACKEND_STORAGE_DIR=/scratch/mobius/mi350x/hicache-l3
stop() { P=$(cat logs/$1.pid); kill -TERM -- -$P 2>/dev/null; while pgrep -g $P >/dev/null; do sleep 2; done
         until [ "$(rocm-smi --showmemuse | grep -c 'VRAM%): 0$')" = 8 ]; do sleep 3; done; }
up() { scripts/start_bg.sh "$@" >> $ST; scripts/wait_ready.sh $1 > logs/$1.ready.txt 2>&1; grep -v setlocale logs/$1.ready.txt | head -1 | sed "s/^/$1 startup: /" >> $ST; grep -q READY logs/$1.ready.txt; }
run() { NAME=$1; shift; echo "=== $NAME $(date +%T)" >> $ST
        if up $NAME 30000 "$@"; then scripts/acc_suite.sh $NAME 30000 smoke gsm8k >> $ST 2>&1; return 0; else return 1; fi; }

export SGL_SRC=/scratch/mobius/cleanup-wt
echo "=== MATRIX2 start $(date +%T) src=$(git -C $SGL_SRC rev-parse --short HEAD)+wt" >> $ST

# D: prefill CP8 (interleave) with breakable prefill CUDA graphs + MTP
run cp8-graphs --tp-size 8 --ep-size 8 --moe-a2a-backend none --mem-fraction-static 0.85 --context-length 65536 --chunked-prefill-size 32768 --max-running-requests 256 --cuda-graph-max-bs-decode 32 --enable-prefill-cp --cp-strategy interleave --attn-cp-size 8 --cuda-graph-backend-prefill breakable $MTP; stop cp8-graphs

# E: TP8 + MTP + HiSparse; HiSparse needs the radix cache off (CUDA runs it on a PD decode server)
run tp8-hisparse $TP8 --disable-prefill-cuda-graph --disable-radix-cache --enable-hisparse --hisparse-config '{"top_k": 2048, "device_buffer_size": 4096, "host_to_device_ratio": 6}' $MTP; stop tp8-hisparse

# C: DEP8 + MTP + HiCache L2 (host) and L3 (file): restore probes, then GSM8K on L2
rm -rf /scratch/mobius/mi350x/hicache-l3; mkdir -p /scratch/mobius/mi350x/hicache-l3 acc/dep8-hc
HC="--enable-hierarchical-cache --hicache-size 200 --hicache-write-policy write_through --hicache-storage-backend file"
if run dep8-hc $DEP8 --disable-prefill-cuda-graph $HC $MTP; then
  B=http://127.0.0.1:30000/v1
  for step in "ref" "fill 260" "read"; do DP_RANK=3 /opt/venv/bin/python scripts/hicache.py $B acc/dep8-hc/hc.json $step 2>&1 | cut -c1-300 | sed "s/^/hicache L2 $step: /" >> $ST; done
fi
stop dep8-hc
if up dep8-hc-l3 30000 $DEP8 --disable-prefill-cuda-graph $HC $MTP; then
  DP_RANK=3 /opt/venv/bin/python scripts/hicache.py http://127.0.0.1:30000/v1 acc/dep8-hc/hc.json read 2>&1 | cut -c1-300 | sed "s/^/hicache L3 read after restart: /" >> $ST
fi
stop dep8-hc-l3
echo "=== MATRIX2 DONE $(date +%T)" >> $ST
