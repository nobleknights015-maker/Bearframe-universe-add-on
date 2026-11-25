from collections import deque,Counter
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json
from bedrock_nbt import Site

base=Path('deliverables')
old=ZipFile(base/'Bearframe_Bedrock_0.6.3.mcaddon')
bp='Bearframe_Behavior/'
root=bp+'structures/bearframe/'
updates={}
categories={
 'settlement':[(2,3),('bread',7,1,4),('wheat_seeds',6,2,6),('potato',4,1,3),('torch',5,2,6),('paper',3,1,4),('iron_nugget',2,2,5)],
 'expedition':[(2,4),('torch',7,3,9),('cooked_beef',5,1,3),('paper',5,2,6),('copper_ingot',4,1,3),('compass',1,1,1),('bearframe:salvaged_alloy',2,1,2)],
 'industrial':[(2,4),('rail',8,3,10),('coal',7,2,5),('torch',5,3,8),('copper_ingot',5,1,4),('iron_ingot',3,1,2),('redstone',3,2,5),('bearframe:salvaged_alloy',2,1,2)],
 'bunker':[(2,4),('torch',7,4,9),('bread',6,1,3),('redstone',5,2,5),('iron_ingot',4,1,3),('book',3,1,2),('bearframe:salvaged_alloy',2,1,2)],
 'archive':[(2,4),('paper',7,3,9),('book',6,1,3),('torch',5,2,6),('amethyst_shard',4,1,3),('compass',2,1,1),('iron_ingot',3,1,3),('bearframe:legacy_cell',1,1,1)],
 'overgrown':[(2,3),('melon_seeds',6,1,4),('bone_meal',5,1,4),('glow_berries',5,1,5),('torch',4,2,5),('iron_nugget',4,2,6),('bearframe:salvaged_alloy',2,1,2)],
}
roles={
 'farfield_camp':'expedition','grid_hub':'industrial','echo_ward':'archive','intrusion_checkpoint':'expedition',
 'foundry_annex':'industrial','maintenance_relay':'industrial','rainline_town':'settlement','saltline_town':'settlement',
 'frontier_colony':'settlement','colony_waystation':'expedition','coalition_city':'settlement','crashed_skiff':'expedition',
 'relay_nine':'archive','frontier_ruin':'archive','syndicate_forge':'industrial','cinder_works':'industrial',
 'nivalis_lab':'archive','verdantis_station':'overgrown','shattered_array':'archive','sealed_archive_bunker':'archive',
 'flooded_pump_bunker':'bunker','collapsed_transit_bunker':'bunker','rootbound_service_bunker':'overgrown',
 'overgrown_colony':'overgrown','collapsed_rail_settlement':'industrial','lost_waystation':'overgrown',
 'shelter_bunker':'bunker','spillway_facility':'industrial',
}
big={'rainline_town','saltline_town','frontier_colony','coalition_city','overgrown_colony','collapsed_rail_settlement'}
large_core={'farfield_camp','grid_hub','echo_ward','intrusion_checkpoint','foundry_annex','maintenance_relay','rainline_town','saltline_town'}
dirs=((1,0,'east'),(-1,0,'west'),(0,1,'south'),(0,-1,'north'))
passable={'air','void'}
tools={'crafting_table','cartography_table','smithing_table','anvil','blast_furnace','lectern','smoker','barrel','composter','lodestone'}

def encode(value):return (json.dumps(value,indent=2)+'\n').encode()
for key,(rolls,*items) in categories.items():
    entries=[{'type':'item','name':k if ':' in k else 'minecraft:'+k,'weight':weight,
              'functions':[{'function':'set_count','count':{'min':lo,'max':hi}}]} for k,weight,lo,hi in items]
    updates[bp+'loot_tables/chests/bearframe_'+key+'.json']=encode({'pools':[{'rolls':{'min':rolls[0],'max':rolls[1]},'entries':entries}]})

script=old.read(bp+'scripts/surface_sites.js').decode()
i=script.index('const crews=')+len('const crews=')
crews,_=json.JSONDecoder().raw_decode(script[i:])
def room_positions(s,y,arrivals):
    def valid(x,z):
        return 0<=x<s.w and 0<=z<s.d and s.get(x,y-1,z) not in passable|{'water','lava'} and s.get(x,y,z) in passable and s.get(x,y+1,z) in passable
    def flood(starts,blocked):
        reached=set()
        q=deque(starts)
        while q:
            x,z=q.popleft()
            p=(x,z)
            if p in reached or p in blocked or not valid(x,z):continue
            reached.add(p)
            q.extend((x+dx,z+dz) for dx,dz,_ in dirs)
        return reached
    return flood(arrivals,set()),flood
