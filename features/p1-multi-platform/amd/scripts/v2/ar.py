import os, time, torch, torch.distributed as dist
dist.init_process_group("nccl"); r = dist.get_rank(); torch.cuda.set_device(r)
t0 = time.time(); x = torch.ones(1, device="cuda"); dist.all_reduce(x); torch.cuda.synchronize()
if r == 0: print("first allreduce (comm init)", round(time.time() - t0, 2), flush=True)
for n in (1 << 10, 1 << 20, 1 << 26):
    x = torch.ones(n, device="cuda", dtype=torch.bfloat16)
    for _ in range(3): dist.all_reduce(x)
    torch.cuda.synchronize(); t = time.time()
    for _ in range(20): dist.all_reduce(x)
    torch.cuda.synchronize(); dt = (time.time() - t) / 20
    if r == 0: print(f"{n*2/1e6:.3f} MB  {dt*1e6:.0f} us  busbw {2*7/8*n*2/dt/1e9:.0f} GB/s", flush=True)
t = time.time()
for _ in range(100): dist.barrier()
if r == 0: print("100 barriers", round(time.time() - t, 3), flush=True)
dist.destroy_process_group()
