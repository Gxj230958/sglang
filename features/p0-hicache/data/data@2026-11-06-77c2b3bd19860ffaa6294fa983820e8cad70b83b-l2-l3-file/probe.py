import fcntl
import hashlib
import json
import os
from pathlib import Path
import random
import re
import shutil
import signal
import socket
import subprocess
import time
import traceback
import urllib.request

R = Path(os.environ['HICACHE_EXPERIMENT_DIR'])
SOURCE = Path(os.environ['GLM_SOURCE_DIR'])
STORE = R / 'l3store'
WHEEL = Path(os.environ['FLASHMLA_SITE'])
PY = os.environ['PYTHON']
MODEL = os.environ['GLM_MODEL']
URL = os.environ.get('HICACHE_URL', 'http://127.0.0.1:35000')
EXPECTED = {
    'python/sglang/srt/layers/attention/dsa_backend.py': '9ddf4ca03c60015426a2a353fe6c802d7f68c36cf9ee6539ed5272374e5d5735',
    'python/sglang/kernels/ops/attention/flash_mla_interface.py': 'cd3d33a1248db6e05f9366ac4c039e90c6ab609b9aafb36184aad4972124babf',
    'python/sglang/srt/configs/glm_loop.py': '700b5d32efd4cebf618924c83edf586250c5d32d52b30db53f2bded9d22f9f7a',
}
QUESTIONS = {
    'N1': (260, 0, 201, 'crates'),
    'N2': (260, 0, 15, 'item'),
    'S1': (80, 1000, 1047, 'crates'),
}
lock = (R / 'controller.lock').open('w')
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
active = None
rows = []
tokenizer = None


def save(name, data):
    p = R / name
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + '.tmp')
    tmp.write_text(json.dumps(data, indent=2) + '\n')
    tmp.replace(p)


def stage(name):
    (R / 'stage').write_text(name + '\n')
    print(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), name, flush=True)


def record(data):
    rows.append(data)
    save('results.json', rows)
    print(json.dumps({k: v for k, v in data.items() if k not in ('output_ids', 'text')}), flush=True)


def req(path, body=None, timeout=1800):
    request = urllib.request.Request(
        URL + path,
        data=None if body is None else json.dumps(body).encode(),
        headers={'Content-Type': 'application/json'},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read()
    try:
        return json.loads(raw)
    except ValueError:
        return raw.decode()


def flush():
    return req('/flush_cache?timeout=120', {}, timeout=150)


def clear_store():
    result = req('/hicache/storage-backend/clear', {}, timeout=150)
    deadline = time.time() + 300
    while time.time() < deadline:
        if store_files()['bin'] == 0:
            return result
        time.sleep(1)
    raise TimeoutError(f'L3 store did not drain: {store_files()}')


def env_for(storage):
    env = os.environ.copy()
    env.update(
        PYTHONPATH=str(SOURCE / 'python') + ':' + str(WHEEL),
        HF_HOME=os.environ.get('HF_HOME', str(R / 'hf-home')),
        SGLANG_UNIFIED_RADIX_TREE_CORE_BACKEND='python',
        SGLANG_HICACHE_FILE_BACKEND_STORAGE_DIR=str(STORE),
    )
    return env


def wait_gpu_free():
    for _ in range(120):
        usage = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader,nounits'], text=True)
        if all(int(x) < 1024 for x in usage.splitlines()):
            return
        time.sleep(2)
    raise RuntimeError('GPU memory did not drain')


def stop():
    global active
    if active is not None:
        if active.poll() is None:
            cmd = Path(f'/proc/{active.pid}/cmdline').read_bytes()
            assert b'sglang.launch_server' in cmd and MODEL.encode() in cmd
            assert os.getpgid(active.pid) == active.pid
            os.killpg(active.pid, signal.SIGTERM)
            try:
                active.wait(timeout=120)
            except subprocess.TimeoutExpired:
                os.killpg(active.pid, signal.SIGKILL)
                active.wait(timeout=30)
        active = None
    wait_gpu_free()


def start(label, storage):
    global active
    command = [
        PY, '-m', 'sglang.launch_server', '--model-path', MODEL,
        '--served-model-name', 'GLM-Loop', '--tp-size', '8',
        '--mem-fraction-static', '0.85', '--kv-cache-dtype', 'bfloat16',
        '--context-length', '32768', '--max-total-tokens', '65536',
        '--max-running-requests', '16', '--chunked-prefill-size', '16384',
        '--page-size', '64', '--dsa-prefill-backend', 'flashmla_sparse',
        '--dsa-decode-backend', 'trtllm', '--reasoning-parser', 'glm45',
        '--tool-call-parser', 'glm47', '--moe-runner-backend', 'deep_gemm',
        '--disable-prefill-cuda-graph', '--random-seed', '463135866',
        '--enable-hierarchical-cache', '--hicache-ratio', '2',
        '--hicache-write-policy', 'write_through', '--enable-cache-report',
        '--hicache-storage-prefetch-policy', 'wait_complete',
        '--host', '127.0.0.1', '--port', '35000',
    ]
    if storage:
        command += ['--hicache-storage-backend', 'file']
    log = R / f'{label}-server.log'
    active = subprocess.Popen(
        command, env=env_for(storage), stdin=subprocess.DEVNULL,
        stdout=log.open('w'), stderr=subprocess.STDOUT, start_new_session=True,
    )
    save(f'{label}-server.json', {'pid': active.pid, 'command': command, 'storage': storage})
    for _ in range(720):
        if active.poll() is not None:
            raise RuntimeError(f'{label} exited {active.returncode}; inspect {log}')
        try:
            req('/health', timeout=3)
            info = req('/get_server_info')
            expected = {
                'tp_size': 8, 'max_total_tokens': 65536, 'kv_cache_dtype': 'bfloat16',
                'enable_hierarchical_cache': True, 'hicache_ratio': 2,
                'hicache_write_policy': 'write_through', 'enable_cache_report': True,
                'hicache_storage_backend': 'file' if storage else None,
            }
            assert all(info.get(k) == v for k, v in expected.items()), {k: info.get(k) for k in expected}
            save(f'{label}-runtime.json', info)
            return
        except (OSError, TimeoutError):
            time.sleep(5)
    raise TimeoutError(label)


def ledger(n, start):
    return ' '.join(
        f'Ledger entry {i}: warehouse {i % 17} shipped {(i * 37) % 101} crates of item {(i * 13) % 59}.'
        for i in range(start, start + n)
    )


def prompt_ids(name):
    n, start, entry, field = QUESTIONS[name]
    question = (
        f'How many crates did ledger entry {entry} ship?'
        if field == 'crates' else f'Which item number did ledger entry {entry} ship?'
    )
    messages = [{
        'role': 'user',
        'content': ledger(n, start) + '\n' + question + ' Reply with the number only.',
    }]
    ids = tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=True)
    if isinstance(ids, dict) or hasattr(ids, 'keys'):
        ids = ids['input_ids']
    want = (entry * 37) % 101 if field == 'crates' else (entry * 13) % 59
    return list(ids), want


