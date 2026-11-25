from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from collections import deque
from copy import deepcopy
import json,re
from bedrock_nbt import Site,blank
exec(compile(Path('structures.py').read_text().split('def container_loot')[0].split('for name,plan in existing.items():')[0], 'structures.py','exec'))
old.close()
old=ZipFile(folder/'Bearframe_Bedrock_0.5.0.mcaddon')
output=folder/'Bearframe_Bedrock_0.5.1.mcaddon'
updates={}
removed={bp+'spawn_rules/'+n+'.json' for n in ('nullframe_hunter','hollow_scout')}

def enc(obj): return (json.dumps(obj,indent=2)+'\n').encode()
def change(path,fn):
    updates[bp+path]=enc(fn(json.loads(old.read(bp+path))))
def js(path,fn):
    updates[bp+'scripts/'+path]=fn(old.read(bp+'scripts/'+path).decode()).encode()
def replace(s,old,new):
    assert old in s,old
    return s.replace(old,new)

# Keep site silhouettes and functional fixtures while reclaiming exposed
# wall feet and roof edges. Use intentional growth clusters, not random flats.
masonry={'stone_bricks','polished_andesite','smooth_quartz','cut_sandstone','smooth_sandstone','calcite','deepslate_bricks','polished_deepslate','polished_blackstone_bricks'}
def weather(site,deck,variant=0,settlement=False):
    old_blocks=site.blocks.copy()
    def was(x,y,z):
        return site.label(old_blocks[site.index(x,y,z)])
    for x in range(1,site.w-1):
        for z in range(1,site.d-1):
            # Leave three-wide travel axes, scripted stations, and sealed rooms alone.
            outside=abs(x-site.w//2)>2 and abs(z-site.d//2)>2
            if not outside:
                continue
            azimuth=(x+2*z+variant)%13
            if azimuth<4 and was(x,deck,z) in masonry and was(x,deck+1,z)=='air':
                put(site,x,deck,z,'mossy_stone_bricks' if azimuth!=0 else 'moss_block')
            for y in range(deck+1,site.h-1):
                block=was(x,y,z)
                if block not in masonry:
                    continue
                outer=any(was(x+dx,y,z+dz) in OPEN for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)))
                if outer and azimuth<=3 and y<=deck+3:
                    put(site,x,y,z,'mossy_stone_bricks' if azimuth<=1 else 'cracked_deepslate_tiles')
                if settlement and y>=deck+4 and azimuth in (1,2) and was(x,y+1,z) in OPEN:
                    put(site,x,y+1,z,'moss_block',OPEN)

def growth(site,deck,points):
    for x,z in points:
        if not (1<x<site.w-2 and 1<z<site.d-2):
            continue
        for xx,zz in ((x,z),(x+1,z),(x,z+1)):
            if site.get(xx,deck,zz) not in OPEN and site.get(xx,deck+1,zz) in OPEN:
                put(site,xx,deck,zz,'moss_block')
                if (xx,zz)!=(x,z):
                    continue
                for y in (deck+1,deck+2):
                    if site.get(xx,y,zz) in OPEN:
                        put(site,xx,y,zz,'mangrove_roots')
                put(site,xx,deck+3,zz,'moss_block',OPEN)
                for dx,dz in ((1,0),(0,1),(-1,0),(0,-1)):
                    put(site,xx+dx,deck+3,zz+dz,'moss_block',OPEN)

settlements={
 'frontier_colony':[(2,6),(26,19)],
 'colony_waystation':[(2,5),(20,16)],
 'coalition_city':[(2,8),(30,21)],
 'frontier_ruin':[(6,7),(20,19)],
 'relay_nine':[(3,13),(19,15)],
 'crashed_skiff':[(4,5),(20,16)],
 'verdantis_station':[(3,14),(23,7)],
}
crew_types={
 'frontier_colony':['ward_resident','echo_drifter','grid_repair_crawler'],
 'colony_waystation':['echo_drifter','grid_hauler'],
 'coalition_city':['ward_resident','echo_drifter','grid_repair_crawler','grid_watcher'],
 'frontier_ruin':['echo_drifter','echo_sentinel'],
 'relay_nine':['grid_protocol_keeper','grid_repair_crawler'],
 'crashed_skiff':['echo_drifter','grid_watcher'],
 'syndicate_forge':['grid_hauler','grid_repair_crawler'],
 'cinder_works':['grid_hauler','grid_watcher'],
 'nivalis_lab':['grid_protocol_keeper','echo_drifter'],
 'verdantis_station':['echo_drifter','grid_repair_crawler'],
 'shattered_array':['grid_walker','grid_watcher'],
}
for key in crew_types:
    path=sp+key+'_site.mcstructure'
    site=Site(old.read(path))
    weather(site,3,len(key)%7,key in settlements)
    if key in settlements:
        growth(site,3,settlements[key])
    reachable(site)
    updates[path]=site.raw()

