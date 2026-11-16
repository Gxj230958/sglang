import json
import pathlib
import subprocess
import sys
import urllib.request

endpoint, model, level, repeat, summary = sys.argv[1:]
level, repeat = int(float(level)), int(repeat)
p = pathlib.Path(summary).parent
n = max(16, 2 * level)
cmd = [sys.executable, '-m', 'sglang.bench_serving', '--backend', 'sglang-oai-chat', '--base-url', endpoint, '--model', model, '--tokenizer', model, '--dataset-name', 'agentic-trace', '--dataset-path', '/scratch/codex-serve-sweep/workload.json', '--num-prompts', str(n), '--agentic-max-turns', '4', '--sharegpt-output-len', '128', '--max-concurrency', str(level), '--request-rate', 'inf', '--seed', str(repeat), '--flush-cache', '--warmup-requests', '1', '--cache-report', '--output-details', '--output-file', str(p/'bench.jsonl'), '--extra-request-body', json.dumps({'temperature':1.0,'top_p':0.95,'chat_template_kwargs':{'enable_thinking':False},'seed':repeat})]
(p/'client-command.json').write_text(json.dumps(cmd,indent=2))
subprocess.run(cmd,check=True)
r=json.loads((p/'bench.jsonl').read_text().splitlines()[-1])
with (p/'requests.jsonl').open('w') as f:
 for i,txt in enumerate(r['generated_texts']):
  row={k:r[k][i] for k in ['input_lens','output_lens','ttfts','itls','errors','cached_tokens'] if k in r}
  row.update(index=i,generated_text=txt)
  f.write(json.dumps(row)+'\n')
input_tokens=sum(r['input_lens'])
assert input_tokens == r['cache_report']['total_prompt_tokens']
total_tps=(input_tokens+r['total_output_tokens'])/r['duration']
row={'level':level,'sent':n*4,'ok':r['completed'],'errors':sum(bool(e) for e in r['errors']),'empty_responses':sum(not t.strip() for t in r['generated_texts']),'ttft_p50':r['median_ttft_ms']/1000,'ttft_p90':r['p90_ttft_ms']/1000,'interactivity_p90':1000/r['p90_itl_ms'],'total_tps_per_gpu':total_tps/4,'output_tps':r['output_throughput'],'total_tps':total_tps,'input':input_tokens,'output':r['total_output_tokens'],'duration_s':r['duration']}
if isinstance(r.get('accept_length'),(int,float)): row['accept_length']=r['accept_length']
if 'cache_report' in r:
 row['cached']=r['cache_report']['total_cached_tokens']
 row['cache_hit']=r['cache_report']['cache_hit_rate_pct']/100
pathlib.Path(summary).write_text(json.dumps(row,indent=2))
for resource in ['metrics','get_server_info']:
 try:
  with urllib.request.urlopen(endpoint+'/'+resource,timeout=10) as response: (p/(resource+'.txt')).write_bytes(response.read())
 except Exception as e: print(resource,type(e).__name__)
