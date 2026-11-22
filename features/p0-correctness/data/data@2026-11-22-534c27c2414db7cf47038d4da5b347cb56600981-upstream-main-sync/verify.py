import collections
import gzip
import json
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASELINE = "746e19554cf257b2db34bdb8afa85077ea2fb14e"
CANDIDATE = "534c27c2414db7cf47038d4da5b347cb56600981"
EXPECTED = {
    "baseline-tp4": {"code": BASELINE, "correct": 1259, "finish_reason": {"stop": 1319}},
    "candidate-tp4": {"code": CANDIDATE, "correct": 1247, "finish_reason": {"stop": 1317, "length": 2}},
    "baseline-dep4": {"code": BASELINE, "correct": 1254, "finish_reason": {"stop": 1317, "length": 2}},
    "candidate-dep4": {"code": CANDIDATE, "correct": 1265, "finish_reason": {"stop": 1319}},
}
FULL = {
    "baseline": {
        "dir": "gate-746e19554c",
        "code": BASELINE,
        "correct": 1238,
        "agentx": {"requests": 1097, "total_tps": 85401.7, "output_tps": 933.4, "ttft_p50": 12093.4, "accept": 2.394},
    },
    "candidate": {
        "dir": "gate-534c27c241",
        "code": CANDIDATE,
        "correct": 1247,
        "agentx": {"requests": 1174, "total_tps": 92770.8, "output_tps": 998.6, "ttft_p50": 14608.1, "accept": 2.444},
    },
}


def samples(run):
    path = next(run.glob("eval/*/output-rs0.jsonl.gz")) if (run / "eval").exists() else next(run.glob("sgl_eval_gsm8k_*/output-rs0.jsonl.gz"))
    rows = [json.loads(line) for line in gzip.open(path, "rt").read().splitlines()]
    metrics = json.loads((path.parent / "metrics.json").read_text())
    assert len(rows) == 1319
    assert len({row["id"] for row in rows}) == 1319
    assert metrics["num_examples"] == 1319
    assert metrics["aggregate"]["error_rate"] == 0.0
    assert metrics["gen"]["temperature"] == 1.0
    assert metrics["gen"]["top_p"] == 0.95
    assert metrics["gen"]["max_tokens"] is None
    return rows


def accept_lengths(log, floor):
    values = []
    for line in log.splitlines():
        match = re.search(r"#running-req: (\d+).*accept len: ([0-9.]+)", line)
        if match and int(match.group(1)) >= floor:
            values.append(float(match.group(2)))
    return {"running_floor": floor, "samples": len(values), "mean": statistics.mean(values) if values else None}


def check_tier2_arm(arm, expected):
    run = ROOT / arm
    rows = samples(run)
    finish = collections.Counter(row["finish_reason"] for row in rows)
    correct = sum(bool(row["symbolic_correct"]) for row in rows)
    assert correct == expected["correct"], (arm, correct)
    assert dict(finish) == expected["finish_reason"], (arm, finish)
    assert (run / "code-revision.txt").read_text().strip() == expected["code"]
    server_info = json.loads((run / "server_info.json").read_text())
    log = gzip.open(run / "server.log.gz", "rt", errors="replace").read()
    versions = (run / "versions.txt").read_text()
    status = (run / "status").read_text()
    assert "Traceback" not in log
    assert server_info["tp_size"] == 4
    assert server_info["kv_cache_dtype"] == "fp8_e4m3"
    assert server_info["speculative_algorithm"] == "EAGLE"
    assert server_info["speculative_draft_model_path"] == server_info["model_path"]
    assert server_info["reasoning_parser"] == "glm45"
    assert server_info["disable_cuda_graph"] is False
    assert server_info["max_running_requests"] == 48
    leg = "tp4" if arm.endswith("tp4") else "dep4"
    if leg == "dep4":
        assert server_info["ep_size"] == 4
        assert server_info["attn_dp_size"] == 4
        assert server_info["moe_a2a_backend"] == "megamoe"
        assert server_info["mem_fraction_static"] == 0.9
    else:
        assert server_info["ep_size"] == 1
        assert server_info["moe_runner_backend"] == "flashinfer_trtllm"
    nccl = re.findall(r"NCCL version ([0-9.]+)\+", log)
    assert nccl == ["2.31.2"], (arm, nccl)
    assert "sgl-deep-ep 0.1.3 " in versions
    assert "eval rc=0" in status
    assert "stopped; gpu apps: 0" in status
    assert status.rstrip().endswith("DONE")
    return {
        "code": expected["code"],
        "correct": correct,
        "accuracy": correct / 1319,
        "finish_reason": dict(finish),
        "stop_rate": finish["stop"] / 1319,
        "non_stop": 1319 - finish["stop"],
        "accept_len": accept_lengths(log, 16 if leg == "tp4" else 8),
    }


