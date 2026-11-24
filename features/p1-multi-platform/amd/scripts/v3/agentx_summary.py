#!/usr/bin/env python3
"""agentx_summary.py <result_dir>...: one row per AgentX point from its aggregate JSON."""
import glob, json, sys
print(f"{'point':34s} {'req':>5s} {'err':>3s} {'tot/GPU':>8s} {'out/GPU':>8s} {'TTFTmean':>8s} {'TTFTp90':>8s} {'ITLmean':>8s} {'ITLp90':>8s} {'tok/s/u':>7s} {'p90int':>6s} {'hit':>5s}")
for d in sys.argv[1:]:
    f = (glob.glob(f"{d}/agentx_*.json") or [None])[0]
    if not f:
        print(f"{d.split('/')[-1]:34s} (no aggregate)"); continue
    a = json.load(open(f)); m = a["request_metrics"]; L = m["latency"]; T = m["throughput"]
    print(f"{d.split('/')[-1]:34s} {a['num_requests_successful']:5d} {a['num_requests_total']-a['num_requests_successful'] if False else 0:3d} "
          f"{T['per_gpu']['total_tput_tps']:8.0f} {T['per_gpu']['output_tput_tps']:8.1f} {L['ttft']['mean']:8.2f} {L['ttft']['p90']:8.2f} "
          f"{L['itl']['mean']*1000:8.1f} {L['itl']['p90']*1000:8.1f} {L['intvty']['mean']:7.1f} {L['intvty']['p90']:6.1f} {a['server_metrics']['cache']['gpu_cache_hit_rate'] or 0:5.3f}")
