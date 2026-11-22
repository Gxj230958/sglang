import ast, subprocess, sys
BASE, UP = sys.argv[1:3]
def git(*a): return subprocess.run(['git',*a],capture_output=True,text=True).stdout
def show(rev,p):
    r=subprocess.run(['git','show',f'{rev}:{p}'],capture_output=True,text=True); return r.stdout if r.returncode==0 else None
def sigs(src):
    out={}
    try: t=ast.parse(src)
    except Exception: return out
    def args(a):
        req=len(a.args)-len(a.defaults)
        return ([x.arg for x in a.posonlyargs+a.args], req, [x.arg for x in a.kwonlyargs], [x.arg for x,d in zip(a.kwonlyargs,a.kw_defaults) if d is None])
    for n in t.body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)): out[n.name]=args(n.args)
        elif isinstance(n,ast.ClassDef):
            out[n.name]='class'
            for m in n.body:
                if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)): out[f'{n.name}.{m.name}']=args(m.args)
    return out
for line in git('diff','--name-status','-M',BASE,UP).splitlines():
    parts=line.split('\t'); st=parts[0]; path=parts[1]
    if not path.endswith('.py') or not path.startswith('python/sglang/srt') and not path.startswith('python/sglang/kernels') and not path.startswith('python/sglang/jit_kernel') and not path.startswith('python/sglang/multimodal_gen'): continue
    b=show(BASE,path)
    if b is None: continue
    newp=parts[2] if st.startswith('R') else path
    u=show(UP,newp) if st!='D' else ''
    sb,su=sigs(b),sigs(u or '')
    for k,v in sb.items():
        if k not in su: print(f'REMOVED {path}::{k}' + (f' (file renamed to {newp})' if newp!=path else ''))
        elif v!=su[k] and v!='class' and su[k]!='class': print(f'CHANGED {path}::{k}\n   {v}\n-> {su[k]}')
