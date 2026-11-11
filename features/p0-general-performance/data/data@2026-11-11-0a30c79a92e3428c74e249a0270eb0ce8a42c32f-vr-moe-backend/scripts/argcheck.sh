cd /tmp && python3 - <<PY 2>&1 | grep -E "RESOLVED|MoE runner|Error|error" | cut -c1-240
from sglang.srt.server_args import prepare_server_args
from sglang.srt.arg_groups.model_override_base import resolved_view
M = "/nfs_home/models/GLM-5-1028-Provider"
for extra in ([], ["--ep-size", "8", "--attn-dp-size", "8", "--moe-a2a-backend", "deepep"]):
    a = prepare_server_args(["--model-path", M, "--tp-size", "8"] + extra)
    a.resolve_once()
    v = resolved_view(a)
    print("RESOLVED", extra, v.moe_runner_backend, v.moe_a2a_backend, v.disable_shared_experts_fusion, v.dsa_decode_backend, v.kv_cache_dtype, v.quantization)
PY
