import math, zipfile, json, io, sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
RP='Bearframe_Resources/'
def matrix(rot):
 x,y,z=np.radians(rot); cx,sx=np.cos(x),np.sin(x);cy,sy=np.cos(y),np.sin(y);cz,sz=np.cos(z),np.sin(z)
 return np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])@np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
def sample(x,t):
 def v3(v):
  if isinstance(v,dict):v=v.get("post",v.get("pre",[0,0,0]))
  return np.array([float(y) if isinstance(y,(float,int)) else 0 for y in v],dtype=float)
 if isinstance(x,list):return v3(x)
 keys=sorted((float(k),v) for k,v in x.items());
 if t<=keys[0][0]:return v3(keys[0][1])
 if t>=keys[-1][0]:return v3(keys[-1][1])
 for (a,u),(b,v) in zip(keys,keys[1:]):
  if a<=t<=b:return v3(u)+(v3(v)-v3(u))*(t-a)/(b-a)
def render(g,tex,anim=None,t=0,w=420,h=380,az=27,el=12):
 bones={b['name']:b for b in g['bones']}; matrices={}; trans={}; faces=[]; allv=[]
 def tr(n):
  if n in matrices:return matrices[n],trans[n]
  b=bones[n];p=np.array(b.get('pivot',[0,0,0])); ch=(anim or {}).get('bones',{}).get(n,{})
  r=np.array(b.get('rotation',[0,0,0]),dtype=float)+sample(ch.get('rotation',[0,0,0]),t);pos=sample(ch.get('position',[0,0,0]),t);sc=sample(ch.get('scale',[1,1,1]),t)
  m=matrix(r)@np.diag(sc);off=p-m@p+pos
  if 'parent' in b:
   mp,op=tr(b['parent']);m,off=mp@m,mp@off+op
  matrices[n],trans[n]=m,off;return m,off
 a,e=np.radians([az,el]);right=np.array([np.cos(a),0,np.sin(a)]);view=np.array([np.sin(a)*np.cos(e),np.sin(e),-np.cos(a)*np.cos(e)]);up=np.cross(right,view);cam=np.stack([right,up,view]);
 F=[('north',[0,2,3,1],[0,0,-1]),('south',[4,5,7,6],[0,0,1]),('west',[0,4,6,2],[-1,0,0]),('east',[1,3,7,5],[1,0,0]),('down',[0,1,5,4],[0,-1,0]),('up',[2,6,7,3],[0,1,0])]
 for b in bones.values():
  m,o=tr(b['name'])
  for c in b.get('cubes',[]):
   org=np.array(c['origin']);sz=np.array(c['size']); pts=np.array([org+sz*[x,y,z] for z in (0,1) for y in (0,1) for x in (0,1)])
   if 'rotation' in c:
    cm=matrix(c['rotation']);p=np.array(c.get('pivot',org+sz/2));pts=(pts-p)@cm.T+p
   else:cm=np.eye(3)
   pts=(pts@m.T+o)@cam.T;allv.extend(pts)
   for name,inds,normal in F:
    n=cam@m@cm@normal
    if n[2]<.0001:continue
    q=pts[inds]; uv=c['uv'];
    if not isinstance(uv,dict):continue
    if name not in uv:continue
    u,v=uv[name]['uv'];a1,b1=uv[name]['uv_size'];tile=np.asarray(tex.crop((min(u,u+a1),min(v,v+b1),max(u,u+a1),max(v,v+b1))).convert('RGBA')).copy()
    if a1<0:tile=tile[:,::-1].copy()
    if b1<0:tile=tile[::-1].copy()
    if tile.size==0:continue
    # face vertex sequence is cyclic, choose UVs consistently; shade by approximate directional lighting
    bright=.62+.36*max(0,float(n[0]*-.4+n[1]*.7+n[2]*.6));tile[:,:,:3]=np.clip(tile[:,:,:3].astype(float)*bright,0,255).astype(np.uint8)
    faces.append((q,tile))
 allv=np.array(allv);lo=allv[:,:2].min(axis=0);hi=allv[:,:2].max(axis=0);scale=min((w-40)/(hi[0]-lo[0]),(h-40)/(hi[1]-lo[1]));center=(lo+hi)/2
 img=np.zeros((h,w,4),np.uint8);img[:]=[29,33,36,255];depth=np.full((h,w),-1e6,dtype=np.float32)
 for q,tile in sorted(faces,key=lambda x:x[0][:,2].mean()):
  p=(q[:,:2]-center)*scale;p[:,1]*=-1;p+=np.array([w/2,h/2]);left,top=np.floor(p.min(axis=0)).astype(int);right,bottom=np.ceil(p.max(axis=0)).astype(int)+1;left=max(0,left);top=max(0,top);right=min(w,right);bottom=min(h,bottom)
  if right<=left or bottom<=top:continue
  p-=np.array([left,top]);th,tw=tile.shape[:2];src=np.array([[0,th-1],[0,0],[tw-1,0]],np.float32);A=cv2.getAffineTransform(src,p[:3].astype(np.float32));warped=cv2.warpAffine(tile,A,(right-left,bottom-top),flags=cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0));
  mat=np.c_[p[:3],np.ones(3)];
  try:coef=np.linalg.solve(mat,q[:3,2])
  except np.linalg.LinAlgError:continue
  yy,xx=np.mgrid[:bottom-top,:right-left];d=coef[0]*xx+coef[1]*yy+coef[2];sub=depth[top:bottom,left:right];mask=(warped[:,:,3]>127)&(d>sub);img[top:bottom,left:right][mask]=warped[mask];sub[mask]=d[mask]
 return Image.fromarray(img)
def sheet(pack,path):
 ids=['echo_seam_riven','echo_veil_regent','echo_rubble_rook','echo_hush_pendulum','grid_palinode','grid_silt_engine','grid_gantry_marrow','grid_cinder_spindle'];im=Image.new('RGB',(1280,800),(22,25,28));d=ImageDraw.Draw(im)
 with zipfile.ZipFile(pack) as z:
  for i,n in enumerate(ids):
   g=json.loads(z.read(RP+'models/entity/'+n+'.geo.json'))['minecraft:geometry'][0];ce=json.loads(z.read(RP+'entity/'+n+'.entity.json'))['minecraft:client_entity']['description'];tex=Image.open(io.BytesIO(z.read(RP+ce['textures']['default']+'.png')));a=json.loads(z.read(RP+'animations/'+n+'.animation.json'))['animations'][ce['animations']['idle']];x=(i%4)*320;y=(i//4)*400;im.paste(render(g,tex,a,min(.3,a['animation_length']/2),320,360), (x,y));d.text((x+12,y+365),n.replace('echo_','').replace('grid_','').replace('_',' ').title(),fill=(220,225,226))
 im.save(path)
if __name__=='__main__':sheet(*sys.argv[1:])
