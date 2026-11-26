"""Extract aggregate motion statistics from an optional local Java reference JAR."""
import json
from statistics import median
from zipfile import ZipFile


def motion_profile(path):
    """Measure keyframe density without transferring any poses or rig data."""
    densities = []
    with ZipFile(path) as archive:
        for name in archive.namelist():
            if not name.startswith("assets/mowziesmobs/animations/") or not name.endswith(".json"):
                continue
            for clip in json.loads(archive.read(name)).get("animations", {}).values():
                duration = clip.get("animation_length", 0)
                if not .55 <= duration <= 8 or clip.get("loop") is True:
                    continue
                times = set()
                for channels in clip.get("bones", {}).values():
                    for track in channels.values():
                        if isinstance(track, dict):
                            for key in track:
                                try:
                                    times.add(float(key))
                                except ValueError:
                                    continue
                if len(times) >= 4:
                    densities.append(len(times) / duration)
    if not densities:
        raise ValueError("No usable Mowzie's Mobs animation tracks in the reference JAR")
    return {"clips": len(densities), "poses_per_second": round(median(densities), 2)}