for key in ('rainline_town_site','saltline_town_site','echo_ward_site','grid_hub_site','foundry_annex_site','maintenance_relay_site'):
    path=sp+key+'.mcstructure'
    site=Site(old.read(path))
    weather(site,13,3,True)
    updates[path]=site.raw()

variant_specs={
 'sealed_archive_bunker':('forest',32,'archive',['ward_resident','grid_protocol_keeper']),
 'flooded_pump_bunker':('swamp',37,'flooded',['grid_watcher','grid_repair_crawler']),
 'collapsed_transit_bunker':('hills',39,'collapsed',['echo_drifter','echo_sentinel']),
 'rootbound_service_bunker':('taiga',34,'rootbound',['echo_drifter','grid_repair_crawler']),
 'overgrown_colony':('forest',37,'frontier_colony',['ward_resident','echo_drifter','grid_repair_crawler']),
 'collapsed_rail_settlement':('mesa',44,'coalition_city',['echo_drifter','grid_hauler','grid_watcher']),
 'lost_waystation':('jungle',39,'colony_waystation',['ward_resident','grid_protocol_keeper','grid_repair_crawler']),
}

def bunker(site,style):
    deck(site,'woods')
    theme={'archive':('polished_deepslate','stone_bricks','mossy_stone_bricks','cyan_terracotta'),
           'flooded':('polished_deepslate','deepslate_bricks','oxidized_cut_copper','cyan_terracotta'),
           'collapsed':('cracked_deepslate_tiles','stone_bricks','mossy_stone_bricks','yellow_terracotta'),
           'rootbound':('mossy_stone_bricks','mud_bricks','moss_block','cyan_terracotta')}[style]
    # Twin rooms with a low defensive profile. Each connects to the lit
    # central trench and the four dry approach lanes.
    if style=='archive':
        shop(site,3,3,21,9,*theme,door='south',height=5)
        for x in (8,16):
            box(site,x,4,4,x,6,6,'polished_deepslate')
    elif style=='flooded':
        shop(site,3,3,10,9,*theme,door='south',height=3)
        shop(site,14,3,21,9,*theme,door='south')
    elif style=='collapsed':
        shop(site,3,3,10,9,*theme,door='south')
        shop(site,14,3,21,9,*theme,door='south')
    else:
        shop(site,3,3,10,9,*theme,door='south',height=3)
        shop(site,14,13,21,18,*theme,door='north')
    walk(site,3,10,21,12,'deepslate_tiles')
    prop(site,5,5,'lectern')
    if style=='archive':
        for x in (5,7,9):
            prop(site,x,7,'chiseled_bookshelf')
        prop(site,17,6,'barrel')
        prop(site,19,6,'smithing_table')
        box(site,3,9,4,9,10,5,'moss_block')
        box(site,15,9,4,20,9,5,'moss_block')
    elif style=='flooded':
        # Isolated sump with a complete retaining wall and an observation rim.
        walk(site,16,14,22,19,'deepslate_tiles')
        box(site,16,4,14,22,4,19,'polished_deepslate')
        box(site,17,4,15,21,4,18,'water')
        prop(site,5,6,'barrel')
        prop(site,17,6,'blast_furnace')
        for x in (17,21): post(site,x,13,7,'oxidized_cut_copper','sea_lantern')
    elif style=='collapsed':
        box(site,15,8,4,18,9,7,'air')
        for x,y,z in ((15,4,5),(16,4,5),(16,5,5),(17,4,6),(19,4,4)):
            put(site,x,y,z,'tuff')
        prop(site,19,7,'barrel')
        for x,z in ((17,15),(20,15),(21,17)):
            post(site,x,z,5,'cracked_deepslate_tiles','moss_block')
    else:
        growth(site,3,[(5,14),(19,16),(2,7),(22,6)])
        box(site,4,9,4,8,10,6,'moss_block')
        box(site,5,8,8,8,8,8,'moss_block')
        prop(site,6,5,'barrel')
        prop(site,18,16,'smithing_table')

