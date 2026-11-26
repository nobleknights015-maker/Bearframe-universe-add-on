"""Verify every packaged member against the actual checked-in source, plus key integration links."""
import json
import sys
from pathlib import Path
from zipfile import ZipFile
ROOT=Path(__file__).resolve().parents[1]
PACKS={"behavior_pack":"Bearframe_Behavior","resource_pack":"Bearframe_Resources"}
def main():
    with ZipFile(sys.argv[1]) as z:
        assert z.testzip() is None
        names=z.namelist()
        assert len(names)==len(set(names))
        expected={}
        for folder,prefix in PACKS.items():
            for p in (ROOT/folder).rglob("*"):
                if p.is_file() and not any(part.startswith(".") for part in p.relative_to(ROOT/folder).parts):
                    expected[prefix+"/"+p.relative_to(ROOT/folder).as_posix()]=p.read_bytes()
        assert set(names)==set(expected), "missing or unexpected package member"
        for name,data in expected.items():
            assert z.read(name)==data, name
        bp="Bearframe_Behavior/"
        rp="Bearframe_Resources/"
        read=lambda p:json.loads(z.read(p))
        items={read(p)["minecraft:item"]["description"]["identifier"]:read(p)["minecraft:item"] for p in names if p.startswith(bp+"items/") and p.endswith(".json")}
        atlas=read(rp+"textures/item_texture.json")["texture_data"]
        animations={}
        for p in names:
            if p.startswith(rp+"animations/") and p.endswith(".json"):
                animations.update(read(p).get("animations",{}))
        count=0
        for p in names:
            if p.startswith(rp+"attachables/") and p.endswith(".json"):
                d=read(p)["minecraft:attachable"]["description"]
                ident=d["identifier"]
                assert ident in items, ident
                icon=items[ident]["components"]["minecraft:icon"]
                assert isinstance(icon,str)
                assert rp+atlas[icon]["textures"]+".png" in expected, ident
                assert rp+d["textures"]["default"]+".png" in expected, ident
                geo=read(rp+"models/entity/held_"+ident.split(":")[1]+".geo.json")["minecraft:geometry"][0]
                assert geo["description"]["identifier"]==d["geometry"]["default"],ident
                bones={b["name"] for b in geo["bones"]}
                for bone in geo["bones"]:
                    assert "parent" not in bone or bone["parent"] in bones,ident
                for alias,anim in d.get("animations",{}).items():
                    assert anim in animations,anim
                    assert set(animations[anim].get("bones",{}))<=bones,anim
                count+=1
        assert count==18
        print(f"Verified {len(names)} byte-identical package members and {count} complete held-item asset chains")
if __name__=="__main__": main()
