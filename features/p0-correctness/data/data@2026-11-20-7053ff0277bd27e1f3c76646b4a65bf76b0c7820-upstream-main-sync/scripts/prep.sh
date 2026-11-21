#!/bin/bash
set -uo pipefail
D=/scratch/glm5lp-upstream-sync; REV=$1; PY=/opt/sglang/bin/python
exec > >(tee -a $D/prep.log) 2>&1
echo "$(date -u +%FT%TZ) prep start rev=$REV"
mkdir -p $D/dg-build $D/overlay-dg
cd $D/dg-build
if [ ! -d DeepGEMM ]; then git clone -q --recursive --depth 1 --branch v0.2.9 https://github.com/sgl-project/DeepGEMM.git DeepGEMM || { echo CLONE_FAIL; exit 1; }; fi
cd DeepGEMM; git checkout -q -- . ; git clean -qfdx -e third-party
echo "deepgemm HEAD $(git rev-parse HEAD)"
for p in $D/$REV/src/docker/patches/deep_gemm/*.patch; do git apply "$p" && echo "applied $(basename $p) sha256=$(sha256sum $p | cut -c1-16)" || { echo PATCH_FAIL; exit 1; }; done
printf '%s' 0.2.9 > sgl_deep_gemm/VERSION
PATH=/opt/sglang/bin:$PATH bash build_sgl_deep_gemm.sh > $D/dg-build/build.log 2>&1 || { echo BUILD_FAIL; tail -30 $D/dg-build/build.log; exit 1; }
ls dist
rm -rf $D/overlay-dg/*; $PY -m pip install -q --no-deps --target $D/overlay-dg dist/sgl_deep_gemm-*.whl || { echo INSTALL_FAIL; exit 1; }
ls $D/overlay-dg
if [ ! -x $D/eval-venv/bin/sgl-eval ]; then python3 -m venv $D/eval-venv && $D/eval-venv/bin/pip install -q sgl-eval==0.1.3 || { echo EVAL_VENV_FAIL; exit 1; }; fi
$D/eval-venv/bin/pip show sgl-eval | grep -E '^(Name|Version)'
echo "$(date -u +%FT%TZ) PREP_OK"