def gen(name, tag):
    ids, want = prompt_ids(name)
    before = time.time()
    result = req('/generate', {
        'input_ids': ids,
        'sampling_params': {'temperature': 0, 'max_new_tokens': 512},
    })
    text = result['text']
    final = text
    for separator in ('</think:opensource>', '</think>'):
        if separator in final:
            final = final.split(separator)[-1]
    numbers = re.findall(r'-?\d+', final.strip())
    got = numbers[-1] if numbers else ''
    meta = result['meta_info']
    details = meta.get('cached_tokens_details') or {}
    if isinstance(details, list):
        assert len(details) == 1
        details = details[0] or {}
    row = {
        'name': name, 'tag': tag, 'prompt_tokens': len(ids), 'want': want, 'got': got,
        'ok': got == str(want), 'finish': meta.get('finish_reason'),
        'cached_tokens': meta.get('cached_tokens'), 'cached_tokens_details': details,
        'completion_tokens': meta.get('completion_tokens'),
        'latency_s': round(time.time() - before, 3),
        'output_ids': result.get('output_ids'), 'final': final.strip()[-100:], 'text': text,
    }
    record(row)
    assert row['ok'], row
    assert (row['finish'] or {}).get('type') == 'stop', row
    return row


def filler(total_tokens=98304):
    rng = random.Random(91027)
    sent = 0
    index = 0
    while sent < total_tokens:
        ids = [rng.randrange(1000, 100000) for _ in range(4096)]
        result = req('/generate', {
            'input_ids': ids,
            'sampling_params': {'temperature': 0, 'max_new_tokens': 1, 'ignore_eos': True},
        })
        assert result['meta_info']['completion_tokens'] == 1
        sent += len(ids)
        index += 1
    record({'event': 'filler', 'requests': index, 'prompt_tokens': sent})


def store_files():
    names = []
    total_bytes = 0
    for p in STORE.glob('*.bin') if STORE.exists() else []:
        try:
            size = p.stat().st_size
        except FileNotFoundError:
            continue
        names.append(p)
        total_bytes += size
    indexer = [p for p in names if '.indexer' in p.name]
    return {
        'bin': len(names), 'indexer': len(indexer), 'kv': len(names) - len(indexer),
        'bytes': total_bytes,
    }


