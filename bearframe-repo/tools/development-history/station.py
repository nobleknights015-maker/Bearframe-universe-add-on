from zipfile import ZipFile,ZIP_DEFLATED
from pathlib import Path
from copy import deepcopy
from collections import deque
import json
from bedrock_nbt import Site,blank

folder=Path('deliverables')
bp='Bearframe_Behavior/'
prefix=bp+'structures/bearframe/'
old=ZipFile(folder/'Bearframe_Bedrock_0.6.1.mcaddon')
sample=Site(old.read(prefix+'orbital_city.mcstructure'))
updates={}
def write(s,x,y,z,n):
    s.blocks[s.index(x,y,z)]=ids.setdefault(n,s.block(n)) if n not in ids else ids[n]
def box(s,x0,y0,z0,x1,y1,z1,n):
    assert 0<=x0<=x1<s.w and 0<=y0<=y1<s.h and 0<=z0<=z1<s.d
    for x in range(x0,x1+1):
        for z in range(z0,z1+1):
            for y in range(y0,y1+1):
                write(s,x,y,z,n)

parts=[
 ('orbit_commons',60,-24,51,47,12,(0,24),'west',[[22,1,19],[35,1,32]]),
 ('orbit_farfield',10,-38,35,27,10,(17,26),'south',[[11,1,12]]),
 ('orbit_operations',10,12,35,27,10,(17,0),'north',[[24,1,13]]),
]
def shell(s,door,side):
    w,d=s.w,s.d
    roof=s.h-2
    # Stepped nose corners and an enclosed pressure shell.
    for x in range(w):
        for z in range(d):
            taper=min(x+z,x+d-1-z,w-1-x+z,w+d-2-x-z)
            if taper<4: continue
            write(s,x,0,z,'polished_deepslate')
            write(s,x,1,z,'smooth_quartz' if taper>6 else 'polished_deepslate')
            edge=min(x,z,w-1-x,d-1-z)==0 or taper==4
            for y in range(2,roof):
                write(s,x,y,z,('tinted_glass' if 3<=y<=roof-3 and (x+z)%8 not in (0,1) else 'polished_deepslate') if edge else 'air')
            write(s,x,roof,z,'tinted_glass' if taper>7 and 3<(x+z)%13<10 else 'polished_deepslate')
            if (x+z)%8==0 and edge: write(s,x,roof+1,z,'smooth_quartz')
    x,z=door
    if side=='west':box(s,x,2,z-2,x,5,z+2,'air')
    else:box(s,x-1,2,z,x+1,5,z,'air')

def path(s,x0,z0,x1,z1,accent):
    box(s,x0,1,z0,x1,1,z1,accent)
    for x,z in [(x0,z0),(x1,z1)]:
        write(s,x,1,z,'sea_lantern')

def room(s,x0,z0,x1,z1,accent,prop,open_south=True):
    # Two ends connect to internal circulation. Low partitions preserve
    # long sightlines from arrivals into the working decks.
    mid=(x0+x1)//2
    box(s,x0,1,z0,x1,1,z1,accent)
    for x in range(x0,x1+1):
        for z in range(z0,z1+1):
            if x not in (x0,x1) and z not in (z0,z1):continue
            if z in (z0,z1) and abs(x-mid)<=1: continue
            write(s,x,2,z,'smooth_quartz')
            write(s,x,3,z,'tinted_glass' if (x+z)%4 else 'polished_deepslate')
    for x in range(x0+2,x1-1,3):
        write(s,x,2,z0+2,prop)
    for x,z in ((x0,z0),(x1,z0),(x0,z1),(x1,z1)):
        box(s,x,4,z,x,s.h-3,z,'polished_deepslate')
        write(s,x,5,z,'sea_lantern')

def garden(s,x0,z0,x1,z1):
    box(s,x0,2,z0,x1,2,z1,'smooth_quartz')
    box(s,x0+1,2,z0+1,x1-1,2,z1-1,'moss_block')
    for x in range(x0+1,x1,3):
        for z in range(z0+1,z1,3):
            write(s,x,3,z,'flowering_azalea' if (x+z)%2 else 'azalea')
    for x,z in ((x0,z0),(x1,z1)):
        write(s,x,3,z,'sea_lantern')

