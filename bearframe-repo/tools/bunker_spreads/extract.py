from analyze import *
import os
ROOT=Path(__file__).resolve().parent
z=zipfile.ZipFile(os.environ['BUNKER_SOURCE'])
# central authored structure
X0,Z0,Y0=-128,-128,-56; W,D,H=288,352,126
world=np.full((W,H,D),-1,dtype=np.int16); pal=[];lookup={}; bes=[]
for c in chunks(z):
 x,z0=c['xPos']*16,c['zPos']*16
 if x>=X0+W or x+16<=X0 or z0>=Z0+D or z0+16<=Z0:continue
 for s in c.get('sections',[]):
  y=s['Y']*16
  if y>=Y0+H or y+16<=Y0:continue
  p=s.get('block_states',{}).get('palette',[])
  if not p:continue
  ix=[]
  for a in p:
   key=json.dumps(a,sort_keys=True)
   if key not in lookup:lookup[key]=len(pal);pal.append(a)
   ix.append(lookup[key])
  v=np.array(ix,dtype=np.int16)[ids(s)].reshape(16,16,16).transpose(2,0,1)
  a,b=max(y,Y0),min(y+16,Y0+H);world[x-X0:x-X0+16,a-Y0:b-Y0,z0-Z0:z0-Z0+16]=v[:,a-y:b-y,:]
 bes.extend(c.get('block_entities',[]))
np.savez_compressed(ROOT/'central.npz',world=world);json.dump(pal,open(ROOT/'palette.json','w'));print('palette',len(pal));
signs=[]
for b in bes:
 if 'sign' not in b['id']:continue
 def lines(key):
  out=[]
  for m in b.get(key,{}).get('messages',[]):
   try:
    data=json.loads(m);out.append(data.get('text','') if isinstance(data,dict) else str(data))
   except Exception:out.append(m)
  return '\n'.join(out)
 signs.append({'pos':[b['x'],b['y'],b['z']],'front':lines('front_text'),'back':lines('back_text')})
json.dump(signs,open(ROOT/'signs.json','w'))