def pick(s,y,key,amount,arrivals):
    reached,flood=room_positions(s,y,arrivals)
    protected={(x,z) for _,x,y0,z in crews.get(key,[]) if y0==y}
    for i,n in enumerate(s.blocks):
        x,y0,z=s.xyz(i)
        if y0==y and s.label(n) in tools:
            protected.update((x+dx,z+dz) for dx,dz,_ in dirs if (x+dx,z+dz) in reached)
    picked=[]
    for x,z in sorted(reached):
        if (x,z) in protected or not (2<x<s.w-3 and 2<z<s.d-3):continue
        if s.get(x,y,z)!='air' or s.get(x,y+1,z)!='air':continue
        if not any(s.get(x,h,z) not in passable for h in range(y+2,min(s.h,y+7))):continue
        adjacent=[(dx,dz,face) for dx,dz,face in dirs if (x+dx,z+dz) in reached]
        if len(adjacent) not in (2,3):continue
        backed=[(dx,dz,face) for dx,dz,face in adjacent if s.get(x-dx,y,z-dz) not in passable|tools|{'water'}]
        if not backed:continue
        pick_face=backed[0][2]
        # Prefer actual rooms with useful blocks nearby and a back wall.
        utility=sum(s.get(xx,y,zz) in tools for xx in range(x-2,x+3) for zz in range(z-2,z+3))
        if key in ('spillway_facility','shelter_bunker') and x>s.w-17:utility+=3
        picked.append((utility*10+((x*31+z*17)%10),x,z,pick_face))
    blocked=set()
    result=[]
    for _,x,z,face in sorted(picked,reverse=True):
        if any(abs(x-u)+abs(z-v)<12 for u,v in blocked):continue
        if (x,z) in arrivals:continue
        trial=blocked|{(x,z)}
        if flood(arrivals,trial)!=reached-trial:continue
        blocked=trial
        result.append((x,y,z,face))
        if len(result)==amount:break
    return result

counts={}
for key,kind in roles.items():
    is_deep=key in ('spillway_facility','shelter_bunker')
    path=root+key+('' if is_deep else '_site')+'.mcstructure'
    s=Site(old.read(path))
    y=5 if key=='spillway_facility' else 9 if key=='shelter_bunker' else 14 if key in large_core else 4
    starts=[(47,18)] if key=='spillway_facility' else [(33,11)] if key=='shelter_bunker' else [(s.w//2,0),(0,s.d//2),(s.w//2,s.d-1),(s.w-1,s.d//2)]
    number=3 if key in big else 1 if key=='crashed_skiff' else 2
    locations=pick(s,y,key,number,starts)
    assert locations,key
    counts[key]=len(locations)
    for x,y,z,face in locations:
        i=s.index(x,y,z)
        assert str(i) not in s.metadata
        s.blocks[i]=s.block('minecraft:chest',{'minecraft:cardinal_direction':(8,face)})
        s.metadata[str(i)]=(10,{'block_entity_data':(10,{
            'id':(8,'Chest'),'x':(3,x),'y':(3,y),'z':(3,z),'isMovable':(1,1),
            'LootTable':(8,'loot_tables/chests/bearframe_'+kind+'.json'),
            'LootTableSeed':(3,0),
        })})
    updates[path]=s.raw()
for pack in ('Bearframe_Behavior','Bearframe_Resources'):
    path=pack+'/manifest.json'
    data=json.loads(old.read(path))
    for row in [data['header'],*data['modules'],*data.get('dependencies',[])]:
        if row.get('version')==[0,6,3]:row['version']=[0,6,4]
    updates[path]=encode(data)
out=base/'Bearframe_Bedrock_0.6.4.mcaddon'
with ZipFile(out,'w',ZIP_DEFLATED) as z:
    for path in sorted(set(old.namelist())|updates.keys()):
        z.writestr(path,updates[path] if path in updates else old.read(path))
with ZipFile(out) as z:
    assert z.testzip() is None
    entries=set(z.namelist())
    for path in updates:
        if path.endswith('.json'):json.loads(z.read(path))
        if not path.endswith('.mcstructure'):continue
        before=Site(old.read(path)); after=Site(z.read(path))
        assert all(after.metadata[k]==v for k,v in before.metadata.items())
        for i in after.metadata.keys()-before.metadata.keys():
            b=after.metadata[i][1]['block_entity_data'][1]
            assert bp+b['LootTable'][1] in entries
            assert after.label(after.blocks[int(i)])=='chest'
    assert all(z.read(k)==old.read(k) for k in old.namelist() if k not in updates)
print(sum(counts.values()),'chests across',len(counts),'sites;',Counter(counts.values()))
