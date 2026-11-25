from zipfile import ZipFile,ZIP_DEFLATED
import json
src=__import__('pathlib').Path('ruin_finish.py').read_text().split('designs={')[0]
exec(compile(src,'ruin_finish.py','exec'))
old.close()
old=ZipFile(folder/'Bearframe_Bedrock_0.5.2.mcaddon')
output=folder/'Bearframe_Bedrock_0.5.3.mcaddon'
updates={}
# Bounds are individual damage footprints keyed to the actual roof layouts.
# Colors describe construction material, while stepped cuts describe failure.
profiles={
 'farfield_camp_site':(13,(4,2,7,5),(4,3),'coarse_dirt'),
 'grid_hub_site':(13,(14,5,17,8),(16,7),'moss_block'),
 'echo_ward_site':(13,(4,10,7,13),(5,12),'rooted_dirt'),
 'intrusion_checkpoint_site':(13,(6,2,9,4),(7,3),'tuff'),
 'foundry_annex_site':(13,(2,4,5,7),(4,6),'tuff'),
 'maintenance_relay_site':(13,(13,3,16,6),(15,4),'moss_block'),
 'rainline_town_site':(13,(23,19,29,24),(28,21),'rooted_dirt'),
 'saltline_town_site':(13,(5,3,10,7),(7,5),'sandstone'),
 'frontier_colony_site':(3,(18,3,23,7),(21,5),'moss_block'),
 'colony_waystation_site':(3,(3,3,7,7),(5,4),'rooted_dirt'),
 'coalition_city_site':(3,(22,3,28,7),(25,6),'tuff'),
 'crashed_skiff_site':(3,(8,8,11,10),(9,9),'coarse_dirt'),
 'relay_nine_site':(3,(4,3,8,7),(6,6),'moss_block'),
 'frontier_ruin_site':(3,(8,6,12,8),(9,7),'rooted_dirt'),
 'syndicate_forge_site':(3,(17,3,21,8),(18,5),'tuff'),
 'cinder_works_site':(3,(4,3,9,7),(6,4),'red_sandstone'),
 'nivalis_lab_site':(3,(15,3,19,7),(17,5),'packed_ice'),
 'verdantis_station_site':(3,(4,3,9,7),(7,6),'moss_block'),
 'shattered_array_site':(3,(17,4,21,8),(19,7),'tuff'),
 'spillway_facility':(20,(5,14,13,18),(8,16),'moss_block'),
 'shelter_bunker':(20,(0,8,5,10),(1,9),'moss_block'),
}
# Nearby dry facilities replace leaf growth with dust and low scrub. Cold
# quarters get rim ice and warm wet quarters get rooted growth.
exposed={'stone_bricks','smooth_quartz','polished_andesite','cut_sandstone','smooth_sandstone','weathered_cut_copper','cut_copper','iron_block','oxidized_cut_copper','calcite','packed_ice','cracked_deepslate_tiles','deepslate_bricks','polished_deepslate','polished_blackstone','polished_blackstone_bricks','mossy_stone_bricks','mud_bricks','mangrove_planks','tinted_glass','glass','chiseled_deepslate','smooth_stone'}

