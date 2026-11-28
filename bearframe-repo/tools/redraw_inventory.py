"""Create silhouette-led, palette-limited inventory sprites from the held models."""
import io
import json
import sys
from copy import copy
from zipfile import ZipFile

from PIL import Image, ImageDraw, ImageFilter, ImageFont
from held_icon_projection import render
from finish_arsenal import ROOT,MODELS

ITEM_ATLAS=ROOT+"textures/item_texture.json"
GEAR="textures/bearframe/gear/"
METAL=((32,44,53),(55,72,83),(83,108,119),(125,149,157),(173,197,197),(218,233,228))
IVORY=((36,43,45),(59,67,65),(94,102,92),(132,139,121),(177,180,152),(222,221,191))
LEGACY={"palinode_ram","gantry_rake","cinder_inductor","silt_discharge","vestige_interlock","oracle_parallax"}


def make_sprite(pack,item):
    render_target=Image.new("RGBA",(512,512))
    render(pack,item,ImageDraw.Draw(render_target),256,256)
    silhouette=render_target.getbbox()
    if not silhouette:
        raise ValueError("Missing visible held model: "+item)
    render_target=render_target.crop(silhouette)
    render_target.thumbnail((29,29),Image.Resampling.BOX)
    small=Image.new("RGBA",(32,32))
    offset=((32-render_target.width)//2,(32-render_target.height)//2)
    small.alpha_composite(render_target,offset)
    opacity=small.getchannel("A").point(lambda a:255 if a>=47 else 0)
    outline=opacity.filter(ImageFilter.MaxFilter(3))
    sprite=Image.new("RGBA",(32,32))
    sprite.paste((16,23,30,255),(0,0,32,32),outline)
    palette=IVORY if item in LEGACY else METAL
    for y in range(1,31):
        for x in range(1,31):
            if not opacity.getpixel((x,y)):
                continue
            r,g,b,_=small.getpixel((x,y))
            luminance=(r*2+g*5+b)//8
            chroma=max(r,g,b)-min(r,g,b)
            if luminance>73 and chroma>=43:
                color=tuple(min(255,round(c*1.18+10)) for c in (r,g,b))
                color=tuple(round(c/12)*12 for c in color)
            else:
                band=min(5,luminance//44+int(not opacity.getpixel((x-1,y))))
                color=palette[band]
            sprite.putpixel((x,y),(*color,255))
    return sprite


def update(source,output,preview):
    with ZipFile(source) as pack:
        atlas=json.loads(pack.read(ITEM_ATLAS))["texture_data"]
        paths=sorted({v["textures"]+".png" for v in atlas.values()
                      if isinstance(v.get("textures"),str) and v["textures"].startswith(GEAR)})
        changes={}
        sheet=Image.new("RGB",(1160,850),"#152026")
        draw=ImageDraw.Draw(sheet)
        title=ImageFont.truetype("DejaVuSans.ttf",25)
        label=ImageFont.truetype("DejaVuSans.ttf",13)
        draw.text((20,18),"THE LAST DISPATCH  /  INVENTORY PIXEL ART 0.11.51",font=title,fill="#edf4ec")
        assert len(paths)==23
        for index,path in enumerate(paths):
            item=path.removeprefix(GEAR).removesuffix(".png")
            assert MODELS+item+".geo.json" in pack.namelist(),item
            icon=make_sprite(pack,item)
            output_png=io.BytesIO()
            icon.save(output_png,format="PNG")
            changes[ROOT+path]=output_png.getvalue()
            assert icon.getbbox() and 0 in icon.getchannel("A").getextrema()
            left=20+(index%6)*190
            top=72+(index//6)*191
            draw.rounded_rectangle((left,top,left+171,top+173),radius=6,
                                   fill="#283942",outline="#435863")
            large=icon.resize((128,128),Image.Resampling.NEAREST)
            sheet.paste(large,(left+12,top+5),large)
            sheet.paste(icon,(left+130,top+103),icon)
            name=item.replace("rrs_","").replace("_signature_weapon","").replace("_"," ").title()
            draw.text((left+85,top+150),name,anchor="mm",font=label,fill="#edf4ec")
        for prefix in ("Bearframe_Behavior/",ROOT):
            path=prefix+"manifest.json"
            manifest=json.loads(pack.read(path))
            assert manifest["header"]["version"]==[0,11,50]
            for entry in [manifest["header"],*manifest["modules"],*manifest.get("dependencies",[])]:
                if entry.get("version")==[0,11,50]:
                    entry["version"]=[0,11,51]
            changes[path]=(json.dumps(manifest,indent=2)+"\n").encode()
        with ZipFile(output,"w") as target:
            for entry in pack.infolist():
                target.writestr(copy(entry),changes[entry.filename] if entry.filename in changes else pack.read(entry))
        with ZipFile(output) as target:
            assert target.testzip() is None
            assert pack.namelist()==target.namelist()
            assert {n for n in target.namelist() if target.read(n)!=pack.read(n)}==changes.keys()
    sheet.save(preview)
    print("Verified 23 inventory sprites, two version manifests and byte-identical remaining pack contents.")


if __name__=="__main__":
    update(*sys.argv[1:])