def route(s,start):
    found=set()
    q=deque([start])
    while q:
        x,z=q.popleft()
        if not (0<=x<s.w and 0<=z<s.d) or (x,z) in found: continue
        if s.get(x,1,z) in ('air','void') or s.get(x,2,z)!='air' or s.get(x,3,z)!='air':continue
        found.add((x,z))
        q.extend((x+dx,z+dz) for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)))
    return found

for key,x,z,w,d,h,door,side,roles in parts:
    s=blank(sample,w,h,d);ids={}
    shell(s,door,side)
    if key=='orbit_commons':
        path(s,0,22,47,26,'cyan_terracotta')
        path(s,23,5,27,41,'cyan_terracotta')
        garden(s,8,10,17,17)
        garden(s,8,30,17,37)
        room(s,32,5,45,18,'pink_terracotta','bookshelf')
        room(s,32,30,45,41,'purple_terracotta','lectern')
        room(s,6,3,20,7,'light_gray_terracotta','barrel')
        room(s,6,40,20,43,'light_gray_terracotta','barrel')
        for zz in (17,30):
            for xx in (22,28): box(s,xx,2,zz,xx,7,zz,'smooth_quartz')
    elif key=='orbit_farfield':
        path(s,15,3,19,26,'cyan_terracotta')
        room(s,5,5,13,20,'blue_terracotta','cartography_table')
        room(s,21,5,30,20,'light_blue_terracotta','lectern')
        for xx in (15,19):box(s,xx,2,7,xx,6,7,'oxidized_cut_copper')
        box(s,15,6,7,19,6,7,'oxidized_cut_copper')
        for xx in (8,25): write(s,xx,1,22,'sea_lantern')
    else:
        path(s,15,0,19,23,'cyan_terracotta')
        room(s,4,5,13,20,'orange_terracotta','smithing_table')
        room(s,21,5,30,20,'red_terracotta','observer')
        for xx in (16,18):
            write(s,xx,1,10,'sea_lantern')
            write(s,xx,1,17,'sea_lantern')
        for xx in (7,10): write(s,xx,2,17,'blast_furnace')
    found=route(s,door)
    assert len(found)>250,key
    for xx,_,zz in roles: assert (xx,zz) in found,(key,xx,zz)
    updates[prefix+key+'.mcstructure']=s.raw()

path=bp+'scripts/regions.js'
regions=old.read(path).decode()
roles=[
 ('city_steward',82.5,101,-4.5,'Commons Reception','The gardens and reading rooms are open every shift.'),
 ('vera_artisan',95.5,101,8.5,'Exhibition Steward','The gallery is open. The panels on display were fabricated here.'),
 ('field_researcher',21.5,101,-25.5,'Farfield Mapping Desk','We chart the approach and mark the hazards before anyone goes in.'),
 ('atlas_rigger',34.5,101,25.5,'Operations Fabrication','This bay handles the equipment that comes back from the surface.'),
]
role_entries=[dict(type='bearframe:'+kind,pos=dict(x=x,y=y,z=z),name=name,line=line) for kind,x,y,z,name,line in roles]
assert regions.rstrip().endswith('];')
updates[path]=(regions.rstrip()[:-2]+',\n'+',\n'.join(json.dumps(e) for e in role_entries)+'\n];\n').encode()

path=bp+'scripts/expedition.js'
script=old.read(path).decode()
parts_js=[
 dict(id='orbit_commons',origin=dict(x=60,y=99,z=-24),size=[51,12,47],roleIds=[7,8],link=[[59,y,z] for y in range(101,105) for z in range(-2,3)]),
 dict(id='orbit_farfield',origin=dict(x=10,y=99,z=-38),size=[35,10,27],roleIds=[9],link=[[x,y,z] for x in range(26,29) for y in range(101,105) for z in (-11,-10)]),
 dict(id='orbit_operations',origin=dict(x=10,y=99,z=12),size=[35,10,27],roleIds=[10],link=[[x,y,z] for x in range(26,29) for y in range(101,105) for z in (10,11)]),
]
s=Site(old.read(prefix+'orbital_city.mcstructure'))
for part in parts_js:
    assert all(s.get(x,1,z+11) not in ('void','air') for x,y,z in part['link'])
