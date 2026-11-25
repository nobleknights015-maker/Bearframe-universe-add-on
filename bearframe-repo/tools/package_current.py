"""Validate and package the checked-in Bearframe Bedrock source."""
import argparse
import json
import subprocess
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
PACKS = {"behavior_pack": "Bearframe_Behavior", "resource_pack": "Bearframe_Resources"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    manifests = {
        folder: json.loads((ROOT / folder / "manifest.json").read_text())
        for folder in PACKS
    }
    behavior = manifests["behavior_pack"]
    resource = manifests["resource_pack"]["header"]
    version = resource["version"]
    if behavior["header"]["version"] != version or not any(
        dependency.get("uuid") == resource["uuid"] and dependency.get("version") == version
        for dependency in behavior["dependencies"]
    ):
        raise ValueError("Behavior and resource pack manifests disagree")

    members = {}
    for folder, prefix in PACKS.items():
        pack = ROOT / folder
        for path in sorted(pack.rglob("*")):
            if not path.is_file():
                continue
            relative = path.relative_to(pack)
            if any(part.startswith(".") for part in relative.parts):
                continue
            data = path.read_bytes()
            if path.suffix == ".json":
                json.loads(data.decode("utf-8-sig"))
            elif path.suffix == ".js":
                subprocess.run(["node", "--input-type=module", "--check"], input=data, check=True)
            members[f"{prefix}/{relative.as_posix()}"] = data

    args.output.mkdir(parents=True, exist_ok=True)
    version_label = ".".join(map(str, version))
    output = args.output / f"Bearframe_Bedrock_{version_label}_Star_Odyssey.mcaddon"
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for member, data in sorted(members.items()):
            archive.writestr(member, data)
    with ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise ValueError(f"Archive integrity check failed: {output}")
    print(f"{output} ({len(members)} pack files)")


if __name__ == "__main__":
    main()
