"""Add two exclusive Ghost Grid boss drops to the 0.11.49 private review build."""
import io
import json
import sys
from copy import copy,deepcopy
from zipfile import ZipFile

from PIL import Image
from rebuild_arsenal import ACCENTS, ATLAS, MODELS, ROOT, SOURCES, WEATHERED, convert, encode

BP = "Bearframe_Behavior/"
TEMPLATE = "cinder_inductor"
ANIMATION = ROOT+"animations/bearframe.held_gear.animation.json"
WEAPONS = {
    "vestige_interlock": ("grid_vestige_arc", "Vestige Interlock", "iron_broadsword",
                           (8,2.75,6.8125), 24, (73,224,219), 11, 720),
    "oracle_parallax": ("grid_oracle_delta", "Oracle Parallax", "phantomguard_partisan",
                        (8,4.4,8), 29, (116,188,255), 10, 680),
}


def icon_for(model,texture):
    """Project the actual broad faces into a transparent 32px inventory sprite."""
    tex=Image.open(io.BytesIO(texture))
    cubes=model["minecraft:geometry"][0]["bones"][1]["cubes"]
    min_x=min(c["origin"][0] for c in cubes)
    max_x=max(c["origin"][0]+c["size"][0] for c in cubes)
    min_y=min(c["origin"][1] for c in cubes)
    max_y=max(c["origin"][1]+c["size"][1] for c in cubes)
    ratio=27/max(max_x-min_x,max_y-min_y)
    sheet=Image.new("RGBA",(32,32))
    for c in sorted(cubes,key=lambda cube:cube["origin"][2]+cube["size"][2]):
        uv=c["uv"].get("south")
        if not uv:
            continue
        u,v=uv["uv"]
        w,h=uv["uv_size"]
        x,y,_=c["origin"]
        sx,sy,_=c["size"]
        left=round(16+(x-(min_x+max_x)/2)*ratio)
        top=round(2+(max_y-y-sy)*ratio)
        right=round(16+(x+sx-(min_x+max_x)/2)*ratio)
        bottom=round(2+(max_y-y)*ratio)
        tile=tex.crop((u,v,u+w,v+h)).resize((max(1,right-left),max(1,bottom-top)),Image.Resampling.NEAREST)
        sheet.alpha_composite(tile,(left,top))
    sheet=sheet.rotate(-30,resample=Image.Resampling.NEAREST)
    output=io.BytesIO()
    sheet.save(output,format="PNG")
    return output.getvalue()