extension='''const STATION_WINGS = '''+json.dumps(parts_js,indent=2)+''';

function ensureCityCrew(dim,index) {
  const role=CITY_ROLES[index];
  const key="bearframe:city_crew:"+index;
  if(world.getDynamicProperty(key))return;
  const cell={x:Math.floor(role.pos.x),y:Math.floor(role.pos.y),z:Math.floor(role.pos.z)};
  if(!canSpawnAt(dim,cell,false))return;
  const e=dim.spawnEntity(role.type,role.pos);
  e.nameTag=role.name;
  e.setDynamicProperty("bearframe:city_role",index);
  world.setDynamicProperty(key,true);
}

async function buildStationWings(dim) {
  for(const wing of STATION_WINGS){
    const [w,h,d]=wing.size;
    const {origin:from}=wing;
    const to=at(from,[w-1,h-1,d-1]);
    const key="bearframe:station_wing:"+wing.id;
    const built=world.getDynamicProperty(key);
    if(!built || wing.roleIds.some(index=>!world.getDynamicProperty("bearframe:city_crew:"+index))){
      await withArea(dim,from,to,"bearframe-build-"+wing.id,()=>{
        if(!built){
          const occupied=dim.getBlocks(new BlockVolume(from,to),{excludeTypes:["minecraft:air"]},true);
          if(occupied.getCapacity())throw Error("Orbital expansion volume is occupied: "+wing.id);
          world.structureManager.place("bearframe:"+wing.id,dim,from,{includeEntities:false});
          world.setDynamicProperty(key,true);
        }
        for(const index of wing.roleIds)ensureCityCrew(dim,index);
      });
    }
    const linkKey="bearframe:station_link:"+wing.id;
    if(!world.getDynamicProperty(linkKey)){
      const first=at(CITY_ORIGIN,[0,0,0]);
      const last=at(first,[CITY_SIZE.x-1,CITY_SIZE.y-1,CITY_SIZE.z-1]);
      await withArea(dim,first,last,"bearframe-connect-"+wing.id,()=>{
        const blocks=wing.link.map(([x,y,z])=>dim.getBlock({x,y,z}));
        const safe=new Set(["minecraft:air","minecraft:tinted_glass","minecraft:polished_blackstone","minecraft:polished_deepslate","minecraft:smooth_quartz"]);
        if(blocks.some(block=>!block||!safe.has(block.typeId)))throw Error("Orbital passage is obstructed: "+wing.id);
        for(const block of blocks)if(!block.isAir)block.setType("minecraft:air");
        world.setDynamicProperty(linkKey,true);
      });
    }
  }
}

'''
i=script.index('async function buildOrbit()')
script=script[:i]+extension+script[i:]
i=script.index('    for(const [index,role] of CITY_ROLES.entries())')
j=script.index('\n}\n',i)
script=script[:i]+'''    for(let index=0;index<7;index++)ensureCityCrew(dim,index);
  });
  await buildStationWings(dim);'''+script[j:]
script=script.replace('All six department bays are active.','The Commons, Farfield annex, and Operations wing are open.')
updates[path]=script.encode()
for pack in ('Bearframe_Behavior','Bearframe_Resources'):
    path=pack+'/manifest.json'
    data=json.loads(old.read(path))
    for r in [data['header'],*data['modules'],*data.get('dependencies',[])]:
        if r.get('version')==[0,6,1]:r['version']=[0,6,2]
    updates[path]=(json.dumps(data,indent=2)+'\n').encode()
out=folder/'Bearframe_Bedrock_0.6.2.mcaddon'
with ZipFile(out,'w',ZIP_DEFLATED) as z:
    for k in sorted(set(old.namelist())|updates.keys()):
        z.writestr(k,updates[k] if k in updates else old.read(k))
from subprocess import run
with ZipFile(out) as z:
    assert z.testzip() is None
    for k in updates:
        if k.endswith('.js'):run(['node','--input-type=module','--check'],input=z.read(k),check=True)
        if k.endswith('.mcstructure'):
            s=Site(z.read(k))
            assert all(len(b)==s.w*s.h*s.d and -1<=min(b)<=max(b)<len(s.palette) for _,b in s.layers)
    for k in old.namelist():
        if k not in updates: assert old.read(k)==z.read(k)
print('Verified three station sections, link floors, visitor routing, and preserved core.')
