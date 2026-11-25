from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json
from subprocess import run

source_code=Path('structures.py').read_text().split('for name,plan in existing.items():')[0]
exec(compile(source_code,'structures.py','exec'))
old.close()
old=ZipFile(folder/'Bearframe_Bedrock_0.5.1.mcaddon')
output=folder/'Bearframe_Bedrock_0.5.2.mcaddon'
updates={}
def cut(s,x1,y1,z1,x2,y2,z2):
    box(s,x1,y1,z1,x2,y2,z2,'air',{'smooth_quartz','glass','tinted_glass','stone_bricks','polished_deepslate','polished_andesite','cracked_deepslate_tiles','mossy_stone_bricks','weathered_cut_copper','oxidized_cut_copper','mud_bricks','moss_block','calcite','deepslate_bricks'})
def roots(s,points):
    for x,z,h in points:
        put(s,x,3,z,'rooted_dirt')
        for y in range(4,h+1):
            put(s,x,y,z,'mangrove_log',OPEN)
        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
            put(s,x+dx,4,z+dz,'mangrove_roots',OPEN)
            for y in (h-1,h):
                put(s,x+dx,y,z+dz,'flowering_azalea_leaves',OPEN)
        put(s,x,h+1,z,'azalea_leaves',OPEN)
        for dx,dz in ((2,0),(-2,0),(0,2),(0,-2),(1,1),(-1,-1),(1,-1),(-1,1)):
            put(s,x+dx,h,z+dz,'azalea_leaves',OPEN)
def breach(s,x,z,direction=1):
    for dx,dz in ((0,0),(1,0),(2,1),(3,1),(4,2),(5,3)):
        xx,zz=x+dx,z+dz*direction
        put(s,xx,3,zz,'rooted_dirt')
        if (dx,dz) in ((0,0),(2,1),(4,2)):
            put(s,xx,4,zz,'tuff',OPEN)

def archive(s):
    # A retained vault with a thick front and a smaller, layered earth cap.
    box(s,3,6,10,21,6,10,'polished_deepslate',OPEN)
    for x in (3,6,18,21):
        box(s,x,4,10,x,5,10,'deepslate_bricks',OPEN)
    for x0,x1,y,z0,z1 in ((2,22,9,2,8),(4,20,10,3,8),(6,18,11,4,7)):
        box(s,x0,y,z0,x1,y,z1,'mossy_stone_bricks')
        box(s,x0+1,y,z0+1,x1-1,y,z1-1,'moss_block')
    for x,z in ((6,12),(18,12)): post(s,x,z,6,'deepslate_bricks','sea_lantern')
    cut(s,18,9,6,21,11,7)
    box(s,18,8,6,20,8,6,'oxidized_cut_copper',OPEN)
    put(s,6,4,6,'bookshelf',OPEN)
    put(s,7,4,6,'chiseled_bookshelf',OPEN)

def flooded(s):
    # The breached pump house feeds the sump through a visible service trench.
    cut(s,16,6,7,20,9,10)
    for x in (17,18,19,20):
        for z in (14,15,16,17,18,19):
            if x in (18,19) and z in (15,16,17):
                put(s,x,4,z,'water')
            elif z==14:
                put(s,x,4,z,'prismarine_bricks')
    for x in (17,21):
        box(s,x,6,13,x,6,18,'oxidized_cut_copper')
        put(s,x,7,18,'tinted_glass')
    for z in range(8,15):
        put(s,20,3,z,'oxidized_cut_copper')
        if z%3==0: put(s,20,4,z,'iron_bars',OPEN)
    box(s,4,8,4,8,8,7,'oxidized_cut_copper',OPEN)
    roots(s,[(3,17,6)])

def transit(s):
    # A severed above-ground service viaduct over two battered service bays.
    cut(s,15,6,3,21,9,6)
    cut(s,17,4,3,20,8,3)
    for x,z in ((4,7),(8,7),(17,7),(21,7)):
        post(s,x,z,10,'deepslate_bricks','polished_deepslate')
    box(s,3,10,6,10,10,8,'polished_deepslate')
    box(s,16,10,6,21,10,8,'polished_deepslate')
    box(s,4,11,6,9,11,6,'iron_bars')
    box(s,18,11,8,21,11,8,'iron_bars')
    for x,z in ((10,6),(16,8),(15,8)):
        put(s,x,9,z,'cracked_deepslate_tiles',OPEN)
    breach(s,11,5)
    breach(s,16,9)

