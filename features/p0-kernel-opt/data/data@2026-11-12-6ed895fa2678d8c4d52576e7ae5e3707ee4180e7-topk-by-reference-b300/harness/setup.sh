set -u
cd /scratch/cc-pr43
for t in base full clean; do rm -rf src-$t; mkdir src-$t; tar xzf xfer/src-$t.tgz -C src-$t; done
rm -rf src-verify; cp -r src-base src-verify; cp xfer/glm_loop.verify.py src-verify/python/sglang/srt/models/glm_loop.py
for t in base full clean verify; do echo "$t $(cd src-$t/python && find sglang -name '*.py' | sort | xargs cat | sha256sum | cut -c1-16)"; done
diff -rq src-base/python src-clean/python; diff -rq src-base/python src-full/python; diff -rq src-base/python src-verify/python
if [ ! -d overlay/flashinfer ]; then
  mkdir -p overlay
  /opt/sglang/bin/pip install --no-deps --target overlay flashinfer-python==0.7.3 flashinfer-cubin==0.7.3 sgl-deep-gemm==0.2.7 sgl-flash-mla==1.0.4 2>&1 | tail -2
  /opt/sglang/bin/pip install --no-deps --target overlay flashinfer-jit-cache==0.7.3 --index-url https://flashinfer.ai/whl/cu130 2>&1 | tail -2
fi
cp box/sitecustomize.py overlay/sitecustomize.py
ls overlay | tr '\n' ' '; echo
cd /tmp && PYTHONPATH=/scratch/cc-pr43/src-base/python:/scratch/cc-pr43/overlay /opt/sglang/bin/python - <<'PY'
import importlib.metadata as m, flashinfer, deep_gemm, flash_mla, sglang
print("flashinfer", flashinfer.__version__, flashinfer.__file__)
for p in ["flashinfer-python","flashinfer-cubin","flashinfer-jit-cache","sgl-deep-gemm","sgl-flash-mla"]:
    print(p, m.version(p))
print("deep_gemm", deep_gemm.__file__); print("flash_mla", flash_mla.__file__); print("sglang", sglang.__file__)
PY
ls ~/.cache/huggingface/hub 2>/dev/null | grep -i -E "gsm|dataset" | head; ls /scratch/qfv-glm5lp-bs1-128k-2026-11-12/hf-home/hub 2>/dev/null | head