def check_full_arm(name, expected):
    run = ROOT / "leg3" / expected["dir"]
    result = json.loads((run / "result.json").read_text())
    assert result["harness_rev"] == "1e31bef84893"
    assert result["src"].endswith(f"/{expected['code'][:10]}/src")
    assert all(result["verdict"].values())
    check1 = result["check1_gsm8k"]
    rows = samples(run / "rank1" / "gsm8k-full")
    raw_correct = sum(bool(row["symbolic_correct"]) for row in rows)
    raw_finish = collections.Counter(row["finish_reason"] for row in rows)
    assert raw_correct == expected["correct"] == check1["correct"]
    assert check1["n"] == 1319
    assert dict(raw_finish) == check1["finish_reason"] == {"stop": 1319}
    cache = result["check2_cache_truth"]
    assert cache["pass"] is True
    assert all(cache["checks"].values())
    assert len(cache["steps"]) == 29
    for step in cache["steps"]:
        assert step["answer"] == cache["code"]
        assert step["answer_has_code"] is True
        assert step["raw_content"] == cache["code"]
        assert step["reasoning_content"] is None
        assert step["finish_reason"] == "stop"
        assert step["completion_tokens"] <= 7
    agentx = result["check3_agentx"]["main"]
    summary = json.loads((run / "rank1" / "agentx" / "main-c64" / "summary.json").read_text())
    wanted = expected["agentx"]
    assert summary["requests"] == wanted["requests"] == agentx["requests"]
    assert summary["profiling_records"] == wanted["requests"]
    assert summary["errors"] == agentx["errors"] == 0
    assert summary["total_tps"] == wanted["total_tps"] == agentx["total_tps"]
    assert summary["output_tps"] == wanted["output_tps"] == agentx["output_tps"]
    assert summary["ttft_ms"]["p50"] == wanted["ttft_p50"] == agentx["ttft_ms"]["p50"]
    assert summary["decode"]["accept_len_mean"] == wanted["accept"] == agentx["decode"]["accept_len_mean"]
    assert summary["decode"]["cuda_graph_lines"] == {"True": summary["decode"]["lines"]}
    for rank in ("rank0", "rank1"):
        totals = result["check4_health"][rank]["totals"]
        for field in ("traceback", "kv_transfer_error", "disagg_timeout", "mooncake_transport", "nixl_error", "oom", "python_core_fallback", "process_crash"):
            assert totals[field] == 0, (name, rank, field, totals[field])
    return {
        "code": expected["code"],
        "harness_rev": result["harness_rev"],
        "started": result["started"],
        "finished": result["finished"],
        "gsm8k": {"correct": raw_correct, "accuracy": raw_correct / 1319, "finish_reason": dict(raw_finish), "accept_len": check1["decode"]["accept_len_mean"]},
        "cache_truth": {"pass": cache["pass"], "checks": cache["checks"], "probe_count": len(cache["steps"]), "max_completion_tokens": max(step["completion_tokens"] for step in cache["steps"])},
        "agentx": {
            "requests": agentx["requests"],
            "errors": agentx["errors"],
            "total_tps": agentx["total_tps"],
            "output_tps": agentx["output_tps"],
            "ttft_p50_ms": agentx["ttft_ms"]["p50"],
            "itl_p50_ms": agentx["itl_ms"]["p50"],
            "accept_len": agentx["decode"]["accept_len_mean"],
        },
    }


results = {arm: check_tier2_arm(arm, expected) for arm, expected in EXPECTED.items()}
for leg in ("tp4", "dep4"):
    baseline = results[f"baseline-{leg}"]
    candidate = results[f"candidate-{leg}"]
    assert candidate["non_stop"] <= 3
    assert candidate["non_stop"] <= baseline["non_stop"] + 2
    assert candidate["accuracy"] >= baseline["accuracy"] - 0.01
    assert candidate["accept_len"]["mean"] >= baseline["accept_len"]["mean"] - 0.2

full = {name: check_full_arm(name, expected) for name, expected in FULL.items()}
baseline = full["baseline"]
candidate = full["candidate"]
assert candidate["agentx"]["total_tps"] >= 0.9 * baseline["agentx"]["total_tps"]
assert candidate["agentx"]["output_tps"] >= 0.9 * baseline["agentx"]["output_tps"]
assert candidate["agentx"]["ttft_p50_ms"] <= 1.3 * baseline["agentx"]["ttft_p50_ms"]
assert candidate["agentx"]["accept_len"] >= baseline["agentx"]["accept_len"] - 0.2

snapshot = {}
for arm in EXPECTED:
    status = (ROOT / arm / "status").read_text().splitlines()
    snapshot[arm] = {
        "code": EXPECTED[arm]["code"],
        "rank": 0 if arm.startswith("baseline") else 1,
        "launch": next(line.split()[0] for line in status if " launch:" in line),
        "ready": next(line.split()[0] for line in status if line.endswith(" ready")),
        "eval_rc": 0,
        "eval_finished": next(line.split()[0] for line in status if "eval rc=0" in line),
        "server_alive_after_eval": any("server alive after eval" in line for line in status),
        "stopped": next(line.split()[0] for line in status if "stopped; gpu apps: 0" in line),
        "gpu_apps": 0,
        "terminal": "DONE",
    }
for name, result in full.items():
    snapshot[f"full-recipe-{name}"] = {"code": result["code"], "started": result["started"], "finished": result["finished"], "terminal": "DONE"}
snapshot["gate_devbox_lock"] = {"held": "2026-11-22T12:54:37Z", "released": "2026-11-22T15:38Z"}
(ROOT / "terminal-snapshot.json").write_text(json.dumps(snapshot, indent=2) + "\n")

output = {
    "gate": "PASS",
    "tp4": "PASS",
    "dep4_megamoe": "PASS",
    "full_recipe": "PASS",
    "tier2_arms": results,
    "full_recipe_arms": full,
}
(ROOT / "verify.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
print(json.dumps({"gate": "PASS", "tier2_arms": len(results), "full_recipe_arms": len(full)}, sort_keys=True))
