import sys,zipfile,struct,json,collections,os
from pathlib import Path
from bed_nbt import NBT
ROOT=Path(__file__).resolve().parent
z=zipfile.ZipFile(os.environ['BUNKER_BASE']);p=collections.defaultdict(dict);tag=b'\x09\x0d\x00block_palette'
for name in z.namelist():
 if not name.endswith('.mcstructure'):continue
 b=z.read(name);i=b.find(tag)
 if i<0:continue
 n=NBT(b);n.p=i+len(tag)
 for d in n.read(9):p[d['name']][json.dumps(d['states'],sort_keys=True)]=d
json.dump({k:list(v.values()) for k,v in p.items()},open(ROOT/'bed_palette.json','w'));print(len(p),sum(map(len,p.values())))
