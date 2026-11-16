import json
import pathlib
import sys
import urllib.request

endpoint,model,out=sys.argv[1:]
p=pathlib.Path(out)
rows=[]
for prompt in ['What is 2 plus 3? Give only the number.','Name the capital of France in one short sentence.','A service returns HTTP 503 while restarting. Give one sensible first diagnostic check in one sentence.']:
 body={'model':model,'messages':[{'role':'user','content':prompt}],'max_tokens':1024,'temperature':1.0,'top_p':0.95,'chat_template_kwargs':{'enable_thinking':False},'stream':False}
 try:
  req=urllib.request.Request(endpoint+'/v1/chat/completions',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=180) as response: result=json.load(response)
  rows.append({'prompt':prompt,'response':result})
 except Exception as e: rows.append({'prompt':prompt,'error':str(e)})
(p.parent/'sanity-requests.json').write_text(json.dumps(rows,indent=2))
stops=empty=errors=0
for r in rows:
 if 'error' in r: errors+=1; continue
 choice=r['response']['choices'][0]
 stops+=choice['finish_reason']=='stop'
 empty+=not (choice['message'].get('content') or '').strip()
metrics={'stop_rate':stops/3,'empty_rate':empty/3,'error_rate':errors/3}
p.write_text(json.dumps(metrics,indent=2))
for resource in ['get_server_info','metrics']:
 with urllib.request.urlopen(endpoint+'/'+resource,timeout=10) as response: (p.parent/(resource+'.txt')).write_bytes(response.read())
print(json.dumps(metrics))
