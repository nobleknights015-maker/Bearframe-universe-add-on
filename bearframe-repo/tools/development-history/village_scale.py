from pathlib import Path
from collections import deque
src=Path('structures.py').read_text().split('for name,plan in existing.items():')[0]
exec(compile(src,'structures.py','exec'))
old.close()
old=ZipFile(folder/'Bearframe_Bedrock_0.5.3.mcaddon')
output=folder/'Bearframe_Bedrock_0.6.0.mcaddon'
updates={}
def encode(d): return (json.dumps(d,indent=2)+'\n').encode()
def rewrite(path,fn):
    updates[bp+'scripts/'+path]=fn(old.read(bp+'scripts/'+path).decode()).encode()

# Width/depth added on each side of the original build. Large social sites
# get multiple neighborhoods, compact relay and wreck sites remain smaller.
districts={
 'rainline_town':(15,12,'industrial'), 'saltline_town':(15,12,'sand'),
 'frontier_colony':(16,14,'civil'), 'coalition_city':(16,14,'civil'),
 'overgrown_colony':(16,14,'woods'), 'collapsed_rail_settlement':(16,14,'industrial'),
 'colony_waystation':(13,11,'civil'), 'lost_waystation':(13,11,'woods'),
 'farfield_camp':(12,10,'civil'), 'grid_hub':(12,10,'woods'),
 'echo_ward':(12,10,'ice'), 'intrusion_checkpoint':(11,10,'dark'),
 'foundry_annex':(12,10,'sand'), 'maintenance_relay':(10,9,'industrial'),
 'crashed_skiff':(11,9,'civil'), 'relay_nine':(11,9,'industrial'),
 'frontier_ruin':(12,10,'woods'), 'syndicate_forge':(12,10,'dark'),
 'cinder_works':(12,10,'sand'), 'nivalis_lab':(12,10,'ice'),
 'verdantis_station':(12,10,'woods'), 'shattered_array':(12,10,'dark'),
 'sealed_archive_bunker':(10,10,'industrial'), 'flooded_pump_bunker':(11,10,'industrial'),
 'collapsed_transit_bunker':(11,10,'industrial'), 'rootbound_service_bunker':(11,10,'woods'),
}
materials={
 'industrial':('stone_bricks','polished_deepslate','oxidized_cut_copper','cyan_terracotta','tuff'),
 'sand':('cut_sandstone','smooth_sandstone','cut_copper','orange_terracotta','coarse_dirt'),
 'civil':('smooth_quartz','polished_andesite','iron_block','cyan_terracotta','moss_block'),
 'woods':('mossy_stone_bricks','mud_bricks','mangrove_planks','cyan_terracotta','rooted_dirt'),
 'ice':('calcite','polished_deepslate','packed_ice','light_blue_terracotta','tuff'),
 'dark':('cracked_deepslate_tiles','polished_blackstone','polished_blackstone_bricks','red_terracotta','tuff'),
}
def embed(prior,w,h,d,dx,dy,dz):
    site=blank(prior,w,h,d)
    for layer,(_,cells) in enumerate(prior.layers):
        current=site.layers[layer][1]
        for i,n in enumerate(cells):
            if n<0: continue
            x,y,z=prior.xyz(i)
            current[site.index(x+dx,y+dy,z+dz)]=n
    for key,entry in prior.metadata.items():
        x,y,z=prior.xyz(int(key))
        x+=dx;y+=dy;z+=dz
        item=deepcopy(entry)
        if 'block_entity_data' in item[1]:
            e=item[1]['block_entity_data'][1]
            for axis,coord in zip('xyz',(x,y,z)):
                if axis in e: e[axis]=(e[axis][0],coord)
        site.metadata[str(site.index(x,y,z))]=item
    return site
from copy import deepcopy

def lane(s,y,x0,z0,x1,z1,block):
    box(s,x0,y,z0,x1,y,z1,block)
    box(s,x0,y+1,z0,x1,y+3,z1,'air',OPEN)