def wait_store_stable(quiet_s=15, max_s=600):
    last = None
    changed = time.time()
    started = time.time()
    while time.time() - started < max_s:
        current = store_files()
        if current != last:
            last = current
            changed = time.time()
        elif time.time() - changed >= quiet_s:
            return current
        time.sleep(3)
    raise TimeoutError(f'L3 store did not stabilize: {last}')


def run_l2():
    stage('L2-cold-warm')
    flush()
    for name in ('N1', 'S1'):
        cold = gen(name, 'L2_cold')
        assert not cold['cached_tokens']
        warm = gen(name, 'L2_warm')
        assert warm['cached_tokens'] > 0
    stage('L2-evict-device')
    filler()
    for name in ('N1', 'S1'):
        restored = gen(name, 'L2_host_restore')
        assert restored['cached_tokens_details'].get('host', 0) > 0, restored
        assert restored['cached_tokens_details'].get('storage', 0) == 0
    shared = gen('N2', 'L2_shared_prefix_after_host_restore')
    assert shared['cached_tokens'] > 0
    assert shared['cached_tokens_details'].get('storage', 0) == 0
    stage('L2-flush-negative-control')
    flush()
    cold = gen('N1', 'L2_after_flush')
    assert not cold['cached_tokens']


def run_l3_populate():
    stage('L3-A-cold-warm')
    flush()
    for name in ('N1', 'S1'):
        cold = gen(name, 'L3_A_cold')
        assert not cold['cached_tokens']
        warm = gen(name, 'L3_A_warm')
        assert warm['cached_tokens'] > 0
    files = wait_store_stable()
    record({'event': 'L3_store_after_warm', **files})
    assert files['bin'] > 0 and files['indexer'] > 0 and files['kv'] > 0, files
    flush()
    after = store_files()
    record({'event': 'L3_store_after_flush', **after})
    assert after == files


def run_l3_restore():
    for name in ('N1', 'S1', 'N2'):
        stage('L3-B-restore-' + name)
        flush()
        restored = gen(name, 'L3_B_storage_restore')
        assert restored['cached_tokens_details'].get('storage', 0) > 0, restored
    for name in ('N1', 'S1', 'N2'):
        stage('L3-C-recompute-' + name)
        flush()
        clear_store()
        files = store_files()
        record({'event': 'L3_store_after_clear', 'name': name, **files})
        assert files['bin'] == 0
        cold = gen(name, 'L3_C_recompute')
        assert not cold['cached_tokens'], cold


try:
    for rel, expected in EXPECTED.items():
        actual = hashlib.sha256((SOURCE / rel).read_bytes()).hexdigest()
        assert actual == expected, (rel, actual, expected)
    with socket.socket() as sock:
        assert sock.connect_ex(('127.0.0.1', 35000)) != 0
    wait_gpu_free()
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    save('provenance.json', {
        'branch': 'glm-5-lp', 'commit': '77c2b3bd19860ffaa6294fa983820e8cad70b83b',
        'source_file_hashes': EXPECTED, 'device_tokens': 65536,
        'host_ratio': 2, 'filler_tokens': 98304, 'storage': 'file',
        'glm_loop_config': 'compatible config retained because installed transformers lacks glm_loop',
    })
    if os.environ.get('HICACHE_NEGATIVE_ONLY') == '1':
        rows.extend(json.loads((R / 'results.json').read_text()))
        stage('starting-L3-negative-control')
        start('l3-c', storage=True)
        for name in ('N1', 'S1', 'N2'):
            stage('L3-C-recompute-' + name)
            flush()
            clear_store()
            files = store_files()
            record({'event': 'L3_store_after_clear', 'name': name, **files})
            assert files['bin'] == 0
            cold = gen(name, 'L3_C_recompute')
            assert not cold['cached_tokens'], cold
    else:
        if STORE.exists():
            shutil.rmtree(STORE)
        STORE.mkdir(parents=True)
        stage('starting-L2-only')
        start('l2', storage=False)
        run_l2()
        stage('stopping-L2-only')
        stop()
        stage('starting-L3-A')
        start('l3-a', storage=True)
        run_l3_populate()
        stage('stopping-L3-A')
        stop()
        stage('starting-L3-B-same-store')
        start('l3-b', storage=True)
        run_l3_restore()
    save('controller-exit.json', {'returncode': 0, 'requests': sum('name' in r for r in rows)})
    stage('complete')
except BaseException:
    (R / 'failure.txt').write_text(traceback.format_exc())
    save('controller-exit.json', {'returncode': 1})
    stage('failed')
    raise
finally:
    stop()
