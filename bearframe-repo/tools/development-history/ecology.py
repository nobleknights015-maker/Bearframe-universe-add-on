from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from collections import deque
from io import BytesIO
import json
from PIL import Image
from bedrock_nbt import Site
from subprocess import run

folder=Path('deliverables')
old=ZipFile(folder/'Bearframe_Bedrock_0.7.1.mcaddon')
bp='Bearframe_Behavior/'
rp='Bearframe_Resources/'
updates={}
def enc(obj):return (json.dumps(obj,indent=2)+'\n').encode()
def replace(s,a,b):
    assert a in s,a
    return s.replace(a,b,1)
def js(n,fn):
    p=bp+'scripts/'+n
    updates[p]=fn(old.read(p).decode()).encode()
def get(path):return json.loads(updates.get(path) or old.read(path))
def rep(path,data):updates[path]=enc(data)
def target(distance):
    return {'priority':2,'must_see':True,'reselect_targets':True,
            'entity_types':[{'filters':{'test':'is_family','subject':'other','value':'player'},'max_dist':distance}]}
def goal(blocks,dist=12):
    return dict(priority=5,speed_multiplier=.8,search_range=dist,search_height=3,goal_radius=1.6,stay_duration=90,start_chance=.45,tick_interval=80,target_blocks=blocks)
def spawn(name,groups,weight,mode='animal',dark=False,ground='surface'):
    tags=[{'test':'has_biome_tag','operator':'==','value':x} for x in groups]
    condition={
      'minecraft:spawns_'+('on_surface' if ground=='surface' else 'underground'):{},
      'minecraft:weight':{'default':weight},
      'minecraft:herd':{'min_size':1,'max_size':1},
      'minecraft:density_limit':{ground:1},
      'minecraft:biome_filter':{'any_of':tags},
    }
    if dark:
        condition['minecraft:brightness_filter']={'min':0,'max':7,'adjust_for_weather':True}
        condition['minecraft:difficulty_filter']={'min':'easy','max':'hard'}
    rep(bp+'spawn_rules/'+name+'.json',{'format_version':'1.8.0','minecraft:spawn_rules':{
        'description':{'identifier':'bearframe:'+name,'population_control':mode},'conditions':[condition]}})
def clone(name,title,base,hostile=False,heavy=False,accent=None,roam=10):
    path=bp+'entities/'+name+'.json'
    def read(p):return old.read(p.replace(name,base)).decode().replace(base,name)
    data=json.loads(read(path));e=data['minecraft:entity']
    c=e['components']
    c.pop('minecraft:persistent',None)
    c['minecraft:despawn']={'despawn_from_distance':{}}
    c['minecraft:behavior.random_stroll'].update(xz_dist=roam,interval=70)
    if hostile:
        c['minecraft:type_family']['family'].append('monster')
        c['minecraft:behavior.nearest_attackable_target']=target(17 if heavy else 20)
        c['minecraft:attack']={'damage':9 if heavy else 5}
        c['minecraft:behavior.melee_attack']={'priority':3,'speed_multiplier':1.07,'track_target':True}
        c['minecraft:movement']['value']=.20 if heavy else .23
        c.pop('minecraft:interact',None)
        # An awakened variant uses an explicit targeting profile.
        e.get('events',{}).pop('minecraft:entity_spawned',None)
    if name=='echo_route_trader':
        c.pop('minecraft:attack',None)
        c.pop('minecraft:behavior.hurt_by_target',None)
        c.pop('minecraft:behavior.melee_attack',None)
        c['minecraft:behavior.avoid_mob_type']={'priority':2,'entity_types':[
            {'filters':{'test':'is_family','subject':'other','value':'monster'},'max_dist':8,'walk_speed_multiplier':1.0,'sprint_speed_multiplier':1.25}]}
        c['minecraft:behavior.move_to_block']=goal(['minecraft:bell','minecraft:campfire','minecraft:cartography_table'],12)
    if name=='grid_wayfarer':
        c['minecraft:behavior.move_to_block']=goal(['minecraft:lodestone','minecraft:lightning_rod'],15)
    rep(path,data)
    for relative in ('entity/'+name+'.entity.json','animations/'+name+'.animation.json','models/entity/'+name+'.geo.json'):
        rep(rp+relative,json.loads(read(rp+relative)))
    atlas=old.read(rp+'textures/bearframe/'+base+'.png')
    if accent:
        im=Image.open(BytesIO(atlas)).convert('RGBA')
        for y in range(im.height):
            for x in range(im.width):
                r,g,b,a=im.getpixel((x,y))
                lit=(g>125 and b>120 and min(g,b)>r+35) if heavy else (max(r,b)>145 and abs(r-g)>38 and b>g+28)
                if lit:im.putpixel((x,y),(*accent,a))
        b=BytesIO();im.save(b,'PNG');atlas=b.getvalue()
    updates[rp+'textures/bearframe/'+name+'.png']=atlas
    return f'entity.bearframe:{name}.name={title}\nitem.spawn_egg.entity.bearframe:{name}.name=Spawn {title}\n'