def age(site,deck,rect,scar,material):
    snapshot=list(site.blocks)
    a,b,c,d=rect
    sx,sz=scar
    def before(x,y,z):
        return site.label(snapshot[site.index(x,y,z)])
    bunker=deck>=20
    for x in range(a,c+1):
        for z in range(b,d+1):
            hits=[y for y in range(deck+3,site.h) if before(x,y,z) in exposed]
            if not hits: continue
            top=max(hits)
            distance=abs(x-sx)+abs(z-sz)
            if distance<=3 or distance<=4 and (x+z)%3!=1:
                put(site,x,top,z,'air')
                if distance<=2 and top>deck+3 and before(x,top-1,z) in exposed:
                    put(site,x,top-1,z,'air')
            elif distance<=6:
                put(site,x,top,z,material,exposed)
                # Material accumulates on surviving roof lips, above routes.
                if material in {'moss_block','rooted_dirt','coarse_dirt'} and top+1<site.h and (x+z)%3==0:
                    put(site,x,top+1,z,'moss_block',OPEN)
    # Place material legs descending from the torn cap. Stop above the
    # two-block path envelope, including the old underground movement path.
    if not bunker:
        for x in range(a,c+1):
            for z in range(b,d+1):
                if abs(x-sx)+abs(z-sz)>4: continue
                for y in range(deck+3,min(deck+5,site.h)):
                    old_block=before(x,y,z)
                    if old_block in exposed and (x+2*z+y)%4!=0:
                        put(site,x,y,z,material if (x+z)%3!=0 else 'cracked_deepslate_tiles')
    # Scar the edges of the circulation surface, leaving its collision
    # and the existing service markers in place.
    mx,mz=site.w//2,site.d//2
    for x in range(1,site.w-1):
        for z in range(1,site.d-1):
            if bunker: continue
            if abs(x-mx)<=1 or abs(z-mz)<=1: continue
            if before(x,deck,z) not in exposed or before(x,deck+1,z) not in OPEN: continue
            near=abs(x-sx)+abs(z-sz)
            # A broken material seam travels outward from the damaged bay.
            seam=(x-sx-2*(z-sz))%11
            if near<=6 and seam in (0,1) or near<=3:
                put(site,x,deck,z,material)
    if bunker:
        # Keep the burial shell intact. Scars on external housing and lip
        # read from the approach without opening underground ceilings.
        for x in range(a,c+1):
            for z in range(b,d+1):
                if before(x,deck,z) in exposed and abs(x-sx)+abs(z-sz)<=4:
                    put(site,x,deck,z,material)

script=old.read(bp+'scripts/surface_sites.js').decode()
a=script.index('const crews=')+len('const crews=')
crews,_=json.JSONDecoder().raw_decode(script[a:])
for key,profile in profiles.items():
    path=sp+key+'.mcstructure'
    site=Site(old.read(path))
    before=list(site.blocks)
    age(site,*profile)
    name=key.removesuffix('_site')
    for _,x,y,z in crews.get(name,[]):
        for yy in (y-1,y,y+1):
            i=site.index(x,yy,z)
            site.blocks[i]=before[i]
    if name in crews: reachable(site)
    assert sum(a!=b for a,b in zip(before,site.blocks))>=3,key
    for i,index in enumerate(before):
        label=site.label(index)
        _,y,_=site.xyz(i)
        if label not in exposed and not (label in OPEN and y>=profile[0]+4):
            assert index==site.blocks[i], (key,site.xyz(i),label)
        if y in (profile[0]+1,profile[0]+2):
            assert (label in OPEN)==(site.label(site.blocks[i]) in OPEN)
    updates[path]=site.raw()

for pack in ('Bearframe_Behavior','Bearframe_Resources'):
    path=pack+'/manifest.json'
    data=json.loads(old.read(path))
    for row in [data['header'],*data['modules'],*data.get('dependencies',[])]:
        if row.get('version')==[0,5,2]:row['version']=[0,5,3]
    updates[path]=(json.dumps(data,indent=2)+'\n').encode()
with ZipFile(output,'w',ZIP_DEFLATED) as out:
    for path in old.namelist(): out.writestr(path,updates[path] if path in updates else old.read(path))
with ZipFile(output) as out:
    assert out.testzip() is None
    actual={path for path in out.namelist() if out.read(path)!=old.read(path)}
    assert actual==updates.keys()
    assert out.read(sp+'orbital_city.mcstructure')==old.read(sp+'orbital_city.mcstructure')
    for path in updates:
        if path.endswith('.mcstructure'):
            s=Site(out.read(path))
            assert all(len(b)==s.w*s.h*s.d and -1<=min(b)<=max(b)<len(s.palette) for _,b in s.layers)
print(f'Validated {len(profiles)} changed sites, seven previous ruin templates, and untouched Bearframe Station.')
