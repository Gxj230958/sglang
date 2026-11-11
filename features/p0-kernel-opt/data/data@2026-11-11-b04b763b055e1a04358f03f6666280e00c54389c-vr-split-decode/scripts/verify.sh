cd /tmp
python3 -u /nfs_home/glm5-lcd/split_rig.py 4,8,16,32,64 "16,4,296,64" 2>&1 | grep -E "rows=|RIG_DONE|Error"
python3 -c "
import sglang.kernels.ops.attention.glm_loop_sparse_decode as sd
print('CFG', sd._decode_config(32, 8), sd._decode_config(32, 64), sd.max_workspace_entries(rows=32, num_heads=8))"
python3 -m pytest -x -q /nfs_home/glm5-lcd/test_glm_loop_attention.py 2>&1 | tail -15
