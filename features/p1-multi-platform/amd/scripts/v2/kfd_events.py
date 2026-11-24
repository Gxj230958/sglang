"""Stream KFD SMI events (queue eviction/restore with trigger, resets, faults) for N seconds."""
import collections, sys, time
import amdsmi
dur = float(sys.argv[1]) if len(sys.argv) > 1 else 30
amdsmi.amdsmi_init()
hs = amdsmi.amdsmi_get_processor_handles()
names = {e.value: e.name for e in amdsmi.AmdSmiEvtNotificationType}
mask = 0
for v in names:
    if v:
        mask |= 1 << (v - 1)
for h in hs:
    amdsmi.amdsmi_init_gpu_event_notification(h)
    amdsmi.amdsmi_set_gpu_event_notification_mask(h, mask)
cnt = collections.Counter(); samples = []
t0 = time.time()
while time.time() - t0 < dur:
    try:
        r = amdsmi.amdsmi_get_gpu_event_notification(500)
    except Exception:
        continue
    for ev in (r or {}).get("data", []):
        name = names.get(ev.get("event"), ev.get("event"))
        msg = " ".join(str(ev.get("message", "")).split())
        cnt[name] += 1
        if name in ("QUEUE_EVICTION", "QUEUE_RESTORE", "GPU_PRE_RESET", "GPU_POST_RESET", "VMFAULT", "UNMAP_FROM_GPU", "MIGRATE_START") and len(samples) < 40:
            samples.append(f"{time.time()-t0:8.3f} {name}: {msg[:200]}")
for h in hs:
    amdsmi.amdsmi_stop_gpu_event_notification(h)
print("counts:", dict(cnt))
print("\n".join(samples))