def build(base,reference,output):
    with ZipFile(base) as pack,ZipFile(reference) as source:
        def read(path):
            return json.loads(pack.read(path))
        icons=read(ROOT+"textures/item_texture.json")
        animation=read(ANIMATION)
        lang=pack.read(ROOT+"texts/en_US.lang").decode().rstrip()+"\n"
        gear=BP+"scripts/rarity/main.js"
        rarity=pack.read(gear).decode()
        changes={}
        for item,(boss,label,source_id,grip,length,accent,damage,durability) in WEAPONS.items():
            SOURCES[item]=(source_id,grip,length)
            ACCENTS[item]=accent
            WEATHERED.add(item)
            identifier="bearframe:"+item
            geom_id="geometry.bearframe.held."+item
            model,texture,_,_=convert(source,item,read(MODELS+TEMPLATE+".geo.json"))
            model["minecraft:geometry"][0]["description"]["identifier"]=geom_id
            changes[MODELS+item+".geo.json"]=encode(model)
            changes[ATLAS+item+".png"]=texture
            changes[ROOT+"textures/bearframe/gear/"+item+".png"]=icon_for(model,texture)
            icons["texture_data"]["bearframe_"+item]={"textures":"textures/bearframe/gear/"+item}
            item_def=read(BP+"items/"+TEMPLATE+".json")
            definition=item_def["minecraft:item"]
            definition["description"]={"identifier":identifier}
            definition["components"].update({
                "minecraft:icon":"bearframe_"+item,
                "minecraft:display_name":{"value":"item."+identifier+".name"},
                "minecraft:damage":damage,
                "minecraft:durability":{"max_durability":durability},
            })
            changes[BP+"items/"+item+".json"]=encode(item_def)
            lang+="item."+identifier+".name=§6[Legendary] "+label+"§r\n"
            attach=read(ROOT+"attachables/"+TEMPLATE+".json")
            description=attach["minecraft:attachable"]["description"]
            description["identifier"]=identifier
            description["textures"]["default"]="textures/bearframe/held/"+item
            description["geometry"]["default"]=geom_id
            for view in ("first","third"):
                old=description["animations"][view]
                new=old.replace(TEMPLATE,item)
                animation["animations"][new]=deepcopy(animation["animations"][old])
                description["animations"][view]=new
            changes[ROOT+"attachables/"+item+".json"]=encode(attach)
            entity_path=BP+"entities/"+boss+".json"
            entity=read(entity_path)
            components=entity["minecraft:entity"]["components"]
            assert "minecraft:loot" not in components
            loot="loot_tables/entities/boss_"+boss+".json"
            components["minecraft:loot"]={"table":loot}
            changes[entity_path]=encode(entity)
            changes[BP+loot]=encode({"pools":[{"rolls":1,"entries":[{"type":"item","name":identifier,"weight":1}]}]})
        needle="const BF_GEAR = new Set(["
        assert rarity.count(needle)==1
        rarity=rarity.replace(needle,needle+", ".join(json.dumps("bearframe:"+key) for key in WEAPONS)+", ")
        changes[gear]=rarity.encode()
        changes[ANIMATION]=encode(animation)
        changes[ROOT+"textures/item_texture.json"]=encode(icons)
        changes[ROOT+"texts/en_US.lang"]=lang.encode()
        for prefix in (BP,ROOT):
            path=prefix+"manifest.json"
            manifest=read(path)
            assert manifest["header"]["version"]==[0,11,49]
            for entry in [manifest["header"],*manifest["modules"],*manifest.get("dependencies",[])]:
                if entry.get("version")==[0,11,49]:
                    entry["version"]=[0,11,50]
            changes[path]=encode(manifest)
        with ZipFile(output,"w") as result:
            for info in pack.infolist():
                result.writestr(copy(info),changes.get(info.filename,pack.read(info)))
            for path in sorted(changes.keys()-set(pack.namelist())):
                info=copy(pack.getinfo(BP+"manifest.json"))
                info.filename=path
                result.writestr(info,changes[path])
    with ZipFile(output) as result:
        assert result.testzip() is None
        for item,(boss,*_) in WEAPONS.items():
            identifier=("bearframe:"+item).encode()
            loot=[name for name in result.namelist() if name.startswith(BP+"loot_tables/") and identifier in result.read(name)]
            assert loot==[BP+"loot_tables/entities/boss_"+boss+".json"],loot
            assert not any(identifier in result.read(name) for name in result.namelist()
                           if name.startswith(BP+"recipes/"))
            assert json.loads(result.read(BP+"entities/"+boss+".json"))["minecraft:entity"]["components"]["minecraft:loot"]["table"]==loot[0].removeprefix(BP)
            attach=json.loads(result.read(ROOT+"attachables/"+item+".json"))["minecraft:attachable"]["description"]
            model=json.loads(result.read(MODELS+item+".geo.json"))["minecraft:geometry"][0]
            assert attach["geometry"]["default"]==model["description"]["identifier"]
            animations=json.loads(result.read(ANIMATION))["animations"]
            assert all(clip in animations for clip in attach["animations"].values())
            assert ROOT+attach["textures"]["default"]+".png" in result.namelist()
            icon=icons["texture_data"]["bearframe_"+item]["textures"]
            assert ROOT+icon+".png" in result.namelist()
        print("Verified two unique boss-drop tables, held asset chains and archive integrity.")


if __name__=="__main__":
    build(*sys.argv[1:])
