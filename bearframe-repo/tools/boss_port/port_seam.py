import json,zipfile,copy,math,hashlib,sys,re,io,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
BP='Bearframe_Behavior/';RP='Bearframe_Resources/';ID='echo_seam_riven'; SOURCE='assets/mowziesmobs/'
def enc(o):return (json.dumps(o,indent=2)+'\n').encode()
def png(im):b=io.BytesIO();im.save(b,format='PNG');return b.getvalue()
def ease(name,t):
 if not name or name=='linear':return t
 if name=='easeOutExpo':return 1 if t==1 else 1-2**(-10*t)
 if name=='easeInOutSine':return (1-math.cos(math.pi*t))/2
 m=re.fullmatch('ease(InOut|In|Out)(Quad|Cubic|Quart|Quint)',name);assert m,name
 p={'Quad':2,'Cubic':3,'Quart':4,'Quint':5}[m[2]]
 return t**p if m[1]=='In' else 1-(1-t)**p if m[1]=='Out' else (2*t)**p/2 if t<.5 else 1-(-2*t+2)**p/2

def vector(v):return [re.sub(r'\bMath\.', 'math.',x) if isinstance(x,str) else x for x in v]
def channel(ch):
 if 'vector' in ch:return vector(ch['vector'])
 keys=sorted((float(t),v) for t,v in ch.items()); out={}
 for i,(t,k) in enumerate(keys):
  v=vector(k['vector']);out[f'{t:.5f}'.rstrip('0').rstrip('.') or '0']=v
  if not i:continue
  start,prev=keys[i-1];a=vector(prev['vector']);name=k.get('easing','linear')
  if name=='linear' or not all(isinstance(x,(int,float)) for x in a+v):continue
  steps=max(1,math.ceil((t-start)*30))
  for j in range(1,steps):
   x=j/steps;f=ease(name,x);ts=start+(t-start)*x;out[f'{ts:.5f}'.rstrip('0').rstrip('.')]=[round(x+(y-x)*f,5) for x,y in zip(a,v)]
 return dict(sorted(out.items(),key=lambda x:float(x[0])))

