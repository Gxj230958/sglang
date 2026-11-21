import re, subprocess, os, ast, sys
BASE,GLM=sys.argv[1:3]
glm_files=[f for f in subprocess.run(['git','diff','--name-only',BASE,GLM],capture_output=True,text=True).stdout.split() if os.path.exists(f)]
env_src=open('python/sglang/srt/environ.py').read()
defined_envs=set(re.findall(r'^\s+(SGLANG_[A-Z0-9_]+)\s*=\s*Env',env_src,re.M))
removed_map=set(re.findall(r'"(SGL(?:ANG)?_[A-Z0-9_]+)"\s*:',env_src))
# all argparse flags in merged tree
flags=set()
for root in ('python/sglang/srt/arg_groups','python/sglang/srt/server_args.py','python/sglang/srt'):
    pass
out=subprocess.run(['git','grep','-hoE',r'"--[a-z0-9][a-z0-9-]+"','--','python/sglang/srt/*.py','python/sglang/*.py','python/sglang/cli/*.py'],capture_output=True,text=True).stdout
flags=set(x.strip('"') for x in out.split())
# server_args fields -> flags
sa=subprocess.run(['git','grep','-hoE',r'^\s+[a-z_0-9]+\s*:','--','python/sglang/srt/server_args.py','python/sglang/srt/arg_groups/'],capture_output=True,text=True).stdout
flags|=set('--'+x.strip().rstrip(':').strip().replace('_','-') for x in sa.split('\n') if x.strip())
print('## env vars referenced by glm-touched files that are not defined in Envs')
for f in glm_files:
    if f.endswith(('.patch','.png')): continue
    try: t=open(f).read()
    except Exception: continue
    for e in sorted(set(re.findall(r'\b(SGLANG_[A-Z0-9_]+)\b',t))):
        if e not in defined_envs:
            tag='REMOVED' if e in removed_map else 'undefined'
            print(f'{tag:9s} {e}  in {f}')
print('\n## --flags in glm docs/scripts/tests not known to merged server args')
for f in glm_files:
    if not f.endswith(('.mdx','.md','.sh','.py','.yaml','.yml','.json')) or f.startswith('python/sglang/srt/arg_groups') or 'server_args' in f: continue
    t=open(f).read()
    for fl in sorted(set(re.findall(r'(?<![\w-])(--[a-z][a-z0-9-]+)',t))):
        if fl not in flags: print(f'{fl}  in {f}')