def shell(s,y,x0,z0,x1,z1,theme,entry,mode):
    wall,frame,cap,accent,ground=materials[theme]
    box(s,x0,y,z0,x1,y,z1,frame)
    box(s,x0,y+1,z0,x1,y+5,z1,'air',OPEN)
    mid=(x0+x1)//2
    for x in range(x0,x1+1):
        for z in range(z0,z1+1):
            border=x in (x0,x1) or z in (z0,z1)
            if border:
                door=z==entry and abs(x-mid)<=1
                if not door:
                    put(s,x,y+1,z,frame)
                    for hh in (2,3):
                        if mode==2 and x<x0+3 and z==z0: continue
                        block=wall if (x+2*z)%5!=0 else 'tinted_glass'
                        put(s,x,y+hh,z,block)
                    if (x+z)%6==0: put(s,x,y+4,z,accent)
            if mode!=2 or x>x0+3 or z>z0+2:
                put(s,x,y+4,z,cap)
            if x in (x0+1,x1-1) and z in (z0+1,z1-1) and mode!=2:
                put(s,x,y+5,z,frame)
    put(s,mid,y+1,(z0+z1)//2,'cartography_table' if mode==0 else 'crafting_table')
    if mode!=2:
        put(s,x0+1,y+1,z0+1,'barrel')
        put(s,x1-1,y+1,z1-1,'lantern')
    else:
        put(s,x0+1,y+1,z0+1,ground)

def terraform(s,prior,dx,dz,deck,theme,key):
    w,d=s.w,s.d
    midx,midz=w//2,d//2
    wall,frame,cap,accent,ground=materials[theme]
    # Roads connect four approaches with side streets outside the old core.
    for x0,z0,x1,z1 in [(midx-1,0,midx+1,dz-1),(midx-1,d-dz,midx+1,d-1),
                       (0,midz-1,dx-1,midz+1),(w-dx,midz-1,w-1,midz+1),
                       (3,2,w-4,4),(3,d-5,w-4,d-3),(2,3,4,d-4),(w-5,3,w-3,d-4)]:
        lane(s,deck,x0,z0,x1,z1,'stone_bricks')
    # Uneven verge strips leave natural terrain between district pads.
    for x in range(1,w-1):
        for z in range(1,d-1):
            outside= x<dx or x>=w-dx or z<dz or z>=d-dz
            if outside and s.get(x,deck,z)=='void' and ((x*7+z*3)%19<4):
                put(s,x,deck,z,ground)
    buildings=[
        (6,5,min(dx+2,midx-4),min(dz-1,10),4,0),
        (w-1-min(dx+2,midx-4),5,w-7,min(dz-1,10),4,2),
        (6,d-max(11,dz),min(dx+2,midx-4),d-6,d-5,1),
        (w-1-min(dx+2,midx-4),d-max(11,dz),w-7,d-6,d-5,2),
    ]
    if dx>=15:
        for x0,x1 in ((midx-11,midx-5),(midx+5,midx+11)):
            buildings.append((x0,5,x1,dz-2,4,1))
            buildings.append((x0,d-dz+1,x1,d-6,d-5,2))
    for x0,z0,x1,z1,entry,mode in buildings:
        # Annexes front onto the outer road. Deck cells under the doorway
        # are part of the shell, with the path touching one block beyond.
        shell(s,deck,x0,z0,x1,z1,theme,z0 if entry==4 else z1,mode)
    for x,z in ((5,midz-3),(w-6,midz+3)):
        put(s,x,deck,z,ground)
        put(s,x,deck+1,z,frame)
        put(s,x,deck+2,z,accent)
    # Set dressing is legible from the road without closing an approach.
    if theme in ('woods','civil'):
        for x,z in ((5,6),(w-6,d-7),(5,d-7)):
            put(s,x,deck,z,'rooted_dirt')
            for h in (1,2,3):put(s,x,deck+h,z,'mangrove_log',OPEN)
            for xx,zz in ((x,z),(x-1,z),(x+1,z),(x,z-1),(x,z+1)):
                put(s,xx,deck+4,zz,'azalea_leaves',OPEN)
    if 'bunker' in key:
        # Short auxiliary side rooms with an exposed roof and a through hall.
        shell(s,deck,5,midz+3,dx-1,midz+8,theme,midz+3,1)
        lane(s,deck,3,midz+1,dx-1,midz+2,frame)
        lane(s,deck,3,midz+2,dx-1,midz+2,frame)

script=old.read(bp+'scripts/surface_sites.js').decode()
i=script.index('const crews=')+len('const crews=')
crews,end=json.JSONDecoder().raw_decode(script[i:])
sizes={}
for key,(dx,dz,theme) in districts.items():
    path=sp+key+'_site.mcstructure'
    prior=Site(old.read(path))
    deck=13 if prior.h in (19,21) and key in set(list(districts)[:2]+['farfield_camp','grid_hub','echo_ward','intrusion_checkpoint','foundry_annex','maintenance_relay']) else 3
    w,h,d=prior.w+2*dx,max(prior.h,deck+7),prior.d+2*dz
    new=embed(prior,w,h,d,dx,0,dz)
    terraform(new,prior,dx,dz,deck,theme,key)
    # Keep all original terrain and fixtures in the central build.
    for layer,(_,blocks) in enumerate(prior.layers):
        for index,value in enumerate(blocks):
            if value<0: continue
            x,y,z=prior.xyz(index)
            new.layers[layer][1][new.index(x+dx,y,z+dz)]=value
    for crew in crews.get(key,[]):
        crew[1]+=dx; crew[3]+=dz
        _,x,y,z=crew
        assert new.get(x,y,z) in OPEN and new.get(x,y+1,z) in OPEN
    sizes[key]=dict(x=w,y=h,z=d)
    # Check that each cardinal road has clearance along the expanded
    # segment and reaches the same edge of the original plan.
    for x,z in ([(w//2,z) for z in range(dz)]+[(w//2,z) for z in range(d-dz,d)]+
                [(x,d//2) for x in range(dx)]+[(x,d//2) for x in range(w-dx,w)]):
        assert new.get(x,deck,z) not in OPEN and new.get(x,deck+1,z) in OPEN and new.get(x,deck+2,z) in OPEN
    updates[path]=new.raw()

# Keep all legacy service coordinates while adding accessible pump/service wings.
# Appended dry bunker wing starts at the old east wall, away from every
# scripted terminal, marker, actor spawn, and cache.
def extend_bunker(key,n,want_z,base,roof,theme):
    path=sp+key+'.mcstructure'
    s=Site(old.read(path)); w=s.w
    new=embed(s,w+n,s.h,s.d,0,0,0)
    # Walkable tunnel at the old end wall. Preserve the central gates.
    for x in range(w-3 if key=="spillway_facility" else w-2,w+n-1):
        for z in range(want_z-1,want_z+2):
            put(new,x,base,z,'polished_deepslate')
            for y in range(base+1,base+4): put(new,x,y,z,'air')
    x0,x1=w-1,w+n-2
    z0,z1=want_z-5,want_z+5
    wall,frame,cap,accent,_=materials[theme]
    box(new,x0,base,z0,x1,roof,z1,frame)
    box(new,x0+1,base+1,z0+1,x1-1,roof-1,z1-1,'air')
    box(new,x0,base+1,want_z-1,x0,base+3,want_z+1,'air')
    for x in range(x0+2,x1,4):
        put(new,x,roof,want_z,'sea_lantern')
        put(new,x,base+1,z1-2,'barrel')
    for x in range(w-4,w+n-2):
        assert new.get(x,base,want_z) not in OPEN
        assert new.get(x,base+1,want_z) in OPEN and new.get(x,base+2,want_z) in OPEN
    updates[path]=new.raw()
    return new.w
shelter_width=extend_bunker('shelter_bunker',15,11,8,14,'industrial')
spillway_width=extend_bunker('spillway_facility',18,18,4,11,'industrial')
# Spillway remains script-built. Include the new service wing in the loaded
# chunk check and in the same protected-terrain/player preflight.
rewrite('spillway_layout.js',lambda s:s.replace('x: 51',f'x: {spillway_width}'))
def spillway(s):
    old_check='if (!clean([22,3,2],[49,13,34],excavationAllowed)'
    assert old_check in s
    return s.replace(old_check, f'if (!clean([48,4,13],[{spillway_width-2},11,23],excavationAllowed)) return false;\n  '+old_check).replace('x<origin.x+50','x<origin.x+SPILLWAY_SIZE.x').replace('maxDistance:65','maxDistance:95')
rewrite('spillway.js',spillway)

layout=old.read(bp+'scripts/surface_layout.js').decode()
layout+='\nconst expandedSizes='+json.dumps(sizes,indent=2)+';\nfor (const site of [...SURFACE_SITES,...LEGACY_SITES]) {\n  if (expandedSizes[site.id]) { site.size=expandedSizes[site.id]; site.expanded=true; }\n}\n'
updates[bp+'scripts/surface_layout.js']=layout.encode()
script=script[:i]+json.dumps(crews,indent=2)+script[i+end:]
# Larger dry footprints need deeper foundations. Keep existing fluid and
# occupied-block guards, and add the below-grade envelope to player checks.
script=script.replace('for(let y=floor-1;y>=floor-3;y--)','for(let y=floor-1;y>=floor-(site.expanded?6:3);y--)').replace('y>=base.y+floor-3&&','y>=base.y+floor-(site.expanded?6:3)&&').replace('maxDistance:45','maxDistance:65')
updates[bp+'scripts/surface_sites.js']=script.encode()
for pack in ('Bearframe_Behavior','Bearframe_Resources'):
    path=pack+'/manifest.json'
    data=json.loads(old.read(path))
    for row in [data['header'],*data['modules'],*data.get('dependencies',[])]:
        if row.get('version')==[0,5,3]:row['version']=[0,6,0]
    updates[path]=encode(data)
with ZipFile(output,'w',ZIP_DEFLATED) as out:
    for path in old.namelist():out.writestr(path,updates[path] if path in updates else old.read(path))
from subprocess import run
with ZipFile(output) as out:
    assert out.testzip() is None
    assert out.read(sp+'orbital_city.mcstructure')==old.read(sp+'orbital_city.mcstructure')
    for path in updates:
        if path.endswith('.js'):run(['node','--input-type=module','--check'],input=out.read(path),check=True)
        if path.endswith('.mcstructure'):
            s=Site(out.read(path))
            assert all(len(b)==s.w*s.h*s.d and -1<=min(b)<=max(b)<len(s.palette) for _,b in s.layers)
print(len(sizes),'surface expansions,',shelter_width,'block Signal Shelter and',spillway_width,'block Spillway Facility')
