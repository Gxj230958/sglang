#!/bin/bash
#SBATCH --job-name=glm5-lcd
#SBATCH --partition=batch
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=1
#SBATCH --gpus-per-node=4
#SBATCH --cpus-per-task=160
#SBATCH --exclusive
#SBATCH --time=01:00:00
#SBATCH --output=/home/sgl-chunan-zeng/glm5-lcd/job-%j.log
set -uo pipefail
U=/home/sgl-chunan-zeng
export MASTER_ADDR=$(scontrol show hostnames "$SLURM_JOB_NODELIST" | head -1)
IMAGE=$U/sglang-nightly-cu134-20261105-732d34b.sqsh
MOUNTS=$U:/nfs_home,/raid/users/sgl-chunan-zeng:/local,$U/cache:/root/.cache
RL=$U/glm5-lcd/runs/$SLURM_JOB_ID-$ARM
mkdir -p $RL
export RUN=/nfs_home/glm5-lcd/runs/$SLURM_JOB_ID-$ARM
echo "ARM_START arm=$ARM nodes=$SLURM_JOB_NODELIST $(date +%T)"
srun --container-image="$IMAGE" --container-mounts="$MOUNTS" --export=ALL bash /nfs_home/glm5-lcd/serve.sh &
SERVER=$!
ready=0
for ((t=0;t<${BOOT_TRIES:-420};t++)); do
  if curl -fsS http://$MASTER_ADDR:30701/health >/dev/null 2>&1; then ready=1; break; fi
  kill -0 "$SERVER" 2>/dev/null || break
  sleep 5
done
echo "ARM_READY arm=$ARM ready=$ready $(date +%T)"
if [[ $ready == 1 ]]; then
  srun --overlap --nodes=1 --ntasks=1 -w $MASTER_ADDR --container-image="$IMAGE" --container-mounts="$MOUNTS" --export=ALL \
    bash /nfs_home/glm5-lcd/${BENCH:-bench.sh} > "$RL/bench.log" 2>&1
  echo "ARM_BENCH_RC $? $(date +%T)"
fi
kill "$SERVER" 2>/dev/null; sleep 5; kill -9 "$SERVER" 2>/dev/null
echo JOB_DONE
