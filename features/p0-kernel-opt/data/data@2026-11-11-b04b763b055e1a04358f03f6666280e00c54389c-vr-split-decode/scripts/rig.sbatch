#!/bin/bash
#SBATCH --job-name=glm5-rig
#SBATCH --partition=batch
#SBATCH --nodes=1
#SBATCH --gpus-per-node=1
#SBATCH --time=00:10:00
#SBATCH --output=/home/sgl-chunan-zeng/glm5-lcd/rig-%j.log
U=/home/sgl-chunan-zeng
srun --container-image=$U/sglang-nightly-cu134-20261105-732d34b.sqsh --container-mounts=$U:/nfs_home,/raid/users/sgl-chunan-zeng:/local,$U/cache:/root/.cache --export=ALL bash -c '
export PYTHONPATH=/nfs_home/glm5-lcd/src/python CUDA_HOME=/usr/local/cuda PATH=/usr/local/cuda/bin:$PATH
export SGLANG_JIT_CACHE_DIR=/local/cache/glm5-rig/jit SGLANG_CACHE_DIR=/local/cache/glm5-rig/sglang; mkdir -p /local/cache/glm5-rig
cd /tmp && bash /nfs_home/glm5-lcd/${SCRIPT:-verify.sh} 2>&1 | tail -150'
echo JOB_DONE