layout=[]
new_names={}
original_marker=old.read(sp+'farfield_camp.mcstructure')
for index,(key,(biome,spacing,style,crew)) in enumerate(variant_specs.items()):
    if style in settlements:
        site=Site(old.read(sp+style+'_site.mcstructure'))
        weather(site,3,index+6,True)
        if key=='overgrown_colony':
            box(site,18,9,16,24,11,20,'air',{'glass','weathered_cut_copper'})
            growth(site,3,[(11,16),(16,19),(15,7),(26,4)])
        elif key=='collapsed_rail_settlement':
            box(site,24,10,5,27,13,8,'air')
            box(site,22,9,20,26,10,24,'air')
            box(site,24,7,24,26,8,25,'air')
            for x,z in ((26,24),(27,24),(27,25),(28,26),(23,26)):
                prop(site,x,z,'tuff')
            box(site,23,4,22,24,4,22,'tuff',OPEN)
            walk(site,9,13,13,13,'polished_deepslate')
            walk(site,10,15,13,15,'polished_deepslate')
            growth(site,3,[(6,15),(26,15)])
        else:
            box(site,6,8,13,11,8,13,'air',{'weathered_cut_copper'})
            growth(site,3,[(3,15),(18,16),(20,4)])
    else:
        site=blank(Site(original_marker),25,14,21)
        bunker(site,style)
        for i,block in enumerate(site.blocks):
            if site.label(block)=='barrel':
                x,y,z=site.xyz(i)
                site.metadata[str(i)]=(10,{'block_entity_data':(10,{'id':(8,'Barrel'),'x':(3,x),'y':(3,y),'z':(3,z),'isMovable':(1,1),
                    'LootTable':(8,'loot_tables/structures/relay_nine.json'),'LootTableSeed':(4,0)})})
    reachable(site)
    crew_types[key]=crew
    updates[sp+key+'_site.mcstructure']=site.raw()
    marker=Site(original_marker)
    b=marker.palette[marker.blocks[0]]
    b['name']=(8,'bearframe:legacy_survey')
    b['states'][1]['bearframe:site']=(3,index)
    updates[sp+key+'.mcstructure']=marker.raw()
    for category in ('structures','template_pools','structure_sets'):
        disk=bp+'worldgen/'+category+'/'
        data=json.loads(old.read(disk+'farfield_camp.json').decode().replace('farfield_camp',key))
        if category=='structures': data['minecraft:jigsaw']['biome_filters'][0]['value']=biome
        if category=='structure_sets': data['minecraft:structure_set']['placement'].update(salt=1009930+index*13,spacing=spacing,separation=spacing//2)
        updates[disk+key+'.json']=enc(data)
    layout.append(dict(id=key,size=dict(x=site.w,y=site.h,z=site.d),deck=3))
    new_names[key]=key.replace('_',' ').title()

# Choose durable, unique, walkable locations from the authored roads. Runtime
# checks still apply so loaded blocks or player edits cannot trap a spawn.
crew_layout={}
for key,crew in crew_types.items():
    path=sp+key+'_site.mcstructure'
    site=Site(updates[path])
    midx,midz=site.w//2,site.d//2
    positions=[]
    found=set()
    q=deque([(midx,0)])
    while q:
        x,z=q.popleft()
        if (x,z) in found or not(0<=x<site.w and 0<=z<site.d): continue
        if site.get(x,3,z) in OPEN or any(site.get(x,y,z) not in OPEN for y in (4,5)): continue
        found.add((x,z))
        q.extend((x+dx,z+dz) for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)))
    options=sorted([p for p in found if 2<=p[0]<site.w-2 and 2<=p[1]<site.d-2],key=lambda p:(abs(p[0]-midx)+abs(p[1]-midz),p))
    for i,unit in enumerate(crew):
        x,z=next(p for p in options if all(abs(p[0]-a)+abs(p[1]-b)>=4 for a,b in positions))
        positions.append((x,z))
    crew_layout[key]=[[unit,x,4,z] for unit,(x,z) in zip(crew,positions,strict=True)]

path=bp+'blocks/surface_survey.json'
data=json.loads(old.read(path))
desc=data['minecraft:block']['description']
desc['identifier']='bearframe:legacy_survey'
desc['states']['bearframe:site']=list(range(len(layout)))
updates[bp+'blocks/legacy_survey.json']=enc(data)
js('surface_layout.js',lambda s:s+'\nexport const LEGACY_DATUM="bearframe:legacy_survey";\nexport const LEGACY_SITES='+json.dumps(layout,indent=2)+';\n')
def placement(s):
    s=replace(s,'SURFACE_DONE,SURFACE_SITES','SURFACE_DONE,SURFACE_SITES,LEGACY_DATUM,LEGACY_SITES')
    s=replace(s,'const mineral=', 'const crews='+json.dumps(crew_layout,indent=2)+';\nconst isDatum=id=>id===SURFACE_DATUM||id===LEGACY_DATUM;\n\nconst mineral=')
    s=replace(s,'block.typeId!==SURFACE_DATUM','!isDatum(block.typeId)')
    s=replace(s,'b?.typeId===SURFACE_DATUM&&','isDatum(b?.typeId)&&')
    s=replace(s,'...clear,SURFACE_DATUM]','...clear,SURFACE_DATUM,LEGACY_DATUM]')
    s=replace(s,'const site=SURFACE_SITES[marker.permutation.getState("bearframe:site")];','const sites=marker.typeId===LEGACY_DATUM?LEGACY_SITES:SURFACE_SITES;\n  const site=sites[marker.permutation.getState("bearframe:site")];')
    s=replace(s,'if(marker.typeId===SURFACE_DATUM)marker.setPermutation(marker.permutation.withState(SURFACE_DONE,true));','''if(isDatum(marker.typeId))marker.setPermutation(marker.permutation.withState(SURFACE_DONE,true));
      // The placement and spawn run synchronously. Mark the successful build
      // before spawning so a failed mob cannot cause a duplicate structure.
      for(const [unit,x,y,z] of crews[site.id]??[]){
        const pos=at(base,[x,y,z]);
        const feet=dim.getBlock(pos);
        if(!feet?.isAir||!feet.above()?.isAir||feet.below()?.isLiquid||feet.below()?.isAir)continue;
        try{
          const frame=dim.spawnEntity("bearframe:"+unit,{x:pos.x+.5,y:pos.y,z:pos.z+.5});
          frame.setDynamicProperty("bearframe:region_role",site.id);
        }catch(error){
          console.warn("Bearframe resident spawn at "+site.id+": "+error);
        }
      }''')
    return s
