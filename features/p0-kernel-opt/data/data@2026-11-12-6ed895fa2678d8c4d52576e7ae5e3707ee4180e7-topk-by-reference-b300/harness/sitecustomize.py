import os, sys, threading, time

_dir = os.environ.get("GLMVAL_MEMLOG")


def _report():
    path = os.path.join(_dir, "mem-%d.log" % os.getpid())
    epoch_file = os.path.join(_dir, "epoch")
    last, epoch = None, None
    while True:
        time.sleep(3)
        torch = sys.modules.get("torch")
        if torch is None or not hasattr(torch, "cuda") or not torch.cuda.is_initialized():
            continue
        try:
            dev = torch.cuda.current_device()
            try:
                now_epoch = open(epoch_file).read().strip()
            except OSError:
                now_epoch = ""
            if now_epoch != epoch:
                epoch = now_epoch
                torch.cuda.reset_peak_memory_stats(dev)
                last = None
            free, _ = torch.cuda.mem_get_info(dev)
            row = (torch.cuda.max_memory_allocated(dev) >> 20, torch.cuda.max_memory_reserved(dev) >> 20)
            if row != last:
                last = row
                with open(path, "a") as f:
                    f.write("%s epoch=%s dev=%d alloc_mib=%d max_alloc_mib=%d max_reserved_mib=%d free_mib=%d\n" % (
                        time.strftime("%H:%M:%S"), epoch, dev, torch.cuda.memory_allocated(dev) >> 20, row[0], row[1], free >> 20))
        except Exception as e:
            with open(path, "a") as f:
                f.write("ERR %r\n" % (e,))
            return


if _dir:
    threading.Thread(target=_report, daemon=True).start()
