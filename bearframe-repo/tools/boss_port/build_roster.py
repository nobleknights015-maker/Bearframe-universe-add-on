"""Build 0.11.24 roster candidate from local 0.11.23 and exact owner-supplied JAR.
New chassis and plating on source rigs; hybrid Ghost Grid mechanisms preserve existing canonical chassis.
No third-party visible meshes, textures or Java bytecode are copied to the repository by this tool.
"""
import argparse, copy, json, math, re, io, hashlib, zipfile, subprocess, ast, collections
from pathlib import Path
from PIL import Image, ImageDraw
BP='Bearframe_Behavior/'; RP='Bearframe_Resources/'; SRC='assets/mowziesmobs/'
VERSION=[0,11,24]
BOSSES={
 'grid_palinode':('bluff','palinode_ram',(82,220,210)),
 'grid_silt_engine':('bluff','silt_discharge',(84,176,228)),
 'grid_gantry_marrow':('elokosa','gantry_rake',(154,218,179)),
 'grid_cinder_spindle':('bluff','cinder_inductor',(247,148,55)),
 'echo_veil_regent':('sculptor','veil_anchor',(194,137,244)),
 'echo_rubble_rook':('elokosa','rook_hammer',(166,100,229)),
 'echo_hush_pendulum':('umvuthana','hush_pendulum',(239,114,81))}
def enc(o): return (json.dumps(o,indent=2,allow_nan=False)+'\n').encode()
def png(im):
 b=io.BytesIO();im.save(b,format='PNG');return b.getvalue()
