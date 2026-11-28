"""Convert Nongko's iron dagger to the Field Cutter held model for private review."""
import argparse
import io
import json
from pathlib import Path
from zipfile import ZipFile
from PIL import Image

ASSETS = "assets/minecraft/"
RP = "Bearframe_Resources/"
GEOMETRY = RP + "models/entity/held_field_cutter.geo.json"
TEXTURE = RP + "textures/bearframe/held/field_cutter.png"
ANIMATION = RP + "animations/bearframe.held_gear.animation.json"
GRIP = (8, 2.375, 8)
SCALE = 2.65


def convert(base, rollback, upstream, output):
    with ZipFile(upstream) as source:
        model = json.loads(source.read(ASSETS + "models/item/iron_dagger.json"))
        atlas = Image.open(io.BytesIO(source.read(ASSETS + "textures/item/iron_dagger.png"))).convert("RGBA")
    original = atlas.copy()
    width, height = atlas.size
    cubes = []
    for index, element in enumerate(model["elements"]):
        if element["rotation"]["angle"] or element["rotation"].get("rescale"):
            raise ValueError("This conversion expects the original unrotated iron dagger elements")
        origin = [round((a - b) * SCALE, 5) for a, b in zip(element["from"], GRIP)]
        size = [round((b - a) * SCALE, 5) for a, b in zip(element["from"], element["to"])]
        uv = {}
        for face, entry in element["faces"].items():
            if entry.get("rotation") or entry["texture"] != "#0":
                raise ValueError("Unexpected face rotation or texture reference")
            u, v, r, b = [round(value * dim / 16) for value, dim in zip(entry["uv"], (width,height,width,height))]
            # Bedrock's top/bottom face UV reference corner is opposite Java's.
            if face in ("up", "down"):
                u, v, r, b = r, b, u, v
            uv[face] = {"uv": [u,v], "uv_size": [r-u,b-v]}
            # Repaint each authored UV island while preserving alpha and pixel detail.
            palette = ((23,34,38),(88,110,115))
            if index in (0,3,4,6,7):
                palette = ((46,69,76),(192,232,229))
            elif index in (5,10,12):
                palette = ((21,53,59),(102,244,225))
            elif index in (1,2,8,9):
                palette = ((54,57,53),(222,221,197))
            for y in range(min(v,b),max(v,b)):
                for x in range(min(u,r),max(u,r)):
                    rr,g,bb,a = original.getpixel((x,y))
                    if not a:
                        continue
                    light = (rr*0.2126+g*0.7152+bb*0.0722)/255
                    atlas.putpixel((x,y), tuple(round(low+(high-low)*light) for low,high in zip(*palette))+(a,))
        cubes.append({"origin": origin, "size": size, "uv": uv})
    png = io.BytesIO()
    atlas.save(png, format="PNG")
    with ZipFile(base) as current, ZipFile(rollback) as approved:
        geometry = json.loads(current.read(GEOMETRY))
        obj = geometry["minecraft:geometry"][0]
        obj["description"].update(texture_width=width,texture_height=height)
        obj["bones"][1].update(pivot=[0,0,0],cubes=cubes)
        animations = json.loads(current.read(ANIMATION))
        for camera in ("first","third"):
            pose = animations["animations"]["animation.bearframe.held.field_cutter."+camera]["bones"]
            pose["sword"]["rotation"][1] += 90
        def encode(obj):
            return (json.dumps(obj,indent=2)+"\n").encode()
        changes = {GEOMETRY:encode(geometry),TEXTURE:png.getvalue(),ANIMATION:encode(animations)}
        for pack in ("Bearframe_Behavior","Bearframe_Resources"):
            path = pack+"/manifest.json"
            manifest = json.loads(current.read(path))
            for section in [manifest["header"],*manifest["modules"],*manifest.get("dependencies",[])]:
                if section.get("version")==[0,11,45]:
                    section["version"]=[0,11,46]
            changes[path]=encode(manifest)
        for name in current.namelist():
            if name.startswith(RP+"textures/bearframe/gear/") and not name.endswith("/"):
                assert current.read(name)==approved.read(name),name
        with ZipFile(output,"w") as result:
            for entry in current.infolist():
                result.writestr(entry,changes[entry.filename] if entry.filename in changes else current.read(entry))
    with ZipFile(output) as result, ZipFile(base) as current:
        assert result.testzip() is None
        assert result.namelist()==current.namelist()
        assert {p for p in result.namelist() if result.read(p)!=current.read(p)}==changes.keys()


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    for file in ("base","rollback","upstream","output"):
        parser.add_argument(file,type=Path)
    args=parser.parse_args()
    convert(args.base,args.rollback,args.upstream,args.output)
