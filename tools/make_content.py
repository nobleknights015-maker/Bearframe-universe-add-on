from pathlib import Path
from uuid import UUID, uuid5
from PIL import Image, ImageDraw
import json
import random

ROOT=Path(__file__).resolve().parents[1]
BP,RP=ROOT/"behavior_pack",ROOT/"resource_pack"
SEED=UUID("d5efd705-1ffa-48c6-8148-6ac108170a38")
VERSION=[0,2,0]
def uid(key):
    return str(uuid5(SEED,key))
def write(root,path,content):
    target=root/path
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(content,indent=2)+"\n")
def png(path,image):
    target=RP/(path+".png")
    target.parent.mkdir(parents=True,exist_ok=True)
    image.save(target)
for root,side,module in [(RP,"Resources","resources"),(BP,"Behavior","data")]:
    data={"format_version":2,"header":{"name":"Bearframe | "+side,"description":"Farfield Survey and Bearframe City",
        "uuid":uid(side),"version":VERSION,"min_engine_version":[1,26,50]},
        "modules":[{"type":module,"uuid":uid(module),"version":VERSION}]}
    if root==BP:
        data["modules"].append({"type":"script","language":"javascript","entry":"scripts/main.js","uuid":uid("script"),"version":VERSION})
        data["dependencies"]=[{"uuid":uid("Resources"),"version":VERSION},{"module_name":"@minecraft/server","version":"2.10.0"}]
    write(root,"manifest.json",data)

write(BP,"blocks/relay_anchor.json",{"format_version":"1.26.50","minecraft:block":{
 "description":{"identifier":"bearframe:relay_anchor","states":{"bearframe:phase":[0,1,2,3]}},
 "components":{"minecraft:geometry":"minecraft:geometry.full_block",
 "minecraft:material_instances":{"*":{"texture":"bearframe_anchor","render_method":"opaque"}},
 "minecraft:destructible_by_mining":False,"minecraft:destructible_by_explosion":False}}})

terrain=Image.new("RGB",(32,32),"#59646a")
paint=ImageDraw.Draw(terrain)
for n in range(1,32,4):
    paint.line((n,0,n,31),fill="#505b61")
png("textures/bearframe/anchor",terrain)
write(RP,"textures/terrain_texture.json",{"resource_pack_name":"bearframe","texture_name":"atlas.terrain",
 "texture_data":{"bearframe_anchor":{"textures":"textures/bearframe/anchor"}}})
icon=Image.new("RGBA",(32,32))
paint=ImageDraw.Draw(icon)
paint.polygon([(4,9),(10,5),(25,5),(28,7),(28,23),(23,27),(4,27)],fill="#222a2d")
paint.polygon([(6,10),(11,7),(24,7),(26,9),(26,22),(22,25),(6,25)],fill="#b8b9a4")
paint.rectangle((9,10,23,22),fill="#27464a")
paint.line([(10,20),(13,20),(13,13),(19,13),(19,18),(23,18)],fill="#8ed5bf",width=2)
png("textures/bearframe/relay_schematic",icon)
write(RP,"textures/item_texture.json",{"resource_pack_name":"bearframe","texture_name":"atlas.items",
 "texture_data":{"bearframe_schematic":{"textures":"textures/bearframe/relay_schematic"}}})
write(BP,"items/relay_schematic.json",{"format_version":"1.21.90","minecraft:item":{
 "description":{"identifier":"bearframe:relay_schematic","menu_category":{"category":"items"}},
 "components":{"minecraft:icon":"bearframe_schematic","minecraft:max_stack_size":16,
 "minecraft:display_name":{"value":"item.bearframe:relay_schematic.name"}}}})
write(BP,"recipes/field_lantern.json",{"format_version":"1.21.0","minecraft:recipe_shapeless":{
 "description":{"identifier":"bearframe:field_lantern"},"tags":["crafting_table"],
 "ingredients":[{"item":"bearframe:relay_schematic"},{"item":"minecraft:torch"},{"item":"minecraft:iron_nugget"}],
 "unlock":[{"item":"bearframe:relay_schematic"}],"result":{"item":"minecraft:soul_lantern","count":2}}})
write(RP,"render_controllers/bearframe.render_controllers.json",{"format_version":"1.8.0","render_controllers":{
 "controller.render.bearframe":{"geometry":"Geometry.default","materials":[{"*":"Material.default"}],"textures":["Texture.default"]}}})
