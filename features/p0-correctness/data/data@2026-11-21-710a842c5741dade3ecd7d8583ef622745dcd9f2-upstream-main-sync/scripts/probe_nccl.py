import ctypes, torch, os
lib=ctypes.CDLL("libnccl.so.2"); v=ctypes.c_int(); lib.ncclGetVersion(ctypes.byref(v)); print("nccl runtime ncclGetVersion", v.value)
print("libnccl mapped", sorted({l.split()[-1] for l in open("/proc/self/maps") if "libnccl.so" in l}))
print("LD_PRELOAD", os.environ.get("LD_PRELOAD"))
