"""Redraw the Field Log Pad sprite and package a before-and-after preview."""
import io
import json
import sys
from copy import copy
from zipfile import ZipFile
from PIL import Image, ImageDraw, ImageFont

TEXTURE="Bearframe_Resources/textures/bearframe/field_log_pad.png"


def draw_pad():
    img=Image.new("RGBA",(32,32))
    d=ImageDraw.Draw(img)
    # Angled chassis, right-side depth, and recessed screen.
    d.polygon([(8,1),(24,4),(29,8),(25,27),(21,31),(4,27),(1,23),(5,5)],fill="#111923")
    d.polygon([(25,5),(28,8),(24,26),(21,30),(20,26)],fill="#344856")
    d.polygon([(8,3),(24,6),(26,8),(22,26),(19,28),(5,25),(3,22),(7,5)],fill="#879b9d")
    d.polygon([(8,4),(23,7),(24,9),(21,25),(19,27),(6,24),(4,22),(8,6)],fill="#273946")
    d.line([(8,5),(22,8)],fill="#c1d5cf")
    d.line([(7,7),(4,21)],fill="#6d8790")
    d.polygon([(9,7),(22,10),(20,22),(7,19)],fill="#121f2b")
    d.polygon([(10,8),(21,11),(19,21),(8,18)],fill="#173f4e")
    d.polygon([(10,8),(21,11),(21,12),(10,10)],fill="#34707c")
    # Route trace and stacked record entries read as a field journal.
    d.line([(10,15),(12,13),(14,15),(17,13),(19,14)],fill="#72e5d5")
    d.point([(10,15),(17,13)],fill="#d7fff1")
    d.line([(10,17),(13,18)],fill="#5caaa9")
    d.line([(10,19),(15,20)],fill="#347d88")
    d.line([(16,18),(18,18)],fill="#93ede0")
    d.polygon([(6,21),(18,24),(18,26),(6,23)],fill="#3c5360")
    d.point([(8,22),(9,22)],fill="#72f6db")
    d.point((12,23),fill="#efbb65")
    d.line([(24,13),(23,16)],fill="#a3b9ae")
    d.line([(23,19),(22,21)],fill="#557281")
    d.line([(5,24),(18,27)],fill="#aac0bb")
    d.point([(8,4),(24,8),(4,22),(20,26)],fill="#e0e7d6")
    return img


def main(base,output,preview):
    new=draw_pad()
    blob=io.BytesIO()
    new.save(blob,format="PNG")
    changes={TEXTURE:blob.getvalue()}
    with ZipFile(base) as pack:
        old=Image.open(io.BytesIO(pack.read(TEXTURE))).convert("RGBA")
        for prefix in ("Bearframe_Behavior/","Bearframe_Resources/"):
            path=prefix+"manifest.json"
            manifest=json.loads(pack.read(path))
            assert manifest["header"]["version"]==[0,11,51]
            for entry in [manifest["header"],*manifest["modules"],*manifest.get("dependencies",[])]:
                if entry.get("version")==[0,11,51]:
                    entry["version"]=[0,11,52]
            changes[path]=(json.dumps(manifest,indent=2)+"\n").encode()
        with ZipFile(output,"w") as new_pack:
            for entry in pack.infolist():
                new_pack.writestr(copy(entry),changes[entry.filename] if entry.filename in changes else pack.read(entry))
        with ZipFile(output) as new_pack:
            assert new_pack.testzip() is None
            assert new_pack.namelist()==pack.namelist()
            assert {p for p in new_pack.namelist() if new_pack.read(p)!=pack.read(p)}==changes.keys()
    sheet=Image.new("RGB",(616,345),"#152026")
    d=ImageDraw.Draw(sheet)
    font=ImageFont.truetype("DejaVuSans.ttf",18)
    for i,(name,icon) in enumerate([("0.11.51",old),("0.11.52",new)]):
        x=16+i*300
        d.rounded_rectangle((x,17,x+281,327),radius=8,fill="#293a43")
        scaled=icon.resize((224,224),Image.Resampling.NEAREST)
        sheet.paste(scaled,(x+28,32),scaled)
        sheet.paste(icon,(x+230,271),icon)
        d.text((x+22,283),name,font=font,fill="#edf4ec")
    sheet.save(preview)


if __name__=="__main__":
    main(*sys.argv[1:])
