"""Reference-directed boss geometry and texture pass. Retargets existing animation poses to new articulated visual rigs; leaves old source skeletons as non-rendering reference tracks."""
import argparse, math, json, zipfile, io, hashlib, random, re, ast
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
from scipy.spatial.transform import Rotation
BP='Bearframe_Behavior/'; RP='Bearframe_Resources/'
IDS=['echo_seam_riven','echo_veil_regent','echo_rubble_rook','echo_hush_pendulum','grid_palinode','grid_silt_engine','grid_gantry_marrow','grid_cinder_spindle']
COLORS=[(48,225,240),(182,87,248),(193,95,241),(244,167,49),(87,222,198),(71,164,226),(130,211,170),(255,144,48)]
FACE=['north','south','west','east','up','down']
def enc(x):return (json.dumps(x,indent=2,allow_nan=False,default=lambda v:v.item())+'\n').encode()
def png(im):b=io.BytesIO();im.save(b,format='PNG');return b.getvalue()
def rgb(c,d=0):return tuple(max(0,min(255,int(v+d))) for v in c)
class Art:
 def __init__(self,accent,echo,seed):
  self.accent=accent;self.echo=echo;self.rng=random.Random(seed);self.img=Image.new('RGBA',(512,512));self.tiles={};self.n=0
  self.pal={'ivory':(200,191,173),'steel':(128,132,126),'dark':(38,42,46),'joint':(78,80,77),'rust':(130,78,45),'moss':(94,119,48),'cloth':(103,49,65) if echo else (76,70,58),'purple':(87,53,110),'light':accent,'blade':(154,165,166),'trim':(100,86,67),'black':(19,22,27),'copper':(151,104,62)}
 def tile(self,kind,face,variant):
  key=kind,face,variant
  if key in self.tiles:return self.tiles[key]
  assert self.n<256
  u,v=(self.n%16)*32,(self.n//16)*32;self.n+=1
  rng=self.rng; im=Image.new('RGBA',(32,32));d=ImageDraw.Draw(im);base=self.pal[kind];side={'up':16,'down':-27,'west':-9,'east':-2,'north':3,'south':-5}[face];c=rgb(base,side)
  d.rectangle((0,0,31,31),fill=c)
  if kind in ('ivory','steel','blade','trim'):
   for k in range(58):
    x,y=rng.randrange(32),rng.randrange(32);s=rng.choice([1,1,2,3]);d.rectangle((x,y,min(31,x+s),min(31,y+rng.randrange(1,3))),fill=rgb(c,rng.choice([-19,-9,8,13])))
   d.line((0,0,31,0),fill=rgb(c,38),width=2);d.line((0,0,0,31),fill=rgb(c,22));d.line((0,31,31,31),fill=rgb(c,-44),width=2);d.line((31,0,31,31),fill=rgb(c,-32))
   # Chipped enamel and corrosion concentrate around edges, not random confetti.
   for k in range(8):
    x=rng.randrange(32);y=rng.choice([0,1,2,28,29,30]);ww=rng.randrange(1,5);hh=rng.randrange(1,4);d.rectangle((x,y,min(31,x+ww),min(31,y+hh)),fill=rgb(self.pal['rust'],rng.randint(-15,18)));d.point((x,y),fill=rgb(c,-52))
   for x,y in [(3,3),(27,3),(3,27),(27,27)]:d.rectangle((x,y,x+2,y+2),fill=rgb(c,-70));d.point((x,y),fill=rgb(c,30))
   if variant%2==0:
    x=rng.randrange(7,23);d.line([(x,3),(x-2,9),(x+1,13),(x-1,19)],fill=rgb(c,-64),width=1);d.line([(x+1,4),(x-1,9),(x+2,13)],fill=rgb(c,24),width=1)
  elif kind in ('dark','joint','black','rust','copper'):
   for y in range(0,32,5):d.line((0,y,31,y),fill=rgb(c,-15));d.line((1,y+1,30,y+1),fill=rgb(c,12))
   for k in range(30):x,y=rng.randrange(32),rng.randrange(32);d.point((x,y),fill=rgb(c,rng.randint(-12,17)))
   d.line((1,1,1,30),fill=rgb(c,25),width=2);d.line((30,0,30,31),fill=rgb(c,-18))
  elif kind in ('cloth','purple'):
   for x in range(32):
    delta=int(10*math.sin(x*.6)+5*math.sin(x*1.7));d.line((x,0,x,31),fill=rgb(c,delta))
   for j in range(55):x,y=rng.randrange(32),rng.randrange(32);d.point((x,y),fill=rgb(c,rng.randint(-14,20)))
   if face in ('north','south','east','west'):
    # ragged lower edge, small actual alpha cutouts
    for x in range(32):
     if rng.random()<.45:
      y=32-rng.randint(1,7);d.line((x,y,x,31),fill=(0,0,0,0))
    for x,y in [(5,23),(21,12),(26,26)]:d.rectangle((x,y,x+rng.randint(1,3),y+rng.randint(1,4)),fill=(0,0,0,0))
    if variant==2:
     d.ellipse((10,9,22,21),outline=(177,152,129,255),width=2);d.line((16,5,16,25),fill=(177,152,129,255));d.line((6,15,26,15),fill=(177,152,129,255))
   d.line((0,0,31,0),fill=rgb(c,15))
  elif kind=='moss':
   for k in range(85):x,y=rng.randrange(32),rng.randrange(32);d.rectangle((x,y,min(x+2,31),min(y+2,31)),fill=rgb(c,rng.randint(-27,32)))
  elif kind=='light':
   d.rectangle((0,0,31,31),fill=rgb(base,-80));d.rectangle((2,2,29,29),fill=rgb(base,-24));d.rectangle((5,5,26,26),fill=rgb(base,22));d.rectangle((8,8,23,23),fill=rgb(base,54));d.line((3,3,28,3),fill=rgb(base,40));
   if variant%2: 
    for y in (10,20):d.line((3,y,28,y),fill=rgb(base,-65),width=2)
  self.img.paste(im,(u,v));self.tiles[key]=[u,v];return [u,v]
 def uv(self,kind,variant=0):
  uv={f:{'uv':self.tile(kind,f,variant%3),'uv_size':[32,32]} for f in FACE}
  if kind in ('cloth','purple'):
   u,v=uv['north']['uv'];uv['south']={'uv':[u+32,v],'uv_size':[-32,32]}
  return uv
class Model:
 def __init__(self,g,art):
  self.g=g;self.a=art;self.old={b['name']:b for b in g['bones']};self.b={};self.map={};self.modes={};self.aux={}
  for b in g['bones']:b.pop('cubes',None)
 def bone(self,n,p,parent=None,source=None,mode='full'):
  n='bfv_'+n;d={'name':n,'pivot':list(p)}
  if parent:d['parent']='bfv_'+parent
  self.g['bones'].append(d);self.b[n[4:]]=d
  if source:
   assert source in self.old,source;self.map[n]=source;self.modes[n]=mode
  return n
 def c(self,n,o,s,k='ivory',r=None,p=None,v=0):
  assert min(s)>0; d={'origin':[round(x,4) for x in o],'size':[round(x,4) for x in s],'uv':self.a.uv(k,v)}
  if r is not None:d.update(rotation=list(r),pivot=list(p if p is not None else [o[i]+s[i]/2 for i in range(3)]))
  self.b[n].setdefault('cubes',[]).append(d)
 def bar(self,n,a,b,w,kind='dark',depth=None,v=0):
  a=np.array(a,dtype=float);b=np.array(b,dtype=float);delta=b-a;l=np.linalg.norm(delta);assert l>0;direction=delta/l
  rot=Rotation.align_vectors([direction],[[0,1,0]])[0].as_euler('xyz',degrees=True);center=(a+b)/2;dp=w if depth is None else depth
  self.c(n,[center[0]-w/2,center[1]-l/2,center[2]-dp/2],[w,l,dp],kind,rot,center,v)
 def ring(self,n,x,y,z,r,kind='ivory',start=-160,end=160,segments=10,w=1.9):
  # Segmented ring in x/y plane. Substructure with separated casing and recessed optical strips.
  for i in range(segments):
   a=math.radians(start+(end-start)*i/segments);b=math.radians(start+(end-start)*(i+1)/segments);p=(x+r*math.sin(a),y+r*math.cos(a),z);q=(x+r*math.sin(b),y+r*math.cos(b),z)
   self.bar(n,p,q,w,'dark',w*1.2)
   aa=math.radians(start+(end-start)*(i+.11)/segments);bb=math.radians(start+(end-start)*(i+.89)/segments);p=(x+r*math.sin(aa),y+r*math.cos(aa),z-.1);q=(x+r*math.sin(bb),y+r*math.cos(bb),z-.1)
   self.bar(n,p,q,w+.55,kind,w*.85,v=i%3)
   if i%2==0:
    p=(p[0],p[1],z-w*.64);q=(q[0],q[1],z-w*.64);self.bar(n,p,q,w*.43,'light',.34)
 def vine(self,n,x,y,z,length,side=1):
  self.c(n,[x-1,y,z-1],[2.3,.6,2.2],'moss',v=1)
  for i in range(length):
   if i%2==0:self.c(n,[x+side*(i%3)*.32,y-i-.4,z-.4],[.55,1.2,.55],'moss',v=i%3)
   if i%3==0:self.c(n,[x+side*.65-.45,y-i-.6,z-.5],[1.2,.8,.45],'moss',v=2)
 def plate(self,n,x,y,z,w,h,d,kind='ivory',angle=0,v=0):
  self.c(n,[x-w/2,y-h/2,z-d/2],[w,h,d],kind,[0,0,angle] if angle else None,[x,y,z],v=v)
 def drape(self,n,x,top,z,w,h,kind='cloth',slant=0,v=2):
  self.c(n,[x-w/2,top-h,z],[w,h,.24],kind,[0,0,slant],[x,top,z],v=v)
  # asymmetrical strips with deliberately different lengths and orientations
  self.c(n,[x-w*.45,top-h*1.16,z+.03],[w*.22,h*.6,.21],kind,[0,0,slant-3],[x-w*.3,top-h*.55,z],v=1)
  self.c(n,[x+w*.18,top-h*.83,z-.02],[w*.25,h*.65,.22],kind,[0,0,slant+5],[x+w*.3,top-h*.35,z],v=0)

def humanoid(m,id):
 rook=id=='echo_rubble_rook';veil=id=='echo_veil_regent';hush=id=='echo_hush_pendulum';um=not(rook or veil)
 # Tall neutral retarget pose; source articulation remains in the archive. Rook is a low, long-armed damaged variant.
 H=46 if not rook else 35;hip=23 if not rook else 18;chest=34 if not rook else 26;head=42 if not rook else 29;sh=5.5 if not rook else 8.0;arm=10 if not rook else 12;leg=10 if not rook else 7.5;fz=-1.1 if not rook else -5.0;cz=0 if not rook else -2.5
 source={'root':'root','pelvis':'hips' if um else 'body' if veil else 'CoM','spine':'stomach' if not veil else 'body','chest':'chest','head':'head'}
 for n,p,parent in [('root',(0,0,0),None),('pelvis',(0,hip,0),'root'),('spine',(0,hip+3,cz),'pelvis'),('chest',(0,chest-5,cz),'spine'),('head',(0,head-4,fz),'chest')]:m.bone(n,p,parent,source[n],mode='root' if n=='root' else 'full')
 c=m.c; bar=m.bar; plate=m.plate
 # Mechanical pelvis and spine; gaps in ribcage reveal central cable/actuator.
 c('pelvis',[-3.8,hip-2,-2.1],[7.6,4.3,4.2],'dark');c('pelvis',[-4.6,hip-.8,-2.9],[9.2,2,5.1],'joint');c('pelvis',[-2.4,hip-2.8,-2.5],[4.8,2.4,1.1],'trim');
 for s in (-1,1):
  plate('pelvis',s*4.1,hip-.6,-2.9,2.8,4.4,1.2,angle=s*20,v=(s+1)%3)
  bar('spine',(s*1.45,hip+.5,cz-.2),(s*1.45,chest-4,cz-.2),1,'joint',1.4)
  bar('spine',(s*2.6,hip+1,cz+.7),(s*3.1,chest-3,cz+.7),.65,'copper')
 c('spine',[-1.25,hip+1,cz-.9],[2.5,chest-hip-3,2.5],'dark')
 for y in np.arange(hip+2,chest-3,2):c('spine',[-1.65,y,cz-1.5],[3.3,.9,3.2],'joint');c('spine',[-.7,y+.05,cz-1.7],[1.4,.65,.3],'light')
 c('chest',[-4.1,chest-5,cz-2.2],[8.2,7.5,4.8],'dark')
 for s in (-1,1):
  for y in (chest-3,chest-.7,chest+1.3):bar('chest',(s*1.7,y,cz-2.65),(s*4.5,y+.8,cz-1.0),1.0,'joint',.9)
  plate('chest',s*3.1,chest+1.7,cz-2.5,4.5,2.7,1.3,angle=-s*15,v=1)
  plate('chest',s*3.85,chest-2.0,cz-2.5,2.25,4.2,1.1,angle=s*13,v=0)
  bar('chest',(s*4.2,chest-3,cz+1.8),(s*2.2,chest-5,cz-1.5),.65,'copper')
 c('chest',[-2.25,chest-2.25,cz-3.1],[4.5,4.5,1.1],'joint');c('chest',[-1.6,chest-1.6,cz-3.75],[3.2,3.2,.8],'light',v=1)
 for a in range(0,360,90):rad=math.radians(a);plate('chest',math.cos(rad)*2.25,chest+math.sin(rad)*2.25,cz-3.5,1.15,2,.75,'ivory',a+90,v=2)
 bar('head',(0,chest+2.1,cz),(0,head-2.2,fz),2.1,'joint',2.2)
 # head shape: narrow fragmented faceplate, recess and offset brow; mask variants from reference.
 c('head',[-2.55,head-3.5,fz-1.7],[5.1,6.6,4.4],'black');c('head',[-2.8,head+1.5,fz-2.4],[5.6,1.9,4.7],'ivory',v=2)
 if hush or veil:
  for s in (-1,1):plate('head',s*2.5,head+.5,fz-2.35,1.8,5.3,2.3,'ivory',-s*18,1);m.drape('head',s*3.3,head+2.7,fz+.5,1.8,8,'purple' if veil else 'cloth',s*6,0)
  c('head',[-1.75,head-2.7,fz-2.55],[3.5,4.5,.5],'black');c('head',[-.26,head-1.8,fz-2.9],[.52,3.6,.4],'light');c('head',[-1.15,head+.2,fz-2.92],[2.3,.43,.4],'light')
 else:
  for s in (-1,1):plate('head',s*1.15,head+.15,fz-2.65,2.1,4.9,.8,'ivory',s*12,v=1 if s==1 else 2);plate('head',s*1.1,head-2.0,fz-2.48,1.55,2,.8,'ivory',-s*22,0)
  c('head',[-.22,head-2.6,fz-3.15],[.44,4.9,.4],'light');
  if rook:c('head',[-1.75,head-.25,fz-3.2],[3.5,.6,.45],'light')
 for s in (-1,1):
  c('head',[s*3-0.7,head-1.9,fz-.1],[1.4,3.8,2.4],'dark');c('head',[s*3-.8,head-1.4,fz-.38],[1.6,2.8,.4],'light',v=1)
 if veil:
  for i in range(-2,3):m.bar('head',(i*1.3,head+2.4,fz+1.4),(i*2.1,head+6.6-abs(i)*.5,fz+1.8),.8,'dark');m.c('head',[i*2.1-.6,head+5.7-abs(i)*.5,fz+1.25],[1.2,1.6,1.2],'light')
 elif rook:
  for s in (-1,1):bar('head',(s*2,head+1.9,fz-.2),(s*4,head+4.5,fz+.4),1.3,'ivory',1.6)
 else:
  for s in (-1,1):plate('head',s*2.25,head+2.9,fz,1.5,3,1.5,'ivory',-s*25,2)
 # Shoulders, exposed upper arm rails, elbows, forearm layered armor, individual fingers.
 for s,side in [(-1,'right'),(1,'left')]:
  a=(s*sh,chest+1,cz);el=(s*(sh+2.1),chest+1-arm*.82,cz-1.3 if rook else cz);hand=(s*(sh+3.1),chest+1-arm*1.65,cz-4.5 if rook else cz-1)
  if veil and s==-1:el=(-8.4,chest-5.8,cz-1.2);hand=(-11.7,chest-4,cz-6.2)
  mp=lambda k: (side+k if um else k+side.title() if veil else side+k)
  upper=mp('Shoulder') if um else mp('upperArm') if veil else mp('Arm');fore=mp('ForeArm') if um or rook else mp('lowerArm');hnd=mp('Hand') if um or rook else mp('hand')
  for n,p,parent,src in [(side+'Arm',a,'chest',upper),(side+'Fore',el,side+'Arm',fore),(side+'Hand',hand,side+'Fore',hnd)]:m.bone(n,p,parent,src)
  n=side+'Arm';bar(n,a,el,2.1,'dark',2.5);bar(n,(a[0]+s*.7,a[1]-1,a[2]-.8),(el[0]+s*.7,el[1]+1,el[2]-.8),.65,'joint');plate(n,a[0]+s*.9,a[1],a[2],4.8 if rook else 4.0,3.7,5.3,'ivory',s*17,1);plate(n,a[0]+s*1.7,a[1]-2,a[2]-.4,2.1,4.3,3.7,'ivory',s*20,2)
  plate(n,(a[0]+el[0])/2,(a[1]+el[1])/2,cz-1.8,2.1,4.2,1.1,'steel',s*10,0);c(n,[el[0]-1.4,el[1]-1.1,el[2]-1.4],[2.8,2.3,2.8],'joint')
  n=side+'Fore';bar(n,el,hand,2.25,'dark',2.8);bar(n,(el[0]+s*.8,el[1]-.9,el[2]-.5),(hand[0]+s*.8,hand[1]+.9,hand[2]-.5),.75,'copper');mid=(np.array(el)+np.array(hand))/2
  plate(n,mid[0],mid[1]+.4,mid[2]-1.5,3.7 if rook else 3.1,5.4,1.6,'ivory',s*9,1);plate(n,mid[0]+s*.85,mid[1]+1.6,mid[2],1.5,4.6,3.9,'steel',s*12,2);plate(n,mid[0],mid[1]-.2,mid[2]-2.43,1.1,2.5,.3,'light',s*9,1)
  n=side+'Hand';x,y,z=hand;c(n,[x-1.25,y-2.4,z-1.1],[2.5,2.6,2.2],'dark');plate(n,x,y-.8,z-1.2,2.7,1.6,.7,'ivory',v=2)
  for j in range(3):
   fx=x+(j-1)*.84;by=y-2.3;fz2=z-.2
   c(n,[fx-.31,by-1.4,fz2-.5],[.62,1.5,1],'joint');c(n,[fx-.33,by-2.45,fz2-.8],[.66,1.35,.85],'ivory',[17,0,0],[fx,by-1.25,fz2]);
  bar(n,(x-s*1.2,y-.9,z-.1),(x-s*1.75,y-2.4,z-.9),.7,'joint');bar(n,(x-s*1.75,y-2.4,z-.9),(x-s*1.45,y-3.1,z-1.2),.7,'ivory')
  if s==1 or rook:m.vine(side+'Arm',a[0]+s*1.1,a[1]+1.9,a[2]-1.8,5 if rook else 4,s)
  # legs: two visible shin rails and split plated feet, joint-based pivots
  thigh=(s*3.1,hip-.7,0);knee=(s*3.9,hip-leg,0 if not rook else 2.5);foot=(s*4.1,2.9,-.1 if not rook else 5.0)
  if rook:knee=(s*4.7,hip-leg,3.7);foot=(s*5,3.2,4.5)
  thsrc=mp('Thigh') if um or rook else mp('thigh');shsrc=mp('Shin') if um else mp('calf') if veil else mp('Calf');ftsrc=mp('Ankle') if um else mp('foot') if veil else mp('Foot')
  for n,p,parent,src in [(side+'Thigh',thigh,'pelvis',thsrc),(side+'Shin',knee,side+'Thigh',shsrc),(side+'Foot',foot,side+'Shin',ftsrc)]:m.bone(n,p,parent,src)
  n=side+'Thigh';bar(n,thigh,knee,2.25,'dark',2.6);mid=(np.array(thigh)+np.array(knee))/2;plate(n,mid[0]+s*.25,mid[1]+1,mid[2]-1.3,3.6,5.8,1.45,'ivory',s*12,1);bar(n,(thigh[0]+s*.65,thigh[1]-1,thigh[2]+.7),(knee[0]+s*.65,knee[1]+.7,knee[2]+.7),.75,'joint');c(n,[knee[0]-1.45,knee[1]-1.15,knee[2]-1.5],[2.9,2.3,3],'joint');plate(n,knee[0],knee[1],knee[2]-1.6,2.7,2.5,.9,'ivory',s*10,2)
  n=side+'Shin';bar(n,knee,foot,1.8,'dark',2.5);bar(n,(knee[0]+.7,knee[1]-1,knee[2]-.8),(foot[0]+.7,foot[1]+.6,foot[2]-.8),.6,'joint');bar(n,(knee[0]-.75,knee[1]-1,knee[2]-.8),(foot[0]-.75,foot[1]+.6,foot[2]-.8),.6,'joint');mid=(np.array(knee)+np.array(foot))/2;plate(n,mid[0],mid[1]+.65,mid[2]-1.5,3.2,5.6,1.4,'ivory',s*7,2);plate(n,mid[0]+s*.65,mid[1]-2.0,mid[2]-1.9,1.0,2.5,.4,'light');
  n=side+'Foot';x,y,z=foot;c(n,[x-1.7,.55,z-2.4],[3.4,2.4,4.6],'dark');plate(n,x,2.2,z-.6,3.6,1.8,3.6,'ivory',v=2)
  for j in range(3):c(n,[x+(j-1)*1.35-.58,.1,z-3.8],[1.16,1.6,3.2],'ivory',v=j)
  if s==-1:m.vine(side+'Shin',mid[0]-.8,mid[1]+3,mid[2]-1.7,4,-1)
 # Mantle, angular armor skirts and alpha-cut cloth. Use individual source cloth tracks where possible.
 m.bone('mantle',(0,chest+1.5,cz),'chest',None);c('mantle',[-3.9,chest+.8,cz-3.6],[7.8,1.4,.65],'purple' if veil else 'cloth',[0,0,-7],[0,chest+1.2,cz]);c('mantle',[-4.6,chest+2.1,cz-2.9],[9.2,1.0,4.8],'purple' if veil else 'cloth',[0,0,6],[0,chest+2.6,cz]);
 for s in (-1,1):
  m.bone('robe'+str(s),(s*3,chest+1.8,cz+2.4),'chest',('feathersBack1' if s==-1 else 'feathersBack2') if um else 'clothBack' if veil else None,mode='cloth');m.drape('robe'+str(s),s*3,chest+1.8,cz+2.6,5.5,hip*.76,'purple' if veil else 'cloth',s*7,2)
  m.bone('tabard'+str(s),(s*2.0,hip+1,-2.7),'pelvis',None);m.drape('tabard'+str(s),s*2,hip+.7,-3.2,3.6,hip*.68,'purple' if veil else 'cloth',s*5,2)
 # Signature profiles: broken halo for Seam / Rook / Hush, staff for Veil, blade for Seam.
 if id!='echo_veil_regent':
  m.bone('halo',(0,chest+1,cz+3.4),'chest',None);rr=8.9 if not rook else 7.6;m.ring('halo',0,head-1,cz+4.5,rr,start=-145 if hush else -153,end=145 if hush else 155,segments=9 if hush else 11,w=1.55 if rook else 1.85);m.vine('halo',-rr*.68,head+rr*.45,cz+4.2,5,-1)
 if id=='echo_seam_riven':
  for s,side in [(-1,'right'),(1,'left')]:
   n=side+'Fore';x=s*(sh+2.8);y=chest+1-arm*1.4;z=cz-2.4;plate(n,x+s*1.6,y+.5,z,3.3,5.6,2.2,'dark',s*9);plate(n,x+s*1.7,y-2.0,z-1.0,2.7,8.4,1.0,'blade',-s*8,2);plate(n,x+s*1.7,y-3.2,z-1.65,1.2,7.5,.5,'light',-s*8,1);plate(n,x+s*2.1,y-7.9,z-1,1.6,3.1,1,'blade',-s*28,1)
 if veil:
  n='rightHand';x,y,z=(-11.7,chest-4,cz-6.2);m.bone('staff',(x,y,z),n,None);n='staff';c(n,[x-.85,1,z-.85],[1.7,H-3,1.7],'dark');
  for yy in [3,11,20,29,37,42]:plate(n,x,yy,z,2.7,2.1,2.6,'ivory',v=yy%3)
  m.ring(n,x,H-2,z,4.6,start=-150,end=150,segments=7,w=1.25);c(n,[x-1.55,H-3.55,z-1.55],[3.1,3.1,3.1],'light');m.vine(n,x-3.3,H+1.5,z,5,-1);m.drape(n,x+3.6,H-.5,z,1.5,9,'cloth',7,0)
 if hush:
  x=-sh-3.1;y=chest+1-arm*1.65;z=cz-1;m.bone('pendulum',(x,y-1,z),'rightHand','pendulum_chain',mode='cloth');
  for i in range(7):plate('pendulum',x,y-2-i*1.35,z,.85,1.6,.85,'joint',(-1)**i*18)
  y-=12;m.bone('weight',(x,y,z),'pendulum','pendulum_weight',mode='cloth');c('weight',[x-2.7,y-2.6,z-2.6],[5.4,5.3,5.2],'dark');plate('weight',x,y,z-2.8,4.8,4.3,.8,'ivory',v=2);plate('weight',x,y,z-3.3,2.8,2.8,.5,'light');plate('weight',x,y-2.7,z,3.8,1.5,4.0,'rust')
 if rook:
  # Salvage scythe tail on real segmented Elokosa tail animation tracks.
  parent='pelvis';a=(0,hip+1,3.0)
  for i in range(1,6):
   b=(0,hip+1+i*1.35,3.0+i*4.0);n='tail'+str(i);m.bone(n,a,parent,n);bar(n,a,b,2.4,'dark',2.8);plate(n,0,(a[1]+b[1])/2,(a[2]+b[2])/2,3.2,2.8,3.3,'ivory',v=i%3);parent=n;a=b
  m.bone('tailblade',a,parent,'scythe');x,y,z=a;plate('tailblade',0,y,z,5.7,2.8,5.0,'joint');plate('tailblade',0,y+1.2,z+3,5.5,2.4,4.7,'blade',v=2);plate('tailblade',0,y+2.9,z+5.1,3.7,4.5,2.1,'ivory',v=1);plate('tailblade',0,y+1.2,z+5.5,2.1,.8,1.2,'light')

def grid(m,id,original,oldtex):
 # Preserve the native articulated chassis and source assembly pose, but replace visible boxes with detailed skins.
 # Retain original cube topology and all existing animations, and add localized structural details on moving parts.
 c=m.c;bar=m.bar;plate=m.plate
 for b in original:
  if not b.get('cubes'):continue
  name=b['name'];m.b[name]=m.old[name]
  for i,cu in enumerate(b['cubes']):
   u=cu['uv']['north'];x,y=u['uv'];w,h=u['uv_size'];color=oldtex.getpixel((int(x+w/2),int(y+h/2)))[:3]
   palette={'ivory':(184,181,163),'steel':(126,131,124),'dark':(38,43,47),'joint':(76,82,84),'rust':(123,77,49),'moss':(63,95,54),'cloth':(66,49,76),'blade':(162,185,185),'trim':(90,97,96),'light':m.a.accent}
   k=min(palette,key=lambda k:sum((a-b)**2 for a,b in zip(color,palette[k])))
   # Center of a light tile is intentionally bright, distinguish it by saturation/color distance.
   if max(color)-min(color)>75 and sum((a-b)**2 for a,b in zip(color,m.a.accent))<16000:k='light'
   cc=dict(cu);cc['uv']=m.a.uv(k,i%3);m.b[name].setdefault('cubes',[]).append(cc)
   o=cu['origin'];s=cu['size'];x,y,z=o;w,h,d=s
   # Armor panel overlay (small offset, no intersecting/overlapping face); inherit rotation from parent cube.
   if k in ('ivory','steel') and w>=4 and h>=3 and d>=2 and not cu.get('rotation'):
    for j in range(2):
     pw=w*.40;ph=h*.70;xx=x+w*(.06+.48*j);yy=y+h*.14
     c(name,[xx,yy,z-.32],[pw,ph,.33],'ivory' if j==0 else 'steel',v=(i+j)%3)
    c(name,[x+w*.15,y+h*.87,z-.48],[w*.7,.38,.48],'joint')
    c(name,[x+w*.12,y+h*.16,z+d+.02],[w*.76,h*.16,.3],'rust',v=2)
    if i%3==0:
     c(name,[x+w*.25,y+h*.20,z-.6],[w*.45,.6,.3],'light')
   if k in ('dark','joint') and h>=5 and w>=2.5 and not cu.get('rotation') and d>=2:
    c(name,[x+.15,y+.8,z-.4],[.65,h-.9,.7],'joint');c(name,[x+w-.8,y+.8,z-.4],[.65,h-.9,.7],'copper');
 # Specific silhouette additions; no new retarget requirement.
 if id=='grid_palinode':
  n='body';c(n,[-12,19,-8],[24,2.5,16],'dark');
  for s in (-1,1):
   plate(n,s*10,21,1,4,5,14,'ivory',s*14,2);plate(n,s*9,17,-12,4,4,4,'steel',s*19,1);bar(n,(s*8,23,8),(s*8,15,-11),.8,'copper');m.vine(n,s*9,24,6,6,s)
  for j in range(5):c(n,[-6+j*2.7,22,1],[1.3,.7,10],'joint');c(n,[-6+j*2.7,22.7,1],[1.3,.6,2],'ivory')
  n='mm_head';c(n,[-8,7,-29],[16,3,3],'dark');
  for s in (-1,1):plate(n,s*5.6,8,-29.5,4,3,2,'ivory',s*15,2);c(n,[s*4-1.1,8.4,-31],[2.2,1.0,.5],'light');bar(n,(s*7,10,-29),(s*7,14,-23),.8,'copper')
  for i,z in enumerate([-10,0,12]):
   for side,s in [('l',-1),('r',1)]:
    x=15 if i!=1 else 18;n=f'leg_{i}_{side}';bar(n,(s*7,16,z+1),(s*x,12,z+1),1.4,'joint');bar(n,(s*8,15,z-2.4),(s*x,13,z-2.4),.8,'copper');n=f'foot_{i}_{side}';c(n,[s*x-3,0,z-5],[6,1.5,2],'dark');
    for j in range(3):c(n,[s*x-2.6+j*1.9,.1,z-6.6],[1.5,1.5,3],'ivory',v=j)
 elif id=='grid_silt_engine':
  n='body';
  for s in (-1,1):
   c(n,[s*9-1.3,15,-10],[2.6,4,21],'dark');c(n,[s*9-1.1,19,-8],[2.2,.8,17],'ivory');m.vine(n,s*9,20,11,5,s)
   for j in range(4):c(n,[s*11-.75,13,-8+j*5],[1.5,4.5,1.3],'steel',v=j%3)
  n='mm_head';
  for s in (-1,1):
   bar(n,(s*5,24,-23),(s*5,29,-3),1.1,'copper');c(n,[s*6-1.5,23,-24],[3,4,9],'joint');c(n,[s*6-1.1,24,-25],[2.2,2,.7],'light');c(n,[s*6-1.7,26,-22],[3.4,1.4,7],'ivory')
  c(n,[-3.7,23,-26],[7.4,7,2.1],'dark');c(n,[-2.2,24.5,-26.5],[4.4,4,.7],'light');
  for s,x in [('l',-15),('r',15)]:
   n='tread_'+s
   for z in (-11,-4,4,11):
    for xx in [x-4.4,x+3.5]:c(n,[xx,2,z-2],[1.0,4.8,4.2],'joint');c(n,[xx-.05,3,z-.8],[1.1,2.4,1.6],'rust')
 elif id=='grid_gantry_marrow':
  n='body';c(n,[-9,22,-6],[18,2.5,17],'dark');
  for s in (-1,1):
   plate(n,s*10,23,2,4.4,4.8,14,'ivory',s*13,2);bar(n,(s*9,25,6),(s*9,16,-8),.9,'copper');m.vine(n,s*10,25,5,7,s)
  for j in range(5):c(n,[-6+j*2.8,24.6,-4],[1.5,.5,12],'steel')
  for n in ['leg_lf','leg_lb','leg_rf','leg_rb']:
   x,y,z=m.b[n]['pivot'];bar(n,(x-1.5,13,z-2),(x-1.5,3,z-2),.9,'copper');plate(n,x,9,z-3.5,4.8,3.2,1.2,'ivory',8,2);c(n,[x-3,0,z-6],[6,1.6,3],'dark');
   for i in range(3):c(n,[x-2.6+i*1.85,.1,z-7],[1.4,1.7,2.5],'ivory',v=i)
  for i in range(1,6):
   n='mm_tail'+str(i);x,y,z=m.b[n]['pivot'];l=3 if i==5 else 4.6;bar(n,(x+2,y,z),(x+2,y,z+l),.8,'copper');bar(n,(x-2,y,z),(x-2,y,z+l),.8,'copper');c(n,[x-2.5,y+1.5,z+.5],[5,1.0,l-1],'ivory',v=i%3)
  n='mm_scythe';x,y,z=m.b[n]['pivot'];
  for s in (-1,1):bar(n,(s*3.1,y,z+4),(s*4.5,y-4,z+8),1.5,'blade');bar(n,(s*4.5,y-4,z+8),(s*2.4,y-5.3,z+9),1.2,'ivory')
 else:
  n='pedestal';m.ring(n,0,9,2,8.2,kind='steel',start=-150,end=150,segments=8,w=1.4)
  for s in (-1,1):bar(n,(s*5,3,-3),(s*6,12,-2),1.25,'joint');m.vine(n,s*6,13,3,5,s)
  n='head';m.ring(n,0,24,2,9.5,start=-160,end=170,segments=10,w=1.55);m.vine(n,-7,28,2,5,-1);c(n,[-5,20,-7],[10,4,1.4],'dark');c(n,[-3.6,20.8,-7.8],[7.2,2.2,.6],'light',v=1)
  for n in ('rods1','rods2','rods3'):
   c(n,[-3.5,12,-18],[7,6,3],'dark');plate(n,0,15,-19,5.7,3.8,1.5,'ivory',v=2);plate(n,0,15,-20,2.8,2.7,.5,'light');bar(n,(-2.7,13,-16),(-2.7,21,-8),.7,'copper')

# Source poses contain numeric or simple MoLang expressions. Retarget only the actual sampled rotation/position values.
ALLOWED={'sin':lambda v:math.sin(math.radians(v)),'cos':lambda v:math.cos(math.radians(v)),'abs':abs,'min':min,'max':max,'clamp':lambda v,a,b:max(a,min(v,b)),'sqrt':math.sqrt,'pow':pow}
CACHE={}
def val(x,t):
 if isinstance(x,(int,float)):return x
 if not isinstance(x,str):return 0
 if x not in CACHE:
  s=x.replace('query.anim_time','t').replace('Math.','').replace('math.','');tree=ast.parse(s.strip(),mode='eval');assert all(isinstance(n,(ast.Expression,ast.Constant,ast.Name,ast.Load,ast.UnaryOp,ast.BinOp,ast.Add,ast.Sub,ast.Mult,ast.Div,ast.Pow,ast.Mod,ast.UAdd,ast.USub,ast.Call)) and (not isinstance(n,ast.Name) or n.id in ALLOWED or n.id=='t') for n in ast.walk(tree)),x;CACHE[x]=compile(tree,'<molang>','eval')
 return eval(CACHE[x],{'__builtins__':{}},{**ALLOWED,'t':t})
def v3(v,t):
 if isinstance(v,dict):v=v.get('post',v.get('pre',v.get('vector')))
 if not isinstance(v,list):v=[v]*3
 return np.array([val(x,t) for x in v],dtype=float)
def track(v,t,default):
 if v is None:return np.array(default,dtype=float)
 if not isinstance(v,dict):return v3(v,t)
 keys=sorted((float(k),vv) for k,vv in v.items());
 if t<=keys[0][0]:return v3(keys[0][1],t)
 if t>=keys[-1][0]:return v3(keys[-1][1],t)
 for (a,u),(b,w) in zip(keys,keys[1:]):
  if a<=t<=b:return v3(u,t)+(v3(w,t)-v3(u,t))*(t-a)/(b-a)
def pose(bones,anim,t):
 out={}
 def tr(n):
  if n in out:return out[n]
  b=bones[n];ch=anim.get('bones',{}).get(n,{});r=np.array(b.get('rotation',[0,0,0]))+track(ch.get('rotation'),t,[0,0,0]);m=Rotation.from_euler('xyz',r,degrees=True).as_matrix();p=track(ch.get('position'),t,[0,0,0]);
  if b.get('parent'):m=tr(b['parent'])[0]@m
  out[n]=(m,p);return m,p
 return tr

def retarget(m,animations,id):
 idle=next(v for k,v in animations.items() if k.endswith('.idle'));rest=pose(m.old,idle,0)
 # Global rest orientation changes converted back into clean target local joint rotations.
 for key,a in animations.items():
  length=a['animation_length'];steps=max(1,math.ceil(length*20));out={n:{'rotation':{}} for n in m.map};root='bfv_root';out[root]['position']={}
  for i in range(steps+1):
   t=length*i/steps;ts=f'{t:.5f}'.rstrip('0').rstrip('.') or '0';src=pose(m.old,a,t);glob={}
   for n in m.g['bones']:
    name=n['name'];
    if not name.startswith('bfv_'):continue
    parent=n.get('parent');pa=glob.get(parent,np.eye(3));
    if name in m.map:
     source=m.map[name];r0,p0=rest(source);r,p=src(source);desired=r@r0.T;local=pa.T@desired;angles=Rotation.from_matrix(local).as_euler('xyz',degrees=True)
     # Retargeting constrains imported motion for a different body silhouette. Avoid extreme twists from quadruped/crouched source poses.
     mode=m.modes[name];cap=np.array([28,36,25]) if mode=='cloth' else np.array([22,45,22]) if mode=='root' else np.array([65,60,55]);
     if name.endswith('Head') or name=='bfv_head':cap=np.array([35,48,28])
     if name.endswith('Thigh') or name.endswith('Shin') or name.endswith('Foot'):cap=np.array([44,25,26]);
     if key.endswith('.idle'):cap=cap*.28
     if id=='echo_veil_regent' and ('Thigh' in name or 'Shin' in name or 'Foot' in name):cap=np.array([9,7,7])
     angles=np.clip(angles,-cap,cap);glob[name]=pa@Rotation.from_euler('xyz',angles,degrees=True).as_matrix();out[name]['rotation'][ts]=[round(float(x),3) for x in angles]
     if name==root:
      dp=np.clip(p-p0,[-2,-2,-2],[2,4,2]);out[root]['position'][ts]=[round(float(x),3) for x in dp]
    else:glob[name]=pa
  # Explicit idle sway on new accessories. Retargeted source still drives their parent bones.
  for n in ('bfv_halo','bfv_mantle','bfv_tabard-1','bfv_tabard1'):
   if n not in {x['name'] for x in m.g['bones']}:continue
   amp=2 if n=='bfv_halo' else 4
   out[n]={'rotation':{'0':[0,0,0],f'{length/2:.5f}':[amp,0,amp if n.endswith('1') else -amp],f'{length:.5f}':[0,0,0]}}
  a['bones'].update(out)

def build(base,out):
 with zipfile.ZipFile(base) as z:
  assert z.testzip() is None;f={n:z.read(n) for n in z.namelist()};assert len(f)==len(z.namelist())
 old=f.copy();summary={}
 for i,id in enumerate(IDS):
  gp=RP+'models/entity/'+id+'.geo.json';gobj=json.loads(f[gp]);g=gobj['minecraft:geometry'][0];oldbones=json.loads(f[gp])['minecraft:geometry'][0]['bones'];ce=json.loads(f[RP+'entity/'+id+'.entity.json'])['minecraft:client_entity']['description'];tp=RP+ce['textures']['default']+'.png';tex=Image.open(io.BytesIO(f[tp])).convert('RGBA');art=Art(COLORS[i],id.startswith('echo_'),93+i);m=Model(g,art);ap=RP+'animations/'+id+'.animation.json'
  if id.startswith('echo_'):
   humanoid(m,id);anim=json.loads(f[ap]);retarget(m,anim['animations'],id);f[ap]=enc(anim)
   g['description'].update(visible_bounds_width=12,visible_bounds_height=10,visible_bounds_offset=[0,2.2,0])
  else:grid(m,id,oldbones,tex)
  g['description'].update(texture_width=512,texture_height=512);f[gp]=enc(gobj);f[tp]=png(art.img)
  summary[id]={'bones':len(g['bones']),'cubes':sum(len(b.get('cubes',[])) for b in g['bones']),'atlas_tiles':art.n}
  print(id,summary[id],flush=True)
 for prefix in (BP,RP):
  p=prefix+'manifest.json';m=json.loads(f[p]);assert m['header']['version']==[0,11,24];m['header']['version']=[0,11,25]
  for mod in m['modules']:mod['version']=[0,11,25]
  for dep in m.get('dependencies',[]):
   if dep.get('version')==[0,11,24]:dep['version']=[0,11,25]
  f[p]=enc(m)
 # No changes to gameplay, source hidden bone definitions, item assets, cities, bunkers, chest policy or station.
 assert all(f[n]==v for n,v in old.items() if n not in {BP+'manifest.json',RP+'manifest.json'} and not (n.startswith(RP+'models/entity/') or n.startswith(RP+'animations/') or n.startswith(RP+'textures/bearframe/')))
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in sorted(f.items()):z.writestr(n,b)
 with zipfile.ZipFile(out) as z:assert z.testzip() is None;assert all(z.read(n)==b for n,b in f.items())
 print(json.dumps({'roster':summary,'changes':sum(f[n]!=old[n] for n in f),'sha256':hashlib.sha256(Path(out).read_bytes()).hexdigest()},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('base');p.add_argument('out');a=p.parse_args();build(a.base,a.out)
