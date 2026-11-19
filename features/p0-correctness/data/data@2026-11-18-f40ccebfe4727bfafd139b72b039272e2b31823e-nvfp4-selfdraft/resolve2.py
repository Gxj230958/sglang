import json, sys, copy, types
import torch
from sglang.srt.layers.quantization.modelopt_quant import ModelOptMixedPrecisionConfig
from sglang.srt.layers.quantization.fp8 import Fp8Config
from sglang.srt.layers.linear import LinearBase, ReplicatedLinear
from sglang.srt.layers.moe.fused_moe_triton import FusedMoE
from sglang.srt.models.glm_loop_nextn import GlmLoopForConditionalGenerationNextN as Draft
from sglang.srt.models.glm5_next_nextn import Glm5NextForConditionalGenerationNextN as SiblingDraft
from sglang.srt.models.glm_loop import GlmLoopForConditionalGeneration as Target
from sglang.srt.models.deepseek_v2 import DeepseekV2ForCausalLM

data = sys.argv[1]
raw = json.load(open(f"{data}/hf_quant_config.json"))
cfg = json.load(open(f"{data}/config.json"))
hf = types.SimpleNamespace(text_config=types.SimpleNamespace(**cfg["text_config"]), model_type=cfg["model_type"], architectures=cfg["architectures"])

print("Draft.packed_modules_mapping        =", Draft.packed_modules_mapping, "| is DeepseekV2ForCausalLM's dict:", Draft.packed_modules_mapping is DeepseekV2ForCausalLM.packed_modules_mapping)
print("SiblingDraft.packed_modules_mapping =", SiblingDraft.packed_modules_mapping)
print("Target.packed_modules_mapping keys  =", sorted(Target.packed_modules_mapping))

def mixed(packed):
    c = copy.deepcopy(raw); c["packed_modules_mapping"] = packed
    q = ModelOptMixedPrecisionConfig.from_config(c)
    q.apply_weight_name_mapper(Draft.get_hf_to_sglang_mapper(hf)); return q
def fp8(packed):
    q = Fp8Config.from_config({"quant_method": "fp8", "fmt": "e4m3", "activation_scheme": "dynamic", "weight_block_size": [128, 128],
        "packed_modules_mapping": packed, "modules_to_not_convert": list(raw["quantization"]["exclude_modules"])})
    q.apply_weight_name_mapper(Draft.get_hf_to_sglang_mapper(hf)); return q

D = "model.decoder"
prefixes = [(FusedMoE, f"{D}.mlp.experts"), (LinearBase, f"{D}.mlp.shared_experts.gate_up_proj"), (LinearBase, f"{D}.mlp.shared_experts.down_proj"),
    (LinearBase, f"{D}.self_attn.fused_qkv_a_proj_with_mqa"), (LinearBase, f"{D}.self_attn.q_b_proj"), (LinearBase, f"{D}.self_attn.kv_b_proj"),
    (LinearBase, f"{D}.self_attn.o_proj"), (LinearBase, f"{D}.self_attn.indexer.wq_b")]
real = Draft.packed_modules_mapping
qm, qf, qfix = mixed(dict(real)), fp8(dict(real)), mixed(dict(Target.packed_modules_mapping))
print(f"\n{'prefix':52s} {'mixed (as served)':42s} {'fp8 (as served)':18s} mixed + target mapping")
for cls, p in prefixes:
    s = lambda q: type(q.get_quant_method(object.__new__(cls), p)).__name__
    print(f"{p:52s} algo={qm.resolve_quant_algo(p)!s:10s} {s(qm):26s} {s(qf):18s} algo={qfix.resolve_quant_algo(p)!s:10s} {s(qfix)}")

print("\n--- parameters the draft registers for the fused q_a/kv_a projection (small stand-in shape)")
p = f"{D}.self_attn.fused_qkv_a_proj_with_mqa"
for label, q in (("mixed", qm), ("fp8", qf), ("mixed+fix", qfix)):
    lin = ReplicatedLinear(256, 384, bias=False, quant_config=q, prefix=p, params_dtype=torch.bfloat16)
    print(f"{label:10s}", {n: (str(t.dtype), tuple(t.shape)) for n, t in lin.named_parameters()})

print("\n--- what the unquantized bf16 parameter holds after the loader copies FP8 bytes into it")
w = torch.randn(256, 256) * 0.02
scale = w.abs().amax() / 448.0
w_q = (w / scale).to(torch.float8_e4m3fn)
lin = ReplicatedLinear(256, 256, bias=False, quant_config=qm, prefix=p, params_dtype=torch.bfloat16)
lin.weight.weight_loader(lin.weight, w_q) if hasattr(lin.weight, "weight_loader") else lin.weight.data.copy_(w_q)
print("true |W| mean %.5f ; loaded |W| mean %.3f ; ratio %.0fx (= 1/weight_scale_inv, scale tensor was dropped)" % (w.abs().mean(), lin.weight.float().abs().mean(), lin.weight.float().abs().mean() / w.abs().mean()))
