import argparse
import io
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BP, RP = ROOT / "behavior_pack", ROOT / "resource_pack"
VERSION = "0.4.0"
VERSION_TUPLE = [0, 4, 0]
MAX_CUBES_PER_ENTITY = 60  # Android 4 GB RAM geometry budget


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def png_dimensions(path: Path):
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"Invalid PNG signature: {path}")
    w, h = struct.unpack(">II", data[16:24])
    return w, h


def archive(directory):
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                z.write(path, path.relative_to(directory).as_posix())
    return payload.getvalue()


def validate():
    b, r = (read(folder / "manifest.json") for folder in (BP, RP))
    assert b["header"]["version"] == VERSION_TUPLE, f"BP version mismatch: {b['header']['version']}"
    assert r["header"]["version"] == VERSION_TUPLE, f"RP version mismatch: {r['header']['version']}"
    assert b["header"]["min_engine_version"] == [1, 26, 50]
    assert r["header"]["min_engine_version"] == [1, 26, 50]
    assert b["dependencies"][0] == {"uuid": r["header"]["uuid"], "version": r["header"]["version"]}
    assert b["dependencies"][1] == {"module_name": "@minecraft/server", "version": "2.10.0"}

    # Validate all JSON files parse cleanly
    for root in (BP, RP):
        for path in root.rglob("*.json"):
            read(path)

    # Validate all JS scripts pass Node syntax checking
    for path in sorted((BP / "scripts").glob("*.js")):
        subprocess.run(["node", "--check", str(path)], check=True)

    # Collect behavior entities, items, blocks, loot tables, spawn rules
    mobs = {}
    for p in (BP / "entities").glob("*.json"):
        doc = read(p)["minecraft:entity"]
        mobs[doc["description"]["identifier"]] = doc

    items = set()
    for p in (BP / "items").glob("*.json"):
        items.add(read(p)["minecraft:item"]["description"]["identifier"])

    # Validate animation & animation controller pools
    render = set().union(*(read(p)["render_controllers"].keys() for p in (RP / "render_controllers").glob("*.json")))
    anim_defs = {}
    for p in (RP / "animations").glob("*.json"):
        anim_defs.update(read(p)["animations"])
    anim_controllers = {}
    for p in (RP / "animation_controllers").glob("*.json"):
        anim_controllers.update(read(p)["animation_controllers"])
    all_anim_keys = set(anim_defs.keys()) | set(anim_controllers.keys())

    # Validate geometry files: bone parents, UV bounds, cube counts
    models = {}
    for p in (RP / "models/entity").glob("*.json"):
        for geo in read(p)["minecraft:geometry"]:
            desc = geo["description"]
            ident = desc["identifier"]
            tw, th = desc["texture_width"], desc["texture_height"]
            bones = geo.get("bones", [])
            bone_names = {b["name"] for b in bones}
            cube_count = 0
            for bone in bones:
                if "parent" in bone:
                    assert bone["parent"] in bone_names, f"{ident}: missing parent bone {bone['parent']}"
                for cube in bone.get("cubes", []):
                    cube_count += 1
                    uv = cube.get("uv")
                    if isinstance(uv, dict):
                        for face, fspec in uv.items():
                            u, v = fspec["uv"]
                            su, sv = fspec["uv_size"]
                            assert 0 <= u <= tw and 0 <= u + su <= tw, f"{ident} {bone['name']} {face} U out of bounds"
                            assert 0 <= v <= th and 0 <= v + sv <= th, f"{ident} {bone['name']} {face} V out of bounds"
            assert cube_count <= MAX_CUBES_PER_ENTITY, f"{ident} exceeds Android cube budget ({cube_count}>{MAX_CUBES_PER_ENTITY})"
            models[ident] = {"bones": bone_names, "cubes": cube_count, "tw": tw, "th": th}

    # Validate client entities match behavior entities, geometry, animations, textures
    clients = set()
    for p in (RP / "entity").glob("*.json"):
        d = read(p)["minecraft:client_entity"]["description"]
        ident = d["identifier"]
        clients.add(ident)
        assert ident in mobs, f"Client entity {ident} missing BP definition"
        assert set(d["geometry"].values()) <= set(models.keys()), f"{ident} missing geometry"
        assert set(d.get("animations", {}).values()) <= all_anim_keys, f"{ident} missing animation/controller"
        assert set(d["render_controllers"]) <= render, f"{ident} missing render controller"
        geo_id = d["geometry"]["default"]
        geo_bones = models[geo_id]["bones"]
        for anim_key in d.get("animations", {}).values():
            if anim_key in anim_defs:
                for bname in anim_defs[anim_key].get("bones", {}).keys():
                    assert bname in geo_bones, f"{ident} anim {anim_key} targets missing bone '{bname}' in {geo_id}"
        for tex in d["textures"].values():
            tpath = RP / (tex + ".png")
            assert tpath.is_file(), f"Missing texture {tpath}"
            w, h = png_dimensions(tpath)
            assert w == models[geo_id]["tw"] and h == models[geo_id]["th"], (
                f"{ident} texture {w}x{h} != geo {models[geo_id]['tw']}x{models[geo_id]['th']}"
            )
    assert clients == set(mobs.keys()), f"Entity mismatch: BP-only={set(mobs.keys())-clients}, RP-only={clients-set(mobs.keys())}"

    # Validate spawn rules reference valid entities
    if (BP / "spawn_rules").is_dir():
        for p in (BP / "spawn_rules").glob("*.json"):
            sr = read(p)["minecraft:spawn_rules"]
            sr_id = sr["description"]["identifier"]
            assert sr_id in mobs, f"Spawn rule {p.name} targets unknown entity {sr_id}"

    # Validate textures registries & PNG headers
    for registry in ("item_texture", "terrain_texture"):
        for key, entry in read(RP / f"textures/{registry}.json")["texture_data"].items():
            tpath = RP / (entry["textures"] + ".png")
            assert key.startswith("bearframe_") and tpath.is_file(), f"Missing {registry} asset {tpath}"
            w, h = png_dimensions(tpath)
            assert w > 0 and h > 0

    # Validate en_US localization covers all entities and items
    lang_text = (RP / "texts/en_US.lang").read_text(encoding="utf-8")
    lang_keys = {line.split("=", 1)[0].strip() for line in lang_text.splitlines() if "=" in line}
    for eid in mobs:
        assert f"entity.{eid}.name" in lang_keys, f"Missing localization for {eid}"
    for iid in items:
        assert f"item.{iid}.name" in lang_keys, f"Missing localization for {iid}"

    # Validate pack icons exist and are valid PNGs
    for folder in (BP, RP):
        w, h = png_dimensions(folder / "pack_icon.png")
        assert w > 0 and h > 0

    # Ensure zero third-party licensed assets leaked in
    assert not any(
        "starbound" in p.name.lower() or "infinity" in p.name.lower()
        for root in (BP, RP)
        for p in root.rglob("*")
    )
    print(
        f"Static validation PASSED: {len(mobs)} entities, {len(items)} items, "
        f"{len(models)} geometries, {len(anim_defs)} animations, {len(anim_controllers)} controllers."
    )


