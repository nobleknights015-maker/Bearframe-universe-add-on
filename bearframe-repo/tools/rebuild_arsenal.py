"""Rebuild held weapons from authored Java cuboids and source UV islands."""
import io
import json
import math
import sys
from copy import copy
from pathlib import Path
from zipfile import ZipFile

from PIL import Image

from finish_arsenal import ACCENTS, ATLAS, MODELS, ROOT

# Source model, grip center in Java coordinates, final length in Bedrock units.
SOURCES = {
    "phase_edge": ("azure_sabre", (8,4.0,8), 24),
    "watchtower_lance": ("crimson_lance", (8,5.5,8), 31),
    "foundry_prototype": ("crimson_cleaver", (8,2.55,8), 25),
    "seam_splitter": ("iron_sai", (8,2.7,8), 22),
    "veil_anchor": ("revenants_gravescepter", (8,4.2,8), 26),
    "hush_pendulum": ("iron_mace", (8,3.5,8), 26),
    "rook_hammer": ("black_iron_clobberer", (8,3.15,8), 28),
    "palinode_ram": ("treacherous_bludgeon", (8,3.4,8), 25),
    "gantry_rake": ("iron_halberd", (7.75,3.6,0.0625), 30),
    "cinder_inductor": ("iron_polearm", (7,4.1,8), 26),
    "silt_discharge": ("opaline_lance", (8,4.5,8), 26),
    "rrs_razor_signature_weapon": ("vengeance_blade", (8,2.4,8), 23),
    "rrs_oreman_signature_weapon": ("amethyst_greatpick", (8,4.3,8), 25),
    "repair_wrench": ("iron_battle_axe", (8,4,8), 19),
}
for tier in range(1,7):
    SOURCES[f"cyber_katana_mk{tier}"] = (
        "uchigatana" if tier <= 3 else "gloomsteel_katana",
        (8,3.45 if tier <= 3 else 2.65,8), 32 + tier*.65,
    )

JAVA = "assets/minecraft/"
BLADED = {"phase_edge","watchtower_lance","foundry_prototype","seam_splitter",
          "gantry_rake","silt_discharge","rrs_razor_signature_weapon"}
WEATHERED = {"palinode_ram","gantry_rake","cinder_inductor","silt_discharge"}


class Atlas:
    def __init__(self):
        self.image = Image.new("RGBA",(256,1024))
        self.x, self.y, self.row = 1,1,0
        self.tiles = {}

    def add(self,tile):
        width,height=tile.size
        key=(tile.size,tile.tobytes())
        if key not in self.tiles:
            if self.x + width >= self.image.width:
                self.x,self.y,self.row=1,self.y+self.row+2,0
            if self.y + height >= self.image.height:
                raise ValueError("Atlas out of space")
            self.image.paste(tile,(self.x,self.y))
            self.tiles[key]=(self.x,self.y)
            self.x += width+2
            self.row=max(self.row,height)
        return {"uv":list(self.tiles[key]),"uv_size":[width,height]}

    def encode(self):
        height=2**math.ceil(math.log2(self.y+self.row+1))
        image=self.image.crop((0,0,self.image.width,height))
        output=io.BytesIO()
        image.save(output,format="PNG")
        return image.size,output.getvalue()


