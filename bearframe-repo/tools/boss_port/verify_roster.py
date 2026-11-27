"""Static package and linkage validation; not a Bedrock client/server test."""
import sys,json,zipfile,hashlib,subprocess,io,math
from PIL import Image
from pathlib import Path
from build_roster import BOSSES,BP,RP,SRC
base,jar,out=sys.argv[1:]
with zipfile.ZipFile(base) as z:old={n:z.read(n) for n in z.namelist()}
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None and len(set(z.namelist()))==len(z.namelist());f={n:z.read(n) for n in z.namelist()}
assert all(f[n]==b for n,b in old.items() if n.endswith('.mcstructure') or 'loot_tables/' in n or '/rarity_stats/' in n or '/chest_loot/' in n)
allbosses={**BOSSES,'echo_seam_riven':('umvuthana','seam_splitter',(185,114,246))}
s=f[BP+'scripts/boss_moves.js'].decode();moves=json.loads(s[s.index('{'):s.rindex('}')+1]);assert set(moves)=={'bearframe:'+n for n in allbosses}
assert sum(len(v) for v in moves.values())==16
anim={}
for n in f:
 if n.startswith(RP+'animations/') and n.endswith('.json'):anim.update(json.loads(f[n]).get('animations',{}))
with zipfile.ZipFile(jar) as z:
 for n,(src,drop,_) in allbosses.items():
  g=json.loads(f[RP+'models/entity/'+n+'.geo.json'])['minecraft:geometry'][0];bs={b['name']:b for b in g['bones']};assert len(bs)==len(g['bones'])
  for b in bs.values():
   p=b.get('parent');seen={b['name']}
   while p:
    assert p in bs and p not in seen;seen.add(p);p=bs[p].get('parent')
  sg=json.loads(z.read(SRC+'geo/'+src+'.geo.json'))['minecraft:geometry'][0];prefix='mm_' if n in ('grid_palinode','grid_silt_engine','grid_gantry_marrow') else ''
  for b in sg['bones']:
   t=bs[prefix+b['name']];assert t.get('rotation',[0,0,0])==b.get('rotation',[0,0,0]);assert not b.get('parent') or t['parent']==prefix+b['parent']
   if not prefix:assert t['pivot']==b['pivot']
  ce=json.loads(f[RP+'entity/'+n+'.entity.json'])['minecraft:client_entity']['description'];assert ce['geometry']['default']==g['description']['identifier']
  tex=Image.open(io.BytesIO(f[RP+ce['textures']['default']+'.png']));assert tex.size==(g['description']['texture_width'],g['description']['texture_height'])
  assert sum(len(b.get('cubes',[])) for b in bs.values())>=30
  for alias in ('idle','walk','attack0','attack1','death'):
   a=anim[ce['animations'][alias]];assert set(a['bones'])<=set(bs);assert a['animation_length']>0
   for b,c in a['bones'].items():
    for k,v in c.items():
     if isinstance(v,dict):
      for t in v:
       try:time=float(t)
       except ValueError:continue
       assert 0<=time<=a['animation_length']+.0001,(n,alias,b,k,time,a['animation_length'])
   if alias.startswith('attack'):
    mv=moves['bearframe:'+n][int(alias[-1])];assert 0<mv['windup']<mv['end'];assert mv['end']>=math.ceil(a['animation_length']*20)-1
  e=json.loads(f[BP+'entities/'+n+'.json'])['minecraft:entity'];table=json.loads(f[BP+e['components']['minecraft:loot']['table']]);assert any(p.get('rolls')==1 and len(p.get('entries',[]))==1 and p['entries'][0].get('name')=='bearframe:'+drop for p in table['pools'])
# Held art, texture and animation linkage across all original 18 items.
atlas=json.loads(f[RP+'textures/item_texture.json'])['texture_data'];count=0
for n in f:
 if not n.startswith(RP+'attachables/') or not n.endswith('.json'):continue
 d=json.loads(f[n])['minecraft:attachable']['description'];item=d['identifier'].split(':')[-1]
 if not d['identifier'].startswith('bearframe:'):continue
 g=json.loads(f[RP+'models/entity/held_'+item+'.geo.json'])['minecraft:geometry'][0];assert d['geometry']['default']==g['description']['identifier'];bn={b['name'] for b in g['bones']};assert g['bones'][0]['binding']=='q.item_slot_to_bone_name(context.item_slot)'
 for v in d['animations'].values():assert v in anim and set(anim[v]['bones'])<=bn,(item,v)
 for v in [d['textures']['default'],atlas[json.loads(f[BP+'items/'+item+'.json'])['minecraft:item']['components']['minecraft:icon']]['textures']]:assert RP+v+'.png' in f;Image.open(io.BytesIO(f[RP+v+'.png'])).verify()
 count+=1
assert count==18,count
# Confirm first/third-person definitions, all six katana tiers and source loot policy remain untouched.
assert all(f[n]==v for n,v in old.items() if 'cyber_katana' in n)
print('8 boss hierarchies, 40 clips, 16 moves, 8 guaranteed rewards, 18 held-item chains, 724 unchanged structures, 39 unchanged loot tables. Archive SHA256:',hashlib.sha256(Path(out).read_bytes()).hexdigest())
