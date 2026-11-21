import collections
import json
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED = {
    "baseline": {
        "code": "13fa8258d2404deedfac9c114c43c4e4069f39b5",
        "correct": 1249,
        "stop": 1318,
        "length": 1,
        "accuracy": 0.9469294920394238,
        "accept_mean": 2.658,
        "accept_median": 2.680,
    },
    "candidate": {
        "code": "7053ff0277bd27e1f3c76646b4a65bf76b0c7820",
        "correct": 1252,
        "stop": 1319,
        "length": 0,
        "accuracy": 0.9492039423805914,
        "accept_mean": 2.653,
        "accept_median": 2.655,
    },
}

results = {}
for arm, expected in EXPECTED.items():
    sample_path = next((ROOT / arm / "eval").glob("*/output-rs0.jsonl"))
    rows = [json.loads(line) for line in sample_path.read_text().splitlines()]
    metrics = json.loads((sample_path.parent / "metrics.json").read_text())
    analysis = json.loads((ROOT / arm / "analysis.json").read_text())
    server_info = json.loads((ROOT / arm / "server_info.json").read_text())
    log = (ROOT / f"{arm}-logs" / "server.log").read_text(errors="replace")
    finish = collections.Counter(row["finish_reason"] for row in rows)
    correct = sum(bool(row["symbolic_correct"]) for row in rows)
    accept = []
    for line in log.splitlines():
        match = re.search(r"#running-req: (\d+).*accept len: ([0-9.]+)", line)
        if match and int(match.group(1)) >= 16:
            accept.append(float(match.group(2)))
    assert len(rows) == 1319
    assert len({row["id"] for row in rows}) == 1319
    assert correct == expected["correct"]
    assert finish == collections.Counter({"stop": expected["stop"], "length": expected["length"]})
    assert metrics["aggregate"]["score"] == expected["accuracy"]
    assert metrics["aggregate"]["error_rate"] == 0.0
    assert metrics["num_examples"] == 1319
    assert metrics["num_threads"] == 64
    assert metrics["gen"]["temperature"] == 1.0
    assert metrics["gen"]["top_p"] == 0.95
    assert metrics["gen"]["max_tokens"] is None
    assert analysis["n"] == 1319
    assert analysis["acc_from_samples"] == correct / 1319
    assert analysis["tracebacks"] == 0
    assert server_info["status"] == "ready"
    assert server_info["launch_command"].startswith("--model-path /scratch/models/GLM-5-1028-Provider")
    assert server_info["tp_size"] == 4
    assert server_info["kv_cache_dtype"] == "fp8_e4m3"
    assert server_info["speculative_algorithm"] == "EAGLE"
    assert server_info["reasoning_parser"] == "glm45"
    assert server_info["disable_cuda_graph"] is False
    assert accept
    assert round(statistics.mean(accept), 3) == expected["accept_mean"]
    assert round(statistics.median(accept), 3) == expected["accept_median"]
    status = (ROOT / arm / "status").read_text()
    assert "eval rc=0" in status
    assert "stopped; gpu apps: 0" in status
    assert status.rstrip().endswith("DONE")
    results[arm] = {
        "code": expected["code"],
        "samples": len(rows),
        "correct": correct,
        "accuracy": correct / 1319,
        "finish_reason": dict(finish),
        "errors": 0,
        "accept_len_running_gte_16": {
            "samples": len(accept),
            "mean": statistics.mean(accept),
            "median": statistics.median(accept),
        },
        "terminal": "eval rc=0; server alive after eval; gpu apps 0; DONE",
    }

assert results["candidate"]["accuracy"] >= results["baseline"]["accuracy"]
assert results["candidate"]["finish_reason"]["stop"] >= results["baseline"]["finish_reason"]["stop"]
print(json.dumps({"gate": "PASS", "arms": results}, indent=2, sort_keys=True))
