from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from collections import deque,Counter
import json,re
from bedrock_nbt import Site,blank

folder=Path('deliverables')
bp='Bearframe_Behavior/'
sp=bp+'structures/bearframe/'
source=folder/'Bearframe_Bedrock_0.4.10.mcaddon'
updates={}
old=ZipFile(source)
palette_cache={}
OPEN={'void','air'}
def put(s,x,y,z,block,allowed=None):
    if not (0<=x<s.w and 0<=y<s.h and 0<=z<s.d): raise ValueError((x,y,z,s.w,s.h,s.d))
    i=s.index(x,y,z)
    if allowed is not None and s.label(s.blocks[i]) not in allowed: return
    key=(s,block)
    if key not in palette_cache: palette_cache[key]=s.block(block)
    s.blocks[i]=palette_cache[key]

def box(s,x1,y1,z1,x2,y2,z2,block,allowed=None):
    for x in range(x1,x2+1):
        for z in range(z1,z2+1):
            for y in range(y1,y2+1):
                put(s,x,y,z,block,allowed)

def shop(s,x0,z0,x1,z1,skin,frame,roof,accent,door='south',height=4):
    y=4
    assert x1-x0>=4 and z1-z0>=4
    box(s,x0,y-1,z0,x1,y-1,z1,frame)
    box(s,x0+1,y,z0+1,x1-1,y+height-1,z1-1,'air')
    for level in range(height):
        for x,z in [(x,z) for x in range(x0,x1+1) for z in (z0,z1)]+[(x,z) for z in range(z0+1,z1) for x in (x0,x1)]:
            corner=x in (x0,x1) and z in (z0,z1)
            mx,mz=(x0+x1)//2,(z0+z1)//2
            entry=(door=='south' and z==z1 or door=='north' and z==z0) and abs(x-mx)<=1 or (door=='east' and x==x1 or door=='west' and x==x0) and abs(z-mz)<=1
            strip=(z in (z0,z1) and (x-x0)%4 in (2,3) or x in (x0,x1) and (z-z0)%4 in (2,3))
            material=frame if corner or level==0 else skin
            if entry:
                material='air' if level<3 else accent
            elif level==1 and strip and not corner:
                material='tinted_glass'
            elif level==height-1 and strip:
                material=accent
            put(s,x,y+level,z,material)
    box(s,x0-1,y+height,z0-1,x1+1,y+height,z1+1,roof)
    box(s,x0+1,y+height+1,z0+1,x1-1,y+height+1,z1-1,frame)
    put(s,(x0+x1)//2,y+height,z0+2,'sea_lantern')

def walk(s,x1,z1,x2,z2,material='polished_andesite'):
    box(s,x1,3,z1,x2,3,z2,material)

def post(s,x,z,top,frame,cap):
    box(s,x,4,z,x,top-1,z,frame)
    put(s,x,top,z,cap)

def prop(s,x,z,block):
    put(s,x,4,z,block)

def bed(s,x,z):
    for dx in (0,1): prop(s,x+dx,z,'white_wool')
    prop(s,x+2,z,'smooth_quartz')

def deck(s,kind):
    w,d=s.w,s.d
    ground={'sand':'smooth_sandstone','warm':'polished_andesite','ice':'calcite','woods':'mossy_stone_bricks','moon':'tuff','forge':'polished_blackstone' }[kind]
    for x in range(w):
        for z in range(d):
            if min(x+z,x+d-1-z,w-1-x+z,w+d-2-x-z)<3:
                continue
            distance=min(x,z,w-1-x,d-1-z)
            edging={'sand':'cut_sandstone','warm':'stone_bricks','ice':'packed_ice','woods':'coarse_dirt','moon':'polished_deepslate','forge':'tuff'}
            put(s,x,3,z,edging[kind] if distance<=1 else ground)
            for yy in (4,5,6): put(s,x,yy,z,'air')
    walk(s,w//2-1,0,w//2+1,d-1)
    walk(s,0,d//2-1,w-1,d//2+1)
    for x,z in ((w//2,2),(w//2,d-3),(2,d//2),(w-3,d//2)):
        put(s,x,3,z,'chiseled_stone_bricks')

white=('smooth_quartz','polished_deepslate','weathered_cut_copper','cyan_terracotta')
orange=('smooth_sandstone','polished_blackstone','cut_copper','orange_terracotta')
dark=('deepslate_tiles','polished_blackstone','polished_blackstone_bricks','red_terracotta')
ice=('calcite','polished_deepslate','packed_ice','light_blue_terracotta')
green=('mossy_stone_bricks','mud_bricks','mangrove_planks','cyan_terracotta')
ruined=('cracked_deepslate_tiles','polished_deepslate','oxidized_cut_copper','cyan_terracotta')

# Starbound's eleven concepts rebuilt as independent Bearframe discoveries.
# Each uses its own plan. Northeast/southwest rooms are deliberate, and all
# four pads meet the paths examined by the dry-ground placement code.
plans={
 'frontier_colony':(29,25,'warm','plains',39),
 'colony_waystation':(23,21,'warm','savanna',37),
 'coalition_city':(33,29,'warm','plains',55),
 'crashed_skiff':(25,21,'warm','plains',34),
 'relay_nine':(23,21,'woods','taiga',40),
 'frontier_ruin':(25,23,'woods','forest',42),
 'syndicate_forge':(29,25,'forge','desert',46),
 'cinder_works':(27,23,'sand','mesa',48),
 'nivalis_lab':(25,23,'ice','ice_plains',52),
 'verdantis_station':(27,23,'woods','jungle',48),
 'shattered_array':(27,25,'moon','hills',55),
}
def build(s,key,land):
    deck(s,land)
    w,d=s.w,s.d
    if key=='frontier_colony':
        shop(s,3,3,11,10,*white)
        shop(s,17,3,25,10,*white)
        shop(s,4,15,11,21,*white,door='north')
        shop(s,17,15,25,21,'glass','polished_andesite','weathered_cut_copper','cyan_terracotta',door='north')
        bed(s,5,5); bed(s,19,5)
        for x in (19,21,23):
            walk(s,x,17,x,19,'moss_block')
            prop(s,x,17,'flowering_azalea')
        prop(s,6,18,'crafting_table'); prop(s,9,18,'barrel')
        for x in (11,17): post(s,x,12,7,'polished_deepslate','sea_lantern')
    elif key=='colony_waystation':
        shop(s,3,3,9,8,*white)
        shop(s,13,3,19,8,*white)
        bed(s,4,5); prop(s,15,5,'smoker')
        for x in (5,17):
            for z in (13,17): post(s,x,z,7,'polished_deepslate','cyan_terracotta')
        box(s,5,7,13,17,7,13,'polished_deepslate')
        box(s,5,7,17,17,7,17,'polished_deepslate')
        box(s,5,8,13,17,8,17,'weathered_cut_copper')
        for x in (7,15): prop(s,x,15,'barrel')
        walk(s,8,11,14,19,'light_gray_concrete')
    elif key=='coalition_city':
        for x,z,theme,door in [(3,3,white,'south'),(21,3,white,'south'),(3,19,white,'north'),(21,19,ice,'north')]:
            shop(s,x,z,x+8,z+6,*theme,door=door,height=5)
            prop(s,x+2,z+2,'barrel')
        for x in (8,24):
            for z in (11,17): post(s,x,z,9,'polished_deepslate','sea_lantern')
        box(s,8,9,11,24,9,11,'smooth_quartz')
        box(s,8,9,17,24,9,17,'smooth_quartz')
        walk(s,12,12,20,16,'cyan_terracotta')
        for x,z in ((13,12),(19,12),(13,16),(19,16)):
            prop(s,x,z,'moss_block'); put(s,x,5,z,'flowering_azalea')
        prop(s,14,5,'cartography_table')
    elif key=='crashed_skiff':
        for x in range(4,22):
            half=1 if x>=19 or x<=6 else 2
            walk(s,x,10-half,x,10+half,'coarse_dirt')
            put(s,x,3,10,'tuff')
        for x in range(6,21):
            h=2 if x<9 or x>17 else 3
            wide=1 if x<9 or x>18 else 2
            for z in (10-wide,10+wide):
                if (x,z) not in {(12,12),(13,12),(14,12),(15,12),(8,9)}:
                    box(s,x,4,z,x,4+h,z,'smooth_quartz' if x%4 else 'weathered_cut_copper')
            if x in (9,10,17,18):
                box(s,x,7,9,x,7,11,'tinted_glass')
        for x in (7,8): prop(s,x,10,'blast_furnace')
        prop(s,17,10,'cartography_table'); prop(s,14,9,'barrel')
        for x,z in ((5,7),(4,8),(3,8),(9,14),(10,15),(12,16)):
            prop(s,x,z,'weathered_cut_copper')
    elif key=='relay_nine':
        shop(s,3,3,9,9,*ruined)
        shop(s,13,3,19,9,*ruined)
        for x,z in ((7,13),(15,13),(7,17),(15,17)): post(s,x,z,11,'polished_deepslate','oxidized_cut_copper')
        box(s,7,10,13,15,10,13,'oxidized_cut_copper')
        box(s,7,10,17,15,10,17,'oxidized_cut_copper')
        box(s,8,11,13,14,11,17,'tinted_glass')
        post(s,11,15,14,'polished_deepslate','sea_lantern')
        prop(s,6,5,'lodestone'); prop(s,16,5,'barrel')
        walk(s,9,12,13,18,'cyan_terracotta')
    elif key=='frontier_ruin':
        for x0,z0,n in ((4,4,5),(16,4,4),(4,15,3),(16,15,5)):
            box(s,x0,4,z0,x0+4,4,z0,'mossy_stone_bricks')
            box(s,x0,4,z0,x0,4,z0+4,'cracked_deepslate_tiles')
            post(s,x0,z0,n+4,'cracked_deepslate_tiles','moss_block')
            for dx in (1,3):
                prop(s,x0+dx,z0+3,'moss_block')
                put(s,x0+dx,5,z0+3,'azalea_leaves')
        walk(s,8,8,16,14,'chiseled_stone_bricks')
        prop(s,12,11,'lodestone'); prop(s,18,16,'barrel')
        box(s,8,7,7,16,7,7,'cracked_deepslate_tiles')
        for x in (8,16): post(s,x,7,8,'polished_deepslate','cracked_deepslate_tiles')
    elif key=='syndicate_forge':
        shop(s,3,3,12,10,*dark,height=5)
        shop(s,16,3,25,10,*dark,height=5)
        prop(s,5,5,'blast_furnace'); prop(s,9,5,'anvil')
        prop(s,19,5,'smithing_table'); prop(s,23,7,'barrel')
        for x in (5,22):
            for z in (15,20): post(s,x,z,10,'polished_blackstone','orange_terracotta')
        box(s,5,9,15,22,9,15,'cut_copper')
        box(s,5,9,20,22,9,20,'cut_copper')
        box(s,13,7,17,13,9,17,'iron_bars')
        box(s,11,7,17,15,7,17,'polished_blackstone')
        walk(s,8,16,20,19,'yellow_terracotta')
    elif key=='cinder_works':
        shop(s,3,3,11,9,*orange)
        shop(s,15,13,23,19,*orange,door='north')
        for x,z,h in ((4,15,8),(6,16,10),(7,17,9),(18,5,10),(19,6,8),(20,6,7)):
            post(s,x,z,h,'basalt','blackstone')
        for x in range(8,19):
            if not 12<=x<=14: walk(s,x,10,x,12,'blackstone')
        prop(s,5,6,'blast_furnace'); prop(s,20,16,'barrel')
        post(s,21,4,11,'polished_blackstone','orange_terracotta')
        box(s,18,9,4,21,9,4,'cut_copper')
    elif key=='nivalis_lab':
        shop(s,3,3,10,9,*ice)
        shop(s,14,3,21,9,*ice)
        box(s,10,8,5,14,8,7,'tinted_glass')
        walk(s,4,14,20,18,'packed_ice')
        walk(s,11,12,13,21,'polished_andesite')
        for x in (5,8,16,19):
            post(s,x,15,7,'packed_ice','calcite')
            prop(s,x,17,'sea_lantern')
        prop(s,6,6,'cartography_table'); prop(s,17,6,'barrel')
    elif key=='verdantis_station':
        shop(s,3,3,11,9,*green)
        shop(s,15,13,23,19,*green,door='north')
        for x,z in ((6,16),(20,6)):
            post(s,x,z,11,'mangrove_log','mangrove_log')
            box(s,x-2,10,z-2,x+2,11,z+2,'flowering_azalea_leaves')
            for nx,nz in ((x-1,z),(x+1,z),(x,z-1),(x,z+1)):
                box(s,nx,4,nz,nx,5,nz,'mangrove_roots')
        walk(s,11,9,15,13,'mangrove_planks')
        prop(s,7,5,'composter'); prop(s,20,16,'barrel')
    else:
        shop(s,3,3,10,9,*dark)
        shop(s,16,15,23,21,*ruined,door='north')
        walk(s,15,4,22,10,'polished_blackstone')
        for x,z in ((16,5),(21,5),(16,9),(21,9)):
            post(s,x,z,10,'polished_deepslate','amethyst_block')
        box(s,16,10,5,21,10,9,'tinted_glass')
        post(s,19,7,13,'polished_blackstone','sea_lantern')
        prop(s,6,5,'lodestone'); prop(s,20,18,'barrel')
        walk(s,4,16,9,20,'end_stone')
    if key=='frontier_colony':
        # Tall greenhouse ridge and exposed framed skylight.
        box(s,18,9,16,24,9,20,'glass')
        box(s,19,10,17,23,10,19,'glass')
        box(s,20,11,18,22,11,18,'weathered_cut_copper')
        for x in (18,21,24):
            box(s,x,9,16,x,9,20,'polished_andesite')
    elif key=='coalition_city':
        # Central communications monument and differentiated civic roofs.
        for x in (14,18):
            post(s,x,14,10,'polished_deepslate','cyan_terracotta')
        box(s,14,9,14,18,9,14,'smooth_quartz')
        box(s,15,10,14,17,10,14,'tinted_glass')
        box(s,16,11,14,16,13,14,'smooth_quartz')
        put(s,16,14,14,'sea_lantern')
        box(s,23,10,4,27,11,8,'smooth_quartz')
        box(s,24,12,5,26,12,7,'weathered_cut_copper')
    elif key=='crashed_skiff':
        # Tapered bow and stepped delta fins. The starboard breach remains
        # open at feet and head height, with salvage visible from the gash.
        for x,z1,z2 in ((6,6,8),(7,5,8),(8,4,8),(9,5,8),(10,6,8),(11,7,8),
                        (6,12,14),(7,12,15),(8,12,16),(9,12,15),(10,12,14),(11,12,13)):
            box(s,x,4,z1,x,4,z2,'smooth_quartz')
        for x,z in ((8,4),(8,16),(9,5),(9,15)): put(s,x,4,z,'cyan_terracotta')
        for x in range(16,23):
            half=2 if x<19 else 1 if x<22 else 0
            for z in range(10-half,11+half):
                put(s,x,6,z,'tinted_glass' if x<20 else 'smooth_quartz')
            put(s,x,7,10,'smooth_quartz' if x>19 else 'tinted_glass')
        for x,z in ((7,9),(7,11)):
            put(s,x,8,z,'oxidized_cut_copper')
    elif key=='syndicate_forge':
        for x,z in ((4,5),(10,7),(18,5),(24,7)):
            box(s,x,10,z,x,13,z,'polished_blackstone_bricks')
            put(s,x,14,z,'cut_copper')
        for x in range(8,21):
            put(s,x,3,16,'polished_blackstone')
            put(s,x,3,19,'polished_blackstone')
    elif key=='cinder_works':
        # Offset exhausts and a partially buried ramp distinguish this from
        # the Syndicate gantry, whose landmark is horizontal.
        for x,z,h in ((4,4,12),(6,4,14),(8,4,11)):
            box(s,x,9,z,x,h,z,'polished_blackstone')
            put(s,x,h,z,'orange_terracotta')
        walk(s,15,14,16,18,'cut_sandstone')
    elif key=='nivalis_lab':
        # Stepped pressure shell across both lab pods.
        for x0,x1 in ((3,10),(14,21)):
            box(s,x0+1,9,4,x1-1,9,8,'calcite')
            box(s,x0+2,10,5,x1-2,10,7,'packed_ice')
            box(s,x0+3,11,6,x1-3,11,6,'sea_lantern')
    elif key=='verdantis_station':
        # Shared canopy spine and roots leading to the research walk.
        box(s,5,11,14,7,11,17,'flowering_azalea_leaves')
        box(s,5,9,14,6,10,14,'azalea_leaves')
        box(s,19,11,4,21,12,8,'flowering_azalea_leaves')
        box(s,21,9,7,22,10,8,'azalea_leaves')
        box(s,6,9,4,8,9,8,'mangrove_planks')
        box(s,7,10,5,7,10,7,'moss_block')
    elif key=='shattered_array':
        # Broken antenna ring frames the remaining emitter.
        for x,z in ((15,5),(16,4),(17,3),(20,3),(21,4),(22,5),(22,8),(21,9)):
            put(s,x,11,z,'polished_deepslate')
        put(s,17,11,3,'amethyst_block')
    # Every discovery gets an intact utility/salvage container near an
    # accessible occupied room; the player can recover the vanilla block.

# Existing gameplay rooms retain their floor height and passages. Update
# walls, roof profiles, material transitions and surrounding architecture.
existing={
 'farfield_camp_site':(13,'iron_block','smooth_quartz','polished_andesite','weathered_cut_copper','cyan_terracotta'),
 'grid_hub_site':(13,'cracked_deepslate_tiles','mossy_stone_bricks','polished_deepslate','oxidized_cut_copper','cyan_terracotta'),
 'echo_ward_site':(13,'smooth_quartz','calcite','polished_andesite','weathered_cut_copper','light_blue_terracotta'),
 'intrusion_checkpoint_site':(13,'polished_blackstone','polished_blackstone_bricks','polished_deepslate','polished_blackstone','red_terracotta'),
 'foundry_annex_site':(13,'smooth_sandstone','cut_sandstone','polished_blackstone','waxed_cut_copper','orange_terracotta'),
 'maintenance_relay_site':(13,'cracked_deepslate_tiles','deepslate_bricks','polished_deepslate','weathered_cut_copper','cyan_terracotta'),
 'rainline_town_site':(13,'polished_andesite','stone_bricks','polished_andesite','oxidized_cut_copper','cyan_terracotta'),
 'saltline_town_site':(13,'smooth_sandstone','cut_sandstone','polished_andesite','smooth_sandstone','orange_terracotta'),
 'shelter_bunker':(8,'polished_deepslate','deepslate_bricks','deepslate_tiles','waxed_cut_copper','yellow_terracotta'),
 'orbital_city':(1,'polished_blackstone','smooth_quartz','polished_deepslate','tinted_glass','cyan_terracotta'),
 'spillway_facility':(4,'smooth_stone','stone_bricks','polished_deepslate','oxidized_cut_copper','cyan_terracotta'),
}
def rebuild_existing(s,key,plan):
    deck_y,wall,skin,base,roof,accent=plan
    original=s.blocks.copy()
    def was(x,y,z):
        if 0<=x<s.w and 0<=y<s.h and 0<=z<s.d:
            return s.label(original[s.index(x,y,z)])
        return 'void'
    surface=key.endswith('_site')
    limit=deck_y+4
    for x in range(s.w):
        for z in range(s.d):
            for y in range(deck_y+1,s.h):
                m=was(x,y,z)
                if m!=wall:
                    continue
                adjacent=[was(x+dx,y,z+dz) for dx,dz in ((1,0),(-1,0),(0,1),(0,-1))]
                if all(a not in OPEN for a in adjacent):
                    if surface and y>=limit and was(x,y+1,z) in OPEN:
                        put(s,x,y,z,roof)
                    continue
                bottom=y==deck_y+1
                cap=was(x,y+1,z) in OPEN
                vertical=was(x,y-1,z)==wall and was(x,y+1,z)==wall
                section=(x if adjacent[0] not in OPEN or adjacent[1] not in OPEN else z)
                new=base if bottom or section%6 in (0,1) else skin
                if surface and cap and y>=limit:
                    new=roof
                elif vertical and y==deck_y+2 and section%6 in (3,4):
                    new='tinted_glass' if surface and key!='grid_hub_site' else accent
                elif vertical and section%6==5 and y>=deck_y+3:
                    new=accent
                put(s,x,y,z,new)
            if surface and was(x,limit,z) not in OPEN and was(x,limit-1,z) not in OPEN and was(x,limit+1,z) in OPEN:
                if (x%6==0 or z%7==0) and was(x,limit,z) in {wall,roof,'cut_sandstone','weathered_cut_copper'}:
                    put(s,x,limit+1,z,base)
    if surface:
        # A floor inlay follows the approach lanes without moving any ports.
        mx,mz=s.w//2,s.d//2
        for x in range(1,s.w-1):
            if x not in range(mx-2,mx+3) and x%5 in (1,2):
                for z in (mz-1,mz+1):
                    if was(x,deck_y+1,z) in OPEN:
                        put(s,x,deck_y,z,accent,{'stone_bricks','polished_andesite','cut_sandstone','mossy_stone_bricks','smooth_sandstone'})
        # Tailored details sit on roofs or existing walls, above travel clearance.
        roof_features={
            'farfield_camp_site':[(6,4,'iron_bars','sea_lantern'),(14,4,'iron_bars','sea_lantern')],
            'grid_hub_site':[(14,7,'oxidized_cut_copper','moss_block'),(17,9,'oxidized_cut_copper','azalea_leaves')],
            'echo_ward_site':[(5,3,'weathered_cut_copper','light_blue_terracotta'),(5,12,'weathered_cut_copper','light_blue_terracotta')],
            'intrusion_checkpoint_site':[(7,3,'polished_blackstone','redstone_block'),(16,13,'polished_blackstone','redstone_block')],
            'foundry_annex_site':[(3,6,'polished_blackstone','cut_copper'),(3,10,'polished_blackstone','cut_copper')],
            'maintenance_relay_site':[(15,5,'iron_bars','sea_lantern'),(15,11,'iron_bars','sea_lantern')],
            'rainline_town_site':[(7,7,'weathered_cut_copper','sea_lantern'),(28,22,'weathered_cut_copper','sea_lantern')],
            'saltline_town_site':[(8,7,'cut_sandstone','orange_terracotta'),(28,22,'cut_sandstone','orange_terracotta')],
        }
        for x,z,frame,cap in roof_features[key]:
            hits=[yy for yy in range(limit-1,s.h) if was(x,yy,z) not in OPEN]
            if hits:
                top=max(hits)
                if top+1<s.h: put(s,x,top+1,z,frame,OPEN)
                if top+2<s.h: put(s,x,top+2,z,cap,OPEN)
    elif key=='orbital_city':
        # Roof trusses and marker bands above the central transit aisle.
        for x in range(10,59,7):
            for z in range(2,21):
                put(s,x,7,z,'polished_deepslate',{'tinted_glass'})
                if z in (4,11,18): put(s,x,7,z,'sea_lantern',{'polished_deepslate'})
    elif key=='spillway_facility':
        for x in range(29,46,4):
            for z in (6,9):
                put(s,x,13,z,'spillway_lamp',{'polished_deepslate'})
    else:
        for x in range(14,34,4):
            for z in range(6,18,4):
                put(s,x,14,z,'sea_lantern',{'polished_deepslate'})
    before=Counter(s.label(b) for b in original)
    after=Counter(s.label(b) for b in s.blocks)
    # Preserve block identities and positions for all scripted machinery,
    # containers, anchor blocks, existing air paths and stair surfaces.
    critical={i for i,b in enumerate(original) if any(q in s.label(b) for q in ('anchor','furnace','barrel','table','coal_block','observer','grate','casing','stairs','lectern','lodestone','water','iron_bars','lodestone','stonecutter'))}
    assert all(original[i]==s.blocks[i] for i in critical),key
    assert sum(a!=b for a,b in zip(original,s.blocks))>50,key

def reachable(s):
    start=next((p for p in [(s.w//2,0),(0,s.d//2),(s.w//2,s.d-1)] if s.get(p[0],4,p[1]) in OPEN),None)
    found={start}
    queue=deque([start])
    while queue:
        x,z=queue.popleft()
        for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)):
            p=(x+dx,z+dz)
            if p in found or not (0<=p[0]<s.w and 0<=p[1]<s.d): continue
            xx,zz=p
            if s.get(xx,3,zz) in OPEN or any(s.get(xx,y,zz) not in OPEN for y in (4,5)): continue
            found.add(p)
            queue.append(p)
    for x,z in ((s.w//2,0),(s.w//2,s.d-1),(0,s.d//2),(s.w-1,s.d//2)):
        assert (x,z) in found,(x,z,len(found))
    for i,idx in enumerate(s.blocks):
        if s.label(idx) not in {'barrel','blast_furnace','cartography_table','lodestone','smithing_table','composter','crafting_table','anvil','smoker'}: continue
        x,y,z=s.xyz(i)
        if y==4:
            assert any((x+dx,z+dz) in found for dx,dz in ((1,0),(-1,0),(0,1),(0,-1))),(x,y,z,s.label(idx))
    return len(found)

for name,plan in existing.items():
    path=sp+name+'.mcstructure'
    site=Site(old.read(path))
    rebuild_existing(site,name,plan)
    updates[path]=site.raw()

def enc(obj): return (json.dumps(obj,indent=2)+'\n').encode()
def rep(obj,a,b):
    return json.loads(json.dumps(obj).replace(a,b))

marker_template=old.read(sp+'farfield_camp.mcstructure')
sample=Site(marker_template)
site_entries=[]
salvage_tables={}
def container_loot(site,key):
    for i,idx in enumerate(site.blocks):
        if site.label(idx)!='barrel':
            continue
        x,y,z=site.xyz(i)
        # Bedrock container block entity, using an original small salvage table.
        site.metadata[str(i)]=(10,{'block_entity_data':(10,{
          'id':(8,'Barrel'),'x':(3,x),'y':(3,y),'z':(3,z),'isMovable':(1,1),
          'LootTable':(8,'loot_tables/structures/'+key+'.json'),
          'LootTableSeed':(4,0),
        })})

materials={
 'frontier_colony':['bread','wheat_seeds','copper_ingot'],
 'colony_waystation':['bread','torch','iron_nugget'],
 'coalition_city':['compass','paper','bearframe:salvaged_alloy'],
 'crashed_skiff':['copper_ingot','redstone','bearframe:salvaged_alloy'],
 'relay_nine':['redstone','amethyst_shard','bearframe:legacy_cell'],
 'frontier_ruin':['gold_nugget','paper','bearframe:salvaged_alloy'],
 'syndicate_forge':['coal','iron_ingot','bearframe:salvaged_alloy'],
 'cinder_works':['coal','copper_ingot','iron_nugget'],
 'nivalis_lab':['amethyst_shard','redstone','paper'],
 'verdantis_station':['melon_seeds','bone_meal','glow_berries'],
 'shattered_array':['amethyst_shard','iron_nugget','bearframe:legacy_cell'],
}
for idx,(key,(w,d,land,biome,spacing)) in enumerate(plans.items(),8):
    s=blank(sample,w,16,d)
    build(s,key,land)
    try:
        coverage=reachable(s)
    except AssertionError as e:
        raise ValueError(key,e) from e
    container_loot(s,key)
    assert s.metadata,key
    print(key,w,d,coverage,len(s.metadata))
    updates[sp+key+'_site.mcstructure']=s.raw()
    m=Site(marker_template)
    existing_marker=m.palette[m.blocks[0]]
    existing_marker['states'][1]['bearframe:site']=(3,idx)
    updates[sp+key+'.mcstructure']=m.raw()
    for category in ('structures','template_pools','structure_sets'):
        path=bp+'worldgen/'+category+'/'
        data=rep(json.loads(old.read(path+'farfield_camp.json')),'farfield_camp',key)
        if category=='structures':
            data['minecraft:jigsaw']['biome_filters'][0]['value']=biome
        if category=='structure_sets':
            placement=data['minecraft:structure_set']['placement']
            placement.update(salt=904100+idx*7,spacing=spacing,separation=spacing//2)
        updates[path+key+'.json']=enc(data)
    site_entries.append(f'  {{id:"{key}",biome:"{biome}",size:{{x:{w},y:16,z:{d}}},deck:3}},')
    entries=[{'type':'item','name':m if ':' in m else 'minecraft:'+m,'weight':4-i,'functions':[{'function':'set_count','count':{'min':1,'max':2 if i<2 else 1}}]} for i,m in enumerate(materials[key])]
    updates[bp+'loot_tables/structures/'+key+'.json']=enc({'pools':[{'rolls':2,'entries':entries}]})

path=bp+'scripts/surface_layout.js'
layout=old.read(path).decode()
assert layout.rstrip().endswith('];')
updates[path]=(layout.rstrip()[:-2]+'\n'+'\n'.join(site_entries)+'\n];\n').encode()
path=bp+'scripts/surface_sites.js'
placement_script=old.read(path).decode().replace('"tuff","gravel","sand"','"tuff","gravel","snow","calcite","packed_ice","andesite","sand"')
placement_script=placement_script.replace('"packed_ice","andesite"','"packed_ice"')
updates[path]=placement_script.encode()
path=bp+'blocks/surface_survey.json'
states=json.loads(old.read(path))
states['minecraft:block']['description']['states']['bearframe:site']=list(range(19))
updates[path]=enc(states)
# The scripted grade checks reject liquid and constrain foundations.
# Require documented surface height for the new candidate markers.
for name in ('Bearframe_Behavior','Bearframe_Resources'):
    path=name+'/manifest.json'
    data=json.loads(old.read(path))
    for entry in (data['header'],*data['modules'],*data.get('dependencies',[])):
        if entry.get('version')==[0,4,10]: entry['version']=[0,5,0]
    updates[path]=enc(data)
output=folder/'Bearframe_Bedrock_0.5.0.mcaddon'
with ZipFile(output,'w',ZIP_DEFLATED) as release:
    for path in sorted(set(old.namelist())|updates.keys()):
        release.writestr(path,updates[path] if path in updates else old.read(path))
with ZipFile(output) as release:
    assert release.testzip() is None
    for path in release.namelist():
        if path.endswith('.json'): json.loads(release.read(path))
        if path.endswith('.mcstructure'):
            s=Site(release.read(path))
            assert all(len(layer)==s.w*s.h*s.d and min(layer)>=-1 and max(layer)<len(s.palette) for _,layer in s.layers)
    for path in old.namelist():
        if path not in updates: assert old.read(path)==release.read(path)
print(f'Validated {len(existing)} rebuilt sites, {len(plans)} new sites, and 22 full templates.')