def textures_for(source,model):
    textures={}
    for key,ref in model["textures"].items():
        if key=="particle":
            continue
        path=JAVA+"textures/"+ref.removeprefix("minecraft:")+".png"
        texture=Image.open(io.BytesIO(source.read(path))).convert("RGBA")
        if path+".mcmeta" in source.namelist():
            animation=json.loads(source.read(path+".mcmeta"))["animation"]
            width=animation.get("width",min(texture.size))
            height=animation.get("height",min(texture.size))
            frame=animation.get("frames",[0])[0]
            if isinstance(frame,dict):
                frame=frame["index"]
            x,y=(frame%(texture.width//width))*width,(frame//(texture.width//width))*height
            texture=texture.crop((x,y,x+width,y+height))
        textures["#"+key]=texture
    return textures


def face_tile(texture,face,entry):
    w,h=texture.size
    u,v,r,b=[round(value*size/16) for value,size in zip(entry["uv"],(w,h,w,h))]
    if r==u:
        r+=1
    if b==v:
        b+=1
    tile=texture.crop((min(u,r),min(v,b),max(u,r),max(v,b)))
    if u>r:
        tile=tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if v>b:
        tile=tile.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    if entry.get("rotation"):
        tile=tile.rotate(-entry["rotation"],expand=True)
    if face in ("up","down"):
        tile=tile.transpose(Image.Transpose.ROTATE_180)
    return tile


def repaint(tile,element,face,item,grip,scale):
    width,height=tile.size
    origin,end=element["from"],element["to"]
    katana=item.startswith("cyber_katana")
    for y in range(height):
        local_y=(end[1]-(end[1]-origin[1])*(y+.5)/height-grip[1])*scale
        for x in range(width):
            r,g,b,a=tile.getpixel((x,y))
            if not a:
                continue
            level=(.2126*r+.7152*g+.0722*b)/255
            grip_zone=-5.5<local_y<3.2
            hot=max(r,g,b)>95 and (max(r,g,b)-min(r,g,b))>43
            local_x=origin[0]+(end[0]-origin[0])*((x+.5)/width if face=="south" else 1-(x+.5)/width)
            bar=face in ("north","south") and abs(local_x-grip[0])<(.095 if katana else .17)
            if grip_zone:
                low,high=(16,25,30),(76,93,101)
            elif item in WEATHERED:
                low,high=(35,44,47),(195,188,157)
            else:
                low,high=(29,42,51),(203,222,220)
            colors=tuple(round(lo+(hi-lo)*level) for lo,hi in zip(low,high))
            if katana and hot and not grip_zone:
                colors=tuple(round(c*(.48+.52*level)) for c in ACCENTS[item])
            if local_y>3.2 and bar:
                if local_y < 5 or 1.1 < local_y%3.6 < 2.7:
                    colors=ACCENTS[item]
                else:
                    colors=(26,47,54)
            if item in BLADED and local_y>8 and face in ("east","west") and level>.45:
                colors=tuple(min(241,c+22) for c in colors)
            tile.putpixel((x,y),(*colors,a))
    return tile


def convert(source,item,previous):
    model_name,grip,length=SOURCES[item]
    java=json.loads(source.read(JAVA+"models/item/"+model_name+".json"))
    elements=java["elements"]
    scale=length/(max(e["to"][1] for e in elements)-min(e["from"][1] for e in elements))
    textures=textures_for(source,java)
    atlas=Atlas()
    model=previous["minecraft:geometry"][0]
    sword=next(b for b in model["bones"] if b["name"]=="sword")
    sword["pivot"]=[0,0,.5]
    sword["cubes"]=[]
    trim_at = {"repair_wrench":7.65,"rook_hammer":5.15}.get(item)
    for element in elements:
        if trim_at is not None and element["from"][1] >= trim_at:
            continue
        assert not element.get("rotation",{}).get("angle"),model_name
        uv={}
        for face,entry in element["faces"].items():
            tile=face_tile(textures[entry["texture"]],face,entry)
            uv[face]=atlas.add(repaint(tile,element,face,item,grip,scale))
        origin=[round((a-b)*scale,5) for a,b in zip(element["from"],grip)]
        origin[2]+=.5
        size=[round((b-a)*scale,5) for a,b in zip(element["from"],element["to"])]
        # Turn authored blade faces to the original Bedrock side-on grip plane.
        sword["cubes"].append({"origin":origin,"size":size,"pivot":[0,0,.5],
                               "rotation":[0,-90,0],"uv":uv})
    if trim_at is not None:
        # Retain the authored handles and replace the fantasy heads with
        # Bearframe tool hardware, sized from the actual shaft coupling.
        top = (trim_at-grip[1])*scale
        metal = Image.new("RGBA",(8,8),(129,150,152,255))
        edge = Image.new("RGBA",(4,8),(183,199,197,255))
        dark = Image.new("RGBA",(4,8),(39,58,66,255))
        emitter = Image.new("RGBA",(4,8),(*ACCENTS[item],255))
        for i in range(8):
            metal.putpixel((i,1),(172,185,181,255))
            metal.putpixel((i,7),(75,91,97,255))
        charts = [atlas.add(tile) for tile in (metal,edge,dark,emitter)]
        if item=="repair_wrench":
            hardware=[
                ((-1.0,top-.7,-1.2),(2.0,2.0,3.4),0),
                ((-.78,top+1.1,-2.1),(1.56,1.25,5.2),2),
                ((-.88,top+2,-2.1),(1.76,3.0,1.05),0),
                ((-.88,top+2,2.0),(1.76,3.0,1.1),0),
                ((-.67,top+4.2,-1.05),(1.34,.8,.52),1),
                ((-.67,top+4.2,1.45),(1.34,.8,.55),1),
                ((-.81,top+1.45,-.25),(1.62,.42,1.45),3),
            ]
        else:
            top+=9
            hardware=[
                ((-.8,top-10,-.4),(1.6,11,1.8),2),
                ((-1.32,top-1,-3.2),(2.64,4.2,7.4),0),
                ((-1.52,top-.6,-1.46),(3.04,3.4,3.92),2),
                ((-1.19,top-.64,-4.48),(2.38,3.35,1.35),1),
                ((-1.19,top-.64,4.13),(2.38,3.35,1.35),1),
                ((-1.55,top+.49,-.65),(3.10,.68,2.30),3),
            ]
        for origin,size,material in hardware:
            sword["cubes"].append({"origin":list(origin),"size":list(size),
                "uv":{face:charts[material] for face in ("north","south","east","west","up","down")}})
    for bone in model["bones"]:
        if not bone["name"].startswith("pulse_"):
            continue
        index=int(bone["name"].split("_")[1])
        y=8+index*3.4
        blade_cells=[c for c in sword["cubes"] if c["origin"][1]<=y<=c["origin"][1]+c["size"][1]]
        if not blade_cells:
            bone.pop("cubes",None)
            continue
        blade=min(blade_cells,key=lambda c:c["origin"][0])
        z=blade["origin"][0]+.5
        right=max(.5-c["origin"][2] for c in blade_cells)
        color=atlas.add(Image.new("RGBA",(2,4),(*ACCENTS[item],255)))
        bone["pivot"]=[0,y+.5,z+.1]
        bone["cubes"]=[{"origin":[side,y,z],"size":[.09,1.0,.20],
                        "uv":{face:color for face in ("north","south","east","west","up","down")}}
                       for side in (right-.035,-right-.055)]
    bounds,texture=atlas.encode()
    model["description"].update(texture_width=bounds[0],texture_height=bounds[1])
    return previous,texture,len(elements),model_name


def encode(value):
    return (json.dumps(value,indent=2)+"\n").encode()


def main(base,reference,output):
    changes={}
    ledger=[]
    with ZipFile(base) as baseline, ZipFile(reference) as source:
        for item in SOURCES:
            path=MODELS+item+".geo.json"
            geometry,atlas,count,model=convert(source,item,json.loads(baseline.read(path)))
            changes[path]=encode(geometry)
            changes[ATLAS+item+".png"]=atlas
            ledger.append(f"{item:30} {model:25} {count:3} authored elements")
        for pack in ("Bearframe_Behavior","Bearframe_Resources"):
            path=pack+"/manifest.json"
            manifest=json.loads(baseline.read(path))
            assert manifest["header"]["version"]==[0,11,47]
            for e in [manifest["header"],*manifest["modules"],*manifest.get("dependencies",[])]:
                if e.get("version")==[0,11,47]:
                    e["version"]=[0,11,49]
            changes[path]=encode(manifest)
        with ZipFile(output,"w") as result:
            for e in baseline.infolist():
                result.writestr(copy(e),changes[e.filename] if e.filename in changes else baseline.read(e))
        with ZipFile(output) as result:
            assert result.testzip() is None
            assert result.namelist()==baseline.namelist()
            changed={p for p in result.namelist() if result.read(p)!=baseline.read(p)}
            assert changed==changes.keys()
            for item in SOURCES:
                image=Image.open(io.BytesIO(result.read(ATLAS+item+".png")))
                g=json.loads(result.read(MODELS+item+".geo.json"))["minecraft:geometry"][0]
                assert image.size==(g["description"]["texture_width"],g["description"]["texture_height"])
                for bone in g["bones"]:
                    for cube in bone.get("cubes",[]):
                        for face in cube["uv"].values():
                            x,y=face["uv"]
                            w,h=face["uv_size"]
                            assert 0<=x<x+w<=image.width and 0<=y<y+h<=image.height,(item,face)
    Path(output).with_suffix(".models.txt").write_text("\n".join(ledger)+"\n")


if __name__=="__main__":
    main(*sys.argv[1:])
