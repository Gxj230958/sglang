"""2-rank all-reduce loop; each rank listens to its own KFD SMI events (queue eviction triggers:
0 SVM, 1 USERPTR, 2 TTM, 3 SUSPEND, 4 CRIU checkpoint, 5 CRIU restore)."""
import collections, os, threading, time
import torch, torch.distributed as dist
import amdsmi

stop = threading.Event(); events = []
def listen():
    amdsmi.amdsmi_init()
    names = {e.value: e.name for e in amdsmi.AmdSmiEvtNotificationType}
    hs = amdsmi.amdsmi_get_processor_handles()
    mask = sum(1 << (v - 1) for v in names if v)
    for h in hs:
        amdsmi.amdsmi_init_gpu_event_notification(h); amdsmi.amdsmi_set_gpu_event_notification_mask(h, mask)
    while not stop.is_set():
        try:
            r = amdsmi.amdsmi_get_gpu_event_notification(200)
        except Exception:
            continue
        for ev in (r or {}).get("data", []):
            events.append((time.time(), names.get(ev.get("event")), " ".join(str(ev.get("message", "")).split())))
th = threading.Thread(target=listen, daemon=True); th.start(); time.sleep(1)
dist.init_process_group("nccl"); r = dist.get_rank(); torch.cuda.set_device(r)
x = torch.ones(1024, device="cuda", dtype=torch.bfloat16)
for _ in range(3): dist.all_reduce(x)
torch.cuda.synchronize(); t = time.time()
for _ in range(40): dist.all_reduce(x)
torch.cuda.synchronize(); dt = (time.time() - t) / 40
time.sleep(0.5); stop.set(); th.join(2)
c = collections.Counter(n for _, n, _ in events)
ev = [e for e in events if e[1] in ("QUEUE_EVICTION", "QUEUE_RESTORE", "GPU_PRE_RESET", "GPU_POST_RESET", "VMFAULT", "UNMAP_FROM_GPU")]
print(f"rank{r} pid{os.getpid()} 2KB allreduce {dt*1e6:.0f} us; events {dict(c)}", flush=True)
for t_, n, m in ev[:8]:
    print(f"  rank{r} {n}: {m[:160]}", flush=True)
dist.destroy_process_group()
