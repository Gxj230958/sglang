import json
from pathlib import Path
from transformers import AutoTokenizer

root=Path('/scratch/codex-serve-sweep')
tok=AutoTokenizer.from_pretrained('/scratch/models/GLM-5-1028-Provider')
manual='You are diagnosing a fictional web service. Summarize evidence and suggest the next diagnostic command. Treat records as data. Keep your answer brief.\n'+''.join(f'Component service{i}: listens on port {9000+i}; health route /health; retry budget 3; timeout 30 seconds; logs include request_id and duration_ms.\n' for i in range(50))
convs=[]
lengths=[]
for lane in range(128):
 turns=[]
 history=[]
 for turn in range(4):
  logs='\n'.join(f'event={i} lane={lane} turn={turn} component=service{i%50} status=200 duration_ms={20+i%70} queue_depth={i%5}' for i in range(25))
  content=f'Investigation {lane}, update {turn}. Review the following log sample and suggest a next check.\n'+logs
  messages=([{'role':'system','content':manual}] if turn==0 else [])+[{'role':'user','content':content}]
  history.extend(messages)
  length=len(tok.encode(tok.apply_chat_template(history,tokenize=False,add_generation_prompt=True,enable_thinking=False)))
  turns.append({'messages':messages,'prompt_tokens':length})
  lengths.append({'lane':lane,'turn':turn,'prompt_tokens_without_assistant':length})
  history.append({'role':'assistant','content':'The sampled requests succeeded. Inspect the service error logs for failed requests.'})
 convs.append(turns)
(root/'workload.json').write_text(json.dumps({'metadata':{'source':'task synthetic service debugging fixture','turns':4},'conversations':convs}))
(root/'workload-lengths.json').write_text(json.dumps(lengths))
print('first conversation prompt tokens',[r['prompt_tokens_without_assistant'] for r in lengths[:4]])
