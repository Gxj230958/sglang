import collections
import gzip
import json
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASELINE = "45bff30acfb5ec97673046ea7b8d36b822bbc520"
CANDIDATE = "710a842c5741dade3ecd7d8583ef622745dcd9f2"
EXPECTED = {
    "baseline-tp4": {
        "code": BASELINE,
        "correct": 1251,
        "finish_reason": {
            "stop": 1319
        },
        "nccl": "2.30.7",
        "deep_ep": "0.1.2.post1"
    },
    "candidate-tp4": {
        "code": CANDIDATE,
        "correct": 1254,
        "finish_reason": {
            "stop": 1319
        },
        "nccl": "2.31.2",
        "deep_ep": "0.1.3"
    },
    "baseline-dep4-r1": {
        "code": BASELINE,
        "correct": 1256,
        "finish_reason": {
            "stop": 1319
        },
        "nccl": "2.30.7",
        "deep_ep": "0.1.2.post1"
    },
    "baseline-dep4-r2": {
        "code": BASELINE,
        "correct": 1249,
        "finish_reason": {
            "stop": 1316,
            "length": 3
        },
        "nccl": "2.30.7",
        "deep_ep": "0.1.2.post1"
    },
    "candidate-dep4-r1": {
        "code": CANDIDATE,
        "correct": 1272,
        "finish_reason": {
            "stop": 1319
        },
        "nccl": "2.31.2",
        "deep_ep": "0.1.3"
    },
    "candidate-dep4-r2": {
        "code": CANDIDATE,
        "correct": 1257,
        "finish_reason": {
            "stop": 1318,
            "length": 1
        },
        "nccl": "2.31.2",
        "deep_ep": "0.1.3"
    }
}
RUNNING_FLOOR = {"tp4": 16, "dep4": 8}


def load_arm(arm):
    run = ROOT / arm
    sample_path = next((run / "eval").glob("*/output-rs0.jsonl.gz"))
    rows = [json.loads(line) for line in gzip.open(sample_path, "rt").read().splitlines()]
    metrics = json.loads((sample_path.parent / "metrics.json").read_text())
    server_info = json.loads((run / "server_info.json").read_text())
    log = gzip.open(run / "server.log.gz", "rt", errors="replace").read()
    versions = (run / "versions.txt").read_text()
    status = (run / "status").read_text()
    return rows, metrics, server_info, log, versions, status


results = {}
for arm, expected in EXPECTED.items():
    leg = "tp4" if arm.endswith("tp4") else "dep4"
    rows, metrics, server_info, log, versions, status = load_arm(arm)
    finish = collections.Counter(row["finish_reason"] for row in rows)
    correct = sum(bool(row["symbolic_correct"]) for row in rows)
    accept = []
    for line in log.splitlines():
        match = re.search(r"#running-req: (\d+).*accept len: ([0-9.]+)", line)
        if match and int(match.group(1)) >= RUNNING_FLOOR[leg]:
            accept.append(float(match.group(2)))
    assert len(rows) == 1319
    assert len({row["id"] for row in rows}) == 1319
    assert correct == expected["correct"], (arm, correct)
    assert dict(finish) == expected["finish_reason"], (arm, finish)
    assert metrics["aggregate"]["error_rate"] == 0.0
    assert metrics["num_examples"] == 1319
    assert metrics["gen"]["temperature"] == 1.0
    assert metrics["gen"]["top_p"] == 0.95
    assert metrics["gen"]["max_tokens"] is None
    assert "Traceback" not in log
    assert server_info["tp_size"] == 4
    assert server_info["kv_cache_dtype"] == "fp8_e4m3"
    assert server_info["speculative_algorithm"] == "EAGLE"
    assert server_info["reasoning_parser"] == "glm45"
    assert server_info["disable_cuda_graph"] is False
    if leg == "dep4":
        assert server_info["ep_size"] == 4
        assert server_info["attn_dp_size"] == 4
        assert server_info["moe_a2a_backend"] == "megamoe"
        assert server_info["mem_fraction_static"] == 0.9
    else:
        assert server_info["ep_size"] == 1
        assert server_info["moe_runner_backend"] == "flashinfer_trtllm"
    nccl = re.findall(r"NCCL version ([0-9.]+)\+", log)
    assert nccl == [expected["nccl"]], (arm, nccl)
    assert f"sgl-deep-ep {expected['deep_ep']} " in versions
    assert "eval rc=0" in status
    assert "stopped; gpu apps: 0" in status
    assert status.rstrip().endswith("DONE")
    results[arm] = {
        "code": expected["code"],
        "correct": correct,
        "accuracy": correct / 1319,
        "finish_reason": dict(finish),
        "stop_rate": finish["stop"] / 1319,
        "nccl": nccl[0],
        "accept_len": {
            "running_floor": RUNNING_FLOOR[leg],
            "samples": len(accept),
            "mean": statistics.mean(accept) if accept else None,
        },
    }

tp4_pass = (
    results["candidate-tp4"]["stop_rate"] >= results["baseline-tp4"]["stop_rate"]
    and results["candidate-tp4"]["accuracy"] >= results["baseline-tp4"]["accuracy"]
)
base_mean = statistics.mean(results[a]["accuracy"] for a in ("baseline-dep4-r1", "baseline-dep4-r2"))
cand_mean = statistics.mean(results[a]["accuracy"] for a in ("candidate-dep4-r1", "candidate-dep4-r2"))
dep4_pass = all(
    results[f"candidate-dep4-{r}"]["stop_rate"] >= results[f"baseline-dep4-{r}"]["stop_rate"]
    for r in ("r1", "r2")
) and cand_mean >= base_mean - 0.01
assert tp4_pass and dep4_pass
print(
    json.dumps(
        {
            "gate": "PASS",
            "tp4": "PASS",
            "dep4_megamoe": {"gate": "PASS", "baseline_mean": base_mean, "candidate_mean": cand_mean},
            "arms": results,
        },
        indent=2,
        sort_keys=True,
    )
)
