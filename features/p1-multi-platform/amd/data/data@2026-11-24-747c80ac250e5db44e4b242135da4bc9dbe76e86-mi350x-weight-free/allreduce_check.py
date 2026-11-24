import os, time, torch, torch.distributed as dist
dist.init_process_group("nccl"); r=dist.get_rank(); torch.cuda.set_device(r)
for n in (1<<12, 1<<20, 1<<26):
    x=torch.full((n,), float(r+1), device="cuda", dtype=torch.bfloat16)
    dist.all_reduce(x); torch.cuda.synchronize()
    ok = bool((x==36).all())
    t=time.time()
    for _ in range(20): dist.all_reduce(x)
    torch.cuda.synchronize(); dt=(time.time()-t)/20
    if r==0: print(f"n={n} ok={ok} {dt*1e6:.0f}us busbw={2*7/8*n*2/dt/1e9:.1f}GB/s", flush=True)
dist.destroy_process_group()