lang=rp+'texts/en_US.lang'
s=old.read(lang).decode().rstrip()+'\n'
s+=clone('echo_route_trader','Echo Route Trader','echo_drifter',accent=(110,219,204),roam=15)
s+=clone('echo_lost','Lost Echo','echo_drifter',hostile=True,accent=(236,111,97),roam=8)
s+=clone('grid_wayfarer','Legacy Route Guardian','grid_guardian',heavy=True,roam=13)
s+=clone('grid_breach_guard','Grid Breach Guardian','grid_guardian',hostile=True,heavy=True,accent=(240,124,60),roam=10)
updates[lang]=s.encode()

spawn('echo_route_trader',['plains','taiga','forest','savanna'],3)
spawn('echo_lost',['forest','taiga','plains','hills','swamp'],17,'monster',True)
path=bp+'spawn_rules/echo_lost.json'
data=get(path)
c=dict(data['minecraft:spawn_rules']['conditions'][0])
c.pop('minecraft:spawns_on_surface')
c['minecraft:spawns_underground']={}
c['minecraft:density_limit']={'underground':2}
c['minecraft:weight']={'default':13}
data['minecraft:spawn_rules']['conditions'].append(c)
rep(path,data)
spawn('grid_repair_crawler',['forest','mesa','hills'],4)
spawn('grid_wayfarer',['plains','forest','mesa','savanna'],2)
spawn('grid_breach_guard',['mesa','hills','forest','taiga'],4,'monster',True,'underground')

# Ordinary site residents seek workstations, while utility machines follow
# the infrastructure that matches their role.
for name,blocks in {
 'ward_resident':['minecraft:smithing_table','minecraft:lectern','minecraft:crafting_table','minecraft:cartography_table'],
 'grid_repair_crawler':['minecraft:anvil','minecraft:lodestone','minecraft:blast_furnace'],
 'grid_protocol_keeper':['minecraft:lodestone','minecraft:lectern','minecraft:observer'],
 'grid_hauler':['minecraft:barrel','minecraft:blast_furnace'],
}.items():
    path=bp+'entities/'+name+'.json'
    data=get(path);c=data['minecraft:entity']['components']
    c['minecraft:behavior.move_to_block']=goal(blocks)
    rep(path,data)

# Keep ambient wanderers from remaining everywhere forever, while preserving
# any resident of the same type after the structure script names its region.
for name in ('echo_drifter','grid_watcher','echo_route_trader','grid_wayfarer','echo_lost','grid_breach_guard','grid_repair_crawler'):
    path=bp+'entities/'+name+'.json'
    data=get(path); e=data['minecraft:entity']
    if name in ('echo_drifter','grid_watcher','echo_route_trader','grid_repair_crawler'):
        e['components'].pop('minecraft:persistent',None)
        e['components']['minecraft:despawn']={'despawn_from_distance':{}}
    e.setdefault('component_groups',{})['bearframe:site_resident']={'minecraft:persistent':{}}
    e['events']['bearframe:settle']={'add':{'component_groups':['bearframe:site_resident']}}
    rep(path,data)

# Build optional, deterministic residents from walkable areas in each ruin.
# Different coordinates and world seeds can give staffed, empty or dangerous
# rooms without respawning everyone each time a player passes the entrance.
p=bp+'scripts/surface_sites.js'
script=old.read(p).decode()
i=script.index('const crews=')+len('const crews=')
crews,_=json.JSONDecoder().raw_decode(script[i:])
wild={
 'sealed_archive_bunker':['ward_resident','grid_protocol_keeper'],
 'flooded_pump_bunker':['grid_repair_crawler','grid_breach_guard'],
 'collapsed_transit_bunker':['echo_lost','grid_breach_guard'],
 'rootbound_service_bunker':['echo_route_trader','grid_protocol_keeper','echo_lost'],
 'overgrown_colony':['ward_resident','echo_route_trader','echo_lost'],
 'collapsed_rail_settlement':['echo_lost','grid_wayfarer'],
 'lost_waystation':['echo_route_trader','ward_resident'],
 'frontier_colony':['ward_resident','echo_route_trader'],
 'coalition_city':['ward_resident','echo_route_trader','grid_repair_crawler'],
 'colony_waystation':['echo_route_trader','grid_repair_crawler'],
 'frontier_ruin':['echo_lost','echo_route_trader'],
 'rainline_town':['ward_resident','echo_route_trader','grid_repair_crawler'],
 'saltline_town':['echo_route_trader','echo_lost'],
 'echo_ward':['ward_resident','echo_route_trader'],
 'grid_hub':['grid_wayfarer','grid_protocol_keeper'],
 'foundry_annex':['grid_wayfarer','grid_repair_crawler'],
 'verdantis_station':['ward_resident','echo_route_trader'],
 'relay_nine':['grid_wayfarer','grid_protocol_keeper'],
}
plans={}
for key,pool in wild.items():
    site=Site(old.read(bp+'structures/bearframe/'+key+'_site.mcstructure'))
    floor=13 if key in ('rainline_town','saltline_town','echo_ward','grid_hub','foundry_annex') else 3
    occupied=[(x,z) for _,x,_,z in crews.get(key,[])]
    mx,mz=site.w//2,site.d//2
    starts=deque([(mx,0),(0,mz),(mx,site.d-1),(site.w-1,mz)])
    seen=set()
    def free(x,z,h):
        return 0<=x<site.w and 0<=z<site.d and site.get(x,floor,z) not in ('air','void','water','lava') and all(site.get(x,y,z)=='air' for y in range(floor+1,floor+h+1))
    while starts:
        x,z=starts.popleft()
        if (x,z) in seen or not free(x,z,2):continue
        seen.add((x,z))
        starts.extend([(x+1,z),(x-1,z),(x,z+1),(x,z-1)])
    available=[]
    for x,z in seen:
        if not (4<=x<site.w-4 and 4<=z<site.d-4):continue
        if any(abs(a-x)+abs(b-z)<5 for a,b in occupied):continue
        if all(free(x+dx,z+dz,3) for dx,dz in ((0,0),(1,0),(-1,0),(0,1),(0,-1))):
            available.append((abs(x-mx)+abs(z-mz),x,z))
    chosen=[]
    for _,x,z in sorted(available):
        if any(abs(a-x)+abs(b-z)<9 for a,_,b in chosen):continue
        chosen.append([x,floor+1,z])
        if len(chosen)==3:break
    assert chosen,key
    plans[key]={'pool':pool,'spots':chosen}

