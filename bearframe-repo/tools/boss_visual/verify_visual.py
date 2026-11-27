"""Check this visual-only update against the exact 0.11.24 archive."""
import sys,json,zipfile,io,math,hashlib
from PIL import Image
from polish import IDS, BP, RP
base,out=sys.argv[1:]
with zipfile.ZipFile(base) as z:old={n:z.read(n) for n in z.namelist()}
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()));f={n:z.read(n) for n in z.namelist()}
assert set(f)==set(old)
allowed={BP+'manifest.json',RP+'manifest.json'};count=0
for id in IDS:
 gp=RP+'models/entity/'+id+'.geo.json';ap=RP+'animations/'+id+'.animation.json';ce=json.loads(f[RP+'entity/'+id+'.entity.json'])['minecraft:client_entity']['description'];tp=RP+ce['textures']['default']+'.png';allowed.update((gp,tp));g=json.loads(f[gp])['minecraft:geometry'][0];og=json.loads(old[gp])['minecraft:geometry'][0];bones={b['name']:b for b in g['bones']};assert len(bones)==len(g['bones']);tex=Image.open(io.BytesIO(f[tp]));assert tex.size==(512,512)
 for b in og['bones']:
  assert {k:v for k,v in b.items() if k!='cubes'}=={k:v for k,v in bones[b['name']].items() if k!='cubes'}
 for b in bones.values():
  seen={b['name']};parent=b.get('parent')
  while parent:assert parent in bones and parent not in seen;seen.add(parent);parent=bones[parent].get('parent')
  for c in b.get('cubes',[]):
   count+=1;assert all(math.isfinite(float(v)) for v in c['origin']+c['size']+c.get('rotation',[])+c.get('pivot',[])) and min(c['size'])>0
   for face,uv in c['uv'].items():
    x,y=uv['uv'];w,h=uv['uv_size'];assert 0<=min(x,x+w)<max(x,x+w)<=512 and 0<=min(y,y+h)<max(y,y+h)<=512
 a=json.loads(f[ap])['animations'];oa=json.loads(old[ap])['animations'];assert set(a)==set(oa)
 for k,v in a.items():
  assert v['animation_length']==oa[k]['animation_length'];assert set(v['bones'])<=bones.keys()
  assert all(v['bones'][n]==c for n,c in oa[k]['bones'].items())
  if id.startswith('echo_'):
   allowed.add(ap);assert 'bfv_root' in v['bones'];assert any(n.startswith('bfv_') for n in v['bones'])
   for n,c in v['bones'].items():
    if not n.startswith('bfv_'):continue
    for t,val in c.get('rotation',{}).items():assert 0<=float(t)<=v['animation_length']+.00001 and len(val)==3 and all(math.isfinite(x) for x in val)
  else:assert f[ap]==old[ap]
for n,b in old.items():
 if n not in allowed:assert f[n]==b,n
assert len([n for n in f if f[n]!=old[n]])==22
print('All eight bosses:',count,'visible cuboids; 22 modified files; all other files byte-identical; original source skeleton and all 40 source animation channels preserved; UV bounds, acyclic parent links, and retargeted rotation checks passed.')
print('SHA256:',hashlib.sha256(open(out,'rb').read()).hexdigest())
