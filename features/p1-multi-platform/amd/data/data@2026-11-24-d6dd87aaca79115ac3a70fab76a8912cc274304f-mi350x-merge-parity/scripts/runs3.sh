#!/bin/bash
# runs3.sh: CP8 with the HIP prefill-CP fix, HiSparse at host ratio 2; cleanup tree.
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
echo "=== RUNS3 start $(date +%T) src=$(git -C $SGL_SRC rev-parse --short HEAD)+wt" >> $ST
run cp8-graphs --tp-size 8 --ep-size 8 --moe-a2a-backend none --mem-fraction-static 0.85 --context-length 65536 --chunked-prefill-size 32768 --max-running-requests 256 --cuda-graph-max-bs-decode 32 --enable-prefill-cp --cp-strategy interleave --attn-cp-size 8 --cuda-graph-backend-prefill breakable $MTP; stop cp8-graphs
# host_to_device_ratio 2: ratio 6 asks 425 GB host per rank, more than this box has
run tp8-hisparse $TP8 --disable-prefill-cuda-graph --disable-radix-cache --enable-hisparse --hisparse-config '{"top_k": 2048, "device_buffer_size": 4096, "host_to_device_ratio": 2}' $MTP; stop tp8-hisparse
echo "=== RUNS3 DONE $(date +%T)" >> $ST