js('surface_sites.js',placement)
js('main.js',lambda s:replace(replace(replace(s,'SURFACE_DATUM,SURFACE_DONE','SURFACE_DATUM,SURFACE_DONE,LEGACY_DATUM'),'SPILLWAY_MARKER,SURFACE_DATUM]}','SPILLWAY_MARKER,SURFACE_DATUM,LEGACY_DATUM]}'),'marker?.typeId===SURFACE_DATUM){','marker?.typeId===SURFACE_DATUM||marker?.typeId===LEGACY_DATUM){'))
js('regions.js',lambda s:replace(s,'[-2,1,-3],hover:true','[-2,0,-3]'))
js('living_world.js',lambda s:replace(s,'A hovering legacy terminal that polls obsolete site permissions.','A walking legacy custodian that polls obsolete site permissions.'))
js('ruins.js',lambda s:replace(replace(s,'panel:"minecraft:cartography_table",actor:"bearframe:directorate_officer"','panel:"minecraft:cartography_table",actor:"bearframe:ward_resident"'),'''     {type:"bearframe:nullframe_hunter",offset:[-4,0,-3],hostile:true},
     {type:"bearframe:hollow_breacher",offset:[-2,0,4],hostile:true}''','''     {type:"bearframe:echo_drifter",offset:[-4,0,-3]},
     {type:"bearframe:grid_repair_crawler",offset:[-2,0,4]}'''))

def wandering(key,biomes,weight):
    path=bp+'spawn_rules/'+key+'.json'
    src=old.read(path if path in old.namelist() else bp+'spawn_rules/echo_drifter.json')
    model=json.loads(src)
    rule=model['minecraft:spawn_rules']
    rule['description']['identifier']='bearframe:'+key
    rule['description']['population_control']='animal'
    c=rule['conditions'][0]
    c['minecraft:weight']['default']=weight
    c['minecraft:biome_filter']['any_of']=[dict(test='has_biome_tag',operator='==',value=b) for b in biomes]
    c['minecraft:density_limit']['surface']=1
    updates[path]=enc(model)

wandering('echo_drifter',['taiga','forest','plains','hills'],7)
wandering('grid_watcher',['forest','swamp','plains','mesa'],5)
# Persistent components are still needed for individual site residents;
# keep natural spawns limited to the two existing roamers.
for pack in ('Bearframe_Behavior','Bearframe_Resources'):
    path=pack+'/manifest.json'
    data=json.loads(old.read(path))
    for entry in [data['header'],*data['modules'],*data.get('dependencies',[])]:
        if entry.get('version')==[0,5,0]:entry['version']=[0,5,1]
    updates[path]=enc(data)
assert not updates.keys()&removed
with ZipFile(output,'w',ZIP_DEFLATED) as out:
    for path in sorted((set(old.namelist())-removed)|updates.keys()):
        out.writestr(path,updates[path] if path in updates else old.read(path))
with ZipFile(output) as out:
    assert out.testzip() is None
    for path in out.namelist():
        if path.endswith('.json'):json.loads(out.read(path))
        if path.endswith('.mcstructure'):
            s=Site(out.read(path))
            assert all(len(b)==s.w*s.h*s.d and min(b)>=-1 and max(b)<len(s.palette) for _,b in s.layers)
    for path in old.namelist():
        if path not in updates and path not in removed: assert old.read(path)==out.read(path)
    assert len(layout)==7 and len(crew_layout)==18
print('Verified 7 variants, 18 resident rosters, and two Nullframe natural spawn rule removals.')
