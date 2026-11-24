import argparse
import io
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]
BP,RP=ROOT/"behavior_pack",ROOT/"resource_pack"
def read(path):
    return json.loads(path.read_text())
def archive(directory):
    payload=io.BytesIO()
    with zipfile.ZipFile(payload,"w",zipfile.ZIP_DEFLATED) as z:
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                z.write(path,path.relative_to(directory).as_posix())
    return payload.getvalue()
def validate():
    b,r=(read(folder/"manifest.json") for folder in (BP,RP))
    assert b["dependencies"][0]=={"uuid":r["header"]["uuid"],"version":r["header"]["version"]}
    for root in (BP,RP):
        for path in root.rglob("*.json"):
            read(path)
    for path in (BP/"scripts").glob("*.js"):
        subprocess.run(["node","--check",str(path)],check=True)
    mobs={read(p)["minecraft:entity"]["description"]["identifier"] for p in (BP/"entities").glob("*.json")}
    clients=set()
    render=set().union(*(read(p)["render_controllers"].keys() for p in (RP/"render_controllers").glob("*.json")))
    anim=set().union(*(read(p)["animations"].keys() for p in (RP/"animations").glob("*.json")))
    models={m["description"]["identifier"] for p in (RP/"models/entity").glob("*.json") for m in read(p)["minecraft:geometry"]}
    for p in (RP/"entity").glob("*.json"):
        d=read(p)["minecraft:client_entity"]["description"]
        clients.add(d["identifier"])
        assert clients <= mobs and set(d["geometry"].values()) <= models
        assert set(d["animations"].values()) <= anim and set(d["render_controllers"]) <= render
        assert all((RP/(t+".png")).is_file() for t in d["textures"].values())
    assert clients==mobs
    for registry in ("item_texture","terrain_texture"):
        for key,entry in read(RP/f"textures/{registry}.json")["texture_data"].items():
            assert key.startswith("bearframe_") and (RP/(entry["textures"]+".png")).is_file()
    assert not any("starbound" in p.name.lower() or "infinity" in p.name.lower() for root in (BP,RP) for p in root.rglob("*"))
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("output",type=Path,nargs="?",default=ROOT/"dist")
    parser.add_argument("--world",type=Path)
    args=parser.parse_args()
    OUT=args.output.resolve()
    validate()
    OUT.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(OUT/"Bearframe_Bedrock_0.2.0.mcaddon","w",zipfile.ZIP_DEFLATED) as z:
        for folder,name in [(BP,"Behavior"),(RP,"Resources")]:
            z.writestr("Bearframe_"+name+".mcpack",archive(folder))
    with zipfile.ZipFile(OUT/"Bearframe_Bedrock_Source_0.2.0.zip","w",zipfile.ZIP_DEFLATED) as z:
        for root in (BP,RP,ROOT/"docs",ROOT/"tests",ROOT/"tools"):
            for path in sorted(root.rglob("*")):
                if path.is_file() and "__pycache__" not in path.parts:
                    z.write(path,path.relative_to(ROOT).as_posix())
        for name in ("README.md","package.json",".gitignore"):
            z.write(ROOT/name,name)
        if (ROOT/".git").is_dir():
            with tempfile.TemporaryDirectory() as directory:
                bundle=Path(directory)/"Bearframe_Bedrock.gitbundle"
                subprocess.run(["git","-C",str(ROOT),"bundle","create",str(bundle),"--all"],check=True)
                z.write(bundle,bundle.name)
    if args.world:
        with zipfile.ZipFile(OUT/"Bearframe_Farfield_Arrival_0.2.0.mcworld","w",zipfile.ZIP_DEFLATED) as z:
            for name in ("level.dat","levelname.txt","world_behavior_packs.json","world_resource_packs.json"):
                z.write(args.world/name,name)
            for kind,root in (("behavior",BP),("resource",RP)):
                manifest=read(root/"manifest.json")["header"]
                expected=[{"pack_id":manifest["uuid"],"version":manifest["version"]}]
                assert read(args.world/f"world_{kind}_packs.json")==expected
                for path in sorted(root.rglob("*")):
                    if path.is_file():
                        z.write(path,f"{kind}_packs/bearframe/"+path.relative_to(root).as_posix())
            for path in (args.world/"db").glob("*"):
                if path.is_file() and path.name not in {"LOCK","LOG","LOG.old"}:
                    z.write(path,"db/"+path.name)
    for p in OUT.glob("*"):
        with zipfile.ZipFile(p) as z:
            assert z.testzip() is None
        print(p,p.stat().st_size)
if __name__=="__main__":
    main()
