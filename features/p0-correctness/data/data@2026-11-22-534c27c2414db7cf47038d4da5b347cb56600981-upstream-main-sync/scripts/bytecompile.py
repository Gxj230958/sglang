import subprocess, sys
files=subprocess.run(['git','ls-files','*.py'],capture_output=True,text=True).stdout.split()
bad=0
for f in files:
    try: compile(open(f,'rb').read(), f, 'exec')
    except SyntaxError as e: bad+=1; print('FAIL',f,e)
print(f'{len(files)} files, {bad} failures')