class Atlas:
 def __init__(self,accent,echo=False):
  self.im=Image.new('RGBA',(256,256));self.d=ImageDraw.Draw(self.im);self.n=0
  self.pal={'shell':(126,131,124) if not echo else (148,143,139),'plate':(184,181,163) if not echo else (199,193,183),'dark':(38,43,47),'joint':(76,82,84),'rust':(123,77,49),'moss':(63,95,54),'cloth':(66,49,76),'light':accent,'blade':(162,185,185),'trim':(90,97,96)}
 def cube(self,o,s,k='shell',r=None,p=None):
  assert all(x>0 for x in s),(o,s);i=self.n;self.n+=1;assert self.n<=256
  u=(i%16)*16;v=(i//16)*16;c=self.pal[k];d=self.d
  shade=lambda a:tuple(max(0,min(255,x+a)) for x in c)
  d.rectangle([u,v,u+15,v+15],fill=c)
  if k!='light':
   d.line([u,v,u+15,v],fill=shade(32));d.line([u,v,u,v+15],fill=shade(20));d.line([u,v+15,u+15,v+15],fill=shade(-36));d.line([u+15,v,u+15,v+15],fill=shade(-22))
   for x,y in [(2,2),(13,2),(2,13),(13,13)]:d.point((u+x,v+y),fill=shade(-36))
   for j in range(5):
    x=2+(i*7+j*5)%12;y=2+(i*3+j*7)%12;d.point((u+x,v+y),fill=shade(-15))
   if k=='moss':
    for j in range(10):d.point((u+2+(i+j*5)%12,v+2+(i*3+j*3)%12),fill=shade(30))
  else:
   d.rectangle([u+1,v+1,u+14,v+14],fill=shade(-35));d.rectangle([u+4,v+4,u+11,v+11],fill=shade(25))
  c={'origin':[round(x,4) for x in o],'size':[round(x,4) for x in s], 'uv':{face:{'uv':[u,v],'uv_size':[16,16]} for face in ['north','south','east','west','up','down']}}
  if r and any(r):c.update(rotation=r,pivot=p if p is not None else [o[i]+s[i]/2 for i in range(3)])
  return c
# Restricted arithmetic evaluator for the JAR's animation expressions, with degree-based trig.
SAFE={'sin':lambda v:math.sin(math.radians(v)),'cos':lambda v:math.cos(math.radians(v)),'max':max,'min':min,'clamp':lambda v,a,b:max(a,min(v,b)),'abs':abs}
EXPRS={};REPAIRS=collections.Counter()
def num(x,t):
 if isinstance(x,(int,float)):return x
 if x not in EXPRS:
  v=re.sub(r'\b(?:Math|math)\.', '', x);v=v.replace('query.anim_time','t')
  if 'NaN' in v:REPAIRS[x]+=1;v=re.sub(r'\bNaN\b','0',v)
  tree=ast.parse(v.strip(),mode='eval')
  allowed=(ast.Expression,ast.BinOp,ast.UnaryOp,ast.Constant,ast.Name,ast.Load,ast.Add,ast.Sub,ast.Mult,ast.Div,ast.Pow,ast.Mod,ast.UAdd,ast.USub,ast.Call)
  assert all(isinstance(n,allowed) and (not isinstance(n,ast.Name) or n.id in SAFE or n.id=='t') for n in ast.walk(tree)),v
  EXPRS[x]=compile(tree,'<animation>','eval')
 result=eval(EXPRS[x],{'__builtins__':{}},{**SAFE,'t':t});assert math.isfinite(result),x;return result
def ease(name,t):
 if not name or name=='linear':return t
 if name=='step':return 0 if t<1 else 1
 m=re.fullmatch(r'ease(InOut|In|Out)(Sine|Quad|Cubic|Quart|Quint|Expo|Back|Elastic)',name);assert m,name
 mode,kind=m.groups()
 def f(x):
  if kind=='Sine':return 1-math.cos(x*math.pi/2)
  if kind=='Expo':return 0 if x==0 else 2**(10*x-10)
  if kind=='Back':return 2.70158*x*x*x-1.70158*x*x
  if kind=='Elastic':return x if x in (0,1) else -(2**(10*x-10))*math.sin((x*10-10.75)*2*math.pi/3)
  return x**{'Quad':2,'Cubic':3,'Quart':4,'Quint':5}[kind]
 return f(t) if mode=='In' else 1-f(1-t) if mode=='Out' else f(2*t)/2 if t<.5 else 1-f(2-2*t)/2

def rawvec(x):
 while isinstance(x,dict):x=x.get('vector',x.get('post',x.get('pre')))
 if not isinstance(x,list):x=[x]*3
 assert len(x)==3,x;return x

def sample(ch,t):
 if not isinstance(ch,dict) or 'vector' in ch:return [num(v,t) for v in rawvec(ch)]
 k=sorted((float(x),y) for x,y in ch.items());assert k
 if t<=k[0][0]:return [num(v,t) for v in rawvec(k[0][1])]
 for (a,v),(b,w) in zip(k,k[1:]):
  if t<=b:
   q=ease(w.get('easing','linear') if isinstance(w,dict) else 'linear',(t-a)/(b-a));return [num(x,t)+(num(y,t)-num(x,t))*q for x,y in zip(rawvec(v),rawvec(w))]
 return [num(v,t) for v in rawvec(k[-1][1])]
def ts(t):return f'{t:.5f}'.rstrip('0').rstrip('.') or '0'
def src_clip(animations, names, bone_map, loop=False, scale=1):
 """Concatenate actual source clips; bake GeckoLib interpolators and arithmetic at 20Hz."""
 clips=[animations[n] for n in names];duration=sum(c['animation_length'] for c in clips);channels={}
 for c in clips:
  for n,chs in c.get('bones',{}).items():
   if n in bone_map:
    for ch in chs:
     if ch in ('rotation','position','scale'):channels.setdefault(n,set()).add(ch)
 out={};offset=0
 for c in clips:
  d=c['animation_length'];steps=math.ceil(d*20)
  for n,chs in channels.items():
   for ch in chs:
    values=out.setdefault(bone_map[n],{}).setdefault(ch,{})
    for k in range(steps+1):
     t=d*k/steps;source=c.get('bones',{}).get(n,{}).get(ch,[1,1,1] if ch=='scale' else [0,0,0]);v=sample(source,t)
     if ch=='position':v=[x*scale for x in v]
     values[ts(offset+t)]=[round(x,4) for x in v]
  offset+=d
 return {'loop':True if loop else 'hold_on_last_frame','animation_length':duration,'bones':out}

def source(j,name):
 g=json.loads(j.read(SRC+'geo/'+name+'.geo.json'))['minecraft:geometry'][0];a=json.loads(j.read(SRC+'animations/'+name+'.animation.json'))['animations'];return g,a

def original_anim(f,id):
 return {k.rsplit('.',1)[1]:v for k,v in json.loads(f[RP+'animations/'+id+'.animation.json'])['animations'].items()}

def bone(name,pivot,parent=None,rotation=None):
 d={'name':name,'pivot':pivot};
 if parent:d['parent']=parent
 if rotation:d['rotation']=rotation
 return d

def cube_fn(bones,atlas):
 def c(n,o,s,k='shell',r=None,p=None):bones[n].setdefault('cubes',[]).append(atlas.cube(o,s,k,r,p))
 return c

def clear_rig(g):
 bones={b['name']:copy.deepcopy(b) for b in g['bones']}
 for b in bones.values():b.pop('cubes',None)
 return bones

def module(bones,source_rig,root,attach,shift=(0,0,0),scale=1,rotation=None):
 """Keep complete source hierarchy under an independent mount. Rebase positions uniformly."""
 prefix='mm_';m={b['name']:prefix+b['name'] for b in source_rig['bones']};mount='source_mount';bones[mount]=bone(mount,list(shift),attach,rotation)
 for src in source_rig['bones']:
  b=copy.deepcopy(src);b.pop('cubes',None);b['name']=m[src['name']];b['pivot']=[x*scale+y for x,y in zip(src.get('pivot',[0,0,0]),shift)];b['parent']=m[src['parent']] if src.get('parent') else mount;bones[b['name']]=b
 def place(c,n,o,s,k='shell',r=None,p=None):
  c(m[n],[x*scale+y for x,y in zip(o,shift)],[x*scale for x in s],k,r,[x*scale+y for x,y in zip(p,shift)] if p else None)
 return m,place

def chassis(f,id,keep,atlas):
 old=json.loads(f[RP+'models/entity/'+id+'.geo.json'])['minecraft:geometry'][0];bones={}
 for b in old['bones']:
  if b['name'] in keep:
   b=copy.deepcopy(b);b.pop('cubes',None);bones[b['name']]=b
 return bones

def legs(c,bones,kind):
 if kind=='hex':
  for i,z in enumerate([-10,0,12]):
   for side,s in [('l',-1),('r',1)]:
    x=15 if i!=1 else 18;n=f'leg_{i}_{side}';f=f'foot_{i}_{side}'
    c(n,[min(s*7,s*x),12,z-2],[x-7,4,4],'joint');c(n,[s*x-3,10,z-3],[6,6,6],'shell');c(n,[s*x-2,15.5,z-2],[4,1.5,4],'plate');c(n,[s*x-1.2,12,z-3.4],[2.4,2,.6],'light')
    c(f,[s*x-2,3,z-2],[4,9,4],'dark');c(f,[s*x-2.5,4,z-2.5],[5,4,5],'shell');c(f,[s*x-3,0,z-4],[6,3,8],'plate');c(f,[s*x-2,0,z-5],[4,1,3],'dark')
 else:
  for side,x in [('l',-12),('r',12)]:
   for pos,z in [('f',-8),('b',9)]:
    n='leg_'+side+pos;c(n,[x-2.5,6,z-2.5],[5,10,5],'shell');c(n,[x-3,7,z-3],[6,3,6],'plate');c(n,[x-1.5,2,z-1.5],[3,6,3],'dark');c(n,[x-3.5,0,z-4],[7,3,8],'shell');c(n,[x-1.2,7,z-3.5],[2.4,2,.5],'light')

def corrosion(c,bone_name,positions):
 for x,y,z in positions:
  c(bone_name,[x,y,z],[2.2,1,3],'moss');c(bone_name,[x+.5,y-2,z+.3],[.8,3,1],'moss');c(bone_name,[x+1.5,y-3,z+.3],[.6,4,1],'moss')

def grid_model(f,id,g,a,atlas):
 old=original_anim(f,id)
 if id=='grid_palinode':
  keep={'root','body'}|{f'{t}_{i}_{side}' for t in ('leg','foot') for i in range(3) for side in ('l','r')};bones=chassis(f,id,keep,atlas);c=cube_fn(bones,atlas);legs(c,bones,'hex')
  c('body',[-7,11,-12],[14,6,28],'dark');c('body',[-10,15,-9],[20,5,22],'shell');c('body',[-8,20,2],[16,4,11],'plate');c('body',[-9,13,9],[18,4,7],'rust');c('body',[-2.5,18,-13],[5,2,2],'light');corrosion(c,'body',[(-8,20,6),(5,23,8)])
  m,place=module(bones,g,'root','body',(0,-7,-15),.8);p=lambda *args:place(c,*args)
  p('head',[-5,18,-6],[10,10,13],'dark');p('head',[-6,18,-13],[12,9,7],'shell');p('head',[-8,17,-17],[16,3,6],'plate');p('head',[-9,19,-16],[4,5,5],'rust');p('head',[5,19,-16],[4,5,5],'rust');p('head',[-4,21,-17],[8,2,1],'light');p('core',[-3,13,-3],[6,6,6],'light')
  for n in ('rods1','rods2','rods3'):p(n,[-1.6,9,-9],[3.2,12,4],'joint');p(n,[-2.2,11,-10],[4.4,4,5],'shell')
  clips={'idle':['idle'],'walk':['idle'],'attack0':['attack_start','attack_end'],'attack1':['attack_start','attack_end'],'death':['death']};scale=.8
 elif id=='grid_silt_engine':
  bones=chassis(f,id,{'root','body','tread_l','tread_r'},atlas);c=cube_fn(bones,atlas)
  c('body',[-12,4,-13],[24,8,30],'dark');c('body',[-10,11,-12],[20,5,28],'shell');c('body',[-10,15,8],[20,5,7],'plate');c('body',[-8,5,-17],[16,5,6],'rust');c('body',[-9,10,-18],[18,2,2],'plate');c('body',[-5,11,-19],[10,2,1],'light')
  for side,x in [('l',-19),('r',11)]:
   n='tread_'+side;c(n,[x,0,-15],[8,8,31],'dark');c(n,[x+.4,2,-13],[7.2,5,27],'joint')
   for z in range(-14,16,4):c(n,[x-.5,0,z],[9,2,2],'trim');c(n,[x-.5,6,z],[9,2,2],'shell')
  corrosion(c,'body',[(-9,16,9),(7,19,11)])
  m,place=module(bones,g,'root','body',(0,3,2),1.1);p=lambda *args:place(c,*args)
  p('head',[-7,18,-4],[14,10,9],'shell');p('head',[-5,19,-22],[10,7,20],'dark');p('head',[-6,18,-24],[12,9,4],'plate');p('head',[-3,20,-24.5],[6,5,.8],'light');p('head',[-4,27,-9],[8,2,12],'trim');p('core',[-4,12,-4],[8,8,8],'light')
  for n in ('rods1','rods2','rods3'):
   p(n,[-2.5,8,-11],[5,13,5],'rust');p(n,[-3,18,-11.5],[6,2,6],'plate');p(n,[-1.5,10,-11.7],[3,6,.6],'light')
  clips={'idle':['idle'],'walk':['idle'],'attack0':['attack_start','attack_end'],'attack1':['attack_start','attack_end'],'death':['death']};scale=1.1
 elif id=='grid_gantry_marrow':
  bones=chassis(f,id,{'root','body','leg_lf','leg_lb','leg_rf','leg_rb'},atlas);c=cube_fn(bones,atlas);legs(c,bones,'quad')
  c('body',[-11,12,-10],[22,7,21],'dark');c('body',[-12,18,-7],[24,4,15],'shell');c('body',[-9,21,3],[18,4,8],'plate');c('body',[-7,14,-12],[14,5,3],'rust');c('body',[-5,16,-13],[10,2,1],'light');corrosion(c,'body',[(-9,22,5),(5,24,7)])
  m,place=module(bones,g,'root_shared','body',(0,15,7),.78,[0,180,0]);p=lambda *args:place(c,*args)
  # The imported tail chain is an industrial five-segment lifting boom. Root motion is deliberately excluded; chassis has its own gait.
  for i,n in enumerate(['tail1','tail2','tail3','tail4','tail5']):
   pv=next(b['pivot'] for b in g['bones'] if b['name']==n);x,y,z=pv;length=[8,7,6,6,3][i]
   p(n,[x-2.1,y-2.1,z],[4.2,4.2,length],'shell');p(n,[x-2.6,y-2.6,z],[5.2,5.2,2.4],'dark');p(n,[x-.9,y+2.15,z+1],[1.8,.6,max(1,length-2)],'light')
  p('scythe',[-4,7.5,37],[8,5,5],'dark');p('scythe',[-5,4,40],[3,7,5],'plate');p('scythe',[2,4,40],[3,7,5],'plate');p('scythe',[-4,3,43],[3,2,4],'rust');p('scythe',[1,3,43],[3,2,4],'rust');p('scythe',[-2,9,42],[4,2,1],'light')
  clips={'idle':['idle'],'walk':['walk'],'attack0':['attack_single'],'attack1':['attack_tail_scythe'],'death':['death_start']};scale=.78
  m={k:v for k,v in m.items() if k in ['tailJoint','tail1','tail2','tail3','tail4','tail5','scythe']}
 else:
  # Complete Bluff rig, re-skinned as a weathered rotary induction engine.
  bones=clear_rig(g);m={n:n for n in bones};bones['pedestal']=bone('pedestal',[0,0,0]);bones['root']['parent']='pedestal';c=cube_fn(bones,atlas);scale=1
  c('pedestal',[-7,0,-7],[14,3,14],'dark');c('pedestal',[-5,3,-5],[10,8,10],'shell');c('pedestal',[-7,9,-7],[14,3,14],'rust');c('pedestal',[-6,12,-6],[12,2,12],'plate');c('pedestal',[-2,7,-6],[4,3,1],'light');corrosion(c,'pedestal',[(-5,12,3),(3,12,-3)])
  c('head',[-6,20,-6],[12,6,12],'shell');c('head',[-5,25,-5],[10,3,10],'plate');c('head',[-4,21,-6.5],[8,2,1],'light');c('head',[-2,27,-2],[4,3,4],'dark');c('core',[-3,13,-3],[6,6,6],'light');c('core',[-4,12,-4],[8,2,8],'trim');c('core',[-4,18,-4],[8,2,8],'trim')
  for n in ('rods1','rods2','rods3'):
   c(n,[-2,10,-13],[4,12,6],'dark');c(n,[-3,13,-16],[6,7,7],'shell');c(n,[-4,17,-15],[8,2,6],'plate');c(n,[-1.2,14,-16.5],[2.4,4,.7],'light');c(n,[-2,10,-14],[4,2,5],'rust')
  clips={'idle':['idle'],'walk':['idle'],'attack0':['attack_start','attack_end'],'attack1':['attack_start','attack_end'],'death':['death']}
 anim={}
 for alias,names in clips.items():
  aa=src_clip(a,names,m,alias in ('idle','walk'),scale)
  # Preserve chassis gait rather than replacing a six-legged or tracked machine with a humanoid rig.
  if id!='grid_cinder_spindle':
   for n,v in old[alias]['bones'].items():
    if n in bones and not n.startswith('mm_'):
     aa['bones'][n]=copy.deepcopy(v)
     if alias.startswith('attack') or alias=='death':
      for channel,value in aa['bones'][n].items():
       if isinstance(value,dict):
        aa['bones'][n][channel]={ts(float(t)*aa['animation_length']/old[alias]['animation_length']):vec for t,vec in value.items()}
  if id=='grid_silt_engine' and 'mm_root' in aa['bones'] and 'position' in aa['bones']['mm_root']:
   aa['bones']['mm_root']['position']={t:[v[0],round(v[1]*.30,4),v[2]] for t,v in aa['bones']['mm_root']['position'].items()}
  if alias in ('attack0','attack1') and id in ('grid_palinode','grid_silt_engine','grid_cinder_spindle'):
   # The two source-backed sequences share the authentic charge/release, but drive distinct mechanical assemblies.
   if alias=='attack0' and id=='grid_palinode':aa['bones']['mm_head']['position']={'0':[0,0,0],'0.5':[0,0,4],'0.72':[0,0,-8],'1.1':[0,0,-8],'1.6':[0,0,0],'2.7083':[0,0,0]}
   if alias=='attack1' and id=='grid_silt_engine':aa['bones']['mm_head']['rotation']={'0':[0,0,0],'0.5':[-20,0,0],'0.72':[8,0,0],'1.4':[8,0,0],'2.7083':[0,0,0]}
   if id=='grid_cinder_spindle':
    aa['bones']['pivot']={'rotation':{'0':[0,0,0],'0.7083':[0,180 if alias=='attack0' else 60,0],'2.7083':[0,720 if alias=='attack0' else 120,0]}}
  anim[alias]=aa
 return bones,anim,clips

def echo_model(f,id,g,a,atlas):
 bones=clear_rig(g);c=cube_fn(bones,atlas);m={n:n for n in bones}; scale=1
 if id=='echo_veil_regent':
  # Ceremonial, damaged humanoid with a floating tattered skirt. The right hand's actual item socket carries the staff.
  c('body',[-4.5,14,-1],[9,12,6],'dark');c('body',[-5,17,-2],[10,6,7],'shell');c('body',[-5.5,14,-2.5],[11,2,7.5],'plate');c('chest',[-7,23,-1.5],[14,8,6.5],'shell');c('chest',[-5,25,-2.2],[10,4,1.1],'plate');c('chest',[-2,25,-3],[4,4,1.2],'light');c('head',[-3.5,28.5,-6],[7,8,7],'dark');c('head',[-4.2,32,-5.8],[8.4,6,7.8],'shell');c('head',[-4.6,36,-6.1],[9.2,2.4,8],'plate');c('head',[-3.1,32,-6.5],[6.2,1.3,.7],'light');c('head',[-5.1,31,-3],[1.6,5,4],'rust');c('head',[3.5,31,-3],[1.6,5,4],'shell');c('head',[4.7,32,-3.1],[.6,2,2],'light')
  for side in ('Right','Left'):
   sign=-1 if side=='Right' else 1
   x=min(sign*8,sign*13);c('shoulder'+side,[x,26,-.4],[5,5,5],'plate' if side=='Right' else 'rust');c('shoulder'+side,[x-.4,30,0],[5.8,1,4],'trim')
   for n in ['upperArm','lowerArm']:
    b=next(v for v in g['bones'] if v['name']==n+side);o=b['cubes'][0]['origin'];s=b['cubes'][0]['size'];x,y,z=o;c(n+side,[x,y-.6,z-.6],[s[0],s[1]+1.2,s[2]+1.2],'dark');c(n+side,[x+1,y-.9,z-.9],[s[0]-2,s[1]+1.8,s[2]+1.8],'shell');c(n+side,[x+2,y-.95,z-.95],[s[0]-4,.8,s[2]+.8],'light')
   h='hand'+side;px,py,pz=bones[h]['pivot'];c(h,[px-2,py-2,pz-1.5],[4,4,3],'dark');c(h,[px-2.2,py-1,pz-2],[4.4,2,1.2],'plate')
  # New hanging robe in place of the source's seated legs, articulated via source cloth joints.
  c('body',[-5.5,7,-3.2],[11,8,7],'cloth');c('body',[-4,1,-2],[8,7,5],'dark')
  c('clothBack',[-6,1,4.7],[6,17,.9],'cloth',[0,0,5],[-3,17,4.7]);c('clothBack',[.5,4,5],[5,14,.9],'cloth',[0,0,-7],[3,17,5]);c('skirtFront',[-5,4,-3],[4,11,.8],'cloth');c('skirtFront',[.2,1.5,-3.1],[4.4,13,.8],'cloth')
  for x in [-3,2]:c('body',[x,1.5,-3.6],[1,7,.5],'trim')
  px,py,pz=bones['itemHandRight']['pivot'];n='itemHandRight';c(n,[px-1,py-18,pz-1],[2,37,2],'dark');c(n,[px-1.4,py-7,pz-1.4],[2.8,9,2.8],'trim');c(n,[px-3,py+16,pz-2],[6,3,4],'plate');c(n,[px-4,py+19,pz-2],[2,7,4],'shell');c(n,[px+2,py+19,pz-2],[2,7,4],'shell');c(n,[px-4,py+25,pz-2],[8,2,4],'plate');c(n,[px-1.6,py+19,pz-1.6],[3.2,6,3.2],'light');c(n,[px-1.5,py-19,pz-1.5],[3,2,3],'plate')
  clips={'idle':['idle'],'walk':['idle'],'attack0':['attack_right','attack_right_end'],'attack1':['attack_left','attack_left_end'],'death':['death_old']}
 elif id=='echo_rubble_rook':
  # Elokosa's night-form, deliberately an asymmetric fractured hulking humanoid with a salvage tail assembly.
  c('stomach',[-4,7,3],[8,10,6],'dark');c('stomach',[-4.5,10,3],[9,6,6.5],'shell');c('chest',[-7,12,-1],[14,11,8],'shell');c('chest',[-6,18,-2],[12,4,2],'plate');c('chest',[-2,15,-2.3],[4,4,1.2],'light');c('head',[-4.5,9.5,-11],[9,7,8],'dark');c('head',[-5,13,-10.5],[10,3.5,7],'shell');c('head',[-3.6,12,-11.5],[7.2,1.6,1],'light');c('head',[-6,11,-7],[2,4,4],'rust');c('head',[4.5,11,-7],[2,4,4],'plate');c('jaw',[-3,6,-9],[6,4,4],'trim',[-57.5,0,0],[0,11,-7]);c('jaw',[-2.4,6,-10],[4.8,2,3],'plate',[-57.5,0,0],[0,11,-7])
  for side in ['left','right']:
   s=1 if side=='left' else -1;arm=side+'Arm';fore=side+'ForeArm';hand=side+'Hand';th=side+'Thigh';calf=side+'Calf';foot=side+'Foot';toes=side+'Toes'
   for n in [arm,fore,th,foot]:
    src=next(b for b in g['bones'] if b['name']==n)['cubes'][0];o=src['origin'];sz=src['size'];r=src.get('rotation');p=src.get('pivot');c(n,[o[0]-.5,o[1]-.3,o[2]-.5],[sz[0]+1,sz[1]+.6,sz[2]+1],'dark',r,p)
    c(n,[o[0]-.8,o[1]+sz[1]*.2,o[2]-.8],[sz[0]+1.6,max(1,sz[1]*.65),sz[2]+1.6],'shell' if side=='left' else 'rust',r,p)
   x,y,z=bones[calf]['pivot'];c(calf,[x-1.4,y-4,z-1.4],[2.8,5,2.8],'joint');x,y,z=bones[hand]['pivot'];c(hand,[x-3.3,y-5,z-2.4],[6.6,6,5],'dark');c(hand,[x-4,y-2,z-2.9],[8,4,6],'plate' if side=='left' else 'shell');c(hand,[x-2.5,y-3,z-3],[5,2,1],'light')
   x,y,z=bones[toes]['pivot'];c(toes,[x-2.3,y-1.5,z-3],[4.6,2.5,5],'shell');c(toes,[x-2.6,y-1.8,z-4],[5.2,1.2,3],'plate')
  for i,n in enumerate(['tail1','tail2','tail3','tail4','tail5']):
   x,y,z=bones[n]['pivot'];length=[8,7,6,6,2.5][i];c(n,[x-1.7,y-1.7,z],[3.4,3.4,length],'joint');c(n,[x-2.2,y-2.2,z],[4.4,4.4,2.1],'rust');c(n,[x-.7,y+1.8,z+1],[1.4,.6,max(1,length-1)],'light')
  c('scythe',[-3.5,7,37],[7,5,6],'dark');c('scythe',[-4,6,40],[8,7,4],'shell');c('scythe',[-4.5,6.5,43.5],[9,6,1],'plate');c('scythe',[-2,8,44.5],[4,2,.8],'light')
  c('chest',[-7,14,5],[6,10,1],'cloth',[0,0,-7],[-4,24,5]);c('stomach',[1,5,8],[5,8,1],'cloth',[0,0,8],[3,13,8]);
  clips={'idle':['idle'],'walk':['walk'],'attack0':['attack_combo'],'attack1':['attack_tail_scythe'],'death':['death_start']}
 else:
  # Hush is tall and shrouded, with one load-bearing arm and a physical counterweight weapon.
  c('hips',[-4.2,10,-1.5],[8.4,5,6],'dark');c('hips',[-5,11,-2],[10,3,7],'shell');c('stomach',[-3.4,13.5,-1.5],[6.8,10,5],'dark');c('stomach',[-4.4,17,-2.5],[8.8,5.5,6],'shell');c('stomach',[-2,17,-3],[4,3,1],'light');c('chest',[-5,21,-2],[10,7,6],'shell');c('chest',[-5.5,25,-2.5],[11,3,7],'plate');c('chest',[-2,22,-3],[4,4,1],'light');c('neck',[-1.6,27,-.5],[3.2,6,3],'dark')
  c('head',[-3.5,30.5,-2.5],[7,7,7],'dark');c('head',[-4.2,34,-3],[8.4,4.5,8],'shell');c('head',[-3.8,32,-3.5],[7.6,2.5,1],'dark');c('head',[-2.8,32.8,-4],[5.6,.75,.6],'light');c('head',[-4.8,31,-1],[1.6,6,5],'cloth');c('head',[3.2,31,-1],[1.6,6,5],'cloth');c('head',[-4.8,37,-2],[9.6,2,7],'cloth');c('head',[-2.8,25,4],[3.2,11,1],'cloth',[0,0,12],[-1.2,36,4]);c('mane',[-6,25,2],[12,3,4],'cloth')
  c('feathersBack1',[-5,14,5],[10,14,1],'cloth');c('feathersBack2',[-5,8,5.2],[5,14,1],'cloth',[0,0,8],[-2.5,22,5]);c('feathersBack3',[1,11,5.4],[4,13,1],'cloth',[0,0,-9],[3,24,5])
  for side,x in [('right',-3.5),('left',3.5)]:
   c(side+'Shoulder',[x-2.1,16,-1.3],[4.2,10,4.4],'dark');c(side+'Shoulder',[x-3,23,-2],[6,4,6],'plate' if side=='right' else 'rust');c(side+'ForeArm',[x-1.8,4,-1],[3.6,10,4],'joint');c(side+'ForeArm',[x-2.4,6,-2],[4.8,7,5],'shell');c(side+'ForeArm',[x-1.3,8,-2.6],[2.6,4,1],'light');c(side+'Hand',[x-1.8,1,-.5],[3.6,4,3],'dark')
  for side,x in [('right',-3),('left',3)]:
   c(side+'Thigh',[x-2,10,-2.8],[4,5,4],'shell');c(side+'Shin',[x-1.4,5,-2],[2.8,5,3],'dark');c(side+'Shin',[x-2,7,-2.7],[4,4,3],'plate');c(side+'Ankle',[x-1.3,4.1,-8.75],[2.6,2,8],'dark');c(side+'Ankle',[x-1.8,3.7,-6.5],[3.6,3,5],'shell');c(side+'ToesFront',[x-2.5,5.1,-8.75],[5,4,4],'shell',[180,0,0],[x,7.1,-6.75]);c(side+'ToesBack',[x-1.5,4.5,-8],[3,2,3],'dark')
  # Hinged weight follows the original weapon wrist rather than floating independently.
  n='rightHand';c(n,[-4.4,-5,-.8],[1.8,9,2],'joint');c(n,[-5,-6,-1.5],[3,2,3],'plate');bones['pendulum_chain']=bone('pendulum_chain',[-3.5,-5,0],n);c('pendulum_chain',[-4,-14,-.5],[1,9,1],'dark');
  for y in range(-13,-5,2):c('pendulum_chain',[-4.6,y,-1],[2.2,1.5,2],'trim')
  bones['pendulum_weight']=bone('pendulum_weight',[-3.5,-14,0],'pendulum_chain');c('pendulum_weight',[-6.5,-20,-3],[6,6,6],'dark');c('pendulum_weight',[-7,-19,-2.7],[7,4,5.4],'plate');c('pendulum_weight',[-5.7,-18,-3.3],[4.4,2.5,.8],'light');c('pendulum_weight',[-5.5,-21,-2],[4,1.5,4],'rust')
  clips={'idle':['idle_aggressive'],'walk':['walk_aggressive'],'attack0':['attack_slash_right'],'attack1':['block_counter'],'death':['die']}
 anim={}
 for alias,names in clips.items():
  aa=src_clip(a,names,m,alias in ('idle','walk'),scale)
  if id=='echo_veil_regent' and alias in ('idle','walk'):
   # The source Sculptor's idle movement is Java-procedural. Supply a restrained hover/robe motion.
   aa['bones']['root']={'position':{'0':[0,0,0],'2':[0,.6,0],'4':[0,0,0],'6':[0,.6,0],'8':[0,0,0]}}
   aa['bones']['clothBack']={'rotation':{'0':[0,0,-2],'4':[3,0,2],'8':[0,0,-2]}}
  if id=='echo_hush_pendulum':
   aa['bones']['pendulum_chain']={'rotation':{'0':[0,0,0],ts(aa['animation_length']*.35):[25,0,-20] if alias.startswith('attack') else [3,0,3],ts(aa['animation_length']*.65):[-32,0,30] if alias.startswith('attack') else [-3,0,-3],ts(aa['animation_length']):[0,0,0]}}
  anim[alias]=aa
 return bones,anim,clips

def reward(f,id,accent):
 p=RP+'models/entity/held_'+id+'.geo.json';g=json.loads(f[p]);geo=g['minecraft:geometry'][0];at=Atlas(accent,True);grip=copy.deepcopy(geo['bones'][0]);grip['cubes']=[];bones={'grip':grip};c=cube_fn(bones,at)
 def shaft(length=14):
  c('grip',[-1,14,-7],[2,length,2],'dark');c('grip',[-1.5,13,-7.5],[3,2,3],'plate');c('grip',[-1.5,19,-7.5],[3,2,3],'trim')
  for y in range(15, min(24,14+length),3):c('grip',[-1.25,y,-7.25],[2.5,1.2,2.5],'joint')
 if id=='palinode_ram':
  shaft(17);c('grip',[-3,26,-9],[6,6,6],'dark');c('grip',[-6,29,-10],[12,7,8],'shell');c('grip',[-7,30,-9],[2,5,6],'plate');c('grip',[5,30,-9],[2,5,6],'plate');c('grip',[-4,31,-10.5],[8,3,1],'light');c('grip',[-4,36,-8],[8,1.2,4],'trim');c('grip',[-3,28,-8],[6,2,4],'rust')
 elif id=='silt_discharge':
  shaft(17);c('grip',[-4,27,-8.5],[8,4,5],'shell');c('grip',[-3.8,31,-7.5],[2.2,13,3],'blade');c('grip',[1.6,31,-7.5],[2.2,13,3],'blade');c('grip',[-3.1,32,-8],[.9,11,.7],'light');c('grip',[2.2,32,-8],[.9,11,.7],'light');c('grip',[-1.5,31,-7],[3,7,2],'dark');c('grip',[-1,33,-7.5],[2,4,.7],'light');c('grip',[-4,43,-7.2],[2.6,2.2,2.4],'plate');c('grip',[1.4,43,-7.2],[2.6,2.2,2.4],'plate')
 elif id=='gantry_rake':
  shaft(20);c('grip',[-3,31,-8],[6,5,4],'shell');c('grip',[-2.5,34,-8],[5,10,4],'dark');c('grip',[-1.7,42,-8],[9,3.5,4],'plate');c('grip',[4.5,35,-8],[3,8,4],'blade');c('grip',[1.8,34,-8],[5,2.5,4],'blade');c('grip',[-1,35,-8.4],[2,7,.6],'light');c('grip',[2,42,-8.4],[4,1.2,.6],'light')
 elif id=='cinder_inductor':
  shaft(13);c('grip',[-3,25,-8],[6,4,4],'dark');c('grip',[-3,29,-7.5],[6,9,3],'shell');c('grip',[-4,33,-7.5],[8,10,3],'blade');c('grip',[-2,31,-8],[4,10,1],'light');c('grip',[-3,39,-8],[6,5,3],'blade')
  for y in [30,34,38,42]:c('grip',[3.8,y,-7.6],[2.5,2.1,3.2],'plate', [0,0,-20],[4.5,y+1,-6]);c('grip',[-5.8,y,-7.6],[2.5,2.1,3.2],'plate',[0,0,20],[-4.5,y+1,-6])
 elif id=='veil_anchor':
  shaft(24);c('grip',[-3,36,-8],[6,3,4],'shell');c('grip',[-4,39,-8],[2,7,4],'plate');c('grip',[2,39,-8],[2,7,4],'plate');c('grip',[-4,45,-8],[8,2,4],'plate');c('grip',[-1.5,39,-7.5],[3,6,3],'light');c('grip',[-1,34,-7.7],[2,4,.7],'light')
 elif id=='rook_hammer':
  shaft(17);c('grip',[-3,27,-8],[6,6,4],'dark');c('grip',[-7,30,-10],[14,8,8],'shell');c('grip',[-8,29,-9],[3,10,6],'plate');c('grip',[5,29,-9],[3,10,6],'rust');c('grip',[-4,31,-10.5],[8,5,1],'dark');c('grip',[-3,32,-11],[6,3,.7],'light');c('grip',[-5,38,-8],[10,1.5,4],'trim')
 else:
  shaft(12);c('grip',[-2,24,-8],[4,3,4],'plate');bones['chain_0']=bone('chain_0',[0,27,-6],'grip');bones['chain_1']=bone('chain_1',[0,32,-6],'chain_0');bones['chain_2']=bone('chain_2',[0,37,-6],'chain_1')
  for i in range(3):
   y=27+5*i;n='chain_'+str(i);c(n,[-.65,y,-6.65],[1.3,5,1.3],'dark');c(n,[-1.4,y+1,-7.4],[2.8,2,2.8],'trim')
  n='chain_2';c(n,[-3.8,40,-9.8],[7.6,6.5,7.6],'dark');c(n,[-4.3,41,-9],[8.6,4.5,6],'plate');c(n,[-2.5,42,-10.1],[5,2.5,.8],'light');c(n,[-3,46,-9],[6,1.4,6],'rust')
 geo['bones']=list(bones.values());geo['description'].update(texture_width=256,texture_height=256,visible_bounds_height=5,visible_bounds_width=5);f[p]=enc(g)
 ap=RP+'attachables/'+id+'.json';ad=json.loads(f[ap]);d=ad['minecraft:attachable']['description'];d['animations'].pop('energy',None);d['scripts']['animate']=[x for x in d['scripts']['animate'] if x!='energy']
 # Existing flail animation references more chain bones than this compact rig; author a matching animation.
 if id=='hush_pendulum':
  animp=RP+'animations/bearframe.held_gear.animation.json';a=json.loads(f[animp]);key=d['animations']['whip'];a['animations'][key]={'loop':True,'bones':{n:{'rotation':[f'variable.bearframe_flail_swing * {24-i*5}',0,0]} for i,n in enumerate(['chain_0','chain_1','chain_2'])}};f[animp]=enc(a)
 f[ap]=enc(ad);f[RP+d['textures']['default']+'.png']=png(at.im)
 # Pixel icons, matching distinct silhouettes, shaded using per-weapon accent.
 im=Image.new('RGBA',(16,16));draw=ImageDraw.Draw(im);light=tuple(accent);edge=(192,194,185);dark=(50,55,59);mid=(114,123,121)
 draw.line([(2,14),(10,6)],fill=dark,width=3);draw.line([(3,13),(9,7)],fill=mid,width=1)
 if id in ('palinode_ram','rook_hammer'):
  draw.polygon([(7,3),(10,0),(15,5),(12,9)],fill=mid);draw.line([(7,3),(10,0),(15,5)],fill=edge,width=2);draw.line([(9,3),(12,6)],fill=light,width=2)
 elif id=='silt_discharge':
  draw.line([(8,7),(13,1)],fill=edge,width=2);draw.line([(10,9),(15,3)],fill=edge,width=2);draw.line([(9,7),(14,2)],fill=light);draw.line([(7,6),(11,10)],fill=mid,width=2)
 elif id=='gantry_rake':
  draw.line([(8,8),(13,2),(15,4),(12,7)],fill=edge,width=2);draw.line([(10,6),(13,3)],fill=light);draw.line([(7,6),(11,10)],fill=mid,width=2)
 elif id=='cinder_inductor':
  draw.polygon([(7,6),(11,0),(15,3),(15,6),(10,11)],fill=edge);draw.line([(9,7),(13,3)],fill=light,width=2);draw.line([(11,0),(12,2),(14,1),(15,3)],fill=mid,width=1)
 elif id=='veil_anchor':
  draw.polygon([(9,3),(12,0),(15,3),(12,6)],outline=edge,fill=dark);draw.polygon([(12,1),(14,3),(12,5),(10,3)],fill=light);draw.line([(8,6),(11,9)],fill=mid,width=2)
 else:
  draw.line([(8,8),(10,6),(12,7),(14,5)],fill=edge,width=1);draw.rectangle([11,1,15,5],fill=mid,outline=edge);draw.point((13,3),fill=light)
 item=json.loads(f[BP+'items/'+id+'.json'])['minecraft:item'];tex=json.loads(f[RP+'textures/item_texture.json'])['texture_data'][item['components']['minecraft:icon']]['textures'];f[RP+tex+'.png']=png(im)

# Build first: preserve existing attack damage/range/campaign semantics while aligning attack event windows to the source clips.
# Exact Mowzie multi-stage Java AI, Frostmaw/Wroughtnaut procedural rigs and projectile mechanics remain a later pass.
TIMINGS={
 'grid_palinode':[(14,55),(14,55)], 'grid_silt_engine':[(14,55),(14,55)], 'grid_gantry_marrow':[(13,40),(9,32)], 'grid_cinder_spindle':[(14,55),(14,55)],
 'echo_veil_regent':[(12,32),(12,32)], 'echo_rubble_rook':[(12,55),(9,32)], 'echo_hush_pendulum':[(13,39),(14,36)]}

def build(base,jar,out):
 with zipfile.ZipFile(base) as z:assert z.testzip() is None;old={n:z.read(n) for n in z.namelist()}
 assert hashlib.sha256(Path(jar).read_bytes()).hexdigest()=='e8ce1768cda6f1e1fadd2321c92921b473bd0cee45ba4b8387fb30f8326cb31c';f=old.copy();summary={}
 with zipfile.ZipFile(jar) as j:
  p=BP+'scripts/boss_moves.js';s=f[p].decode();moves=json.loads(s[s.index('{'):s.rindex('}')+1])
  for id,(src,drop,accent) in BOSSES.items():
   g,a=source(j,src);at=Atlas(accent,id.startswith('echo_'));bones,animations,clips=(grid_model if id.startswith('grid_') else echo_model)(f,id,g,a,at)
   desc=copy.deepcopy(g['description']);desc.update(identifier='geometry.bearframe.'+id,texture_width=256,texture_height=256,visible_bounds_width=10,visible_bounds_height=8,visible_bounds_offset=[0,2,0]);f[RP+'models/entity/'+id+'.geo.json']=enc({'format_version':'1.12.0','minecraft:geometry':[{'description':desc,'bones':list(bones.values())}]});f[RP+'textures/bearframe/'+id+'.png']=png(at.im)
   # Animate visible geometry and its ancestor bones; preserve the complete hierarchy for future source mechanics.
   visible={n for n,b in bones.items() if b.get('cubes')}; todo=list(visible)
   while todo:
    parent=bones[todo.pop()].get('parent')
    if parent and parent not in visible:visible.add(parent);todo.append(parent)
   for aa in animations.values():
    aa['bones']={n:ch for n,ch in aa['bones'].items() if n in visible}
   f[RP+'animations/'+id+'.animation.json']=(json.dumps({'format_version':'1.8.0','animations':{'animation.bearframe.'+id+'.'+k:v for k,v in animations.items()}},separators=(',',':'),allow_nan=False)+'\n').encode()
   for i,(wind,end) in enumerate(TIMINGS[id]):
    mv=moves['bearframe:'+id][i];mv.update(windup=wind,end=max(end,math.ceil(animations['attack'+str(i)]['animation_length']*20)));mv['sourceRig']=src
   # Rubble Rook's imported combo has a second distinct strike; hit window follows source combo, not every tick.
   if id=='echo_rubble_rook':moves['bearframe:'+id][0]['extraHits']=[24];moves['bearframe:'+id][0]['damage']=7
   # Keep damage/collision broadly compatible with prior encounter arenas. Align movement range only for close-range Echo.
   if id=='echo_hush_pendulum':
    ep=BP+'entities/'+id+'.json';e=json.loads(f[ep]);e['minecraft:entity']['components']['minecraft:behavior.move_towards_target']['within_radius']=2.3;f[ep]=enc(e)
   reward(f,drop,accent)
   summary[id]={'source':src,'source_bones':len(g['bones']),'installed_bones':len(bones),'visible_cubes':at.n,'clips':clips,'attack_ticks':[(v['windup'],v['end']) for v in moves['bearframe:'+id]]}
  f[p]=('// Generated from the source-backed 0.11.24 roster build.\nexport const BOSS_MOVES = '+json.dumps(moves,indent=2)+';\n').encode()
 # Add bounded combo hit windows and per-faction impact particles. Preserve the pilot slash branch, defeat credit and HUD.
 p=BP+'scripts/boss_combat.js';s=f[p].decode();target='    if (elapsed < strike.move.windup && elapsed % 8 === 2) showWarning(entity, strike);';assert s.count(target)==1
 s=s.replace(target,'''    for (const hitTick of strike.move.extraHits ?? []) {
      strike.extraReleased ??= new Set();
      if (elapsed >= hitTick && elapsed < hitTick + 4 && !strike.extraReleased.has(hitTick)) {
        strike.extraReleased.add(hitTick);
        release(entity, {...strike, origin: entity.location, move: {...strike.move, drive: 0}}, players);
      }
    }
'''+target)
 # Keep warning geometry but use one cheap, faction-coloured impact burst at the impact origin.
 target='  dimension.playSound("random.anvil_land", origin, { volume: .55, pitch: move.shape === "mark" ? 1.5 : .76 });';assert s.count(target)==1
 s=s.replace(target,target+'''\n  if (move.sourceRig) {
    const impact = move.shape === "mark" ? strike.mark : {x: origin.x + direction.x * Math.min(move.radius, 2), y: origin.y + .5, z: origin.z + direction.z * Math.min(move.radius, 2)};
    if (dimension.isChunkLoaded(impact) && clearPath(dimension, source, height(impact, .1))) {
      try { dimension.spawnParticle("bearframe:" + entity.typeId.split(":")[1] + "_impact", impact); } catch {}
    }
  }''');f[p]=s.encode()
 # Local custom impact texture and component-only particles; no external particle textures.
 tex=Image.new('RGBA',(16,16));d=ImageDraw.Draw(tex);d.polygon([(8,0),(10,6),(16,8),(10,10),(8,16),(6,10),(0,8),(6,6)],fill=(255,255,255,255));f[RP+'textures/particle/bearframe_boss_spark.png']=png(tex)
 for id,(_,_,accent) in BOSSES.items():
  part={'format_version':'1.10.0','particle_effect':{'description':{'identifier':'bearframe:'+id+'_impact','basic_render_parameters':{'material':'particles_alpha','texture':'textures/particle/bearframe_boss_spark'}},'components':{'minecraft:emitter_rate_instant':{'num_particles':12},'minecraft:emitter_lifetime_once':{'active_time':.1},'minecraft:emitter_shape_sphere':{'radius':.6,'direction':'outwards'},'minecraft:particle_lifetime_expression':{'max_lifetime':.45},'minecraft:particle_initial_speed':3,'minecraft:particle_motion_dynamic':{'linear_acceleration':[0,-5,0],'linear_drag_coefficient':2},'minecraft:particle_appearance_billboard':{'size':[.19,.19],'facing_camera_mode':'lookat_xyz','uv':{'texture_width':16,'texture_height':16,'uv':[0,0],'uv_size':[16,16]}},'minecraft:particle_appearance_tinting':{'color':[*(round(v/255,4) for v in accent),1]}}}}
  f[RP+'particles/'+id+'_impact.json']=enc(part)
 for prefix in (BP,RP):
  p=prefix+'manifest.json';m=json.loads(f[p]);assert m['header']['version']==[0,11,23];m['header']['version']=VERSION
  for mod in m['modules']:mod['version']=VERSION
  for dep in m.get('dependencies',[]):
   if dep.get('version')==[0,11,23]:dep['version']=VERSION
  f[p]=enc(m)
 changed=[n for n in f if f[n]!=old.get(n)];assert all(f[n]==old[n] for n in old if n.endswith('.mcstructure') or 'loot_tables/' in n)
 for n in changed:
  if n.endswith('.json'):json.loads(f[n])
  if n.endswith('.js'):subprocess.run(['node','--input-type=module','--check'],input=f[n],check=True)
 for id,(_,drop,_) in BOSSES.items():
  geo=json.loads(f[RP+'models/entity/'+id+'.geo.json'])['minecraft:geometry'][0];names={b['name'] for b in geo['bones']};assert len(names)==len(geo['bones']);assert all(b.get('parent') in names or 'parent' not in b for b in geo['bones']);anim=json.loads(f[RP+'animations/'+id+'.animation.json'])['animations'];assert len(anim)==5;assert all(set(a['bones'])<=names for a in anim.values());
  d=json.loads(f[RP+'entity/'+id+'.entity.json'])['minecraft:client_entity']['description'];assert d['geometry']['default']==geo['description']['identifier'];assert all(d['animations'][k] in anim for k in ('idle','walk','attack0','attack1','death'))
  assert f[BP+'loot_tables/entities/boss_'+id+'.json']==old[BP+'loot_tables/entities/boss_'+id+'.json']
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in sorted(f.items()):z.writestr(n,b)
 with zipfile.ZipFile(out) as z:assert z.testzip() is None;assert all(z.read(n)==b for n,b in f.items())
 summary['seam_riven']='0.11.23 pilot unchanged';summary['validation']={'files':len(f),'changed':len(changed),'structures_unchanged':sum(n.endswith('.mcstructure') for n in old),'loot_tables_unchanged':sum('loot_tables/' in n for n in old),'nonfinite_source_expression_repairs':dict(REPAIRS),'sha256':hashlib.sha256(Path(out).read_bytes()).hexdigest()}
 print(json.dumps(summary,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('base',type=Path);p.add_argument('jar',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(a.base,a.jar,a.out)
