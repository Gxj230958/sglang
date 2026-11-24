#!/opt/venv/bin/python
"""doctor.py <name> [--interval S] [--stall S]: watch a server started by start_bg.sh
without ever stopping or killing it.

Every interval it logs, to logs/<name>.doctor.log, the server log's growth, the CUDA graph
capture shape in progress, and per rank (amd-smi process): KFD queue-eviction time and GFX
busy time over the interval. Queue evictions are the signature of the node degradation seen
after the MTP draft capture (each eviction costs KFD's ~100 ms restore delay).

Before the server is up: when the log stops growing for --stall seconds or one CUDA graph
capture shape lasts that long. After: when the log stops growing for --stall seconds while
the last batch line shows running or queued requests (an idle server is silent). Always: when
a rank spends >30% of the interval evicted. it writes every rank's Python + native stack
(py-spy dump; the ranks opt in to tracing via pyhooks/sitecustomize.py) to
logs/<name>.doctor/<HHMMSS>/, again every 5 minutes while it persists. If py-spy fails it
sends SIGUSR1, which faulthandler turns into a stack dump in the server log. Exits when
the server is gone.
"""

import argparse
import json
import os
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = "/persistent/work/glm_loop_amd"
CAPTURE = re.compile(rb"Capturing batches \(bs=(\d+)")
READY = b"The server is fired up"
BATCH = re.compile(rb"(?:Decode|Prefill) batch.*?#running-req: (\d+).*?#queue-req: (\d+)")


def ranks(pgid):
    out = {}
    for p in os.listdir("/proc"):
        if not p.isdigit():
            continue
        try:
            stat = open(f"/proc/{p}/stat").read()
            fields = stat[stat.rindex(")") + 2 :].split()
            if fields[0] == "Z" or int(fields[2]) != pgid:
                continue
            cmd = open(f"/proc/{p}/cmdline", "rb").read().replace(b"\0", b" ").decode()
        except (OSError, ValueError):
            continue
        m = re.search(r"sglang::scheduler\S*?TP(\d+)", cmd)
        if m:
            out[int(p)] = f"tp{m.group(1)}"
        elif cmd.startswith("sglang::scheduler"):
            out[int(p)] = f"sched{p}"
    return out


def gpu_procs():
    try:
        raw = subprocess.run(
            ["amd-smi", "process", "--json"], capture_output=True, text=True, timeout=45
        ).stdout
        data = json.loads(raw)
    except Exception:
        return {}
    out = {}
    for gpu in data:
        for entry in gpu.get("process_list", []):
            info = entry.get("process_info", entry)
            if not isinstance(info, dict) or "pid" not in info:
                continue
            ev = info.get("evicted_time", {}).get("value", 0)
            gfx = info.get("usage", {}).get("gfx", {}).get("value", 0)
            out[int(info["pid"])] = (
                ev if isinstance(ev, int) else 0,
                gfx if isinstance(gfx, int) else 0,
            )
    return out


def dump(name, rk, reason):
    d = f"{ROOT}/logs/{name}.doctor/{time.strftime('%H%M%S')}"
    os.makedirs(d, exist_ok=True)
    open(f"{d}/reason.txt", "w").write(reason + "\n")

    def one(item):
        pid, tag = item
        r = subprocess.run(
            ["py-spy", "dump", "--native", "--pid", str(pid)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if r.returncode != 0:
            os.kill(pid, 10)  # SIGUSR1 -> faulthandler, non-destructive
            return f"{tag}: py-spy failed ({r.stderr.strip()[:200]}); sent SIGUSR1"
        open(f"{d}/{tag}.txt", "w").write(r.stdout)
        return f"{tag}: ok"

    with ThreadPoolExecutor(len(rk) or 1) as ex:
        results = list(ex.map(one, sorted(rk.items(), key=lambda kv: kv[1])))
    return d, results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--interval", type=float, default=15)
    ap.add_argument("--stall", type=float, default=90)
    a = ap.parse_args()
    pgid = int(open(f"{ROOT}/logs/{a.name}.pid").read())
    logf = f"{ROOT}/logs/{a.name}.log"
    out = open(f"{ROOT}/logs/{a.name}.doctor.log", "a", buffering=1)
    last_size, last_growth = 0, time.time()
    shape, shape_since = None, time.time()
    ready, busy_reqs = READY in open(logf, "rb").read(), False
    prev = {}
    last_dump = 0.0
    while True:
        try:
            os.kill(pgid, 0)
            if open(f"/proc/{pgid}/stat").read().split(")")[1].split()[0] == "Z":
                raise ProcessLookupError
        except (ProcessLookupError, FileNotFoundError):
            out.write(f"{time.strftime('%H:%M:%S')} server gone\n")
            return
        now = time.time()
        size = os.path.getsize(logf)
        if size != last_size:
            last_size, last_growth = size, now
            with open(logf, "rb") as f:
                f.seek(max(0, size - 65536))
                tail = f.read()
            caps = CAPTURE.findall(tail)
            if caps and caps[-1] != shape:
                shape, shape_since = caps[-1], now
            ready = ready or READY in tail
            batches = BATCH.findall(tail)
            if batches:
                busy_reqs = any(int(x) > 0 for x in batches[-1])
        rk = ranks(pgid)
        gp = gpu_procs()
        evict, busy = [], []
        storm = False
        for pid, tag in sorted(rk.items(), key=lambda kv: kv[1]):
            ev, gfx = gp.get(pid, (0, 0))
            pev, pgfx, pt = prev.get(pid, (ev, gfx, now - a.interval))
            dt = max(now - pt, 1e-3)
            evict.append(f"{(ev - pev) / (dt * 1e3):.0%}")
            busy.append(f"{(gfx - pgfx) / (dt * 1e9):.0%}")
            storm |= (ev - pev) > 0.3 * dt * 1e3
            prev[pid] = (ev, gfx, now)
        stalled = now - last_growth >= a.stall and (not ready or busy_reqs)
        stuck_shape = not ready and shape is not None and now - shape_since >= a.stall
        reasons = [
            r
            for r, on in (
                (f"log silent {now - last_growth:.0f}s", stalled),
                (f"capture bs={shape.decode() if shape else '-'} for {now - shape_since:.0f}s", stuck_shape),
                ("queue-eviction storm", storm),
            )
            if on
        ]
        line = (
            f"{time.strftime('%H:%M:%S')} ranks={len(rk)} log+={time.strftime('%M:%S', time.gmtime(now - last_growth))}"
            f" {'up' if ready else 'bs=' + (shape.decode() if shape else '-')} evicted={','.join(evict)} gfx={','.join(busy)}"
        )
        if reasons:
            line += "  ALERT: " + "; ".join(reasons)
        out.write(line + "\n")
        if reasons and rk and now - last_dump >= 300:
            last_dump = now
            d, res = dump(a.name, rk, "; ".join(reasons))
            out.write(f"    stacks -> {d}: {' '.join(res)}\n")
        time.sleep(max(0.0, a.interval - (time.time() - now)))


if __name__ == "__main__":
    main()
