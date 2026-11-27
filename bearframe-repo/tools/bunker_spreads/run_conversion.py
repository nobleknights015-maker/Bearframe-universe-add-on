import argparse,hashlib,subprocess,sys,os
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('base',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
a.source=a.source.resolve();a.base=a.base.resolve();a.output=a.output.resolve()
assert hashlib.sha256(a.source.read_bytes()).hexdigest()=='6c444825727931856d20bdda338628db170ca2b1d2727ebaeb33f4bea7c8e44b'
assert hashlib.sha256(a.base.read_bytes()).hexdigest()=='75ab778e115abe9bc9a6b19d8741f7b509a8a6dc068a8b00e73ed99b6039fb12'
env={**os.environ,'BUNKER_SOURCE':str(a.source),'BUNKER_BASE':str(a.base)};root=Path(__file__).resolve().parent
for name,args in [('extract.py',[]),('mask.py',[]),('bed_palette.py',[]),('build_bunker.py',[str(a.base),str(a.output)]),('verify.py',[str(a.base),str(a.output)])]:
 subprocess.run([sys.executable,str(root/name),*args],env=env,check=True)
