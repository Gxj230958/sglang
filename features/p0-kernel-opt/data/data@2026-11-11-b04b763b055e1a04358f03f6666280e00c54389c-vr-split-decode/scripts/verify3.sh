export PYTHONPATH=/nfs_home/glm5-lcd/src-pr/python
cd /tmp
python3 - <<PY
import sglang, sglang.kernels.ops.attention.glm_loop_sparse_decode as sd
assert sglang.__file__.startswith('/nfs_home/glm5-lcd/src-pr'), sglang.__file__
print('CFG', [(h, r, sd._decode_config(r, h)) for h in (8, 16, 32, 64) for r in (2, 4, 32)])
PY
sed -i 's#startswith("/nfs_home/glm5-lcd/src")#startswith("/nfs_home/glm5-lcd/src")#' /dev/null
for h in 8 16 32 64; do HEADS=$h DUAL=1 python3 -u /nfs_home/glm5-lcd/split_rig.py 2,3,4,8,12,16,32,64 "16,4,296,64" 2>&1 | grep -E "rows=.*cfg=\(0|FAIL|Error"; done
python3 -m pytest -q /nfs_home/glm5-lcd/test_glm_loop_attention_base.py 2>&1 | grep -E "passed|failed|FAILED|Error" | tail -8
echo VERIFY_DONE
