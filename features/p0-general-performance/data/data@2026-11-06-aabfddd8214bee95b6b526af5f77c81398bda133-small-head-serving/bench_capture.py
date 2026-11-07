#!/usr/bin/env python3
"""Run bench_one_batch_server unchanged, recording per-request and input evidence."""
import hashlib
import inspect
import json
import os
from pathlib import Path
import re
import runpy
import statistics
import time

import requests
import sglang.benchmark.one_batch_server as bench

OUT = Path(os.environ['HEAD32_BENCH_CAPTURE'])
OUT.mkdir(parents=True, exist_ok=True)
LOG = Path(os.environ['HEAD32_BENCH_SERVER_LOG'])
bench.DEFAULT_TIMEOUT = 3600
context = {}
original_dataset = bench.get_dataset
original_post = requests.post
original_case = bench.run_one_case
original_recorder = bench.BatchStreamRecorder


def dataset(*args, **kwargs):
    rows = original_dataset(*args, **kwargs)
    context['inputs'] = [dict(tokens=len(row.prompt), sha256=hashlib.sha256(
        json.dumps(row.prompt, separators=(',', ':')).encode()).hexdigest()) for row in rows]
    return rows


def post(url, *args, **kwargs):
    if str(url).endswith('/generate') and 'input_ids' in kwargs.get('json', {}):
        context['start'] = time.perf_counter()
    return original_post(url, *args, **kwargs)


class Recorder(original_recorder):
    def __init__(self, batch_size):
        super().__init__(batch_size)
        self.first = [None] * batch_size
        self.last_increment = [None] * batch_size
        self.finished = [None] * batch_size
        self.counts = [0] * batch_size
        context['recorder'] = self

    def record_chunk(self, *, index, completion_tokens, finish_type, now):
        if completion_tokens > self.counts[index]:
            self.first[index] = self.first[index] or now
            self.last_increment[index] = now
        if finish_type is not None:
            self.finished[index] = now
        self.counts[index] = completion_tokens
        super().record_chunk(index=index, completion_tokens=completion_tokens,
                             finish_type=finish_type, now=now)


def case(*args, **kwargs):
    context.clear()
    bound = inspect.signature(original_case).bind(*args, **kwargs)
    bound.apply_defaults()
    params = bound.arguments
    offset = LOG.stat().st_size
    result = original_case(*args, **kwargs)
    recorder = context['recorder']
    assert len(context['inputs']) == params['batch_size']
    assert all(x['tokens'] == params['input_len'] for x in context['inputs'])
    assert all(x == params['output_len'] for x in recorder.counts)
    assert all(t is not None for t in recorder.finished)
    start = context['start']
    requests_out = [dict(index=i, input_tokens=context['inputs'][i]['tokens'],
                         prompt_sha256=context['inputs'][i]['sha256'],
                         output_tokens=recorder.counts[i],
                         ttft_s=recorder.first[i]-start,
                         latency_s=recorder.finished[i]-start,
                         tpot_s=(recorder.last_increment[i]-recorder.first[i])/(recorder.counts[i]-1))
                    for i in range(recorder.batch_size)]
    with LOG.open('rb') as f:
        f.seek(offset)
        log = f.read().decode(errors='replace')
    observed = [int(x) for x in re.findall(r'Decode batch, #running-req: (\d+)', log)]
    label = ('warmup' if not params['result_filename'] else 'measured')
    name = f"{label}-bs{params['batch_size']}-il{params['input_len']}-ol{params['output_len']}"
    (OUT/(name+'-server.log')).write_text(log)
    (OUT/(name+'-requests.json')).write_text(json.dumps(requests_out, indent=2)+'\n')
    summary = dict(kind=label, result=result.model_dump(),
                   median_ttft_s=statistics.median(x['ttft_s'] for x in requests_out),
                   median_tpot_s=statistics.median(x['tpot_s'] for x in requests_out),
                   median_latency_s=statistics.median(x['latency_s'] for x in requests_out),
                   wall_output_tokens_s=sum(recorder.counts)/result.latency,
                   observed_decode_batch_samples={str(x):observed.count(x) for x in sorted(set(observed))})
    (OUT/(name+'-summary.json')).write_text(json.dumps(summary, indent=2)+'\n')
    print('HEAD32_CAPTURE '+json.dumps(summary), flush=True)
    return result


bench.get_dataset = dataset
requests.post = post
bench.BatchStreamRecorder = Recorder
bench.run_one_case = case
runpy.run_module('sglang.bench_one_batch_server', run_name='__main__')
