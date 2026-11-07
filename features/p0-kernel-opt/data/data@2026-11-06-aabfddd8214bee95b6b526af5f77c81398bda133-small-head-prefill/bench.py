import json,os,random,statistics,time
from pathlib import Path
import torch
from flash_mla import flash_mla_sparse_fwd as base, flash_mla_sparse_fwd_small_heads as small
R=Path(os.environ['FLASHMLA_BENCH_OUT']);R.mkdir(parents=True,exist_ok=True);rows=[]
for seed in [4101,4102,4103]:
 torch.manual_seed(seed);random.seed(seed)
 for heads in [8,32]:
  for dim in [512,576]:
   for context in [8192,16384,102400]:
    q=torch.zeros(8192,64,dim,device='cuda',dtype=torch.bfloat16);q[:,:heads].normal_()
    kv=torch.randn(context,1,dim,device='cuda',dtype=torch.bfloat16)
    ids=torch.randint(context,(8192,1,2048),device='cuda',dtype=torch.int32)
    scale=dim**-.5
    fns={'head64':lambda:base(q,kv,ids,scale,use_legacy=True,return_log2_lse=False)[0], 'small_heads':lambda:small(q,kv,ids,scale,heads)[0]}
    outputs={k:f() for k,f in fns.items()}
    torch.testing.assert_close(outputs['small_heads'],outputs['head64'][:,:heads],atol=.02,rtol=.02)
    error=(outputs['small_heads']-outputs['head64'][:,:heads]).abs().max().item()
    graphs={}
    for k,f in fns.items():
     for _ in range(3):f()
     g=torch.cuda.CUDAGraph()
     with torch.cuda.graph(g):f()
     graphs[k]=g
    samples={k:[] for k in fns}
    for _ in range(15):
     keys=list(fns);random.shuffle(keys)
     for k in keys:
      graphs[k].replay();a,b=torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True)
      a.record()
      for _ in range(5):graphs[k].replay()
      b.record();b.synchronize();samples[k].append(a.elapsed_time(b)*1000/5)
    med={k:statistics.median(v) for k,v in samples.items()}
    row=dict(seed=seed,heads=heads,dim=dim,context=context,queries=8192,topk=2048,max_abs_error=error,median_us=med,samples_us=samples,latency_reduction_pct=100*(1-med['small_heads']/med['head64']))
    rows.append(row);(R/'kernel-results.json').write_text(json.dumps(rows,indent=2));print(json.dumps({k:v for k,v in row.items() if k!='samples_us'}),flush=True)
    del graphs,outputs,q,kv,ids;torch.cuda.empty_cache()
print('COMPLETE',flush=True)