def write_folder_into_zip(z: zipfile.ZipFile, directory: Path, prefix: str = ""):
    for path in sorted(directory.rglob("*")):
        if path.is_file():
            rel = path.relative_to(directory).as_posix()
            arcname = f"{prefix}/{rel}" if prefix else rel
            z.write(path, arcname)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path, nargs="?", default=ROOT / "dist")
    parser.add_argument("--world", type=Path)
    args = parser.parse_args()
    OUT = args.output.resolve()
    validate()
    OUT.mkdir(parents=True, exist_ok=True)

    # 1. Official directory-based .mcaddon (Bearframe_Behavior/ + Bearframe_Resources/)
    #    Reliably imports in Android Minecraft Bedrock without nested-zip failures.
    mcaddon_path = OUT / f"Bearframe_Bedrock_{VERSION}.mcaddon"
    with zipfile.ZipFile(mcaddon_path, "w", zipfile.ZIP_DEFLATED) as z:
        write_folder_into_zip(z, BP, "Bearframe_Behavior")
        write_folder_into_zip(z, RP, "Bearframe_Resources")

    # 2. Standalone .mcpack files (manifest.json directly at ZIP root) for direct 1-tap fallback
    bp_mcpack = OUT / f"Bearframe_Behavior_{VERSION}.mcpack"
    rp_mcpack = OUT / f"Bearframe_Resources_{VERSION}.mcpack"
    with zipfile.ZipFile(bp_mcpack, "w", zipfile.ZIP_DEFLATED) as z:
        write_folder_into_zip(z, BP)
    with zipfile.ZipFile(rp_mcpack, "w", zipfile.ZIP_DEFLATED) as z:
        write_folder_into_zip(z, RP)

    # 3. Full source archive + git bundle
    source_zip = OUT / f"Bearframe_Bedrock_Source_{VERSION}.zip"
    with zipfile.ZipFile(source_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for root in (BP, RP, ROOT / "docs", ROOT / "tests", ROOT / "tools"):
            for path in sorted(root.rglob("*")):
                if path.is_file() and "__pycache__" not in path.parts:
                    z.write(path, path.relative_to(ROOT).as_posix())
        for name in ("README.md", "package.json", ".gitignore"):
            z.write(ROOT / name, name)
        if (ROOT / ".git").is_dir():
            with tempfile.TemporaryDirectory() as directory:
                bundle = Path(directory) / "Bearframe_Bedrock.gitbundle"
                subprocess.run(["git", "-C", str(ROOT), "bundle", "create", str(bundle), "--all"], check=True)
                z.write(bundle, bundle.name)

    if args.world:
        with zipfile.ZipFile(OUT / f"Bearframe_Ruins_Expedition_{VERSION}.mcworld", "w", zipfile.ZIP_DEFLATED) as z:
            for name in ("level.dat", "levelname.txt", "world_behavior_packs.json", "world_resource_packs.json"):
                z.write(args.world / name, name)
            for kind, root in (("behavior", BP), ("resource", RP)):
                manifest = read(root / "manifest.json")["header"]
                expected = [{"pack_id": manifest["uuid"], "version": manifest["version"]}]
                assert read(args.world / f"world_{kind}_packs.json") == expected
                for path in sorted(root.rglob("*")):
                    if path.is_file():
                        z.write(path, f"{kind}_packs/bearframe/" + path.relative_to(root).as_posix())
            for path in (args.world / "db").glob("*"):
                if path.is_file() and path.name not in {"LOCK", "LOG", "LOG.old"}:
                    z.write(path, "db/" + path.name)

    # Verify exact Bedrock archive structures & CRC integrity
    with zipfile.ZipFile(mcaddon_path) as z:
        names = set(z.namelist())
        assert "Bearframe_Behavior/manifest.json" in names, "Missing Bearframe_Behavior/manifest.json in .mcaddon"
        assert "Bearframe_Resources/manifest.json" in names, "Missing Bearframe_Resources/manifest.json in .mcaddon"
        assert not any(n.endswith(".mcpack") for n in names), ".mcaddon should use folders, not nested .mcpack zips"
        assert z.testzip() is None
    for pack_file in (bp_mcpack, rp_mcpack):
        with zipfile.ZipFile(pack_file) as z:
            assert "manifest.json" in set(z.namelist()), f"Missing root manifest.json in {pack_file.name}"
            assert z.testzip() is None
    with zipfile.ZipFile(source_zip) as z:
        assert z.testzip() is None

    for p in sorted(OUT.glob("*")):
        if p.is_file() and p.suffix in {".mcaddon", ".mcpack", ".zip", ".mcworld"}:
            print(p, p.stat().st_size)


if __name__ == "__main__":
    main()
