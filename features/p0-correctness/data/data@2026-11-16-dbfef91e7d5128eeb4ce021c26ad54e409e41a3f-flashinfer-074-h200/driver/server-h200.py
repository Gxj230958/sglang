import importlib.metadata as metadata
import json
import os
import runpy

if __name__ == "__main__":
    import flashinfer
    import sglang
    import torch
    names = ["flashinfer-python", "flashinfer-cubin", "flashinfer-jit-cache", "sglang-kernel", "sgl-deep-gemm", "sgl-flash-mla", "kernels", "torch", "transformers", "sgl-eval", "sgl-fa3"]
    print("SERVER_IMPORTS " + json.dumps({"pid": os.getpid(), "versions": {n: metadata.version(n) for n in names}, "flashinfer_file": flashinfer.__file__, "flashinfer_version": flashinfer.__version__, "sglang_file": sglang.__file__, "jit_providers": [{"id": x.provider_id, "version": x.version, "path": str(x.jit_cache_dir)} for x in __import__("flashinfer_jit_cache").get_jit_cache_providers()], "sgl_fa3_file": __import__("sgl_fa3").__file__, "torch_cuda": torch.version.cuda}), flush=True)
    runpy.run_module("sglang.launch_server", run_name="__main__")