class Atlas:
 def __init__(self):self.im=Image.new('RGBA',(256,256));self.d=ImageDraw.Draw(self.im);self.i=0
 def cube(self,origin,size,style,rotation=None,pivot=None):
  colors={'metal':(128,126,119),'dark':(42,46,48),'edge':(191,182,165),'rust':(104,76,61),'cloth':(52,45,65),'light':(130,224,232),'blade':(169,185,191),'violet':(185,114,246)};c=colors[style];u=(self.i%16)*16;v=(self.i//16)*16;self.i+=1;assert self.i<=256
  self.d.rectangle((u,v,u+15,v+15),fill=(*c,255));
  if style not in ('light','violet'):
   self.d.line((u,v,u+15,v),fill=tuple(min(255,x+28) for x in c));self.d.line((u,v+15,u+15,v+15),fill=tuple(max(0,x-24) for x in c));self.d.line((u+2,v+2,u+2,v+13),fill=tuple(max(0,x-18) for x in c));
   for i in range(4):
    x=(i*7+self.i*3)%12+2;y=(i*5+self.i)%12+2;self.d.point((u+x,v+y),fill=tuple(max(0,x-22) for x in c))
  cube={'origin':origin,'size':size,'uv':{face:{'uv':[u+1,v+1],'uv_size':[14,14]} for face in ('north','south','east','west','up','down')}}
  if rotation:cube.update(rotation=rotation,pivot=pivot)
  return cube

def build(base,jar,out):
 with zipfile.ZipFile(base) as z:old={n:z.read(n) for n in z.namelist()};assert z.testzip() is None
 f=old.copy();
 with zipfile.ZipFile(jar) as j:
  g=json.loads(j.read(SOURCE+'geo/umvuthana.geo.json'));source_anim=json.loads(j.read(SOURCE+'animations/umvuthana.animation.json'))['animations']
 geo=g['minecraft:geometry'][0]; bones={b['name']:b for b in geo['bones']}; atlas=Atlas()
 for b in bones.values():b.pop('cubes',None)
 def c(n,o,s,k,r=None,p=None):bones[n].setdefault('cubes',[]).append(atlas.cube(o,s,k,r,p))
 # Original rig retained; all visible geometry is newly authored metal, cloth and blades.
 c('hips',[-4.5,10,-1.5],[9,5,6],'dark');c('hips',[-5,11,-2],[10,3,7],'metal')
 c('stomach',[-3.5,13.5,-1.5],[7,10,5],'dark');c('stomach',[-4.5,17,-2.5],[9,6,6],'metal');c('stomach',[-2,17,-3],[4,4,1],'light')
 c('chest',[-5,21,-2],[10,7,6],'metal');c('chest',[-3,22,-3],[6,4,1],'edge');c('chest',[-2,23,-3.5],[4,2,1],'violet')
 c('neck',[-1.5,27,-.5],[3,6,3],'dark')
 c('head',[-3.5,30.5,-2.5],[7,7,7],'metal');c('head',[-4,35,-3],[8,3,8],'edge');c('head',[-3.2,33,-3.3],[6.4,2,1],'dark');c('head',[-2.8,33.4,-3.5],[5.6,.7,.5],'light');c('head',[-4.5,32,-1],[1.5,4,4],'dark');c('head',[3,32,-1],[1.5,4,4],'metal');c('head',[4,33,-1.2],[.7,2,2],'violet')
 # Jagged cowl, asymmetrical shoulder armour and back drapery.
 c('mane',[-6,25,1],[12,3,5],'cloth');c('feathersBack1',[-5,18,5],[10,10,1],'cloth');c('feathersBack2',[-5,13,5.2],[5,10,1],'cloth',[0,0,10],[-2.5,21,5]);c('feathersBack3',[1,15,5.4],[4,9,1],'cloth',[0,0,-10],[3,22,5]);c('crestLeft',[-5,24,0],[3,5,4],'rust');c('crestRight',[2,25,0],[3,4,4],'edge')
 for side,x in [('right',-3.5),('left',3.5)]:
  c(side+'Shoulder',[x-2.4,17, -1.4],[4.8,9,4.8],'metal');c(side+'Shoulder',[x-3,23,-2],[6,4,6],'edge' if side=='right' else 'rust');c(side+'ForeArm',[x-1.9,4,-1],[3.8,10,4],'dark');c(side+'ForeArm',[x-2.5,7,-2],[5,6,5],'metal');c(side+'ForeArm',[x-1.3,8,-2.6],[2.6,4,1],'light');c(side+'Hand',[x-1.6,1,-.5],[3.2,4,3],'dark')
  # Split energy blades on each wrist follow the original index bones and attack extension.
  c(side+'Index',[x-1.6,-3,-1],[3.2,6,2],'dark');c(side+'Index',[x-2.2,-10,-1],[1.8,8,2],'blade');c(side+'Index',[x+.4,-12,-1],[1.8,10,2],'blade');c(side+'Index',[x-1.8,-10,-1.4],[.7,7,.6],'violet');c(side+'Index',[x+.8,-12,-1.4],[.7,9,.6],'violet')
 for side,x in [('right',-3),('left',3)]:
  c(side+'Thigh',[x-2,10,-2.8],[4,5,4],'metal');c(side+'Shin',[x-1.4,5,-2],[2.8,5,3],'dark');c(side+'Shin',[x-2,7,-2.7],[4,4,3],'edge');c(side+'Ankle',[x-1.2,4.1,-8.75],[2.4,2,8],'dark');c(side+'Ankle',[x-1.7,3.7,-6.5],[3.4,3,5],'metal');c(side+'ToesFront',[x-2.5,5.1,-8.75],[5,4,4],'metal',[180,0,0],[x,7.1,-6.75]);c(side+'ToesBack',[x-1.5,4.5,-8],[3,2,3],'dark')
 geo['description'].update(identifier='geometry.bearframe.'+ID,texture_width=256,texture_height=256,visible_bounds_width=8,visible_bounds_height=6,visible_bounds_offset=[0,1.5,0]);f[RP+'models/entity/'+ID+'.geo.json']=enc(g);f[RP+'textures/bearframe/'+ID+'.png']=png(atlas.im)
 mapping={'idle':'idle_aggressive','walk':'walk_aggressive','attack0':'attack_slash_right','attack1':'attack_slash_left','death':'die'};animations={}
 for alias,src in mapping.items():
  a=copy.deepcopy(source_anim[src]);a['bones']={bone:{k:channel(v) for k,v in channels.items()} for bone,channels in a['bones'].items() if bone in bones and not bone.endswith('Controller')};
  if alias=='death':a['loop']='hold_on_last_frame'
  animations['animation.bearframe.'+ID+'.'+alias]=a
 f[RP+'animations/'+ID+'.animation.json']=enc({'format_version':'1.8.0','animations':animations})
 # Retain identifiers, quest credit, drops, faction and HUD. Close to the source's 3-block range.
 p=BP+'entities/'+ID+'.json';e=json.loads(f[p]);e['minecraft:entity']['components']['minecraft:behavior.move_towards_target']['within_radius']=2.2;f[p]=enc(e)
 p=BP+'scripts/boss_moves.js';s=f[p].decode();data=json.loads(s[s.index('{'):s.rindex('}')+1]);data['bearframe:'+ID]=[dict(name='Right Splitblade',shape='cone',radius=3,windup=13,end=39,damage=9,dot=0.25,sourceSlash=True),dict(name='Left Splitblade',shape='cone',radius=3,windup=13,end=39,damage=9,dot=0.25,sourceSlash=True)];f[p]=('// Generated boss moves; Seam-Riven uses source slash timings.\nexport const BOSS_MOVES = '+json.dumps(data,indent=2)+';\n').encode()
 p=BP+'scripts/boss_combat.js';s=f[p].decode();target='    if (!strike.released && elapsed >= strike.move.windup && elapsed < strike.move.end) {';assert s.count(target)==1
 s=s.replace(target,'''    if (strike.move.sourceSlash) {
      const victim=players.find(player=>player.id===strike.targetId);
      if (!strike.lunged && elapsed>=5 && elapsed<strike.move.windup) {
        strike.lunged=true;
        const from=height(entity.location,.8), to={x:from.x+strike.direction.x,y:from.y,z:from.z+strike.direction.z};
        if(clearPath(dimension,from,to))entity.applyImpulse({x:strike.direction.x*.5,y:0,z:strike.direction.z*.5});
      }
      if (!strike.released && elapsed>=strike.move.windup && elapsed<strike.move.windup+4) {
        strike.released=true;
        const current=entity.location;
        if(victim && inside(strike.move,{...strike,origin:current},victim.location) && clearPath(dimension,height(current,.8),height(victim.location,.8))) {
          victim.applyDamage(strike.move.damage+(strike.enraged?2:0),{cause:EntityDamageCause.entityAttack,damagingEntity:entity});
        }
        dimension.playSound("random.anvil_land",current,{volume:.55,pitch:1.35});
      }
      if(elapsed>=strike.move.end)reset(entity,state,now,strike.enraged?10:18);
      return;
    }
'''+target)
 s=s.replace('state.strike = { started: now, origin, mark, direction, move, enraged };','state.strike = { started: now, origin, mark, direction, move, enraged, targetId:target.player.id };');f[p]=s.encode()
 # Matching splitblade drop: original binding and item ID, new physical split-prong silhouette.
 p=RP+'models/entity/held_seam_splitter.geo.json';held=json.loads(f[p]);h=held['minecraft:geometry'][0];ha=Atlas();h['description'].update(texture_width=256,texture_height=256);grip=h['bones'][0];grip['cubes']=[];h['bones']=[grip]
 def hc(o,sz,k):grip['cubes'].append(ha.cube(o,sz,k))
 hc([-1,14,-7],[2,10,2],'dark');hc([-3,23,-7.5],[6,3,3],'metal');hc([-2.7,25,-7],[2,15,2],'blade');hc([.7,25,-7],[2,18,2],'blade');hc([-2.2,26,-7.4],[.7,13,.7],'violet');hc([1.2,26,-7.4],[.7,16,.7],'violet');hc([-1.5,13,-7.5],[3,2,3],'edge');f[p]=enc(held)
 ap=RP+'attachables/seam_splitter.json'; ad=json.loads(f[ap]);attach=ad['minecraft:attachable']['description'];attach['animations'].pop('energy',None);attach['scripts']['animate']=[a for a in attach['scripts']['animate'] if a!='energy'];f[ap]=enc(ad);f[RP+attach['textures']['default']+'.png']=png(ha.im)
 item=json.loads(f[BP+'items/seam_splitter.json'])['minecraft:item'];tex=json.loads(f[RP+'textures/item_texture.json'])['texture_data'][item['components']['minecraft:icon']]['textures'];im=Image.new('RGBA',(16,16));d=ImageDraw.Draw(im);d.line([(2,13),(7,8)],fill='#52575a',width=2);d.line([(6,8),(13,1)],fill='#bbc3c8',width=2);d.line([(8,10),(15,3)],fill='#bbc3c8',width=2);d.line([(7,7),(13,1)],fill='#b972f6',width=1);d.line([(9,9),(15,3)],fill='#b972f6',width=1);d.line([(5,7),(9,11)],fill='#716964',width=2);f[RP+tex+'.png']=png(im)
 for prefix in [BP,RP]:
  p=prefix+'manifest.json';m=json.loads(f[p]);assert m['header']['version']==[0,11,22];m['header']['version']=[0,11,23]
  for mod in m['modules']:mod['version']=[0,11,23]
  for dep in m.get('dependencies',[]):
   if dep.get('version')==[0,11,22]:dep['version']=[0,11,23]
  f[p]=enc(m)
 changed=[n for n in f if f[n]!=old[n]]
 assert all(f[n]==old[n] for n in old if n.endswith('.mcstructure') or 'loot_tables/' in n)
 assert len(bones)==70 and all(b.get('parent') in bones or 'parent' not in b for b in bones.values());assert all(set(a['bones'])<=set(bones) for a in animations.values())
 for n in changed:
  if n.endswith('.json'):json.loads(f[n])
  if n.endswith('.js'):subprocess.run(['node','--input-type=module','--check'],input=f[n],check=True)
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in sorted(f.items()):z.writestr(n,b)
 with zipfile.ZipFile(out) as z:assert z.testzip() is None;assert all(z.read(n)==b for n,b in f.items())
 print(json.dumps({'changed':changed,'bones':len(bones),'cubes':sum(len(b.get('cubes',[])) for b in bones.values()),'animations':mapping,'structures':sum(n.endswith('.mcstructure') for n in old),'sha256':hashlib.sha256(Path(out).read_bytes()).hexdigest()}))
if __name__=='__main__':build(*sys.argv[1:])
