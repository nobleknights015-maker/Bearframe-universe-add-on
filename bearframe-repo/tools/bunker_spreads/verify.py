import zipfile,json,sys,struct,subprocess,hashlib,collections
from pathlib import Path
import numpy as np
base=Path(sys.argv[1]);out=Path(sys.argv[2]);bp='Bearframe_Behavior/';rp='Bearframe_Resources/'
class NBT:
 def __init__(self,b):self.b=b;self.p=0
 def take(self,n):v=self.b[self.p:self.p+n];self.p+=n;return v
 def num(self,f):return struct.unpack('<'+f,self.take(struct.calcsize('<'+f)))[0]
 def string(self):return self.take(self.num('H')).decode()
 def read(self,t):
  if t==10:
   d={}
   while (k:=self.num('B')):n=self.string();d[n]=self.read(k)
   return d
  if t==9:
   k=self.num('B');n=self.num('i');return np.frombuffer(self.take(4*n),dtype='<i4') if k==3 else [self.read(k) for _ in range(n)]
  if t==8:return self.string()
  if t in (7,11,12):return self.take(self.num('i')*{7:1,11:4,12:8}[t])
  return self.num({1:'b',2:'h',3:'i',4:'q',5:'f',6:'d'}[t])
 def root(self):assert self.num('B')==10;self.string();d=self.read(10);assert self.p==len(self.b);return d
with zipfile.ZipFile(base) as old,zipfile.ZipFile(out) as new:
 assert new.testzip() is None
 names=new.namelist();assert len(set(names))==len(names);assert {n.split('/')[0] for n in names}=={bp[:-1],rp[:-1]}
 old_names=set(old.namelist());changed=[n for n in old_names if (new.getinfo(n).CRC,new.getinfo(n).file_size)!=(old.getinfo(n).CRC,old.getinfo(n).file_size)];print('changed base members:',sorted(changed),flush=True);assert set(changed)=={bp+'manifest.json',rp+'manifest.json',bp+'scripts/main.js'}
 b=json.loads(new.read(bp+'manifest.json'));r=json.loads(new.read(rp+'manifest.json'));assert b['header']['version']==r['header']['version']==[0,11,20];assert b['header']['uuid']==json.loads(old.read(bp+'manifest.json'))['header']['uuid'];assert any(d.get('uuid')==r['header']['uuid'] and d['version']==r['header']['version'] for d in b['dependencies'])
 count=0;js=0;containers=0;encounters=0;signs=0;occupied=0;palette=set();pnames=[];parts=json.loads(new.read(bp+'scripts/legacy_bunker_layout.js').decode().split('=',1)[1].strip().rstrip(';'))
 for n in set(names)-old_names|set(changed):
  if n.endswith('.json'):json.loads(new.read(n).decode('utf-8-sig'));count+=1
  if n.endswith('.js'):subprocess.run(['node','--input-type=module','--check'],input=new.read(n),check=True,capture_output=True);js+=1
  if n.startswith(bp+'structures/bearframe/legacy_bunker_') and n.endswith('.mcstructure'):
   data=NBT(new.read(n)).root();w,h,d=data['size'];assert w<=32 and d<=32 and h<=256
   p=data['structure']['palette']['default'];pi=p['block_palette'];ind,sec=data['structure']['block_indices'];assert len(ind)==len(sec)==w*h*d;assert np.all((ind>=-1)&(ind<len(pi))) and np.all((sec>=-1)&(sec<len(pi)));assert not data['structure']['entities']
   palette|={a['name'] for a in pi};occupied+=int((ind>=0).sum())
   for i,a in enumerate(pi):
    if a['name']=='bearframe:legacy_bunker_encounter':encounters+=int((ind==i).sum())
   for k,v in p.get('block_position_data',{}).items():
    e=v['block_entity_data'];assert 0<=int(k)<len(ind)
    if e['id'] in ('Chest','Barrel'):assert e['LootTable']=='loot_tables/chests/legacy_bunker.json';containers+=1
    if e['id']=='Sign':signs+=1
   pnames.append(n)
 assert len(pnames)==44 and len(parts)==43
 for part in parts:assert bp+'structures/bearframe/'+part['id']+'.mcstructure' in pnames
 for i,a in enumerate(parts):
  for b in parts[i+1:]:assert not all(a['offset'][k]<b['offset'][k]+b['size'][k] and b['offset'][k]<a['offset'][k]+a['size'][k] for k in range(3)),(a,b)
 loot=new.read(bp+'loot_tables/chests/legacy_bunker.json');assert b'bearframe:field_cutter' not in loot
 assert all(x.startswith('minecraft:') or x in ('bearframe:legacy_bunker_datum','bearframe:legacy_bunker_encounter') for x in palette)
 print({'members':len(names),'changed_json':count,'changed_js':js,'new_structures':len(pnames),'occupied':occupied,'containers':containers,'encounters':encounters,'signs':signs,'original_structures_preserved':sum(n.endswith('.mcstructure') for n in old_names),'palette_ids':len(palette),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()},flush=True)
