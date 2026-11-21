import ast, subprocess, sys, re, os, collections
BASE, UP, GLM = sys.argv[1:4]
def git(*a): return subprocess.run(['git',*a],capture_output=True,text=True).stdout
def show(rev,path):
    r=subprocess.run(['git','show',f'{rev}:{path}'],capture_output=True,text=True)
    return r.stdout if r.returncode==0 else None
def parse(src):
    try: return ast.parse(src)
    except SyntaxError: return None
def top_names(t):
    out=set(); dyn=False
    for n in t.body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
            out.add(n.name)
            if n.name=='__getattr__': dyn=True
        elif isinstance(n,ast.Assign):
            for tg in n.targets:
                for x in ast.walk(tg):
                    if isinstance(x,ast.Name): out.add(x.id)
        elif isinstance(n,ast.AnnAssign) and isinstance(n.target,ast.Name): out.add(n.target.id)
        elif isinstance(n,(ast.Import,ast.ImportFrom)):
            for a in n.names: out.add((a.asname or a.name).split('.')[0])
            if isinstance(n,ast.ImportFrom) and any(a.name=='*' for a in n.names): dyn=True
        elif isinstance(n,(ast.If,ast.Try,ast.With)):
            sub=ast.Module(body=[*getattr(n,'body',[]),*getattr(n,'orelse',[]),*[h for hh in getattr(n,'handlers',[]) for h in hh.body],*getattr(n,'finalbody',[])],type_ignores=[])
            o,d=top_names(sub); out|=o; dyn|=d
    return out,dyn
def defs(src):
    out={}
    t=parse(src)
    if t is None: return out
    for n in t.body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
            a=n.args; out[n.name]=('func',[x.arg for x in a.posonlyargs+a.args+a.kwonlyargs],a.kwarg is not None)
        elif isinstance(n,ast.ClassDef):
            out[n.name]=('class',None,None)
            for m in n.body:
                if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)):
                    a=m.args; out[f'{n.name}.{m.name}']=('method',[x.arg for x in a.posonlyargs+a.args+a.kwonlyargs],a.kwarg is not None)
                elif isinstance(m,ast.AnnAssign) and isinstance(m.target,ast.Name):
                    out[f'{n.name}.{m.target.id}']=('field',None,None)
                elif isinstance(m,ast.Assign):
                    for tg in m.targets:
                        if isinstance(tg,ast.Name): out[f'{n.name}.{tg.id}']=('field',None,None)
        elif isinstance(n,ast.Assign):
            for tg in n.targets:
                if isinstance(tg,ast.Name): out[tg.id]=('var',None,None)
    return out
glm_files=sorted(set(git('diff','--name-only','6de483b326c7dd4145fde06afcac9866bf491024',GLM).splitlines()))
glm_py=[f for f in glm_files if f.endswith('.py') and os.path.exists(f)]
# (A) import resolution
modcache={}
def resolve(mod):
    if mod in modcache: return modcache[mod]
    base='python/'+mod.replace('.','/')
    for p in (base+'.py', base+'/__init__.py'):
        if os.path.exists(p):
            t=parse(open(p).read()); r=(p,)+(top_names(t) if t else (set(),True)); modcache[mod]=r; return r
    if os.path.isdir(base): modcache[mod]=(base,set(),True); return modcache[mod]
    modcache[mod]=None; return None
print('## (A) unresolved sglang imports in glm-touched files (merged tree)')
for f in glm_py:
    t=parse(open(f).read())
    if t is None: print('SYNTAX', f); continue
    for n in ast.walk(t):
        if isinstance(n,ast.ImportFrom) and n.module and n.level==0 and n.module.startswith('sglang'):
            r=resolve(n.module)
            if r is None: print(f'{f}:{n.lineno} module missing: {n.module}'); continue
            path,names,dyn=r
            for a in n.names:
                if a.name=='*' or dyn: continue
                if a.name in names: continue
                if resolve(n.module+'.'+a.name): continue
                print(f'{f}:{n.lineno} {n.module} has no {a.name}')
        elif isinstance(n,ast.Import):
            for a in n.names:
                if a.name.startswith('sglang') and resolve(a.name) is None: print(f'{f}:{n.lineno} module missing: {a.name}')
# (B)/(C)
removed=[]; resig=[]
for line in git('diff','--name-status','-M',BASE,UP).splitlines():
    parts=line.split('\t'); st,path=parts[0],parts[1]
    if not path.endswith('.py'): continue
    b=show(BASE,path)
    if b is None: continue
    u=show(UP,parts[2] if st.startswith('R') else path) if st!='D' else ''
    db,du=defs(b),defs(u or '')
    for k,v in db.items():
        if k not in du: removed.append((path,k,v[0]))
        elif v[0] in('func','method') and du[k][0] in('func','method') and not du[k][2]:
            gone=[p for p in v[1] if p not in du[k][1] and p not in('self','cls')]
            if gone: resig.append((path,k,gone,[p for p in du[k][1] if p not in v[1]]))
defined_anywhere={}
def still_defined(leaf):
    if leaf not in defined_anywhere:
        out=subprocess.run(['git','grep','-lE',rf'(def|class) {re.escape(leaf)}\b|^\s*{re.escape(leaf)}\s*(:|=[^=])','--','*.py'],capture_output=True,text=True).stdout.split()
        defined_anywhere[leaf]=out
    return defined_anywhere[leaf]
texts={f:open(f).read() for f in glm_files if os.path.exists(f) and not f.endswith(('.patch','.png','.jpg','.whl'))}
print('\n## (B) names upstream removed (no definition left anywhere) still referenced in glm-touched files')
seen=set()
for path,k,kind in removed:
    leaf=k.split('.')[-1]
    if leaf.startswith('__') or leaf in seen: continue
    seen.add(leaf)
    rx=re.compile(r'\b'+re.escape(leaf)+r'\b')
    refs=[f for f,t in texts.items() if rx.search(t)]
    if refs and not still_defined(leaf):
        print(f'{kind:6s} {path}::{k} -> {refs[:8]}')
    if kind=='field' and k.startswith('ServerArgs.'):
        flag='--'+leaf.replace('_','-')
        frefs=[f for f,t in texts.items() if re.search(re.escape(flag)+r'\b',t)]
        if frefs and not still_defined(leaf): print(f'  flag {flag} -> {frefs[:8]}')
print('\n## (C) calls in glm-touched files passing a keyword upstream removed')
want=collections.defaultdict(list)
for path,k,gone,added in resig: want[k.split('.')[-1]].append((path,k,gone,added))
for f in glm_py:
    t=parse(open(f).read())
    if t is None: continue
    for n in ast.walk(t):
        if isinstance(n,ast.Call):
            nm=n.func.id if isinstance(n.func,ast.Name) else n.func.attr if isinstance(n.func,ast.Attribute) else None
            if nm in want:
                kws={kw.arg for kw in n.keywords if kw.arg}
                for path,k,gone,added in want[nm]:
                    bad=kws & set(gone)
                    if bad: print(f'{f}:{n.lineno} {k} kw {sorted(bad)} removed (upstream {path}; new params {added})')
