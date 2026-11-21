import re,sys,statistics
for p in sys.argv[1:]:
    vals=[];allv=[]
    for l in open(p,errors='replace'):
        m=re.search(r'#running-req: (\d+).*accept len: ([0-9.]+)',l)
        if m:
            allv.append(float(m.group(2)))
            if int(m.group(1))>=16: vals.append(float(m.group(2)))
    print(p.split('/')[3], 'running>=16: n=%d mean=%.3f median=%.3f | all: n=%d median=%.3f'%(len(vals),statistics.mean(vals),statistics.median(vals),len(allv),statistics.median(allv)))