def rootbound(s):
    cut(s,4,6,3,8,9,7)
    cut(s,14,6,14,18,9,17)
    cut(s,14,4,16,14,7,18)
    roots(s,[(7,6,10),(16,16,10),(21,5,8)])
    for x in range(4,11):
        put(s,x,3,11,'mossy_stone_bricks')
    for x,z in ((16,5),(18,6),(7,13),(8,14)):
        put(s,x,4,z,'moss_block',OPEN)

def colony(s):
    # Greenhouse roof and rear wall fell inward. One neighboring home is
    # still sheltered, and Echoes have marked it with a low amber lamp.
    cut(s,19,4,20,24,11,22)
    cut(s,18,5,18,20,11,21)
    cut(s,4,6,3,9,10,5)
    breach(s,17,19,-1)
    roots(s,[(22,20,10),(4,4,9),(25,13,8)])
    box(s,5,6,19,9,6,19,'dark_oak_planks',OPEN)
    put(s,5,4,18,'ochre_froglight',OPEN)

def rail(s):
    # Broken crossing and displaced roof plates. A side route bends
    # around the wreckage to the preserved doors and stockrooms.
    cut(s,22,5,21,27,12,25)
    cut(s,13,9,10,19,9,11)
    cut(s,12,9,17,17,10,17)
    for x in range(10,23):
        for z in (13,15):
            put(s,x,3,z,'polished_deepslate' if x not in (15,16,17) else 'coarse_dirt')
    breach(s,15,13)
    for x,z in ((14,12),(15,12),(17,13),(20,16),(22,21),(25,23)):
        put(s,x,4,z,'cracked_deepslate_tiles',OPEN)
    roots(s,[(25,22,8),(7,16,9)])

def waystation(s):
    cut(s,12,7,13,17,8,17)
    cut(s,3,5,3,7,9,5)
    cut(s,16,7,7,20,9,8)
    roots(s,[(6,3,10),(17,14,10),(15,18,8)])
    breach(s,12,14)
    # Makeshift Echo refuge under the surviving half of the loading canopy.
    box(s,5,7,14,10,7,16,'dark_oak_planks',OPEN)
    box(s,5,4,14,5,6,14,'dark_oak_planks',OPEN)
    put(s,7,4,16,'ochre_froglight',OPEN)
    put(s,8,4,16,'brown_wool',OPEN)

designs={
 'sealed_archive_bunker':archive,'flooded_pump_bunker':flooded,
 'collapsed_transit_bunker':transit,'rootbound_service_bunker':rootbound,
 'overgrown_colony':colony,'collapsed_rail_settlement':rail,'lost_waystation':waystation,
}
script=old.read(bp+'scripts/surface_sites.js').decode()
a=script.index('const crews=')+len('const crews=')
crews,end=json.JSONDecoder().raw_decode(script[a:])
for key,build in designs.items():
    path=sp+key+'_site.mcstructure'
    site=Site(old.read(path))
    baseline=list(site.blocks)
    build(site)
    # Restore functional blocks and the scripted resident spawn clearance
    # if nearby damage cuts pass within those cells.
    for i,index in enumerate(baseline):
        if site.label(index) in {'barrel','lectern','smithing_table','blast_furnace','cartography_table','crafting_table','smoker','water'}:
            site.blocks[i]=index
    for _,x,y,z in crews[key]:
        for yy in (y-1,y,y+1):
            idx=site.index(x,yy,z)
            site.blocks[idx]=baseline[idx]
    reachable(site)
    assert sum(i!=j for i,j in zip(baseline,site.blocks))>45,key
    updates[path]=site.raw()

for pack in ('Bearframe_Behavior','Bearframe_Resources'):
    path=pack+'/manifest.json'
    data=json.loads(old.read(path))
    for row in [data['header'],*data['modules'],*data.get('dependencies',[])]:
        if row.get('version')==[0,5,1]:row['version']=[0,5,2]
    updates[path]=(json.dumps(data,indent=2)+'\n').encode()
with ZipFile(output,'w',ZIP_DEFLATED) as out:
    for path in old.namelist(): out.writestr(path,updates[path] if path in updates else old.read(path))
with ZipFile(output) as out:
    assert out.testzip() is None
    assert {path for path in out.namelist() if out.read(path)!=old.read(path)}==updates.keys()
    for path in updates:
        if path.endswith('.mcstructure'):
            s=Site(out.read(path))
            assert all(len(b)==s.w*s.h*s.d and -1<=min(b)<=max(b)<len(s.palette) for _,b in s.layers)
print('Seven revised ruin templates passed route, resident-clearance, and archive checks.')