def surface(s):
    s='import {populateRuin,retainResident} from "./ecology.js";\n'+s
    s=replace(s,'frame.setDynamicProperty("bearframe:region_role",site.id);','frame.setDynamicProperty("bearframe:region_role",site.id);\n          retainResident(frame);')
    return replace(s,'      return base;','      populateRuin(dim,site.id,base);\n      return base;')
js('surface_sites.js',surface)
def expedition(s):
    s='import {populateBuriedSite,retainResident,fieldInteraction} from "./ecology.js";\n'+s
    s=replace(s,'  const primaryKey="bearframe:crew:"+keyAt(pos);','  populateBuriedSite(site,at);\n  const primaryKey="bearframe:crew:"+keyAt(pos);')
    s=s.replace('entity.setDynamicProperty("bearframe:region_role",def.id);','entity.setDynamicProperty("bearframe:region_role",def.id);\n        retainResident(entity);')
    return replace(s,'    const {player,target}=event;\n    const staff=', '    const {player,target}=event;\n    if(fieldInteraction(player,target))return;\n    const staff=')
js('expedition.js',expedition)
def living(s):
    s='import {fieldInteraction} from "./ecology.js";\n'+s
    return replace(s,'    const isCityStaff=typeof target.getDynamicProperty("bearframe:city_role")==="number";','    if(fieldInteraction(player,target))return;\n    const isCityStaff=typeof target.getDynamicProperty("bearframe:city_role")==="number";')
js('living_world.js',living)
def main(s):
    s='import {installEcology,retainResident} from "./ecology.js";\n'+s
    s=replace(s,'    dim.spawnEntity(ACTOR_TYPES[role],{x:pos.x+.5,y:pos.y,z:pos.z+.5});','    retainResident(dim.spawnEntity(ACTOR_TYPES[role],{x:pos.x+.5,y:pos.y,z:pos.z+.5}));')
    s=s.replace('loc.x)-21','loc.x)-40').replace('loc.z)-21','loc.z)-40').replace('loc.x)+21','loc.x)+40').replace('loc.z)+21','loc.z)+40')
    return s+'\ninstallEcology();\n'
js('main.js',main)
def campaign(s):
    s='import {fieldProgress} from "./ecology.js";\n'+s
    return replace(s,'  const state=read(player);\n  const fresh=applySignal','  fieldProgress(player,type,id,place);\n  const state=read(player);\n  const fresh=applySignal')
js('campaign.js',campaign)
updates[bp+'scripts/ecology.js']=('const HABITATS='+json.dumps(plans,indent=2)+';\n'+Path('campaign_src/ecology.js').read_text()).encode()

for pack in ('Bearframe_Behavior','Bearframe_Resources'):
    path=pack+'/manifest.json'
    data=get(path)
    for row in [data['header'],*data['modules'],*data.get('dependencies',[])]:
        if row.get('version')==[0,7,1]:row['version']=[0,7,2]
    rep(path,data)
out=folder/'Bearframe_Bedrock_0.7.2.mcaddon'
with ZipFile(out,'w',ZIP_DEFLATED) as z:
    for path in sorted(set(old.namelist())|updates.keys()):
        z.writestr(path,updates[path] if path in updates else old.read(path))
with ZipFile(out) as z:
    assert z.testzip() is None
    for p in updates:
        if p.endswith('.js'):run(['node','--input-type=module','--check'],input=z.read(p),check=True)
        if p.endswith('.json'):json.loads(z.read(p))
    for p in old.namelist():
        if p not in updates:assert z.read(p)==old.read(p)
print(f'Validated {len(plans)} variable ruin habitats and four new unit registrations.')
