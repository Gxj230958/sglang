"""symm_stress.py [iters]: does a torch symmetric-memory rendezvous put the node into the
KFD queue-eviction state? Run: torchrun --nproc-per-node 8 scripts/symm_stress.py 50

Each iteration repeats SGLang's MultimemAllGatherer probe (triton_symm_mem_ag.create_state):
set the signal pad, symm_mem.empty a (128, 6144) bf16 buffer, rendezvous it over the world
group, read multicast_ptr, drop it. Between iterations it times a 2 KB all-reduce and reads
this rank's KFD evicted_ms (sysfs). Stops at the first iteration whose all-reduce exceeds
5 ms or whose evicted time grows, so a positive run costs one host reboot, not more.
"""
import gc
import glob
import os
import sys
import time

import torch
import torch.distributed as dist
import torch.distributed._symmetric_memory as symm_mem


def evicted_ms():
    total = 0
    for f in glob.glob(f"/sys/class/kfd/kfd/proc/{os.getpid()}/stats_*/evicted_ms"):
        total = max(total, int(open(f).read()))
    return total


def allreduce_us(x, n=20):
    torch.cuda.synchronize()
    t = time.perf_counter()
    for _ in range(n):
        dist.all_reduce(x)
    torch.cuda.synchronize()
    return (time.perf_counter() - t) / n * 1e6


def main():
    iters = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    dist.init_process_group("nccl")
    r = dist.get_rank()
    torch.cuda.set_device(r)
    x = torch.ones(1024, device="cuda", dtype=torch.bfloat16)
    for _ in range(5):
        dist.all_reduce(x)
    base_us, base_ev = allreduce_us(x), evicted_ms()
    if r == 0:
        print(f"baseline 2KB all-reduce {base_us:.0f} us, evicted {base_ev} ms", flush=True)
    group = dist.group.WORLD
    for it in range(iters):
        symm_mem.set_signal_pad_size(max(symm_mem.get_signal_pad_size(), 1024 * group.size() * 4))
        buf = symm_mem.empty((128, 6144), dtype=torch.bfloat16, device="cuda")
        hdl = symm_mem.rendezvous(buf, group=group)
        mc = hdl.multicast_ptr
        del hdl, buf
        gc.collect()
        torch.cuda.empty_cache()
        dist.barrier()
        us, ev = allreduce_us(x), evicted_ms()
        flag = torch.tensor([us > 5000 or ev > base_ev], device="cuda", dtype=torch.int32)
        dist.all_reduce(flag)
        if r == 0:
            print(f"iter {it}: multicast_ptr={mc} 2KB all-reduce {us:.0f} us evicted {ev} ms", flush=True)
        if flag.item():
            if r == 0:
                print(f"ONSET at iteration {it}", flush=True)
            break
    dist.destroy_process_group()


if __name__ == "__main__":
    main()
