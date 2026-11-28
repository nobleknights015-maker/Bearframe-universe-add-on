"""Apply the Field Cutter finish to the held models in the 0.11.47 review build."""
import io
from copy import copy
import json
import math
import sys
from zipfile import ZipFile

from PIL import Image

ROOT = "Bearframe_Resources/"
MODELS = ROOT + "models/entity/held_"
ATLAS = ROOT + "textures/bearframe/held/"
VERSION = [0, 11, 48]
ACCENTS = {
    "phase_edge": (99, 207, 255), "watchtower_lance": (255, 113, 123),
    "foundry_prototype": (255, 184, 75), "seam_splitter": (92, 237, 251),
    "veil_anchor": (213, 150, 255), "hush_pendulum": (255, 192, 81),
    "rook_hammer": (216, 150, 255), "palinode_ram": (78, 222, 237),
    "gantry_rake": (78, 222, 237), "cinder_inductor": (95, 222, 233),
    "silt_discharge": (113, 206, 224), "rrs_razor_signature_weapon": (219, 151, 255),
    "rrs_oreman_signature_weapon": (255, 192, 83), "repair_wrench": (98, 225, 198),
}
for tier,color in enumerate(((210,230,235),(67,222,152),(48,201,244),
                             (183,104,243),(255,191,69),(250,84,120)),1):
    ACCENTS[f"cyber_katana_mk{tier}"] = color


def engrave(tile, cube, face, accent, katana):
    width,height = tile.size
    _,base_y,base_z = cube["origin"]
    _,length,span = cube["size"]
    if face not in ("east","west") or width < 2:
        return
    for y in range(height):
        y_coord = base_y + length * (1-(y+.5)/height)
        for x in range(width):
            r,g,b,a = tile.getpixel((x,y))
            if not a or (max(r,g,b)>175 and max(r,g,b)-min(r,g,b)>43):
                continue
            z_coord = base_z + span * ((x+.5)/width if face=="east" else 1-(x+.5)/width)
            light = (r+2*g+b)/4
            color = None
            if -4.0 < y_coord < 3.8 and 1.1 <= (y_coord+4)%1.25:
                color = (min(140,int(light)+27),min(153,int(light)+33),min(157,int(light)+37))
            elif 3.8 <= y_coord < 6.6 and abs(z_coord-.5)<.43:
                color = accent if 4.45 < y_coord < 5.65 else (28,45,53)
            elif y_coord >= 7:
                # The channel follows blade segments on katanas and the tool axis on compact heads.
                center = base_z + span*.5 if katana else .68
                distance = abs(z_coord-center)
                if distance < .20 and (katana or span>1.1):
                    color = accent if .55 < (y_coord-7)%3.1 < 2.35 else (40,59,66)
                elif distance < .41 and span>1.1:
                    color = (32,48,54)
                elif light > 105 and (y_coord-7)%4.8 < .15:
                    color = (int(light*.72),int(light*.77),int(light*.78))
            if color:
                tile.putpixel((x,y),(*color,a))


def repaint(blob, geometry, item):
    source = Image.open(io.BytesIO(blob)).convert("RGBA")
    model = geometry["minecraft:geometry"][0]
    canvas = Image.new("RGBA",(256,1024))
    canvas.paste(source,(0,0))
    packed = {}
    cursor_x,cursor_y,row_height = 1,130,0
    for bone in model["bones"]:
        for cube in bone.get("cubes",[]):
            for face in ("east","west"):
                uv = cube["uv"][face]
                u,v = map(int,uv["uv"])
                du,dv = map(int,uv["uv_size"])
                tile = source.crop((min(u,u+du),min(v,v+dv),max(u,u+du),max(v,v+dv)))
                if du<0:
                    tile=tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                if dv<0:
                    tile=tile.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
                original = tile.tobytes()
                engrave(tile,cube,face,ACCENTS[item],item.startswith("cyber_katana"))
                if tile.tobytes()==original:
                    continue
                w,h=tile.size
                key=(w,h,tile.tobytes())
                if key not in packed:
                    if cursor_x+w+1>canvas.width:
                        cursor_x,cursor_y,row_height=1,cursor_y+row_height+2,0
                    if cursor_y+h>=canvas.height:
                        raise ValueError("Texture capacity exceeded for "+item)
                    canvas.paste(tile,(cursor_x,cursor_y))
                    packed[key]=[cursor_x,cursor_y]
                    cursor_x+=w+2
                    row_height=max(row_height,h)
                uv.update(uv=packed[key],uv_size=[w,h])
    assert packed,item
    height=2**math.ceil(math.log2(cursor_y+row_height+1))
    canvas=canvas.crop((0,0,canvas.width,height))
    model["description"].update(texture_width=canvas.width,texture_height=canvas.height)
    output=io.BytesIO()
    canvas.save(output,format="PNG")
    return output.getvalue()


def main(base, output):
    with ZipFile(base) as original:
        changes={}
        for item in ACCENTS:
            path=MODELS+item+".geo.json"
            texture=ATLAS+item+".png"
            geometry=json.loads(original.read(path))
            changes[texture]=repaint(original.read(texture),geometry,item)
            changes[path]=(json.dumps(geometry,indent=2)+"\n").encode()
        for pack in ("Bearframe_Behavior","Bearframe_Resources"):
            path=pack+"/manifest.json"
            manifest=json.loads(original.read(path))
            assert manifest["header"]["version"]==[0,11,47]
            for entry in [manifest["header"],*manifest["modules"],*manifest.get("dependencies",[])]:
                if entry.get("version")==[0,11,47]:
                    entry["version"]=VERSION
            changes[path]=(json.dumps(manifest,indent=2)+"\n").encode()
        with ZipFile(output,"w") as result:
            for entry in original.infolist():
                result.writestr(copy(entry),changes[entry.filename] if entry.filename in changes else original.read(entry))
        with ZipFile(output) as result:
            assert result.testzip() is None
            assert result.namelist()==original.namelist()
            assert {entry for entry in result.namelist() if result.read(entry)!=original.read(entry)}==changes.keys()
            for item in ACCENTS:
                path=MODELS+item+".geo.json"
                before,after=[json.loads(pack.read(path))["minecraft:geometry"][0] for pack in (original,result)]
                for model in (before,after):
                    for bone in model["bones"]:
                        for cube in bone.get("cubes",[]):
                            cube.pop("uv")
                assert before["bones"]==after["bones"],item
    print(f"Verified {len(ACCENTS)+1} weapons including Field Cutter and all six katanas.")


if __name__=="__main__":
    main(*sys.argv[1:])
