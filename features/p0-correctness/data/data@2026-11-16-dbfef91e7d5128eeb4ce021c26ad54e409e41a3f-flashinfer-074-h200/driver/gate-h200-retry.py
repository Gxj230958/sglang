import datetime
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import urllib.request

R = Path("/scratch/codex-fi074")
arm = sys.argv[1]
L = R / arm
L.mkdir(exist_ok=False)
status = L / "status"
def mark(s):
    with status.open("a") as f:
        f.write(datetime.datetime.now(datetime.timezone.utc).isoformat() + " " + s + "\n")
def get(path):
    return urllib.request.urlopen("http://127.0.0.1:31874" + path, timeout=5).read()
def snapshot(name):
    for endpoint in ["metrics", "get_server_info"]:
        try:
            (L / (name + "-" + endpoint + ".txt")).write_bytes(get("/" + endpoint))
        except Exception as exc:
            mark(repr(exc))
def stop(p):
    if p is None:
        return
    try:
        os.killpg(p.pid, signal.SIGTERM)
        time.sleep(8)
        os.killpg(p.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        p.wait(timeout=10)
    except subprocess.TimeoutExpired:
        pass

env = os.environ.copy()
env["PYTHONPATH"] = str(R / "overlay") + ":" + str(R / "src/python")
env["SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND"] = "python"
env["HF_HOME"] = "/scratch/cc-pr43/hf-home" if not arm.startswith("h200") else str(R / "hf-home")
env["HF_HUB_CACHE"] = env["HF_HOME"] if not arm.startswith("h200") else env["HF_HOME"] + "/hub"
model = "/scratch/models/GLM-5-1028-Provider"
cmd = ["/opt/sglang/bin/python", str(R / "server.py"), "--model-path", model, "--host", "127.0.0.1", "--port", "31874", "--tp-size", "8"]
if arm == "b300-dep8":
    cmd += "--ep-size 8 --attn-dp-size 8 --moe-runner-backend flashinfer_trtllm --moe-a2a-backend none --dsa-prefill-backend trtllm --dsa-decode-backend trtllm --kv-cache-dtype fp8_e4m3 --context-length 147456 --mem-fraction-static 0.88 --chunked-prefill-size 65536 --enable-fp32-lm-head".split()
else:
    cmd += "--mem-fraction-static 0.75 --context-length 65536 --chunked-prefill-size 32768".split()
cmd += "--max-running-requests 32 --cuda-graph-max-bs-decode 32 --disable-prefill-cuda-graph --speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4".split()
cmd += ["--speculative-draft-model-path", model]
cmd += "--enable-cache-report --reasoning-parser glm45 --tool-call-parser glm47 --enable-metrics".split()
(L / "launch.json").write_text(json.dumps({"command":cmd,"env":{k:env[k] for k in ["PYTHONPATH","HF_HOME","HF_HUB_CACHE","SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND"]}},indent=2))
server = None
client = None
try:
    gpu = subprocess.check_output(["nvidia-smi","--query-gpu=index,name,memory.total,memory.used,utilization.gpu","--format=csv"])
    (L / "gpu-before.csv").write_bytes(gpu)
    used = subprocess.check_output(["nvidia-smi","--query-gpu=memory.used","--format=csv,noheader,nounits"]).decode().split()
    if any(int(v)>2000 for v in used):
        raise RuntimeError("GPU_BUSY_FOREIGN")
    with (L / "serve.log").open("wb") as f:
        server = subprocess.Popen(cmd,env=env,cwd=R / "src",stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    (L / "server.pid").write_text(str(server.pid))
    mark("STARTED")
    ready = False
    start = last = time.monotonic()
    oldsize = -1
    while time.monotonic()-start < 3600:
        if server.poll() is not None:
            raise RuntimeError("SERVER_EXIT " + str(server.returncode))
        try:
            get("/health")
            ready = True
            break
        except Exception:
            pass
        size=(L / "serve.log").stat().st_size
        if size != oldsize:
            oldsize=size
            last=time.monotonic()
        if time.monotonic()-last > 900:
            raise RuntimeError("STARTUP_STALLED_900S")
        time.sleep(10)
    if not ready:
        raise RuntimeError("STARTUP_TIMEOUT_3600S")
    mark("READY")
    suite=(R / "suite.py").read_text().replace("31743","31874")
    (L / "suite.py").write_text(suite)
    def run_client(command,filename,budget):
        global client
        with (L / filename).open("wb") as f:
            client=subprocess.Popen(command,env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
        begin=last=time.monotonic()
        sizes=None
        while client.poll() is None:
            if server.poll() is not None:
                raise RuntimeError("SERVER_DIED_DURING_"+filename)
            current=((L / filename).stat().st_size,(L / "serve.log").stat().st_size)
            if current != sizes:
                sizes=current
                last=time.monotonic()
            if time.monotonic()-begin>budget or time.monotonic()-last>900:
                raise RuntimeError("CLIENT_TIMEOUT_OR_STALL_"+filename)
            time.sleep(10)
        mark(filename+" rc="+str(client.returncode))
    run_client(["/opt/sglang/bin/python",str(L / "suite.py"),str(L / "suite.json"),"smoke"],"suite.log",2400)
    snapshot("before-eval")
    mark("EVAL_START")
    run_client(["/opt/sglang/bin/sgl-eval","run","gsm8k","--base-url","http://127.0.0.1:31874/v1","--temperature","1.0","--top-p","0.95","--out-dir",str(L / "eval")],"gsm8k.log",14400)
    mark("EVAL_END")
    snapshot("after-eval")
    get("/health")
    mark("ALIVE_AT_END")
except Exception as exc:
    mark("FAIL "+repr(exc))
    raise
finally:
    if client is not None and client.poll() is None:
        stop(client)
    stop(server)
    (L / "gpu-after.csv").write_bytes(subprocess.check_output(["nvidia-smi","--query-gpu=index,memory.used,utilization.gpu","--format=csv"]))
    mark("DONE")
