set -uo pipefail
D=/scratch/glm5lp-upstream-sync; O=$D/overlay-deps-ff776255fc; PY=/opt/sglang/bin/python
mkdir -p $D/wheels && cd $D/wheels
$PY -m pip download -q --only-binary=:all: --no-deps -d $D/wheels "sgl-deep-ep==0.1.3" "nvidia-nccl-cu13==2.31.2" 2>&1 | tail -3
ls -la $D/wheels
for w in $D/wheels/sgl_deep_ep-0.1.3-*.whl; do unzip -p $w '*.dist-info/METADATA' | grep -E '^(Name|Version|Requires-Dist)'; done
rm -rf $O; $PY -m pip install -q --no-deps --target $O $D/wheels/sgl_deep_ep-0.1.3-*.whl $D/wheels/nvidia_nccl_cu13-2.31.2-*.whl 2>&1 | tail -3
ls $O $O/nvidia/nccl/lib
sha256sum $D/wheels/*.whl
echo OVL_OK
