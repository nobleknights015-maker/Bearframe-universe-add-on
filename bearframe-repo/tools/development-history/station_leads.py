from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from io import BytesIO
import json
import re
from PIL import Image,ImageDraw
from subprocess import run

# Reuse the same pixel-art cuboid UV writer as the Farfield clothing.
src=Path('wraps.py').read_text()
exec(src[src.index('from math import'):src.index('def hood(')])
bp='Bearframe_Behavior/'
rp='Bearframe_Resources/'
old=ZipFile(folder/'Bearframe_Bedrock_0.6.2.mcaddon')
profiles=[
 ('auren','Auren','city_engineer',(79,153,251),(35,55,93),(36.5,101,-6.5),None,'Systems is monitoring the station from here. If a compartment loses power, we can isolate it without taking the rest of the station offline.'),
 ('atlas','Atlas','atlas_vanguard',(245,174,52),(172,115,37),(21.5,101,25.5),'orbit_operations','Surface gear comes back here. We fix what we can, reclaim what we cannot. Saves a lot of hauling.'),
 ('vera','Vera','vera_artisan',(211,104,243),(98,44,132),(94.5,101,10.5),'orbit_commons','Welcome to the Visual Production gallery. Walk all the way around the exhibits. I design the backs too.'),
 ('mira','Mira','farfield_surveyor',(69,219,204),(29,106,108),(22.5,101,-23.5),'orbit_farfield','Farfield has new routes to survey. Log what you see, mark what is unsafe, and give any Echo you meet room to decide whether to talk.'),
 ('sentinel','Sentinel','city_watch',(230,49,65),(47,29,38),(30.5,101,0.5),None,'Different department. Same objective. Watchtower is doing a round. Let me know if you see anything out of place.'),
 ('penney','Penney','city_steward',(244,130,151),(179,108,107),(83.5,101,-6.5),'orbit_commons','The Commons is open. Take a minute in the gardens if you have just come back from the surface.'),
]
updates={}
lang=old.read(rp+'texts/en_US.lang').decode().rstrip()+'\n'
for key,name,base,light,main,pos,wing,line in profiles:
    eid='city_'+key
    original_id='bearframe:'+base
    def clone(path):
        return json.loads(old.read(path.replace(eid,base)).decode().replace(base,eid))
    path=bp+'entities/'+eid+'.json'
    behavior=clone(path)
    entity=behavior['minecraft:entity']
    entity['description']['is_spawnable']=False
    entity['description']['is_summonable']=True
    cmp=entity['components']
    for name_ in tuple(cmp):
        if name_ in ('minecraft:attack','minecraft:behavior.melee_attack','minecraft:behavior.nearest_attackable_target','minecraft:behavior.hurt_by_target'):
            del cmp[name_]
    cmp['minecraft:type_family']['family'].append('station_lead')
    cmp['minecraft:damage_sensor']={'triggers':[{'cause':'all','deals_damage':'no'}]}
    if key=='sentinel':
        cmp['minecraft:behavior.random_stroll'].update(xz_dist=22,y_dist=1,speed_multiplier=.85)
        cmp['minecraft:navigation.walk']['can_path_over_water']=False
    else:
        cmp.pop('minecraft:behavior.random_stroll',None)
    updates[path]=encode(behavior)
    for tail in ('entity/'+eid+'.entity.json','animations/'+eid+'.animation.json'):
        updates[rp+tail]=encode(clone(rp+tail))
    gpath=rp+'models/entity/'+eid+'.geo.json'
    model=clone(gpath)
    geom=model['minecraft:geometry'][0]
    tex=rp+'textures/bearframe/'+eid+'.png'
    original=Image.open(BytesIO(old.read(rp+'textures/bearframe/'+base+'.png'))).convert('RGBA')
    atlas=Image.new('RGBA',(256,256));atlas.paste(original,(0,0))
    geom['description']['texture_height']=256
    c=Cloth(eid,geom,atlas,main,light,False)
    a=c.add
    # The chest screen, existing player-model armor coverage and base rig
    # stay legible. Regional and role cues use profile overlays.
    if key in ('auren','vera','mira','sentinel'):
        mantle={'auren':(10,13),'vera':(9,11),'mira':(8,12),'sentinel':(11,9)}[key]
        for i,(x,width) in enumerate(((-3.65,3.65),(0,3.65))):
            low=mantle[i]
            base_depth=3.98 if key=='mira' else 2.98
            a('body',x,low,base_depth,width,22.3-low,.59,'hem')
            a('body',x+.18,low+.8,base_depth+.46,.52,20.2-low,.34,'binding')
    if key=='auren':
        a('head',-2.95,30.45,-4.42,5.9,.62,.51,'binding')
        a('body',-3.12,19.2,-2.74,.6,4.15,.51,'binding')
        a('body',2.52,19.2,-2.74,.6,4.15,.51,'binding')
    elif key=='atlas':
        for side,x in (('arm0',-8.55),('arm1',3.8)):
            a(side,x,21.2,-2.47,4.75,2.6,4.87)
            a(side,x+.2,21.2,-2.69,4.3,.65,.44,'binding')
            a(side,x+.42,13.25,-2.85,3.5,2.45,.66)
    elif key in ('vera','sentinel','mira'):
        if key=='sentinel': c.main=(46,47,52)
        for x in (-4.2,3.56):
            a('head',x,30.6,.48,.62,3.45,1.49)
            a('head',x+.09,32.81,.72,.42,1.37,.71,'binding')
        if key=='mira':
            a('head',-3.05,30.8,-4.55,2.05,1.6,.75,'hem')
            a('head',1.05,30.8,-4.55,2.05,1.6,.75,'hem')
            a('body',-3.7,22.15,-2.94,7.4,1.4,5.1,'hem')
            a('body',2.1,13.3,-2.93,1.53,3.1,1.12)
        if key=='vera':
            a('body',-3.62,19.1,-2.85,.72,4.5,.44,'binding')
            a('body',2.95,19.1,-2.85,.72,4.5,.44,'binding')
        if key=='sentinel':
            north=c.bones['head']['cubes'][0]['uv']['north']
            u,v=north['uv']; w,h=north['uv_size']
            red=[]
            for yy in range(v,v+h):
                for xx in range(u,u+w):
                    r,g,b,_=atlas.getpixel((xx,yy))
                    if r>140 and r>g*1.8 and r>b*1.65: red.append((xx,yy))
            if red:
                for pt in red: atlas.putpixel(pt,(26,27,31,255))
                yy=sorted(y for _,y in red)[len(red)//2]
                ImageDraw.Draw(atlas).line((min(x for x,_ in red),yy,max(x for x,_ in red),yy),fill=(*light,255))
            a('body',-1.97,18.25,-3.47,3.94,2.47,.63,'fold')
            a('body',-.28,18.61,-3.69,.56,1.52,.36,'binding')
            a('body',-.65,18.55,-3.68,1.3,.37,.34,'binding')
            a('body',-.51,19.79,-3.68,1.02,.32,.34,'binding')
            a('body',-3.5,21.72,-2.15,7,1.05,4.6,'hem')
    else:
        a('body',-3.75,14,-2.95,1.56,3.25,1.05,'hem')
        a('head',-2.75,30.45,-4.42,5.5,.52,.48,'binding')
    for bone in geom['bones']:
        for cub in bone.get('cubes',[]):
            for uv in cub['uv'].values():
                x,y=uv['uv'];w,h=uv['uv_size']
                assert x+w<=256 and y+h<=256
    image=BytesIO();atlas.save(image,'PNG')
    updates[tex]=image.getvalue()
    updates[gpath]=encode(model)
    lang+=f'entity.bearframe:{eid}.name={name}\n'
updates[rp+'texts/en_US.lang']=lang.encode()

def replace(s,a,b):
    assert a in s,a
    return s.replace(a,b)
path=bp+'scripts/regions.js'
s=old.read(path).decode()
new_roles=[]
for key,name,base,light,main,p,wing,line in profiles:
    new_roles.append(dict(type='bearframe:city_'+key,pos=dict(zip('xyz',p)),name=name,line=line))
updates[path]=(s.rstrip()[:-2].rstrip()+',\n'+',\n'.join('  '+json.dumps(role) for role in new_roles)+'\n];\n').encode()

path=bp+'scripts/expedition.js'
s=old.read(path).decode()
prefix='const STATION_WINGS = '
start=s.index(prefix)+len(prefix)
wings,end=json.JSONDecoder().raw_decode(s[start:])
for i,profile in enumerate(profiles,11):
    wing=profile[6]
    if wing:
        next(w for w in wings if w['id']==wing)['roleIds'].append(i)
s=s[:start]+json.dumps(wings,indent=2)+s[start+end:]
s=replace(s,'for(let index=0;index<7;index++)ensureCityCrew(dim,index);','for(const index of [0,1,2,3,4,5,6,11,15])ensureCityCrew(dim,index);')
updates[path]=s.encode()

for pack in ('Bearframe_Behavior','Bearframe_Resources'):
    path=pack+'/manifest.json'
    data=json.loads(old.read(path))
    for v in [data['header'],*data['modules'],*data.get('dependencies',[])]:
        if v.get('version')==[0,6,2]:v['version']=[0,6,3]
    updates[path]=encode(data)
out=folder/'Bearframe_Bedrock_0.6.3.mcaddon'
with ZipFile(out,'w',ZIP_DEFLATED) as z:
    for path in sorted(set(old.namelist())|updates.keys()):
        z.writestr(path,updates[path] if path in updates else old.read(path))
with ZipFile(out) as z:
    assert z.testzip() is None
    for name in updates:
        if name.endswith('.js'):run(['node','--input-type=module','--check'],input=z.read(name),check=True)
        if name.endswith('.json'): json.loads(z.read(name))
    assert all(z.read(n)==old.read(n) for n in old.namelist() if n.endswith('.mcstructure'))
print('Six named leads installed with dedicated models and dialogue.')
