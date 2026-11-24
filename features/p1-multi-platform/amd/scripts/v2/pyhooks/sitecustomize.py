# Hang diagnostics for every Python process of a server launched by scripts/launch.sh
# (PYTHONPATH puts this directory first, so spawned ranks import it too):
#  - prctl(PR_SET_PTRACER, ANY): yama ptrace_scope=1 otherwise lets only ancestors attach,
#    so `py-spy dump --pid <rank>` (scripts/doctor.py) works from any shell, non-destructively.
#  - SIGUSR1 -> faulthandler dump of all threads to stderr; the process keeps running.
# Never diagnose a stuck rank with SIGABRT/SIGQUIT: the core dump of a ROCm process streams
# hundreds of GB of mappings to the host's apport.
import ctypes
import faulthandler
import signal

try:
    ctypes.CDLL(None, use_errno=True).prctl(0x59616D61, ctypes.c_ulong(-1), 0, 0, 0)
except Exception:
    pass
try:
    faulthandler.register(signal.SIGUSR1, all_threads=True, chain=False)
except Exception:
    pass

# chain to the distribution's sitecustomize (apport hook), which this module shadows
try:
    with open("/usr/lib/python3.12/sitecustomize.py") as _f:
        exec(compile(_f.read(), _f.name, "exec"))
except Exception:
    pass
