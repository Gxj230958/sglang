#!/usr/bin/env python3
import argparse
import hashlib
import itertools
import json
import math
import os
import re
import signal
import statistics
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

MODES = {"open_loop", "closed_loop", "fixed_concurrency"}


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(value, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def fingerprint(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def metric(value, name):
    require(name in value, f"missing required metric {name!r}")
    number = value[name]
    require(isinstance(number, (int, float)) and math.isfinite(number), f"metric {name!r} must be finite, got {number!r}")
    return float(number)


def expand_candidates(config):
    candidates = []
    for index, candidate in enumerate(config.get("candidates", []), 1):
        item = dict(candidate)
        item.setdefault("name", f"candidate-{index:03d}")
        candidates.append(item)
    matrix = config.get("matrix", {})
    if matrix:
        keys = list(matrix)
        require(all(isinstance(matrix[key], list) and matrix[key] for key in keys), "matrix values must be non-empty lists")
        for index, values in enumerate(itertools.product(*(matrix[key] for key in keys)), 1):
            bound = dict(zip(keys, values))
            name = "-".join(f"{key}={value}" for key, value in bound.items())
            candidates.append({"name": name or f"matrix-{index:03d}", "values": bound})
    require(candidates, "configuration must define candidates or matrix")
    names = [candidate["name"] for candidate in candidates]
    require(len(names) == len(set(names)), f"candidate names must be unique, got {names!r}")
    require(all(re.fullmatch(r"[A-Za-z0-9_.=-]+", name) for name in names), "candidate names may contain only letters, digits, _, ., =, -")
    return candidates


def validate_config(config):
    require(isinstance(config, dict), "configuration root must be an object")
    server = config.get("server", {})
    load = config.get("load", {})
    require(isinstance(server.get("command"), list) and server["command"], "server.command must be a non-empty array")
    require(isinstance(server.get("replicas"), list) and server["replicas"], "server.replicas must be a non-empty array")
    require(isinstance(load.get("command"), list) and load["command"], "load.command must be a non-empty array")
    require(load.get("mode") in MODES, f"load.mode must be one of {sorted(MODES)!r}")
    levels = load.get("levels")
    require(isinstance(levels, list) and levels and all(isinstance(x, (int, float)) and x > 0 for x in levels), "load.levels must contain positive numbers")
    require(len(set(levels)) == len(levels), "load.levels must not contain duplicates")
    require(isinstance(load.get("repeat", 1), int) and load.get("repeat", 1) > 0, "load.repeat must be a positive integer")
    gates = load.get("gates", {})
    require(isinstance(gates, dict), "load.gates must be an object")
    for name, gate in gates.items():
        require(isinstance(gate, dict) and ("min" in gate or "max" in gate), f"gate {name!r} needs min or max")
    if load["mode"] == "open_loop":
        require(gates, "open_loop requires at least one SLO gate")
    expand_candidates(config)


def render(value, values):
    if isinstance(value, str):
        try:
            return value.format_map(values)
        except KeyError as exc:
            raise ValueError(f"unknown placeholder {exc.args[0]!r} in {value!r}") from exc
    if isinstance(value, list):
        return [render(item, values) for item in value]
    if isinstance(value, dict):
        return {key: render(item_value, values) for key, item_value in value.items()}
    return value


def command_for(section, candidate, values, kind):
    command = list(section.get("command", [])) + list(section.get("args", []))
    command += list(candidate.get(f"{kind}_args", []))
    rendered = []
    for part in command:
        value = render(part, values)
        if isinstance(value, list):
            rendered.extend(str(item) for item in value)
        else:
            rendered.append(str(value))
    return rendered


def environment(config, candidate, section, values):
    merged = dict(config.get("env", {}))
    merged.update(candidate.get("env", {}))
    merged.update(section.get("env", {}))
    result = os.environ.copy()
    for key, value in merged.items():
        result[key] = str(render(value, values))
    return result


def process_record(process, command, env, config, log_path):
    allowed = set(config.get("record_env_keys", []))
    return {
        "pid": process.pid,
        "pgid": process.pid,
        "command": command,
        "env": {key: env[key] for key in sorted(allowed) if key in env},
        "log": str(log_path),
    }


def start_process(name, command, env, config, directory, cwd=None):
    log_path = Path(directory) / f"{name}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as log:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    write_json(Path(directory) / f"{name}.process.json", process_record(process, command, env, config, log_path))
    return process, log_path


def stop_process(process, timeout_s=30):
    if process is None or process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=timeout_s)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        return
    process.wait(timeout=10)


def run_command(name, command, env, config, directory, timeout_s, cwd=None):
    process, log_path = start_process(name, command, env, config, directory, cwd)
    try:
        return_code = process.wait(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        stop_process(process, 5)
        raise RuntimeError(f"{name} timed out after {timeout_s}s; log={log_path}")
    if return_code != 0:
        raise RuntimeError(f"{name} exited with code {return_code}; log={log_path}")
    return log_path


def http_ready(url, expected):
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            if response.status != 200:
                return False
            if not expected:
                return True
            payload = json.loads(response.read().decode("utf-8"))
            return all(get_path(payload, key) == value for key, value in expected.items())
    except Exception:
        return False


def get_path(value, path):
    for part in path.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def wait_ready(process, log_path, url, health, timeout_s):
    deadline = time.monotonic() + timeout_s
    required = health.get("required_log_regex", [])
    forbidden = health.get("forbidden_log_regex", [])
    expected = health.get("json_equals", {})
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"process {process.pid} exited with code {process.returncode}; log={log_path}")
        text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
        if any(re.search(pattern, text, re.MULTILINE) for pattern in forbidden):
            raise RuntimeError(f"forbidden startup log pattern found; log={log_path}")
        logs_ok = all(re.search(pattern, text, re.MULTILINE) for pattern in required)
        if logs_ok and http_ready(url, expected):
            return
        time.sleep(2)
    raise RuntimeError(f"readiness timed out after {timeout_s}s; url={url}; log={log_path}")


def check_ports(config, candidate):
    addresses = []
    for replica in candidate.get("replicas", config["server"]["replicas"]):
        values = replica.get("values", {})
        if "port" in values:
            addresses.append((values.get("host", "127.0.0.1"), int(values["port"])))
    router_values = config.get("router", {}).get("values", {})
    if "port" in router_values:
        addresses.append((router_values.get("host", "127.0.0.1"), int(router_values["port"])))
    import socket

    for host, port in addresses:
        try:
            with socket.create_connection((host, port), timeout=1):
                raise RuntimeError(f"preflight port is already serving: {host}:{port}")
        except (ConnectionRefusedError, TimeoutError, OSError):
            continue


def check_gpus(config):
    preflight = config.get("preflight", {})
    if not preflight.get("check_gpus", False):
        return
    gpus = preflight.get("gpus")
    require(isinstance(gpus, list) and gpus, "preflight.gpus is required when check_gpus is true")
    limit = preflight.get("max_memory_mib", 1000)
    command = ["nvidia-smi", "--query-gpu=index,memory.used", "--format=csv,noheader,nounits"]
    output = subprocess.check_output(command, text=True)
    usage = {int(line.split(",")[0]): int(line.split(",")[1]) for line in output.splitlines() if line.strip()}
    busy = [gpu for gpu in gpus if usage.get(int(gpu), limit + 1) > limit]
    if busy:
        raise RuntimeError(f"preflight GPUs are busy: {busy!r}")


def summary_row(path, level):
    payload = read_json(path)
    if isinstance(payload, dict):
        return payload
    require(isinstance(payload, list) and payload, f"summary must be an object or non-empty array: {path}")
    matches = [row for row in payload if float(row.get("level", -1)) == float(level)]
    require(matches, f"summary has no row for level {level}: {path}")
    return matches[-1]


def derived_metrics(row, level, load, repeat_count=1):
    result = dict(row)
    sent = result.get("sent")
    for numerator, denominator, output in [
        ("errors", "sent", "error_rate"),
        ("empty_responses", "sent", "empty_rate"),
        ("stopped", "sent", "stop_rate"),
    ]:
        if output not in result and numerator in result and sent:
            result[output] = result[numerator] / sent
    if "ok_ratio" not in result and "ok" in result and sent:
        result["ok_ratio"] = result["ok"] / sent
    if load["mode"] == "open_loop" and "measure_s" in load and sent is not None:
        count = repeat_count if "sent" in load.get("sum_metrics", []) else 1
        expected = float(level) * load["measure_s"] * count
        if expected:
            deviation = (sent - expected) / expected * 100
            result["arrival_deviation_pct"] = deviation
            result["abs_arrival_deviation_pct"] = abs(deviation)
    return result


def aggregate_rows(rows, level, load):
    numeric = {}
    for key in set().union(*(row.keys() for row in rows)):
        values = [row[key] for row in rows if isinstance(row.get(key), (int, float)) and math.isfinite(row[key])]
        if values:
            numeric[key] = statistics.median(values)
    for key in load.get("sum_metrics", []):
        values = [row.get(key) for row in rows]
        if all(isinstance(value, (int, float)) for value in values):
            numeric[key] = sum(values)
    return derived_metrics(numeric, level, load, len(rows))


def gate_failures(metrics, gates):
    failures = []
    for name, gate in gates.items():
        if name not in metrics:
            failures.append(f"missing:{name}")
            continue
        value = metrics[name]
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            failures.append(f"nonfinite:{name}={value!r}")
            continue
        if "min" in gate and value < gate["min"]:
            failures.append(f"{name}={value}<{gate['min']}")
        if "max" in gate and value > gate["max"]:
            failures.append(f"{name}={value}>{gate['max']}")
    return failures


def point_paths(run_dir, candidate, level, repeat):
    label = f"{float(level):g}"
    return Path(run_dir) / "candidates" / candidate["name"] / f"level-{label}" / f"repeat-{repeat}"


def run_point(config, candidate, level, repeat, run_dir):
    point_dir = point_paths(run_dir, candidate, level, repeat)
    result_path = point_dir / "result.json"
    load = config["load"]
    values = dict(config.get("values", {}))
    values.update(candidate.get("values", {}))
    values.update(load.get("values", {}))
    values.update(
        {
            "name": candidate["name"],
            "level": level,
            "repeat": repeat,
            "measure_s": load.get("measure_s"),
            "settle_s": load.get("settle_s"),
            "run_dir": str(Path(run_dir).resolve()),
            "candidate_dir": str((Path(run_dir) / "candidates" / candidate["name"]).resolve()),
            "point_dir": str(point_dir.resolve()),
            "summary_path": str((point_dir / "summary.json").resolve()),
        }
    )
    command = command_for(load, candidate, values, "load")
    key = {"config": config, "candidate": candidate, "level": level, "repeat": repeat, "command": command}
    point_fingerprint = fingerprint(key)
    if result_path.exists():
        previous = read_json(result_path)
        if previous.get("fingerprint") == point_fingerprint:
            if previous.get("status") == "done":
                return previous
            raise RuntimeError(f"recorded load failure for {candidate['name']} level={level} repeat={repeat}: {previous.get('error')}")
    point_dir.mkdir(parents=True, exist_ok=True)
    env = environment(config, candidate, load, values)
    record = {"candidate": candidate["name"], "level": level, "repeat": repeat, "fingerprint": point_fingerprint, "command": command}
    try:
        run_command("load", command, env, config, point_dir, load.get("timeout_s", 7200), load.get("cwd"))
        row = summary_row(values["summary_path"], level)
        record["raw_metrics"] = row
        record["status"] = "done"
    except Exception as exc:
        record["status"] = "invalid"
        record["error"] = str(exc)
    write_json(result_path, record)
    if record["status"] != "done":
        raise RuntimeError(f"load failed for {candidate['name']} level={level} repeat={repeat}: {record.get('error')}")
    return record


def completed_point(config, candidate, level, run_dir):
    load = config["load"]
    records = [run_point(config, candidate, level, repeat, run_dir) for repeat in range(1, load.get("repeat", 1) + 1)]
    metrics = aggregate_rows([record["raw_metrics"] for record in records], level, load)
    failures = gate_failures(metrics, load.get("gates", {}))
    result = {
        "candidate": candidate["name"],
        "level": level,
        "pass": not failures,
        "failures": failures,
        "metrics": metrics,
        "repeats": [str(point_paths(run_dir, candidate, level, record["repeat"]) / "result.json") for record in records],
    }
    write_json(Path(run_dir) / "candidates" / candidate["name"] / f"level-{float(level):g}" / "result.json", result)
    return result


def interpolate_knee(points, gates):
    ordered = sorted(points, key=lambda point: point["level"])
    passing = [point for point in ordered if point["pass"]]
    if not passing:
        return {"knee": 0, "binding_gate": "all_levels_failed"}
    last = passing[-1]
    following = [point for point in ordered if point["level"] > last["level"]]
    if not following:
        return {"knee": last["level"], "binding_gate": "not_reached"}
    nxt = following[0]
    crossings = []
    for name, gate in gates.items():
        before = last["metrics"].get(name)
        after = nxt["metrics"].get(name)
        if not all(isinstance(value, (int, float)) and math.isfinite(value) for value in (before, after)) or before == after:
            continue
        fraction = None
        if "min" in gate and after < gate["min"] and before >= gate["min"]:
            fraction = (before - gate["min"]) / (before - after)
        if "max" in gate and after > gate["max"] and before <= gate["max"]:
            fraction = (gate["max"] - before) / (after - before)
        if fraction is not None and 0 <= fraction <= 1:
            crossings.append((last["level"] + fraction * (nxt["level"] - last["level"]), name))
    if not crossings:
        return {"knee": last["level"], "binding_gate": "non_metric_failure"}
    knee, gate = min(crossings)
    return {"knee": knee, "binding_gate": gate}


def candidate_results(run_dir, candidate):
    root = Path(run_dir) / "candidates" / candidate["name"]
    return [read_json(path) for path in sorted(root.glob("level-*/result.json"))]


def run_candidate(config, candidate, run_dir):
    candidate_dir = Path(run_dir) / "candidates" / candidate["name"]
    candidate_dir.mkdir(parents=True, exist_ok=True)
    processes = []
    try:
        check_ports(config, candidate)
        check_gpus(config)
        replica_values = []
        replicas = candidate.get("replicas", config["server"]["replicas"])
        for index, replica in enumerate(replicas):
            values = dict(config.get("values", {}))
            values.update(candidate.get("values", {}))
            values.update(replica.get("values", {}))
            values.update({"name": candidate["name"], "replica": index, "run_dir": str(Path(run_dir).resolve()), "candidate_dir": str(candidate_dir.resolve())})
            replica_values.append(values)
            command = command_for(config["server"], candidate, values, "serve")
            command += [str(render(part, values)) for part in replica.get("args", [])]
            env = environment(config, candidate, config["server"], values)
            for key, value in replica.get("env", {}).items():
                env[key] = str(render(value, values))
            process, log_path = start_process(f"replica-{index}", command, env, config, candidate_dir, config["server"].get("cwd"))
            processes.append(process)
            health = config["server"].get("health", {})
            url = render(health.get("url", "http://{host}:{port}/health"), {**values, "host": values.get("host", "127.0.0.1")})
            wait_ready(process, log_path, url, health, config["server"].get("startup_timeout_s", 3600))
        urls = [f"http://{values.get('host', '127.0.0.1')}:{values['port']}" for values in replica_values]
        worker_urls = ",".join(urls)
        endpoint = urls[0]
        router = config.get("router")
        if router:
            values = dict(config.get("values", {}))
            values.update(candidate.get("values", {}))
            values.update(router.get("values", {}))
            values.update({"name": candidate["name"], "worker_urls": worker_urls, "worker_urls_argv": urls, "run_dir": str(Path(run_dir).resolve()), "candidate_dir": str(candidate_dir.resolve())})
            command = command_for(router, candidate, values, "router")
            env = environment(config, candidate, router, values)
            process, log_path = start_process("router", command, env, config, candidate_dir, router.get("cwd"))
            processes.append(process)
            health = dict(router.get("health", {}))
            health.update(candidate.get("router_health", {}))
            url = render(health.get("url", "http://{host}:{port}/health"), {**values, "host": values.get("host", "127.0.0.1")})
            wait_ready(process, log_path, url, health, router.get("startup_timeout_s", 300))
            endpoint = f"http://{values.get('host', '127.0.0.1')}:{values['port']}"
        config["load"].setdefault("values", {})
        config["load"]["values"].update({"endpoint": endpoint, "worker_urls": worker_urls, "worker_urls_argv": urls})
        for phase in ("correctness", "warmup"):
            section = config.get(phase)
            if not section:
                continue
            values = dict(config.get("values", {}))
            values.update(candidate.get("values", {}))
            values.update(section.get("values", {}))
            values.update({"name": candidate["name"], "endpoint": endpoint, "worker_urls": worker_urls, "candidate_dir": str(candidate_dir.resolve())})
            command = command_for(section, candidate, values, phase)
            env = environment(config, candidate, section, values)
            run_command(phase, command, env, config, candidate_dir, section.get("timeout_s", 3600), section.get("cwd"))
            if "metrics_path" in section:
                metrics = read_json(render(section["metrics_path"], values))
                failures = gate_failures(metrics, section.get("gates", {}))
                if failures:
                    raise RuntimeError(f"{phase} gates failed: {failures!r}")
        load = config["load"]
        levels = sorted(load["levels"])
        refine_step = load.get("refine_step")
        round_levels = [levels]
        for round_index, current_levels in enumerate(round_levels):
            for level in current_levels:
                result = completed_point(config, candidate, level, run_dir)
                if load["mode"] == "open_loop" and not result["pass"] and load.get("early_stop", True):
                    break
            if load["mode"] != "open_loop" or not refine_step or round_index > 0:
                continue
            points = candidate_results(run_dir, candidate)
            passing = [point for point in points if point["pass"]]
            if not passing:
                continue
            last = max(passing, key=lambda point: point["level"])
            following = [point for point in points if point["level"] > last["level"]]
            if not following:
                continue
            upper = min(point["level"] for point in following)
            refined = []
            value = last["level"] + refine_step
            while value < upper - 1e-9:
                refined.append(round(value, 6))
                value += refine_step
            if refined:
                round_levels.append(refined)
        points = candidate_results(run_dir, candidate)
        write_json(candidate_dir / "result.json", {"candidate": candidate, "points": points})
        return points
    except Exception as exc:
        write_json(candidate_dir / "failure.json", {"candidate": candidate, "error": str(exc)})
        raise
    finally:
        for process in reversed(processes):
            stop_process(process, config.get("teardown_timeout_s", 30))


def pareto(points, throughput, latency, per_user):
    result = []
    for point in points:
        dominated = False
        for other in points:
            if other is point:
                continue
            no_worse = other["metrics"].get(throughput, 0) >= point["metrics"].get(throughput, 0)
            no_worse = no_worse and other["metrics"].get(latency, float("inf")) <= point["metrics"].get(latency, float("inf"))
            if per_user:
                no_worse = no_worse and other["metrics"].get(per_user, 0) >= point["metrics"].get(per_user, 0)
            strictly = other["metrics"].get(throughput, 0) > point["metrics"].get(throughput, 0)
            strictly = strictly or other["metrics"].get(latency, float("inf")) < point["metrics"].get(latency, float("inf"))
            if per_user:
                strictly = strictly or other["metrics"].get(per_user, 0) > point["metrics"].get(per_user, 0)
            if no_worse and strictly:
                dominated = True
                break
        if not dominated:
            result.append(point)
    return result


def select_report(config, candidates, all_points):
    load = config["load"]
    selection = load.get("selection", {})
    throughput = selection.get("throughput_metric", "output_tps")
    latency = selection.get("latency_metric", "ttft_p50")
    per_user = selection.get("per_user_metric")
    entries = []
    for candidate in candidates:
        points = [dict(point, candidate_values=candidate.get("values", {})) for point in all_points.get(candidate["name"], [])]
        valid = [point for point in points if point["pass"]]
        entry = {"candidate": candidate["name"], "points": points, "valid_points": len(valid)}
        if load["mode"] == "open_loop":
            entry.update(interpolate_knee(points, load.get("gates", {})))
        elif valid:
            required = [throughput, latency] + ([per_user] if per_user else [])
            valid = [
                point
                for point in valid
                if all(
                    isinstance(point["metrics"].get(name), (int, float)) and math.isfinite(point["metrics"][name])
                    for name in required
                )
            ]
            if selection.get("interactivity_min") is not None:
                name = selection.get("interactivity_metric", "interactivity_p90")
                valid = [point for point in valid if point["metrics"].get(name, float("-inf")) >= selection["interactivity_min"]]
            entry["frontier"] = pareto(valid, throughput, latency, per_user)
            if valid:
                entry["best_point"] = max(valid, key=lambda point: (point["metrics"].get(throughput, float("-inf")), -point["metrics"].get(latency, float("inf"))))
        entries.append(entry)
    eligible = []
    for entry in entries:
        if load["mode"] == "open_loop" and entry.get("knee", 0) > 0:
            score = entry["knee"]
        elif entry.get("best_point"):
            score = entry["best_point"]["metrics"].get(throughput, 0)
        else:
            continue
        eligible.append((score, entry))
    recommended = None
    near_ties = []
    if eligible:
        best_score = max(score for score, _ in eligible)
        tolerance = selection.get("near_tie_pct", 0) / 100
        near_ties = [entry["candidate"] for score, entry in eligible if score >= best_score * (1 - tolerance)]
        recommended = max((entry for score, entry in eligible if score == best_score), key=lambda entry: entry["candidate"])
    return {"mode": load["mode"], "candidates": entries, "recommended": recommended["candidate"] if recommended else None, "near_ties": near_ties}


def write_report(run_dir, report):
    write_json(Path(run_dir) / "report.json", report)
    lines = ["# Serve sweep report", "", f"Recommended: `{report['recommended']}`", ""]
    for entry in report["candidates"]:
        lines.append(f"## {entry['candidate']}")
        lines.append("")
        if "knee" in entry:
            lines.append(f"Knee: `{entry['knee']:.6g}`; binding gate: `{entry['binding_gate']}`")
        if "best_point" in entry:
            best = entry["best_point"]
            lines.append(f"Best level: `{best['level']}`; metrics: `{best['metrics']}`")
        lines.append(f"Valid points: {entry['valid_points']}")
        lines.append("")
    (Path(run_dir) / "report.md").write_text("\n".join(lines), encoding="utf-8")


def command_plan(args):
    config = read_json(args.config)
    validate_config(config)
    candidates = expand_candidates(config)
    plan = {"mode": config["load"]["mode"], "levels": sorted(config["load"]["levels"]), "candidates": candidates, "repeat": config["load"].get("repeat", 1)}
    print(json.dumps(plan, indent=2, sort_keys=True))


def command_run(args):
    config = read_json(args.config)
    validate_config(config)
    run_dir = Path(args.run_dir)
    if run_dir.exists() and any(run_dir.iterdir()) and not args.resume:
        raise ValueError(f"run directory is not empty; use --resume: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=True)
    candidates = expand_candidates(config)
    write_json(run_dir / "config.json", config)
    all_points = {}
    failures = {}
    for candidate in candidates:
        print(f"RUN candidate={candidate['name']}", flush=True)
        try:
            all_points[candidate["name"]] = run_candidate(config, candidate, run_dir)
        except (RuntimeError, ValueError, OSError) as exc:
            all_points[candidate["name"]] = candidate_results(run_dir, candidate)
            failures[candidate["name"]] = str(exc)
            print(f"INVALID candidate={candidate['name']} error={exc}", file=sys.stderr, flush=True)
        report = select_report(config, candidates, all_points)
        report["failures"] = failures
        write_report(run_dir, report)
    report = select_report(config, candidates, all_points)
    report["failures"] = failures
    write_report(run_dir, report)
    print(json.dumps({"recommended": report["recommended"], "near_ties": report["near_ties"], "failures": failures, "report": str(run_dir / "report.json")}, indent=2))


def command_report(args):
    run_dir = Path(args.run_dir)
    config = read_json(run_dir / "config.json")
    validate_config(config)
    candidates = expand_candidates(config)
    all_points = {candidate["name"]: candidate_results(run_dir, candidate) for candidate in candidates}
    report = select_report(config, candidates, all_points)
    failures = {}
    for candidate in candidates:
        failure_path = run_dir / "candidates" / candidate["name"] / "failure.json"
        if failure_path.exists():
            failures[candidate["name"]] = read_json(failure_path)["error"]
    report["failures"] = failures
    write_report(run_dir, report)
    print(json.dumps(report, indent=2, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description="Config-driven serve sweep runner")
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan = subparsers.add_parser("plan")
    plan.add_argument("--config", required=True)
    plan.set_defaults(func=command_plan)
    run = subparsers.add_parser("run")
    run.add_argument("--config", required=True)
    run.add_argument("--run-dir", required=True)
    run.add_argument("--resume", action="store_true")
    run.set_defaults(func=command_run)
    report = subparsers.add_parser("report")
    report.add_argument("--run-dir", required=True)
    report.set_defaults(func=command_report)
    args = parser.parse_args()
    try:
        args.func(args)
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