FACES=["north","south","east","west","up","down"]

def cube(origin,size,material,front=None):
    return {"origin":origin,"size":size,"uv":{
        f:{"uv":[((front if f=="north" and front is not None else material)%4)*16,
                 ((front if f=="north" and front is not None else material)//4)*16],"uv_size":[16,16]} for f in FACES}}
def bone(name,pivot,cubes,parent=None):
    return {"name":name,"pivot":pivot,"cubes":cubes,**({"parent":parent} if parent else {})}

def humanoid():
    c=cube
    return [
      bone("body",[0,15,0],[c([-4,10,-2],[8,10,4],0),c([-3,10,-2.4],[6,3,4.8],1),
       c([-2,15,-2.5],[4,3,.6],2,3),c([-3,12,2],[6,7,2],1),c([-2,15,3.7],[4,4,1],5)]),
      bone("head",[0,20,0],[c([-3,20,-2.5],[6,6,5],0,4),
       c([-4,21,-1.6],[1.2,3.4,3.2],2,3),c([2.8,21,-1.6],[1.2,3.4,3.2],2,3)],"body"),
      *[bone(f"arm{i}",[x,19,0],[c([x-1.4,15,-1.6],[2.8,5,3.2],0),c([x-1.1,10,-1.15],[2.2,5,2.3],1),
       c([x-1.3,10,-1.4],[2.6,3,2.8],5)],"body") for i,x in enumerate((-5.8,5.8))],
      *[bone(f"leg{i}",[x,11,0],[c([x-1.6,5,-1.6],[3.2,6,3.2],1),
       c([x-1.6,0,-1.6],[3.2,5,3.2],0),c([x-1.7,0,-2.5],[3.4,2,4.4],5)]) for i,x in enumerate((-2,2))]
    ]
def walker(scout):
    c=cube
    body=[c([-4,4,-5],[8,4,10],0),c([-3,8,-4],[6,2,7],5),
        c([-2,5,-5.5],[4,2,1],2,3),c([-4,3,2],[8,2,2],1)]
    if not scout:
        body.extend([c([-2,9,1],[4,2,5],6),c([-4,8.7,-2],[4,.8,5],6)])
    else:
        body.append(c([-1,10,1],[2,2,2],5))
    return [bone("body",[0,6,0],body),*[bone(f"leg{i}",[x,5,z],[
      c([x-1.5,4,z-1.3],[3,2.4,2.6],1),c([x-1.2,0,z-1.2],[2.4,4,2.4],0),c([x-1.6,0,z-2],[3.2,1.5,4],5)],"body")
      for i,(x,z) in enumerate([(-5,-3),(5,-3),(-5,3),(5,3)])]]

PALETTES={
 "farfield_surveyor":["#bfcbd0","#242e34","#35494f","#77dac4","#4c7a80","#387b72","#4a6353"],
 "grid_walker":["#656257","#343b39","#344c50","#68acc2","#43595d","#816d4c","#536c43"],
 "hollow_scout":["#a8afb0","#272b32","#592e33","#ea675b","#62313a","#3d3c42","#55545a"],
 "ward_resident":["#826e61","#36363e","#43364c","#c6a5dc","#634a5e","#937c69","#534e49"],
 "city_steward":["#eee0da","#393642","#513648","#f2a3c4","#9c687b","#966375","#7a796e"],
 "city_engineer":["#cdd8e0","#28333f","#384769","#87b9ed","#435f87","#596f87","#3a5668"],
 "city_watch":["#c5cbd0","#1d232d","#3c2634","#df6f75","#4a2f39","#66535c","#44404b"]}
TITLES={"farfield_surveyor":"Farfield Surveyor","grid_walker":"Legacy Maintenance Walker","hollow_scout":"Hollow Perimeter Scout",
 "ward_resident":"Ward Resident","city_steward":"Commons Steward","city_engineer":"Systems Engineer","city_watch":"Watchtower Officer"}

for name,colors in PALETTES.items():
    humanoid_model=name not in {"grid_walker","hollow_scout"}
    hostile=name=="hollow_scout"
    ident="bearframe:"+name
    atlas=Image.new("RGB",(64,32))
    draw=ImageDraw.Draw(atlas)
    rng=random.Random(name)
    for i,color in enumerate(colors):
        x,y=(i%4)*16,(i//4)*16
        draw.rectangle((x,y,x+15,y+15),fill=color,outline="#242b2d")
        for _ in range(22):
            px,py=x+rng.randrange(2,14),y+rng.randrange(2,14)
            rgb=atlas.getpixel((px,py))
            draw.point((px,py),fill=tuple(max(0,q-10) for q in rgb))
        if i in (3,4):
            draw.rectangle((x+2,y+4,x+13,y+11),fill=colors[2])
            draw.line((x+4,y+7,x+11,y+7),fill=colors[3],width=2)
        elif i!=6:
            draw.line((x+1,y+1,x+13,y+1),fill="#889594")
            draw.line((x+4,y+13,x+11,y+13),fill="#333c3f")
    texture="textures/bearframe/"+name
    png(texture,atlas)
    bones=humanoid() if humanoid_model else walker(hostile)
    if name=="ward_resident":
        bones[1]["cubes"]=bones[1]["cubes"][:1]
        bones[0]["cubes"]=[cube([-3.5,10,-2],[7,10,4],0),cube([-3,15,-2.4],[5,2,.7],2,3),
                            cube([2,10,-2.6],[1.5,8,5.2],1),cube([-4.3,11,-2.2],[1,7,2],5)]
        bones[2]["cubes"]=[cube([-7.1,11,-.8],[2,7,1.8],1),cube([-7.5,10,-1],[2.8,3,2.2],5)]
    elif name=="city_watch":
        bones[0]["cubes"].append(cube([-4.6,11,2],[9.2,8,1.3],1,2))
        bones[2]["cubes"].append(cube([-7.8,16,-2],[3.5,4,4],0))
        bones[3]["cubes"].append(cube([4.3,16,-2],[3.5,4,4],0))
    elif name=="city_steward":
        bones[0]["cubes"].append(cube([-4,11,-2.7],[1.4,8,5.1],5))
    elif name=="city_engineer":
        bones[0]["cubes"].append(cube([1.2,12,-2.65],[2.7,3,.8],5))
    geometry="geometry.bearframe."+name
    write(RP,"models/entity/"+name+".geo.json",{"format_version":"1.12.0","minecraft:geometry":[{
      "description":{"identifier":geometry,"texture_width":64,"texture_height":32,"visible_bounds_width":2,
       "visible_bounds_height":3,"visible_bounds_offset":[0,.8,0]},"bones":bones}]})
    prefix="animation.bearframe."+name
    moves={f"leg{i}":{"rotation":[f"math.sin(query.modified_distance_moved * 42) * {25 if i%2==0 else -25}",0,0]}
           for i in range(2 if humanoid_model else 4)}
    if humanoid_model:
        for i in range(2):
            moves[f"arm{i}"]={"rotation":[f"math.sin(query.modified_distance_moved * 42) * {-19 if i==0 else 19}",0,0]}
    animations={prefix+".idle":{"loop":True,"bones":{
      "body":{"rotation":[0,0,"math.sin(query.life_time * 85) * 1.4"]}}},
      prefix+".walk":{"loop":True,"bones":moves}}
    write(RP,"animations/"+name+".animation.json",{"format_version":"1.8.0","animations":animations})
    write(RP,"entity/"+name+".entity.json",{"format_version":"1.10.0","minecraft:client_entity":{"description":{
      "identifier":ident,"materials":{"default":"entity"},"textures":{"default":texture},"geometry":{"default":geometry},
      "animations":{"idle":prefix+".idle","walk":prefix+".walk"},
      "scripts":{"animate":["idle",{"walk":"query.modified_move_speed > 0.02"}]},
      "render_controllers":["controller.render.bearframe"],"spawn_egg":{"base_color":colors[0],"overlay_color":colors[3]}}}})
    components={"minecraft:type_family":{"family":[name,"mob"]+(["monster"] if hostile else [])},
     "minecraft:health":{"value":24 if hostile else 26,"max":24 if hostile else 26},
     "minecraft:collision_box":{"width":.72 if humanoid_model else .92,"height":1.7 if humanoid_model else .82},
     "minecraft:physics":{},"minecraft:persistent":{},"minecraft:movement":{"value":.23 if hostile else .13},
     "minecraft:movement.basic":{},"minecraft:navigation.walk":{"avoid_damage_blocks":True},
     "minecraft:jump.static":{},"minecraft:behavior.float":{"priority":0},
     "minecraft:behavior.random_stroll":{"priority":6,"speed_multiplier":.7,"xz_dist":4,"y_dist":1},
     "minecraft:behavior.look_at_player":{"priority":7,"look_distance":6,"probability":.2}}
    if hostile:
        components.update({"minecraft:attack":{"damage":4},
         "minecraft:behavior.melee_attack":{"priority":3,"speed_multiplier":1.05,"track_target":True},
         "minecraft:behavior.nearest_attackable_target":{"priority":2,"must_see":True,"must_see_forget_duration":2,
          "entity_types":[{"filters":{"test":"is_family","subject":"other","value":"player"},"max_dist":10}]},
         "minecraft:loot":{"table":"loot_tables/entities/hollow_scout.json"}})
    else:
        components["minecraft:interact"]={"interactions":[{"interact_text":"Talk" if humanoid_model else "Inspect","on_interact":{"event":"bearframe:look","target":"self"}}]}
        if humanoid_model:
            components["minecraft:damage_sensor"]={"triggers":[{"cause":"all","deals_damage":"no"}]}
    write(BP,"entities/"+name+".json",{"format_version":"1.21.0","minecraft:entity":{"description":{
        "identifier":ident,"is_spawnable":True,"is_summonable":True},"components":components,
        "events":{} if hostile else {"bearframe:look":{}}}})
write(BP,"loot_tables/entities/hollow_scout.json",{"pools":[{"rolls":1,"entries":[
 {"type":"item","name":"minecraft:copper_ingot","weight":3},
 {"type":"item","name":"minecraft:redstone","weight":2}]}]})
write(RP,"texts/languages.json",["en_US"])
(RP/"texts/en_US.lang").write_text("item.bearframe:relay_schematic.name=Relay Schematic\n"+"\n".join(
 f"entity.bearframe:{key}.name={name}\nitem.spawn_egg.entity.bearframe:{key}.name=Spawn {name}" for key,name in TITLES.items())+"\n")

approach=json.loads((BP/"blocks/relay_anchor.json").read_text())
approach["minecraft:block"]["description"]={"identifier":"bearframe:approach_anchor","states":{"bearframe:graded":[False,True]}}
write(BP,"blocks/approach_anchor.json",approach)

region=json.loads((BP/"blocks/relay_anchor.json").read_text())
region["minecraft:block"]["description"]={"identifier":"bearframe:region_anchor","states":{
    "bearframe:region":[0,1,2,3,4],"bearframe:status":[0,1,2]}}
write(BP,"blocks/region_anchor.json",region)
write(BP,"dimensions/city_orbit.json",{"format_version":"1.26.50","minecraft:dimension":{
 "description":{"identifier":"bearframe:city_orbit"},"components":{
 "minecraft:dimension_height":{"min_y":-64,"height_range":384},
 "minecraft:generation":{"generator_type":"void"},"minecraft:default_biome":{"biome":"minecraft:the_end"}}}})

badge=Image.new("RGBA",(32,32))
paint=ImageDraw.Draw(badge)
paint.polygon([(16,3),(26,9),(26,23),(16,29),(6,23),(6,9)],fill="#253039")
paint.polygon([(16,5),(24,10),(24,22),(16,27),(8,22),(8,10)],fill="#a5abae")
paint.polygon([(16,8),(22,12),(22,20),(16,24),(10,20),(10,12)],fill="#315657")
paint.line([(11,20),(16,11),(21,20)],fill="#8ee3c6",width=2)
paint.line([(12,18),(20,18)],fill="#b4e1d3",width=2)
png("textures/bearframe/farfield_insignia",badge)
atlas=json.loads((RP/"textures/item_texture.json").read_text())
atlas["texture_data"]["bearframe_insignia"]={"textures":"textures/bearframe/farfield_insignia"}
write(RP,"textures/item_texture.json",atlas)
write(BP,"items/farfield_insignia.json",{"format_version":"1.21.90","minecraft:item":{
 "description":{"identifier":"bearframe:farfield_insignia","menu_category":{"category":"items"}},
 "components":{"minecraft:icon":"bearframe_insignia","minecraft:max_stack_size":1,
 "minecraft:display_name":{"value":"item.bearframe:farfield_insignia.name"}}}})
with (RP/"texts/en_US.lang").open("a") as language:
    language.write("item.bearframe:farfield_insignia.name=Farfield Survey Insignia\n")
