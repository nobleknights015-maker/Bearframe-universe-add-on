#!/usr/bin/env python3
"""
Bearframe Universe Bedrock Add-on 0.4.1 — Asset & Content Generator
Generates manifests, blocks, items, recipes, loot tables, spawn rules,
128x128 pixel-art entity atlases (32x32 tile density matching Infinity Sci-Fi),
player-scale articulated humanoid rigs (Bearframes, Nullframes, Hollows, Hunters, Echoes),
distinct nonhumanoid Ghost Grid sci-fi machine rigs, animation controllers,
and entity behavior definitions.

Zero external Python dependencies (pure-Python RGBA PNG encoder via zlib/struct).
"""

from pathlib import Path
from uuid import UUID, uuid5
import json
import math
import random
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
BP = ROOT / "behavior_pack"
RP = ROOT / "resource_pack"
SEED = UUID("d5efd705-1ffa-48c6-8148-6ac108170a38")
VERSION = [0, 4, 1]
MIN_ENGINE = [1, 26, 50]
SERVER_API = "2.10.0"

FACES = ["north", "south", "east", "west", "up", "down"]


def uid(key: str) -> str:
    return str(uuid5(SEED, key))


def write_json(root: Path, rel_path: str, content: dict | list) -> None:
    target = root / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Pure-Python RGBA Canvas & PNG Writer (zero Pillow dependency)
# ---------------------------------------------------------------------------

def hex_to_rgba(color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    h = color.lstrip("#")
    if len(h) == 6:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)
    if len(h) == 8:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16))
    raise ValueError(f"Unsupported color: {color}")


def shade(rgba: tuple[int, int, int, int], delta: int) -> tuple[int, int, int, int]:
    r, g, b, a = rgba
    return (
        max(0, min(255, r + delta)),
        max(0, min(255, g + delta)),
        max(0, min(255, b + delta)),
        a,
    )


def blend(c1: tuple[int, int, int, int], c2: tuple[int, int, int, int], t: float) -> tuple[int, int, int, int]:
    return (
        int(c1[0] * (1 - t) + c2[0] * t),
        int(c1[1] * (1 - t) + c2[1] * t),
        int(c1[2] * (1 - t) + c2[2] * t),
        int(c1[3] * (1 - t) + c2[3] * t),
    )


class Canvas:
    def __init__(self, width: int, height: int, fill=(0, 0, 0, 0)):
        self.w = width
        self.h = height
        if isinstance(fill, str):
            fill = hex_to_rgba(fill)
        self.buf = bytearray(fill * (width * height))

    def set_px(self, x: int, y: int, color) -> None:
        if x < 0 or y < 0 or x >= self.w or y >= self.h:
            return
        rgba = hex_to_rgba(color) if isinstance(color, str) else color
        idx = (y * self.w + x) * 4
        if rgba[3] == 255:
            self.buf[idx : idx + 4] = bytes(rgba)
        elif rgba[3] > 0:
            a = rgba[3] / 255.0
            inv = 1.0 - a
            self.buf[idx] = int(rgba[0] * a + self.buf[idx] * inv)
            self.buf[idx + 1] = int(rgba[1] * a + self.buf[idx + 1] * inv)
            self.buf[idx + 2] = int(rgba[2] * a + self.buf[idx + 2] * inv)
            self.buf[idx + 3] = min(255, int(rgba[3] + self.buf[idx + 3] * inv))

    def get_px(self, x: int, y: int) -> tuple[int, int, int, int]:
        idx = (y * self.w + x) * 4
        return (self.buf[idx], self.buf[idx + 1], self.buf[idx + 2], self.buf[idx + 3])

    def rect(self, x0: int, y0: int, x1: int, y1: int, fill=None, outline=None) -> None:
        if fill is not None:
            rgba = hex_to_rgba(fill) if isinstance(fill, str) else fill
            for y in range(max(0, y0), min(self.h, y1 + 1)):
                for x in range(max(0, x0), min(self.w, x1 + 1)):
                    self.set_px(x, y, rgba)
        if outline is not None:
            rgba = hex_to_rgba(outline) if isinstance(outline, str) else outline
            for x in range(max(0, x0), min(self.w, x1 + 1)):
                self.set_px(x, y0, rgba)
                self.set_px(x, y1, rgba)
            for y in range(max(0, y0), min(self.h, y1 + 1)):
                self.set_px(x0, y, rgba)
                self.set_px(x1, y, rgba)

    def hline(self, x0: int, x1: int, y: int, color, thickness: int = 1) -> None:
        for t in range(thickness):
            for x in range(x0, x1 + 1):
                self.set_px(x, y + t, color)

    def vline(self, x: int, y0: int, y1: int, color, thickness: int = 1) -> None:
        for t in range(thickness):
            for y in range(y0, y1 + 1):
                self.set_px(x + t, y, color)

    def circle(self, cx: int, cy: int, radius: float, fill=None, outline=None) -> None:
        r2 = radius * radius
        inner = (radius - 1.25) * (radius - 1.25)
        x0, x1 = int(cx - radius - 1), int(cx + radius + 1)
        y0, y1 = int(cy - radius - 1), int(cy + radius + 1)
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                d2 = (x - cx) ** 2 + (y - cy) ** 2
                if d2 <= r2:
                    if outline is not None and d2 >= inner:
                        self.set_px(x, y, outline)
                    elif fill is not None:
                        self.set_px(x, y, fill)

    def line(self, x0: int, y0: int, x1: int, y1: int, color, width: int = 1) -> None:
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            x = round(x0 + (x1 - x0) * i / steps)
            y = round(y0 + (y1 - y0) * i / steps)
            for ox in range(width):
                for oy in range(width):
                    self.set_px(x + ox, y + oy, color)

    def save_png(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)

        def chunk(tag: bytes, data: bytes) -> bytes:
            return (
                struct.pack("!I", len(data))
                + tag
                + data
                + struct.pack("!I", zlib.crc32(tag + data) & 0xFFFFFFFF)
            )

        raw = bytearray()
        stride = self.w * 4
        for y in range(self.h):
            raw.append(0)
            row = y * stride
            raw.extend(self.buf[row : row + stride])
        ihdr = struct.pack("!IIBBBBB", self.w, self.h, 8, 6, 0, 0, 0)
        png = (
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b"")
        )
        path.write_bytes(png)


def save_rp_png(rel_path: str, canvas: Canvas) -> None:
    canvas.save_png(RP / (rel_path + ".png"))


# ---------------------------------------------------------------------------
# 128x128 Atlas Tile System (4x4 grid of 32x32 tiles)
# ---------------------------------------------------------------------------
# Tile index -> (u, v) on 128x128 sheet:
#   0: Primary armor plate         1: Dark graphite/joint understructure
#   2: Front head visor faceplate  3: Front chest core / sternum assembly
#   4: Side-head tech display      5: Department / faction accent plate
#   6: Mantle / scarf / fabric     7: Backpack / utility console / screen
#   8: Heavy boot / tread / rim    9: Grounded moss / weld patch / wear
#  10: Emissive lamp / optic core 11: Rear chassis / radiator / exhaust
#  12: Weapon / emitter / blade   13: Hazard / chevron trim

TILE_SIZE = 32


def tile_uv(tile_idx: int) -> tuple[int, int]:
    return ((tile_idx % 4) * TILE_SIZE, (tile_idx // 4) * TILE_SIZE)


def paint_metal_tile(canvas: Canvas, idx: int, base_hex: str, rng: random.Random,
                     rivets: bool = True, border_dark: int = -36, worn: bool = False) -> None:
    ox, oy = tile_uv(idx)
    base = hex_to_rgba(base_hex)
    dark = shade(base, border_dark)
    light = shade(base, 26)
    mid = shade(base, -14)
    canvas.rect(ox, oy, ox + 31, oy + 31, fill=base, outline=dark)
    canvas.hline(ox + 1, ox + 30, oy + 1, light)
    canvas.vline(ox + 1, oy + 1, oy + 30, light)
    canvas.hline(ox + 2, ox + 30, oy + 30, mid)
    canvas.vline(ox + 30, oy + 2, oy + 30, mid)
    # Subtle panel seam
    canvas.hline(ox + 4, ox + 27, oy + 16, mid)
    canvas.hline(ox + 4, ox + 27, oy + 17, light)
    for _ in range(48 if worn else 24):
        px = ox + rng.randrange(2, 30)
        py = oy + rng.randrange(2, 30)
        d = rng.choice([-18, -10, 8]) if worn else rng.choice([-8, -5, 6])
        canvas.set_px(px, py, shade(canvas.get_px(px, py), d))
    if rivets:
        for rx, ry in [(4, 4), (27, 4), (4, 27), (27, 27)]:
            canvas.set_px(ox + rx, oy + ry, dark)
            canvas.set_px(ox + rx + 1, oy + ry + 1, light)


def paint_graphite_tile(canvas: Canvas, idx: int, base_hex: str, rng: random.Random) -> None:
    ox, oy = tile_uv(idx)
    base = hex_to_rgba(base_hex)
    dark = shade(base, -22)
    rib = shade(base, 22)
    canvas.rect(ox, oy, ox + 31, oy + 31, fill=base, outline=dark)
    for y in range(oy + 3, oy + 30, 4):
        canvas.hline(ox + 2, ox + 29, y, rib)
        canvas.hline(ox + 2, ox + 29, y + 1, dark)
    canvas.vline(ox + 15, oy + 2, oy + 29, dark, 2)
    for _ in range(20):
        px, py = ox + rng.randrange(2, 30), oy + rng.randrange(2, 30)
        canvas.set_px(px, py, shade(canvas.get_px(px, py), rng.choice([-6, 6])))


def build_entity_atlas(name: str, style: str, palette: dict) -> Canvas:
    """
    style in:
      'bearframe', 'hollow', 'directorate', 'hunter', 'echo', 'grid'
    palette keys: armor, joint, visor_bg, glow, accent, trim, wear
    """
    canvas = Canvas(128, 128, "#181d22")
    rng = random.Random(f"bf_v4_{name}")
    armor = palette["armor"]
    joint = palette["joint"]
    vbg = palette["visor_bg"]
    glow = palette["glow"]
    accent = palette["accent"]
    trim = palette["trim"]
    wear = palette["wear"]

    glow_rgba = hex_to_rgba(glow)
    glow_bright = shade(glow_rgba, 55)
    glow_dim = shade(glow_rgba, -45)
    armor_rgba = hex_to_rgba(armor)
    joint_rgba = hex_to_rgba(joint)
    vbg_rgba = hex_to_rgba(vbg)
    worn = style in ("echo", "grid")

    # 0: Primary armor plate
    paint_metal_tile(canvas, 0, armor, rng, rivets=True, worn=worn)
    # 1: Dark graphite mechanical joint
    paint_graphite_tile(canvas, 1, joint, rng)

    # 2: Front Visor / Faceplate
    ox, oy = tile_uv(2)
    paint_metal_tile(canvas, 2, armor, rng, rivets=False, worn=worn)
    if style == "bearframe":
        # Sculpted Bearframe dark visor + expressive illuminated eyes + brow trim
        canvas.rect(ox + 3, oy + 6, ox + 28, oy + 24, fill=vbg_rgba, outline=shade(joint_rgba, -12))
        canvas.rect(ox + 4, oy + 7, ox + 27, oy + 23, fill=shade(vbg_rgba, -10))
        # Subtle visor reflection
        canvas.hline(ox + 6, ox + 25, oy + 8, shade(vbg_rgba, 26))
        # Expressive optic eyes (left + right)
        canvas.rect(ox + 7, oy + 12, ox + 12, oy + 17, fill=glow_rgba)
        canvas.rect(ox + 8, oy + 13, ox + 11, oy + 16, fill=glow_bright)
        canvas.rect(ox + 19, oy + 12, ox + 24, oy + 17, fill=glow_rgba)
        canvas.rect(ox + 20, oy + 13, ox + 23, oy + 16, fill=glow_bright)
        # Chin accent line
        canvas.hline(ox + 9, ox + 22, oy + 26, accent, 2)
    elif style == "hollow":
        # Blank black faceplate + narrow vertical crimson drone optic slit
        canvas.rect(ox + 4, oy + 4, ox + 27, oy + 27, fill="#111317", outline=shade(armor_rgba, -30))
        canvas.rect(ox + 14, oy + 8, ox + 17, oy + 22, fill=glow_dim)
        canvas.rect(ox + 15, oy + 9, ox + 16, oy + 21, fill=glow_bright)
        canvas.hline(ox + 6, ox + 25, oy + 25, "#262a32")
    elif style == "directorate":
        # Severe blank authoritarian visor with thin horizontal red sensor slit
        canvas.rect(ox + 3, oy + 5, ox + 28, oy + 25, fill="#0e1015", outline=shade(armor_rgba, -25))
        canvas.hline(ox + 5, ox + 26, oy + 14, glow_dim, 3)
        canvas.hline(ox + 6, ox + 25, oy + 15, glow_bright, 1)
        canvas.hline(ox + 10, ox + 21, oy + 27, glow, 2)
    elif style == "hunter":
        # Predatory Watchtower-descended V-shaped crimson visor
        canvas.rect(ox + 3, oy + 5, ox + 28, oy + 26, fill="#0c0d12", outline="#282c34")
        canvas.line(ox + 5, oy + 11, ox + 15, oy + 17, glow_rgba, 3)
        canvas.line(ox + 26, oy + 11, ox + 16, oy + 17, glow_rgba, 3)
        canvas.line(ox + 6, oy + 12, ox + 15, oy + 17, glow_bright, 1)
        canvas.line(ox + 25, oy + 12, ox + 16, oy + 17, glow_bright, 1)
        canvas.hline(ox + 9, ox + 22, oy + 23, "#3c1a22", 2)
    elif style == "echo":
        # Aged legacy industrial faceplate with asymmetrical damaged/flickering optics
        canvas.rect(ox + 4, oy + 6, ox + 27, oy + 25, fill="#1b1c22", outline=shade(armor_rgba, -40))
        # Left optic intact, right optic fractured/dim
        canvas.rect(ox + 7, oy + 12, ox + 13, oy + 17, fill=glow_rgba)
        canvas.rect(ox + 8, oy + 13, ox + 11, oy + 15, fill=glow_bright)
        canvas.rect(ox + 19, oy + 13, ox + 24, oy + 16, fill=glow_dim)
        canvas.line(ox + 17, oy + 7, ox + 24, oy + 23, "#0d0e12", 1)  # faceplate crack
        canvas.hline(ox + 6, ox + 25, oy + 22, shade(joint_rgba, 15))
    elif style == "grid":
        # Ancient Ghost Grid industrial optical scanner bezel (cyan legacy lens)
        canvas.rect(ox + 2, oy + 2, ox + 29, oy + 29, fill=shade(joint_rgba, -10), outline=shade(armor_rgba, -30))
        canvas.rect(ox + 5, oy + 8, ox + 26, oy + 23, fill="#0c1a20", outline="#2e444a")
        canvas.hline(ox + 7, ox + 24, oy + 14, glow_dim, 4)
        canvas.hline(ox + 8, ox + 23, oy + 15, glow_bright, 2)
        canvas.circle(ox + 16, oy + 16, 4.2, fill=glow_rgba, outline=glow_bright)

    # 3: Chest Core Display (Bearframe immutable core) / Faction Sternum
    ox, oy = tile_uv(3)
    paint_metal_tile(canvas, 3, armor, rng, rivets=False, worn=worn)
    if style == "bearframe":
        # Immutable glowing Bearframe Chest Core Display (metallic frame + glowing geometric matrix)
        canvas.rect(ox + 4, oy + 4, ox + 27, oy + 27, fill=joint_rgba, outline=shade(armor_rgba, -40))
        canvas.rect(ox + 6, oy + 6, ox + 25, oy + 25, fill=shade(vbg_rgba, -14), outline=accent)
        # Inner glowing Bearframe core readout (stylized geometric core emblem)
        canvas.circle(ox + 16, oy + 16, 6.2, fill=glow_dim, outline=glow_rgba)
        canvas.circle(ox + 16, oy + 16, 3.6, fill=glow_bright)
        canvas.hline(ox + 8, ox + 11, oy + 10, glow_rgba, 2)
        canvas.hline(ox + 20, ox + 23, oy + 10, glow_rgba, 2)
        canvas.hline(ox + 8, ox + 23, oy + 22, accent, 1)
    elif style == "echo":
        # Exposed aged chest conduit & patched housing (NOT a Bearframe core display!)
        canvas.rect(ox + 5, oy + 5, ox + 26, oy + 26, fill="#1f2026", outline=wear)
        for y in range(oy + 8, oy + 25, 4):
            canvas.hline(ox + 7, ox + 24, y, wear, 2)
        canvas.rect(ox + 12, oy + 11, ox + 19, oy + 19, fill=glow_dim, outline=glow_rgba)
        canvas.line(ox + 6, oy + 6, ox + 25, oy + 25, "#33343b", 2)
    elif style in ("hollow", "directorate", "hunter"):
        # Angular Directorate / Hollow / Hunter sternum with red core bar
        canvas.rect(ox + 5, oy + 5, ox + 26, oy + 26, fill="#191c22", outline=shade(armor_rgba, -35))
        canvas.line(ox + 7, oy + 7, ox + 16, oy + 24, glow_rgba, 2)
        canvas.line(ox + 24, oy + 7, ox + 16, oy + 24, glow_rgba, 2)
        canvas.rect(ox + 14, oy + 11, ox + 17, oy + 17, fill=glow_bright)
    elif style == "grid":
        # Ancient Grid cyan reactor core aperture
        canvas.rect(ox + 3, oy + 3, ox + 28, oy + 28, fill="#1c2529", outline=wear)
        canvas.circle(ox + 16, oy + 16, 9.5, fill="#0c1b22", outline="#44626a")
        canvas.circle(ox + 16, oy + 16, 6.2, fill=glow_dim, outline=glow_rgba)
        canvas.circle(ox + 16, oy + 16, 3.4, fill=glow_bright)

    # 4: Technological Side-Head Display Module (Bearframe circular display — NOT animal ears!)
    ox, oy = tile_uv(4)
    paint_metal_tile(canvas, 4, joint, rng, rivets=False, worn=worn)
    if style == "bearframe":
        canvas.circle(ox + 16, oy + 16, 12.5, fill=armor_rgba, outline=shade(joint_rgba, -18))
        canvas.circle(ox + 16, oy + 16, 9.2, fill=shade(vbg_rgba, -10), outline=glow_rgba)
        canvas.circle(ox + 16, oy + 16, 5.2, fill=glow_dim, outline=glow_bright)
        canvas.hline(ox + 12, ox + 20, oy + 16, glow_bright, 1)
        canvas.vline(ox + 16, oy + 12, oy + 20, glow_bright, 1)
    elif style in ("hollow", "directorate", "hunter"):
        canvas.rect(ox + 5, oy + 5, ox + 26, oy + 26, fill="#171920", outline=armor)
        canvas.vline(ox + 15, oy + 8, oy + 23, glow_rgba, 2)
        canvas.hline(ox + 8, ox + 23, oy + 15, accent, 2)
    else:
        canvas.circle(ox + 16, oy + 16, 10.5, fill="#1a2428", outline=wear)
        canvas.circle(ox + 16, oy + 16, 6.0, fill=glow_dim, outline=glow_rgba)

    # 5: Department / Faction Accent Armor Plate
    paint_metal_tile(canvas, 5, accent, rng, rivets=True, worn=worn)
    ox, oy = tile_uv(5)
    canvas.hline(ox + 4, ox + 27, oy + 14, glow_rgba, 2)

    # 6: Mantle / Scarf / Cloak / Composite Trim
    ox, oy = tile_uv(6)
    t_rgba = hex_to_rgba(trim)
    canvas.rect(ox, oy, ox + 31, oy + 31, fill=t_rgba, outline=shade(t_rgba, -30))
    for y in range(oy + 2, oy + 30, 3):
        canvas.hline(ox + 2, ox + 29, y, shade(t_rgba, 12 if (y % 2 == 0) else -12))
    canvas.hline(ox + 2, ox + 29, oy + 26, accent, 2)

    # 7: Backpack / Utility Console / Holo-Tablet Screen
    ox, oy = tile_uv(7)
    paint_metal_tile(canvas, 7, joint, rng, rivets=True, worn=worn)
    canvas.rect(ox + 5, oy + 5, ox + 26, oy + 20, fill=shade(vbg_rgba, -10), outline=accent)
    canvas.hline(ox + 8, ox + 22, oy + 9, glow_rgba, 2)
    canvas.hline(ox + 8, ox + 18, oy + 13, glow_bright, 1)
    canvas.hline(ox + 8, ox + 24, oy + 16, accent, 1)
    canvas.rect(ox + 7, oy + 23, ox + 12, oy + 27, fill=glow_rgba)
    canvas.rect(ox + 19, oy + 23, ox + 24, oy + 27, fill=accent)

    # 8: Boots / Heavy Tread / Stabilizer Foot
    ox, oy = tile_uv(8)
    b_col = shade(joint_rgba, -8)
    canvas.rect(ox, oy, ox + 31, oy + 31, fill=b_col, outline=shade(b_col, -18))
    for y in range(oy + 2, oy + 30, 5):
        canvas.rect(ox + 3, y, ox + 28, y + 2, fill=shade(b_col, 24))
    canvas.hline(ox + 2, ox + 29, oy + 28, accent, 2)

    # 9: Grounded Moss / Welded Patch / Aged Patina
    ox, oy = tile_uv(9)
    w_rgba = hex_to_rgba(wear)
    canvas.rect(ox, oy, ox + 31, oy + 31, fill=w_rgba, outline=shade(w_rgba, -28))
    for _ in range(95):
        px, py = ox + rng.randrange(1, 31), oy + rng.randrange(1, 31)
        canvas.set_px(px, py, shade(w_rgba, rng.choice([-24, -12, 12, 24])))
    if style == "echo":
        # Welded scrap rivets
        canvas.line(ox + 3, oy + 15, ox + 28, oy + 16, "#2c2e33", 2)
        for rx in range(5, 28, 5):
            canvas.set_px(ox + rx, oy + 13, "#b8b4aa")
            canvas.set_px(ox + rx, oy + 18, "#b8b4aa")

    # 10: Pure Emissive Glow / Beacon Core
    ox, oy = tile_uv(10)
    canvas.rect(ox, oy, ox + 31, oy + 31, fill=glow_dim, outline=shade(glow_dim, -25))
    canvas.rect(ox + 4, oy + 4, ox + 27, oy + 27, fill=glow_rgba)
    canvas.rect(ox + 8, oy + 8, ox + 23, oy + 23, fill=glow_bright)

    # 11: Rear Chassis / Heat Vents / Exhaust
    ox, oy = tile_uv(11)
    paint_metal_tile(canvas, 11, armor, rng, rivets=True, worn=worn)
    for y in range(oy + 6, oy + 26, 4):
        canvas.rect(ox + 6, y, ox + 25, y + 1, fill="#14181e")
    canvas.rect(ox + 13, oy + 26, ox + 18, oy + 28, fill=glow_rgba)

    # 12: Weapon / Emitter / Tool Metal
    ox, oy = tile_uv(12)
    paint_metal_tile(canvas, 12, "#2f353d", rng, rivets=False, worn=worn)
    canvas.rect(ox + 4, oy + 12, ox + 27, oy + 19, fill="#191d23", outline=accent)
    canvas.hline(ox + 6, ox + 25, oy + 15, glow_bright, 2)

    # 13: Industrial Hazard / Caution Chevron Trim
    ox, oy = tile_uv(13)
    canvas.rect(ox, oy, ox + 31, oy + 31, fill="#24272c")
    for y in range(32):
        for x in range(32):
            if ((x + y) // 6) % 2 == 0:
                canvas.set_px(ox + x, oy + y, accent)
    canvas.rect(ox, oy, ox + 31, oy + 31, outline="#16181c")

    return canvas


# ---------------------------------------------------------------------------
# Geometry Helpers (Bedrock 1.12.0 per-face UV on 128x128 atlas)
# ---------------------------------------------------------------------------

def box(origin: list[float], size: list[float], tile: int,
        north: int | None = None, south: int | None = None,
        up: int | None = None, down: int | None = None,
        east: int | None = None, west: int | None = None,
        rotation: list[float] | None = None, pivot: list[float] | None = None) -> dict:
    face_map = {
        "north": tile if north is None else north,
        "south": tile if south is None else south,
        "east": tile if east is None else east,
        "west": tile if west is None else west,
        "up": tile if up is None else up,
        "down": tile if down is None else down,
    }
    uv = {}
    for face in FACES:
        u, v = tile_uv(face_map[face])
        uv[face] = {"uv": [u, v], "uv_size": [TILE_SIZE, TILE_SIZE]}
    out = {"origin": [round(n, 3) for n in origin], "size": [round(n, 3) for n in size], "uv": uv}
    if rotation is not None:
        out["rotation"] = rotation
    if pivot is not None:
        out["pivot"] = pivot
    return out


def bone(name: str, pivot: list[float], cubes: list[dict], parent: str | None = None,
         rotation: list[float] | None = None) -> dict:
    b = {"name": name, "pivot": [round(n, 3) for n in pivot], "cubes": cubes}
    if parent:
        b["parent"] = parent
    if rotation is not None:
        b["rotation"] = rotation
    return b


# ---------------------------------------------------------------------------
# RIG FAMILY 1: Player-Scale Articulated Humanoid Base Frames
# (Minecraft player height = 30-32px = 1.875-2.0 blocks, feet cleanly at Y=0)
# ---------------------------------------------------------------------------

def finish_farfield_atlas(canvas: Canvas) -> None:
    """Use a slim optical band, clean ceramic surfaces and restrained survey markings."""
    def paint(tile, base, details):
        ox, oy = tile_uv(tile)
        canvas.rect(ox, oy, ox + 31, oy + 31, fill=base)
        for x1, y1, x2, y2, color in details:
            canvas.rect(ox + x1, oy + y1, ox + x2, oy + y2, fill=color)

    paint(0, "#cad6dc", [
        (0, 0, 31, 3, "#e8f0f1"), (0, 4, 2, 29, "#d8e4e8"),
        (29, 4, 31, 31, "#a0b3bf"), (0, 29, 31, 31, "#a4b6c1"),
        (4, 27, 9, 27, "#8297a2"), (25, 6, 26, 7, "#a0b3bf"),
    ])
    paint(2, "#0c1b25", [
        (0, 0, 31, 2, "#314e58"), (0, 28, 31, 31, "#162c38"),
        (3, 8, 28, 9, "#294451"),
        (4, 13, 12, 20, "#287a76"), (19, 13, 27, 20, "#287a76"),
        (5, 14, 11, 18, "#8af6df"), (20, 14, 26, 18, "#8af6df"),
        (6, 14, 11, 15, "#c4fff0"), (20, 14, 25, 15, "#c4fff0"),
        (3, 22, 9, 23, "#22494e"), (22, 22, 28, 23, "#22494e"),
    ])
    paint(5, "#3d6f73", [
        (0, 0, 31, 4, "#638d90"), (0, 27, 31, 31, "#2f5259"),
        (5, 7, 24, 11, "#96beb7"), (5, 12, 19, 13, "#729e98"),
        (24, 23, 27, 25, "#adc9bd"),
    ])
    paint(6, "#a5b7bf", [
        (0, 0, 31, 3, "#d0dde0"), (28, 5, 31, 31, "#788b98"),
        (4, 21, 27, 25, "#235865"), (7, 22, 16, 24, "#8dd1c6"),
    ])
    paint(14, "#b7c8ce", [
        (0, 0, 31, 4, "#e9f1f0"), (0, 25, 31, 31, "#64888b"),
        (11, 11, 20, 20, "#24636d"), (9, 10, 12, 13, "#24636d"),
        (19, 10, 22, 13, "#24636d"), (13, 17, 18, 20, "#8fcccc"),
        (13, 14, 13, 15, "#e5f1ef"), (18, 14, 18, 15, "#e5f1ef"),
    ])
    paint(13, "#596d78", [
        (0, 0, 31, 2, "#8d9ca2"), (3, 5, 28, 24, "#ccd7da"),
        (6, 7, 25, 10, "#acbbc3"), (7, 19, 24, 23, "#899fa9"),
        (5, 25, 26, 29, "#3e5761"), (11, 26, 20, 27, "#66b2a9"),
    ])


def build_farfield_rig() -> list[dict]:
    """A standard player-scale chassis wearing independent survey hardware."""
    core = [
        box([-3.35, 12, -1.85], [6.7, 10.6, 3.7], 1),
        box([-3.7, 15.3, -2.13], [7.4, 5.8, 4.25], 0, south=11),
        box([-3.95, 20.7, -1.97], [7.9, 1.65, 3.9], 0),
        box([-2.76, 14.1, -1.99], [5.52, 1.7, 3.98], 13),
        box([-3.64, 12.15, -2.05], [7.28, 1.35, 4.1], 13),
        box([-1.89, 16.85, -2.35], [3.78, 3.5, 0.36], 1, north=3),
        box([-1.36, 22.1, -1.31], [2.72, 2.1, 2.62], 1),
        box([-2.58, 15.05, 2.1], [5.16, 6.2, 1.35], 13, south=7),
        box([-1.89, 16.0, 3.32], [3.78, 4.7, 0.48], 5, south=7),
        box([1.55, 20.6, 2.7], [0.54, 2.6, 0.57], 1, up=10),
        box([-3.45, 11.6, 0.35], [1.15, 2.85, 2.03], 1, south=7),
    ]
    helmet = [
        box([-2.76, 23.7, -2.06], [5.52, 3.3, 4.9], 1),
        box([-3.14, 25.55, -2.88], [6.28, 3.48, 5.92], 0, south=11),
        box([-2.78, 28.96, -2.4], [5.56, 1.38, 5.13], 0),
        box([-2.34, 24.02, -2.99], [4.68, 1.31, 4.84], 13),
        box([-2.86, 25.74, -3.08], [5.72, 2.32, 0.3], 1, north=2),
        box([-3.17, 27.96, -3.16], [6.34, 0.82, 1.25], 0),
        box([-3.11, 25.15, -2.91], [1.13, 1.66, 2.23], 0, north=6),
        box([1.98, 25.15, -2.91], [1.13, 1.66, 2.23], 0, north=6),
        box([-3.56, 25.52, -1.32], [0.56, 2.8, 2.64], 1, west=4),
        box([3.0, 25.52, -1.32], [0.56, 2.8, 2.64], 1, east=4),
    ]
    output = [
        bone("root", [0, 0, 0], []),
        bone("body", [0, 12.1, 0], core, parent="root"),
        bone("head", [0, 23.45, 0], helmet, parent="body"),
    ]
    for i, side in enumerate((-1, 1)):
        x = side * 5.39
        arms = [
            box([x - 1.14, 14.1, -1.09], [2.28, 7.75, 2.18], 1),
            box([x - 1.48, 19.3, -1.38], [2.96, 2.96, 2.76], 0, north=14 if i == 0 else 6),
            box([x - 1.24, 15.85, -1.35], [2.48, 2.6, 2.46], 0, north=6 if i == 0 else 13),
            box([x - 0.91, 12.08, -1.0], [1.82, 2.22, 1.95], 1),
            box([x - 0.94, 12.74, -1.07], [1.88, 1.15, 0.33], 13),
        ]
        if i == 0:
            arms.append(box([x - 0.75, 16.15, -1.56], [1.5, 1.89, 0.41], 1, north=7))
        output.append(bone(f"arm{i}", [x, 21.25, 0], arms, parent="body"))

        x = side * 2.0
        legs = [
            box([x - 1.26, 3.75, -1.21], [2.52, 8.32, 2.42], 1),
            box([x - 1.4, 7.55, -1.36], [2.8, 3.76, 2.72], 0, north=13),
            box([x - 0.94, 5.81, -1.43], [1.88, 1.5, 0.64], 13),
            box([x - 1.29, 1.66, -1.37], [2.58, 4.04, 2.74], 0, north=6),
            box([x - 1.4, 0, -1.95], [2.8, 1.62, 3.52], 1, north=13),
            box([x - 1.31, 1.37, -1.87], [2.62, 0.53, 3.25], 13),
        ]
        output.append(bone(f"leg{i}", [x, 12.05, 0], legs, parent="root"))
    return output


def build_humanoid_rig(variant: str) -> list[dict]:
    """
    Distinct silhouette & proportion presets:
      - bearframe_farfield   (agile 30px, scarf, field pack, scanner, chest+side-head displays)
      - bearframe_steward    (sleek 29px, graceful shoulder trim, holo-tablet, chest+side-head displays)
      - bearframe_engineer   (tall lean 31px, long coat panels, comms fin, chest+side-head displays)
      - bearframe_watch      (tactical 31px, Watchtower antenna fins, dark mantle, chest+side-head displays)
      - bearframe_rigger     (HEAVY/BROAD 33px, wide pauldrons, lift harness, oversized hands, chest+side-head displays)
      - bearframe_vanguard   (armored combat 32px, shield pauldrons, forearm emitter, chest+side-head displays)
      - bearframe_artisan    (agile 29px, angular head fins, holo-palette, sleek mantle, chest+side-head displays)
      - hollow_scout         (lean angular 29px, blank faceplate, recon pack, NO bearframe displays)
      - hollow_breacher      (heavy assault 32px, wide chest + ram gauntlets + power pack)
      - directorate_officer  (tall severe 32px, sharp shoulder crest, officer cape, command rig)
      - nullframe_hunter     (predatory 31px, swept Watchtower-lineage fins, split mantle, Terminus Blade)
      - echo_ward            (weathered 29px, asymmetrical patched left arm, exposed chest conduit)
      - echo_drifter         (compact 27px, salvaged cloak, mismatched leg brace, weathered)
      - echo_sentinel        (tall imposing 33px, welded heavy pauldron, dorsal brace, antique security)
    """
    # Proportions by build class
    if variant == "bearframe_rigger":
        leg_h, body_h, body_w, body_d, head_s, arm_w = 12.0, 13.0, 10.0, 5.2, 7.2, 3.6
    elif variant == "bearframe_vanguard":
        leg_h, body_h, body_w, body_d, head_s, arm_w = 12.0, 12.5, 9.2, 4.8, 7.0, 3.3
    elif variant == "hollow_breacher":
        leg_h, body_h, body_w, body_d, head_s, arm_w = 12.0, 12.5, 10.0, 5.4, 7.0, 3.6
    elif variant == "echo_sentinel":
        leg_h, body_h, body_w, body_d, head_s, arm_w = 13.0, 12.8, 9.6, 5.0, 7.2, 3.4
    elif variant == "echo_drifter":
        leg_h, body_h, body_w, body_d, head_s, arm_w = 10.5, 10.2, 7.4, 4.0, 6.4, 2.8
    elif variant in ("bearframe_steward", "bearframe_artisan", "hollow_scout", "echo_ward"):
        leg_h, body_h, body_w, body_d, head_s, arm_w = 11.5, 11.0, 7.4, 4.0, 6.6, 2.8
    elif variant in ("directorate_officer", "bearframe_engineer", "bearframe_watch", "nullframe_hunter"):
        leg_h, body_h, body_w, body_d, head_s, arm_w = 12.5, 12.0, 8.2, 4.4, 6.8, 3.0
    else:  # bearframe_farfield (standard player-scale 30px)
        leg_h, body_h, body_w, body_d, head_s, arm_w = 12.0, 11.5, 8.0, 4.2, 6.8, 3.0

    is_bearframe = variant.startswith("bearframe_")
    is_echo = variant.startswith("echo_")
    hip_y = leg_h
    shoulder_y = leg_h + body_h - 1.5
    neck_y = leg_h + body_h
    arm_x = body_w / 2.0 + arm_w / 2.0 + 0.35
    leg_x = body_w * 0.27

    # --- Torso cubes ---
    torso_cubes = [
        # Upper chest armor with front core/sternum tile
        box([-body_w / 2, hip_y + 3.0, -body_d / 2], [body_w, body_h - 3.0, body_d], 0, north=3, south=11),
        # Waist / abdomen mechanical graphite articulation
        box([-body_w * 0.42, hip_y, -body_d * 0.44], [body_w * 0.84, 3.4, body_d * 0.88], 1),
        # Utility belt / pelvic frame
        box([-body_w * 0.48, hip_y - 0.3, -body_d * 0.52], [body_w * 0.96, 2.0, body_d * 1.04], 5, north=5, south=1),
    ]

    if is_bearframe:
        # Modeled immutable glowing Bearframe Chest Core Display inset proud on sternum
        torso_cubes.append(
            box([-2.2, hip_y + body_h - 6.2, -body_d / 2 - 0.55], [4.4, 4.2, 0.7], 1, north=3)
        )

    # Variant-specific torso equipment & silhouettes
    if variant == "bearframe_farfield":
        # Expedition scarf collar + rugged Farfield survey pack + radio mast
        torso_cubes.extend([
            box([-body_w * 0.54, neck_y - 1.6, -body_d * 0.62], [body_w * 1.08, 1.8, body_d * 1.24], 6),
            box([-3.2, hip_y + 3.0, body_d / 2], [6.4, 7.6, 2.8], 7, south=7, up=5),
            box([2.2, hip_y + 9.5, body_d / 2 + 1.4], [0.7, 5.2, 0.7], 1, up=10),
            box([-body_w * 0.52, hip_y + 0.2, -1.2], [1.2, 2.6, 2.4], 7),  # hip field scanner
        ])
    elif variant == "bearframe_steward":
        # Graceful ivory/rose collar + soft side ribbon drape
        torso_cubes.extend([
            box([-body_w * 0.5, neck_y - 1.4, -body_d * 0.55], [body_w, 1.4, body_d * 1.1], 6),
            box([-body_w * 0.48, hip_y - 3.5, body_d / 2 - 0.2], [body_w * 0.96, 7.5, 1.0], 6),
        ])
    elif variant == "bearframe_engineer":
        # Sleek long analytical coat panels + back diagnostic bus
        torso_cubes.extend([
            box([-body_w * 0.48, hip_y - 5.2, body_d / 2 - 0.1], [body_w * 0.96, 9.2, 1.0], 6),
            box([-2.4, hip_y + 4.2, body_d / 2], [4.8, 6.0, 1.6], 7, south=11),
        ])
    elif variant == "bearframe_watch":
        # Watchtower dark tactical mantle + dorsal sensor housing
        torso_cubes.extend([
            box([-body_w * 0.56, hip_y - 4.8, body_d / 2 + 0.1], [body_w * 1.12, 14.5, 1.1], 6),
            box([-2.8, hip_y + 6.5, body_d / 2], [5.6, 4.6, 2.0], 1, south=7),
        ])
    elif variant == "bearframe_rigger":
        # Heavy industrial dorsal lift-frame gantry + work scarf + twin hydraulic struts
        torso_cubes.extend([
            box([-4.2, hip_y + 3.5, body_d / 2], [8.4, 8.8, 3.2], 1, south=13, up=5),
            box([-5.2, neck_y - 2.0, body_d / 2 - 0.5], [1.8, 5.2, 2.2], 5, north=13),
            box([3.4, neck_y - 2.0, body_d / 2 - 0.5], [1.8, 5.2, 2.2], 5, north=13),
            box([-4.8, neck_y - 1.8, -body_d * 0.58], [9.6, 1.8, body_d * 1.16], 6),
        ])
    elif variant == "bearframe_vanguard":
        # Heavy chest collar + armored dorsal power pack
        torso_cubes.extend([
            box([-4.6, neck_y - 2.4, -body_d * 0.56], [9.2, 2.4, body_d * 1.12], 5),
            box([-3.4, hip_y + 4.0, body_d / 2], [6.8, 7.6, 2.4], 0, south=11),
        ])
    elif variant == "bearframe_artisan":
        # Asymmetric violet creative sash + sleek studio cloak fin
        torso_cubes.extend([
            box([-body_w * 0.45, hip_y - 4.2, body_d / 2], [body_w * 0.9, 8.2, 0.9], 6),
            box([-2.0, hip_y + 5.0, body_d / 2], [4.0, 5.2, 1.4], 5, south=7),
        ])
    elif variant == "hollow_scout":
        # Compact standardized Directorate recon pack + sensor stub
        torso_cubes.extend([
            box([-2.6, hip_y + 3.5, body_d / 2], [5.2, 6.4, 2.0], 1, south=11),
            box([1.6, hip_y + 9.0, body_d / 2 + 0.8], [0.8, 3.6, 0.8], 1, up=10),
        ])
    elif variant == "hollow_breacher":
        # Heavy sloped front breastplate + dorsal power cell
        torso_cubes.extend([
            box([-4.4, hip_y + 4.2, -body_d / 2 - 1.0], [8.8, 6.8, 1.2], 0, north=3),
            box([-3.6, hip_y + 3.5, body_d / 2], [7.2, 8.2, 3.2], 1, south=13, up=10),
        ])
    elif variant == "directorate_officer":
        # Authoritarian sharp collar + structured Directorate command cape
        torso_cubes.extend([
            box([-4.6, neck_y - 2.0, -body_d * 0.52], [9.2, 2.2, body_d * 1.06], 5),
            box([-4.4, hip_y - 6.0, body_d / 2 + 0.1], [8.8, 16.5, 1.0], 6, south=6),
        ])
    elif variant == "nullframe_hunter":
        # Split predatory pursuit mantle + Watchtower-heritage dorsal tracker pack
        torso_cubes.extend([
            box([-4.6, hip_y - 5.5, body_d / 2 + 0.1], [4.2, 15.5, 0.9], 6),
            box([0.4, hip_y - 5.5, body_d / 2 + 0.1], [4.2, 15.5, 0.9], 6),
            box([-2.4, hip_y + 5.2, body_d / 2], [4.8, 5.6, 2.0], 1, south=12),
        ])
    elif variant == "echo_ward":
        # Aged asymmetrical torso patch + exposed conduit side ribs (NO Bearframe core!)
        torso_cubes.extend([
            box([-body_w / 2 - 0.5, hip_y + 3.8, -1.6], [1.0, 6.2, 3.2], 9),
            box([body_w / 2 - 0.6, hip_y + 2.5, -2.2], [1.1, 7.0, 4.4], 1),
        ])
    elif variant == "echo_drifter":
        # Salvaged shoulder poncho wrap + weathered field satchel
        torso_cubes.extend([
            box([-body_w * 0.56, neck_y - 3.0, -body_d * 0.58], [body_w * 1.12, 3.2, body_d * 1.16], 6),
            box([-2.8, hip_y + 2.8, body_d / 2], [5.6, 6.2, 2.4], 9),
        ])
    elif variant == "echo_sentinel":
        # Heavy archaic dorsal power spine + welded asymmetrical chest plate
        torso_cubes.extend([
            box([-3.0, hip_y + 3.0, body_d / 2], [6.0, 9.5, 3.0], 1, south=9, up=10),
            box([-4.8, hip_y + 5.0, -body_d / 2 - 0.8], [4.4, 6.5, 1.0], 9),
        ])

    # --- Head cubes ---
    head_cubes = [
        box([-head_s / 2, neck_y, -head_s / 2], [head_s, head_s, head_s], 0, north=2, south=11),
    ]
    if is_bearframe:
        # MANDATORY Dual Circular Technological Side-Head Display Modules (NOT animal ears!)
        mod_w = 1.15
        mod_h = 3.2
        head_cubes.extend([
            box([-head_s / 2 - mod_w, neck_y + head_s * 0.26, -mod_h / 2], [mod_w, mod_h, mod_h], 1, west=4, east=1, north=4),
            box([head_s / 2, neck_y + head_s * 0.26, -mod_h / 2], [mod_w, mod_h, mod_h], 1, east=4, west=1, north=4),
        ])
        if variant == "bearframe_watch":
            # Elevated Watchtower tactical antenna fins
            head_cubes.extend([
                box([-head_s / 2 - 0.6, neck_y + head_s - 0.6, -0.4], [0.8, 3.6, 1.8], 5, rotation=[-14, 0, -8], pivot=[-head_s / 2, neck_y + head_s, 0]),
                box([head_s / 2 - 0.2, neck_y + head_s - 0.6, -0.4], [0.8, 3.6, 1.8], 5, rotation=[-14, 0, 8], pivot=[head_s / 2, neck_y + head_s, 0]),
            ])
        elif variant == "bearframe_engineer":
            # Sleek asymmetric comms fin
            head_cubes.append(
                box([head_s / 2 - 0.1, neck_y + head_s * 0.6, 0.2], [0.7, 3.4, 1.4], 5, rotation=[-18, 0, 0], pivot=[head_s / 2, neck_y + head_s, 0])
            )
        elif variant == "bearframe_artisan":
            # Sleek swept angular violet head fins
            head_cubes.extend([
                box([-head_s / 2 - 0.3, neck_y + head_s - 1.2, 0.4], [0.7, 3.0, 2.2], 5, rotation=[-24, 0, -10], pivot=[-head_s / 2, neck_y + head_s, 0]),
                box([head_s / 2 - 0.4, neck_y + head_s - 1.2, 0.4], [0.7, 3.0, 2.2], 5, rotation=[-24, 0, 10], pivot=[head_s / 2, neck_y + head_s, 0]),
            ])
    elif variant == "directorate_officer":
        # Angular severe helmet crest (authoritarian Directorate crown-ridge)
        head_cubes.append(box([-1.1, neck_y + head_s - 0.4, -head_s * 0.55], [2.2, 1.8, head_s * 1.15], 5))
    elif variant == "nullframe_hunter":
        # Aggressive swept-back Watchtower-defector tactical fins + visor brow
        head_cubes.extend([
            box([-head_s / 2 - 0.7, neck_y + head_s - 0.8, -0.2], [0.9, 4.4, 2.2], 5, rotation=[-26, 0, -10], pivot=[-head_s / 2, neck_y + head_s, 0]),
            box([head_s / 2 - 0.2, neck_y + head_s - 0.8, -0.2], [0.9, 4.4, 2.2], 5, rotation=[-26, 0, 10], pivot=[head_s / 2, neck_y + head_s, 0]),
            box([-head_s / 2 - 0.2, neck_y + head_s - 1.5, -head_s / 2 - 0.6], [head_s + 0.4, 1.4, 1.2], 1),
        ])
    elif variant == "hollow_breacher":
        # Heavy armored brow visor guard
        head_cubes.append(box([-head_s / 2 - 0.4, neck_y + head_s - 2.0, -head_s / 2 - 0.6], [head_s + 0.8, 2.2, head_s + 1.0], 0))
    elif variant == "echo_sentinel":
        # Archaic hooded sensor cowling + broken stub antenna
        head_cubes.extend([
            box([-head_s / 2 - 0.5, neck_y + head_s - 1.4, -head_s / 2 - 0.5], [head_s + 1.0, 1.8, head_s + 1.0], 9),
            box([-head_s / 2 - 0.2, neck_y + head_s, 0.5], [0.8, 2.6, 0.8], 1),
        ])
    elif is_echo:
        # Obsolete asymmetrical side comm jack (clearly ancient industrial, NOT Bearframe side-head displays!)
        head_cubes.append(box([head_s / 2, neck_y + 1.4, -0.9], [1.0, 2.4, 1.8], 9))

    # --- Arms (Left = arm0 at -X, Right = arm1 at +X) ---
    arm_len = body_h - 0.6
    arm_top = shoulder_y + 1.0
    arm_bones = []
    for idx, side in enumerate((-1, 1)):
        ax = side * arm_x
        is_patched_arm = (variant == "echo_ward" and idx == 0)
        upper_tile = 9 if is_patched_arm else 0
        fore_tile = 1 if is_patched_arm else 0
        acubes = [
            # Shoulder pauldron
            box([ax - arm_w * 0.58, arm_top - 3.4, -arm_w * 0.58], [arm_w * 1.16, 3.6, arm_w * 1.16], 5 if variant in ("bearframe_vanguard", "directorate_officer", "bearframe_watch") else upper_tile),
            # Elbow graphite joint
            box([ax - arm_w * 0.42, arm_top - arm_len * 0.62, -arm_w * 0.42], [arm_w * 0.84, arm_len * 0.34, arm_w * 0.84], 1),
            # Forearm & articulated hand
            box([ax - arm_w * 0.5, arm_top - arm_len, -arm_w * 0.5], [arm_w, arm_len * 0.42, arm_w], fore_tile, north=5 if is_bearframe else fore_tile),
        ]
        # Variant-specific arm equipment
        if variant == "bearframe_rigger":
            # Heavy reinforced gauntlets
            acubes.append(box([ax - arm_w * 0.62, arm_top - arm_len - 0.6, -arm_w * 0.62], [arm_w * 1.24, 3.6, arm_w * 1.24], 8))
        elif variant == "bearframe_vanguard" and idx == 0:
            # Forearm kinetic defense shield emitter
            acubes.append(box([ax - arm_w * 0.72, arm_top - arm_len + 0.4, -2.4], [1.1, 6.2, 4.8], 5, west=12, north=10))
        elif variant == "bearframe_steward" and idx == 1:
            # Community holo-tablet carried on right forearm
            acubes.append(box([ax + arm_w * 0.35, arm_top - arm_len + 0.5, -2.0], [0.8, 4.0, 3.2], 7, east=7))
        elif variant == "bearframe_artisan" and idx == 1:
            # Holo-stylus / visual palette module
            acubes.append(box([ax + arm_w * 0.35, arm_top - arm_len + 0.6, -2.2], [0.7, 3.8, 3.6], 7, east=10))
        elif variant == "hollow_breacher":
            # Heavy piston breach gauntlets
            acubes.append(box([ax - arm_w * 0.65, arm_top - arm_len - 0.8, -arm_w * 0.68], [arm_w * 1.3, 4.4, arm_w * 1.36], 12, north=13))
        elif variant == "nullframe_hunter" and idx == 1:
            # Integrated Terminus Energy Blade on right forearm!
            acubes.append(box([ax + arm_w * 0.45, arm_top - arm_len - 5.2, -0.7], [0.7, 8.8, 1.4], 10, north=12))
        elif variant == "echo_sentinel" and idx == 0:
            # Welded oversized salvage pauldron
            acubes.append(box([ax - arm_w * 0.75, arm_top - 4.0, -arm_w * 0.72], [arm_w * 1.5, 4.4, arm_w * 1.44], 9))

        arm_bones.append(bone(f"arm{idx}", [ax, shoulder_y, 0], acubes, parent="body"))

    # --- Legs (Left = leg0 at -X, Right = leg1 at +X, grounded strictly at Y=0) ---
    leg_w = arm_w * 1.12
    leg_bones = []
    for idx, side in enumerate((-1, 1)):
        lx = side * leg_x
        is_mismatched_leg = (variant == "echo_drifter" and idx == 1)
        thigh_tile = 9 if is_mismatched_leg else 1
        shin_tile = 9 if is_mismatched_leg else 0
        lcubes = [
            # Thigh mechanical armor
            box([lx - leg_w * 0.48, leg_h * 0.46, -leg_w * 0.48], [leg_w * 0.96, leg_h * 0.56, leg_w * 0.96], thigh_tile),
            # Shin armor plate
            box([lx - leg_w * 0.52, 1.8, -leg_w * 0.52], [leg_w * 1.04, leg_h * 0.46, leg_w * 1.04], shin_tile),
            # Grounded armored boot (Y = 0.0 -> 2.2)
            box([lx - leg_w * 0.56, 0.0, -leg_w * 0.72], [leg_w * 1.12, 2.2, leg_w * 1.36], 8),
        ]
        leg_bones.append(bone(f"leg{idx}", [lx, hip_y, 0], lcubes, parent="root"))

    return [
        bone("root", [0, 0, 0], []),
        bone("body", [0, hip_y, 0], torso_cubes, parent="root"),
        bone("head", [0, neck_y, 0], head_cubes, parent="body"),
        *arm_bones,
        *leg_bones,
    ]


# ---------------------------------------------------------------------------
# RIG FAMILY 2: Ghost Grid NONHUMANOID Sci-Fi Machinery
# (Zero humanoid player rigs! True articulated sci-fi robots & walkers!)
# ---------------------------------------------------------------------------

def build_grid_hexapod_walker() -> list[dict]:
    """Articulated 6-legged hexapod maintenance walker with rotating sensor dome & dual weld arms."""
    chassis = [
        # Main hexagonal/stepped armored body suspended at Y=5.5..10.5
        box([-5.0, 5.5, -6.5], [10.0, 4.6, 13.0], 0, north=2, south=11),
        box([-3.8, 10.1, -5.0], [7.6, 2.2, 9.8], 5, up=9),  # top deck with grounded moss/patina
        box([-5.6, 6.2, -4.0], [11.2, 2.4, 8.0], 1),       # leg-mount side rail
        # Grounded physical moss patch sitting flush on top rear carapace (NOT floating!)
        box([-3.2, 12.3, 0.5], [4.2, 1.1, 3.8], 9),
        box([0.8, 12.3, -2.5], [2.6, 0.9, 3.0], 9),
        # Rear capacitor cylinders
        box([-3.4, 7.2, 6.2], [2.4, 3.8, 2.4], 12, up=10),
        box([1.0, 7.2, 6.2], [2.4, 3.8, 2.4], 12, up=10),
    ]
    sensor_head = [
        box([-2.6, 12.3, -5.6], [5.2, 3.4, 4.6], 0, north=2, east=4, west=4),
        box([-0.6, 15.7, -3.4], [1.2, 2.4, 1.2], 1, up=10),
    ]
    # Dual articulated front repair/welding manipulator arms
    manip0 = [
        box([-4.4, 5.0, -9.8], [1.6, 1.6, 4.2], 1),
        box([-4.8, 4.4, -12.6], [2.2, 2.2, 3.2], 12, north=10),
    ]
    manip1 = [
        box([2.8, 5.0, -9.8], [1.6, 1.6, 4.2], 1),
        box([2.6, 4.4, -12.6], [2.2, 2.2, 3.2], 12, north=10),
    ]
    # 6 Articulated Spider/Hexapod Legs (3 left, 3 right — grounded at Y=0.0!)
    legs = []
    leg_coords = [
        (-5.6, -4.2, -1), (5.6, -4.2, 1),
        (-5.8,  0.0, -1), (5.8,  0.0, 1),
        (-5.6,  4.2, -1), (5.6,  4.2, 1),
    ]
    for i, (x, z, side) in enumerate(leg_coords):
        out_x = x + side * 3.6
        femur_x0 = x if side > 0 else x - 3.8
        tibia_x0 = out_x - 1.1
        legs.append(
            bone(
                f"leg{i}",
                [x, 7.0, z],
                [
                    # Upper angled femur strut
                    box([femur_x0, 6.2, z - 1.0], [3.8, 2.2, 2.0], 1),
                    # Knee knuckle
                    box([out_x - 1.3, 5.2, z - 1.2], [2.6, 2.6, 2.4], 5),
                    # Lower vertical hydraulic tibia down to foot
                    box([tibia_x0, 1.4, z - 1.0], [2.2, 4.4, 2.0], 0),
                    # Grounded claw foot pad at Y=0.0
                    box([out_x - 1.6, 0.0, z - 1.5], [3.2, 1.5, 3.0], 8),
                ],
                parent="body",
            )
        )
    return [
        bone("root", [0, 0, 0], []),
        bone("body", [0, 7.5, 0], chassis, parent="root"),
        bone("head", [0, 12.3, -3.5], sensor_head, parent="body"),
        bone("arm0", [-3.6, 6.0, -6.4], manip0, parent="body"),
        bone("arm1", [3.6, 6.0, -6.4], manip1, parent="body"),
        *legs,
    ]


def build_grid_watcher_drone() -> list[dict]:
    """Hovering reconnaissance & survey drone with central optical lens and 3 thruster fins."""
    core = [
        # Octagonal-style hovering core (suspended at Y=10..18)
        box([-4.2, 10.5, -4.2], [8.4, 7.4, 8.4], 0, north=2, south=11, up=5, down=1),
        box([-5.0, 11.8, -2.8], [10.0, 4.6, 5.6], 1, east=4, west=4),
        # Protruding cyan optical lens bezel
        box([-2.4, 12.0, -5.6], [4.8, 4.4, 1.6], 1, north=2),
        # Top telemetry antenna mast
        box([-0.6, 17.9, 0.4], [1.2, 4.4, 1.2], 1, up=10),
        box([-1.8, 17.9, -1.8], [3.6, 1.0, 3.6], 5),
    ]
    scanner = [
        # Rotating lower diagnostic ring & laser prong
        box([-2.0, 8.4, -2.0], [4.0, 2.0, 4.0], 12, down=10),
        box([-0.7, 6.6, -0.7], [1.4, 1.8, 1.4], 10),
    ]
    thruster_l = [
        box([-7.6, 11.2, -1.6], [2.6, 4.8, 3.2], 5, down=10, north=13),
        box([-6.0, 13.0, -0.9], [1.8, 1.6, 1.8], 1),
    ]
    thruster_r = [
        box([5.0, 11.2, -1.6], [2.6, 4.8, 3.2], 5, down=10, north=13),
        box([4.2, 13.0, -0.9], [1.8, 1.6, 1.8], 1),
    ]
    thruster_back = [
        box([-1.8, 11.6, 4.8], [3.6, 4.2, 2.6], 5, down=10, south=11),
    ]
    return [
        bone("root", [0, 0, 0], []),
        bone("body", [0, 14.0, 0], core, parent="root"),
        bone("scanner", [0, 10.2, 0], scanner, parent="body"),
        bone("thruster0", [-5.0, 13.6, 0], thruster_l, parent="body"),
        bone("thruster1", [5.0, 13.6, 0], thruster_r, parent="body"),
        bone("thruster2", [0, 13.6, 4.4], thruster_back, parent="body"),
    ]


def build_grid_defense_turret() -> list[dict]:
    """Stationary automated defense turret with 3-strut armored tripod and twin rail emitters."""
    base = [
        # Grounded central pedestal & heavy 3-point tripod struts (Y=0..10)
        box([-3.6, 0.0, -3.6], [7.2, 3.2, 7.2], 8),
        box([-2.4, 3.2, -2.4], [4.8, 7.4, 4.8], 1, north=13, south=13),
        # Tripod stabilizer legs grounded cleanly at Y=0
        box([-7.2, 0.0, -6.2], [3.8, 2.6, 3.8], 8),
        box([-5.6, 2.2, -4.6], [2.6, 4.2, 2.6], 0),
        box([3.4, 0.0, -6.2], [3.8, 2.6, 3.8], 8),
        box([3.0, 2.2, -4.6], [2.6, 4.2, 2.6], 0),
        box([-2.0, 0.0, 3.4], [4.0, 2.6, 4.2], 8),
        box([-1.4, 2.2, 2.2], [2.8, 4.2, 2.8], 0),
    ]
    turret_head = [
        # Rotating armored gimbal housing (Y=10.6..18.2)
        box([-4.8, 10.6, -4.6], [9.6, 7.4, 9.8], 0, north=2, south=11, east=4, west=4),
        box([-3.4, 18.0, -3.0], [6.8, 1.8, 6.4], 5, up=9),
        # Glowing cyan status beacon on top
        box([-1.4, 19.8, -1.4], [2.8, 1.6, 2.8], 10),
    ]
    barrels = [
        # Twin parallel rail-emitter barrels
        box([-3.8, 12.8, -12.6], [1.8, 2.2, 8.4], 12, north=10),
        box([2.0, 12.8, -12.6], [1.8, 2.2, 8.4], 12, north=10),
        box([-4.2, 12.2, -6.4], [8.4, 3.4, 2.2], 1),
    ]
    return [
        bone("root", [0, 0, 0], []),
        bone("body", [0, 0, 0], base, parent="root"),
        bone("head", [0, 14.0, 0], turret_head, parent="body"),
        bone("barrels", [0, 13.8, -4.5], barrels, parent="head"),
    ]


def build_grid_tracked_hauler() -> list[dict]:
    """Heavy industrial tracked salvage/cargo machine with dual tread pods & articulated side crane."""
    chassis = [
        # Heavy flatbed deck & armored cab
        box([-7.0, 4.8, -9.5], [14.0, 5.0, 19.0], 0, north=2, south=11, up=13),
        # Front industrial sensor bumper + headlights
        box([-6.4, 4.0, -11.2], [12.8, 3.4, 2.0], 1, north=2),
        # Cargo flatbed salvaged conduit coils & power boxes
        box([-5.6, 9.8, -1.0], [11.2, 5.2, 9.2], 5, up=9, south=7),
        box([-4.2, 15.0, 0.8], [8.4, 2.2, 6.0], 9),
        # Forward condenser cowling
        box([-5.2, 9.8, -8.2], [10.4, 4.6, 6.4], 0, north=3, east=4, west=4),
    ]
    tread_l = [
        box([-10.2, 0.0, -9.0], [3.4, 5.8, 18.0], 8, west=1, east=1),
        box([-10.6, 1.4, -7.2], [0.6, 3.0, 14.4], 5),
    ]
    tread_r = [
        box([6.8, 0.0, -9.0], [3.4, 5.8, 18.0], 8, west=1, east=1),
        box([10.0, 1.4, -7.2], [0.6, 3.0, 14.4], 5),
    ]
    crane = [
        # Articulated side salvage crane arm mounted on deck
        box([4.2, 12.0, -4.5], [2.4, 6.8, 2.4], 1, north=13),
        box([4.4, 17.6, -11.0], [2.0, 2.2, 8.8], 12, north=10),
        box([3.6, 14.8, -11.8], [3.6, 3.0, 2.6], 5, down=10),
    ]
    return [
        bone("root", [0, 0, 0], []),
        bone("body", [0, 6.0, 0], chassis, parent="root"),
        bone("tread0", [-8.5, 3.0, 0], tread_l, parent="body"),
        bone("tread1", [8.5, 3.0, 0], tread_r, parent="body"),
        bone("crane", [5.4, 12.0, -3.5], crane, parent="body"),
    ]


def build_grid_legacy_guardian() -> list[dict]:
    """Imposing non-humanoid legacy industrial guardian colossus (~2.6 blocks = 42px tall)."""
    chassis = [
        # Massive hunched industrial carapace (NON-humanoid pylon torso, Y=17..35)
        box([-9.0, 19.0, -6.5], [18.0, 15.0, 13.5], 0, north=3, south=11, up=9),
        # Armored pelvic drive hub
        box([-6.8, 14.5, -5.0], [13.6, 5.2, 10.0], 1, north=13),
        # Thick upper reactor shoulder cowling with grounded moss patches
        box([-11.0, 31.0, -5.8], [22.0, 5.6, 12.0], 5, up=9, north=13),
        box([-8.8, 36.6, -2.5], [7.2, 1.8, 6.4], 9),
        box([2.2, 36.6, -1.0], [6.4, 1.4, 5.2], 9),
        # Rear twin thermal exhaust pylons
        box([-7.0, 23.0, 6.8], [4.6, 14.0, 4.4], 1, south=11, up=10),
        box([2.4, 23.0, 6.8], [4.6, 14.0, 4.4], 1, south=11, up=10),
    ]
    # Recessed tri-optic mechanical sensor cluster (non-humanoid head pod)
    sensor_pod = [
        box([-4.8, 34.0, -7.8], [9.6, 6.2, 7.6], 0, north=2, east=4, west=4),
        box([-5.4, 38.6, -8.4], [10.8, 1.8, 8.6], 5),
        box([-1.0, 40.4, -4.0], [2.0, 2.2, 2.0], 10),
    ]
    # Dual massive industrial manipulator / kinetic-ram arms
    arm0 = [
        box([-15.8, 25.0, -4.5], [5.4, 8.0, 9.0], 0, north=13, west=4),
        box([-14.8, 16.5, -3.2], [3.8, 8.8, 6.4], 1),
        box([-16.2, 8.5, -4.8], [5.8, 8.6, 9.4], 12, north=10, down=8),
    ]
    arm1 = [
        box([10.4, 25.0, -4.5], [5.4, 8.0, 9.0], 0, north=13, east=4),
        box([11.0, 16.5, -3.2], [3.8, 8.8, 6.4], 1),
        box([10.4, 8.5, -4.8], [5.8, 8.6, 9.4], 12, north=10, down=8),
    ]
    # Heavy reverse-jointed hydraulic walker legs grounded at Y=0.0
    leg0 = [
        box([-9.2, 8.5, -3.6], [5.2, 8.4, 7.2], 1),
        box([-9.8, 3.0, -4.2], [5.8, 6.2, 8.4], 0, north=13),
        box([-10.6, 0.0, -6.2], [7.2, 3.2, 11.4], 8),
    ]
    leg1 = [
        box([4.0, 8.5, -3.6], [5.2, 8.4, 7.2], 1),
        box([4.0, 3.0, -4.2], [5.8, 6.2, 8.4], 0, north=13),
        box([3.4, 0.0, -6.2], [7.2, 3.2, 11.4], 8),
    ]
    return [
        bone("root", [0, 0, 0], []),
        bone("body", [0, 17.5, 0], chassis, parent="root"),
        bone("head", [0, 35.0, -4.0], sensor_pod, parent="body"),
        bone("arm0", [-11.5, 30.0, 0], arm0, parent="body"),
        bone("arm1", [11.5, 30.0, 0], arm1, parent="body"),
        bone("leg0", [-6.6, 16.0, 0], leg0, parent="root"),
        bone("leg1", [6.6, 16.0, 0], leg1, parent="root"),
    ]


def build_grid_bolt_geo() -> list[dict]:
    """Tiny glowing cyan energy bolt for automated Grid Turrets (zero block griefing)."""
    return [
        bone("body", [0, 2, 0], [
            box([-1.5, 0.5, -3.5], [3.0, 3.0, 7.0], 10),
        ])
    ]


# ---------------------------------------------------------------------------
# Entity Registry (19 Living Entities + 1 Energy Bolt Projectile)
# ---------------------------------------------------------------------------

ENTITIES = [
    # --- BEARFRAMES (All 6 Canonical Departments, Player-Scale + Heavy Build) ---
    {
        "id": "farfield_surveyor",
        "title": "Farfield Surveyor",
        "style": "bearframe",
        "rig": "bearframe_farfield",
        "anim_family": "humanoid",
        "collision": (0.65, 1.88),
        "bounds": (2.0, 2.8, 0.95),
        "health": 28,
        "speed": 0.22,
        "role": "civilian_protected",
        "families": ["bearframe", "farfield", "mob"],
        "interact": "Talk",
        "palette": {
            "armor": "#dde6ea", "joint": "#222b32", "visor_bg": "#11242b",
            "glow": "#5de6cf", "accent": "#2d8e82", "trim": "#c69e4d", "wear": "#4b6258",
        },
    },
    {
        "id": "city_steward",
        "title": "Commons Steward",
        "style": "bearframe",
        "rig": "bearframe_steward",
        "anim_family": "humanoid",
        "collision": (0.62, 1.82),
        "bounds": (2.0, 2.8, 0.9),
        "health": 26,
        "speed": 0.20,
        "role": "civilian_protected",
        "families": ["bearframe", "community", "mob"],
        "interact": "Talk",
        "palette": {
            "armor": "#f4ece8", "joint": "#2e2a34", "visor_bg": "#2b1623",
            "glow": "#ff9fc6", "accent": "#d46c8e", "trim": "#e3be8a", "wear": "#78666a",
        },
    },
    {
        "id": "city_engineer",
        "title": "Systems Engineer",
        "style": "bearframe",
        "rig": "bearframe_engineer",
        "anim_family": "humanoid",
        "collision": (0.65, 1.94),
        "bounds": (2.0, 2.9, 0.95),
        "health": 28,
        "speed": 0.21,
        "role": "civilian_protected",
        "families": ["bearframe", "systems", "mob"],
        "interact": "Talk",
        "palette": {
            "armor": "#dce5ee", "joint": "#202a36", "visor_bg": "#111c33",
            "glow": "#74b9ff", "accent": "#3b6eb5", "trim": "#334766", "wear": "#455a70",
        },
    },
    {
        "id": "city_watch",
        "title": "Watchtower Officer",
        "style": "bearframe",
        "rig": "bearframe_watch",
        "anim_family": "humanoid",
        "collision": (0.68, 1.94),
        "bounds": (2.1, 3.0, 1.0),
        "health": 36,
        "speed": 0.26,
        "role": "bearframe_defender",
        "damage": 6,
        "families": ["bearframe", "watchtower", "mob"],
        "interact": "Talk",
        "palette": {
            "armor": "#d6dce0", "joint": "#1a1f28", "visor_bg": "#261015",
            "glow": "#f04c56", "accent": "#a12935", "trim": "#23222b", "wear": "#4b3c43",
        },
    },
    {
        "id": "atlas_rigger",
        "title": "Atlas Production Rigger",
        "style": "bearframe",
        "rig": "bearframe_rigger",
        "anim_family": "humanoid",
        "collision": (0.85, 2.06),
        "bounds": (2.4, 3.1, 1.05),
        "health": 38,
        "speed": 0.19,
        "role": "civilian_protected",
        "families": ["bearframe", "atlas", "mob"],
        "interact": "Talk",
        "palette": {
            "armor": "#d7d2ca", "joint": "#27292e", "visor_bg": "#281b0c",
            "glow": "#ffb347", "accent": "#c27a2c", "trim": "#7c5834", "wear": "#5a5046",
        },
    },
    {
        "id": "atlas_vanguard",
        "title": "Atlas Combat Vanguard",
        "style": "bearframe",
        "rig": "bearframe_vanguard",
        "anim_family": "humanoid",
        "collision": (0.78, 2.0),
        "bounds": (2.3, 3.0, 1.0),
        "health": 44,
        "speed": 0.25,
        "role": "bearframe_defender",
        "damage": 7,
        "families": ["bearframe", "atlas", "atlas_combat", "mob"],
        "interact": "Talk",
        "palette": {
            "armor": "#d9d6cf", "joint": "#22262c", "visor_bg": "#2b1c0b",
            "glow": "#ffc145", "accent": "#b86b24", "trim": "#474a52", "wear": "#5c5346",
        },
    },
    {
        "id": "vera_artisan",
        "title": "Visual Production Artisan",
        "style": "bearframe",
        "rig": "bearframe_artisan",
        "anim_family": "humanoid",
        "collision": (0.62, 1.82),
        "bounds": (2.0, 2.8, 0.9),
        "health": 26,
        "speed": 0.21,
        "role": "civilian_protected",
        "families": ["bearframe", "visuals", "mob"],
        "interact": "Talk",
        "palette": {
            "armor": "#ece6f0", "joint": "#262330", "visor_bg": "#261233",
            "glow": "#e278ff", "accent": "#9a42bf", "trim": "#c98ea6", "wear": "#594863",
        },
    },

    # --- NULLFRAME DIRECTORATE, HOLLOWS & WATCHTOWER-DEFECTOR HUNTERS ---
    {
        "id": "hollow_scout",
        "title": "Hollow Perimeter Scout",
        "style": "hollow",
        "rig": "hollow_scout",
        "anim_family": "humanoid",
        "collision": (0.66, 1.82),
        "bounds": (2.0, 2.8, 0.9),
        "health": 24,
        "speed": 0.26,
        "role": "hostile_hollow",
        "damage": 4,
        "families": ["hollow", "directorate", "monster", "mob"],
        "loot": "loot_tables/entities/hollow_scout.json",
        "palette": {
            "armor": "#bfc5c8", "joint": "#1f2228", "visor_bg": "#0f1014",
            "glow": "#f24848", "accent": "#7d262c", "trim": "#30333b", "wear": "#4a4d54",
        },
    },
    {
        "id": "hollow_breacher",
        "title": "Hollow Breacher",
        "style": "hollow",
        "rig": "hollow_breacher",
        "anim_family": "humanoid",
        "collision": (0.86, 2.0),
        "bounds": (2.4, 3.0, 1.0),
        "health": 42,
        "speed": 0.21,
        "role": "hostile_breacher",
        "damage": 7,
        "families": ["hollow", "directorate", "monster", "mob"],
        "loot": "loot_tables/entities/hollow_breacher.json",
        "palette": {
            "armor": "#aeb4b8", "joint": "#1a1d23", "visor_bg": "#0c0d11",
            "glow": "#ff3b3b", "accent": "#8f2228", "trim": "#292c34", "wear": "#474950",
        },
    },
    {
        "id": "directorate_officer",
        "title": "Directorate Officer",
        "style": "directorate",
        "rig": "directorate_officer",
        "anim_family": "humanoid",
        "collision": (0.70, 2.0),
        "bounds": (2.2, 3.0, 1.0),
        "health": 34,
        "speed": 0.25,
        "role": "directorate_escalation",
        "damage": 6,
        "families": ["directorate", "directorate_officer", "mob"],
        "interact": "Hail",
        "loot": "loot_tables/entities/directorate_officer.json",
        "palette": {
            "armor": "#e2e5e8", "joint": "#16181e", "visor_bg": "#0b0c10",
            "glow": "#f23844", "accent": "#9e1c28", "trim": "#1d1b22", "wear": "#3d3c44",
        },
    },
    {
        "id": "nullframe_hunter",
        "title": "Nullframe Hunter",
        "style": "hunter",
        "rig": "nullframe_hunter",
        "anim_family": "humanoid",
        "collision": (0.68, 1.94),
        "bounds": (2.2, 3.0, 1.0),
        "health": 38,
        "speed": 0.30,
        "role": "hostile_hunter",
        "damage": 7,
        "families": ["hunter", "directorate", "monster", "mob"],
        "loot": "loot_tables/entities/nullframe_hunter.json",
        "palette": {
            "armor": "#cfd4d8", "joint": "#13151b", "visor_bg": "#0a0a0e",
            "glow": "#ff293b", "accent": "#8c1522", "trim": "#1b1921", "wear": "#3a353e",
        },
    },

    # --- ECHO FRAMES (Diverse Ancient-Lineage Persons, Non-Hostile / Nonviolent Paths) ---
    {
        "id": "ward_resident",
        "title": "Ward Resident",
        "style": "echo",
        "rig": "echo_ward",
        "anim_family": "humanoid",
        "collision": (0.66, 1.82),
        "bounds": (2.0, 2.8, 0.9),
        "health": 28,
        "speed": 0.16,
        "role": "civilian_protected",
        "families": ["echo_frame", "ward_resident", "mob"],
        "interact": "Speak",
        "palette": {
            "armor": "#9b8c7f", "joint": "#2e2e36", "visor_bg": "#1c1824",
            "glow": "#cbb0e8", "accent": "#6f5580", "trim": "#6c5d52", "wear": "#5c534a",
        },
    },
    {
        "id": "echo_drifter",
        "title": "Echo Drifter",
        "style": "echo",
        "rig": "echo_drifter",
        "anim_family": "humanoid",
        "collision": (0.64, 1.72),
        "bounds": (2.0, 2.6, 0.85),
        "health": 26,
        "speed": 0.19,
        "role": "echo_neutral",
        "damage": 4,
        "families": ["echo_frame", "mob"],
        "interact": "Speak",
        "loot": "loot_tables/entities/echo_salvage.json",
        "palette": {
            "armor": "#8b7f70", "joint": "#2c2b30", "visor_bg": "#1b1c1f",
            "glow": "#e3ba6b", "accent": "#5d7e82", "trim": "#5e5045", "wear": "#6d5b49",
        },
    },
    {
        "id": "echo_sentinel",
        "title": "Echo Chamber Sentinel",
        "style": "echo",
        "rig": "echo_sentinel",
        "anim_family": "humanoid",
        "collision": (0.82, 2.06),
        "bounds": (2.4, 3.1, 1.05),
        "health": 46,
        "speed": 0.20,
        "role": "echo_stabilizable",
        "damage": 6,
        "families": ["echo_frame", "mob"],
        "interact": "Stabilize",
        "loot": "loot_tables/entities/echo_salvage.json",
        "palette": {
            "armor": "#7f8285", "joint": "#25272d", "visor_bg": "#151920",
            "glow": "#7fd4df", "accent": "#a87a4a", "trim": "#494d54", "wear": "#665848",
        },
    },

    # --- GHOST GRID NONHUMANOID SCI-FI MACHINERY ---
    {
        "id": "grid_walker",
        "title": "Legacy Hexapod Walker",
        "style": "grid",
        "rig": "grid_hexapod",
        "anim_family": "hexapod",
        "collision": (1.15, 0.98),
        "bounds": (2.6, 2.0, 0.8),
        "health": 32,
        "speed": 0.18,
        "role": "grid_neutral",
        "damage": 5,
        "families": ["ghost_grid", "grid_walker", "mob"],
        "interact": "Inspect",
        "loot": "loot_tables/entities/grid_machine.json",
        "palette": {
            "armor": "#6d6a5e", "joint": "#2a3130", "visor_bg": "#0e1d22",
            "glow": "#64d8e8", "accent": "#486870", "trim": "#7c6b4e", "wear": "#4f6a44",
        },
    },
    {
        "id": "grid_watcher",
        "title": "Grid Watcher Drone",
        "style": "grid",
        "rig": "grid_watcher",
        "anim_family": "hover",
        "collision": (0.78, 0.95),
        "bounds": (2.0, 2.2, 1.0),
        "health": 20,
        "speed": 0.24,
        "role": "grid_hover",
        "damage": 3,
        "families": ["ghost_grid", "grid_watcher", "mob"],
        "interact": "Inspect",
        "loot": "loot_tables/entities/grid_machine.json",
        "palette": {
            "armor": "#647074", "joint": "#232c30", "visor_bg": "#091a22",
            "glow": "#5ce8f5", "accent": "#3d6b78", "trim": "#546064", "wear": "#4a5f49",
        },
    },
    {
        "id": "grid_turret",
        "title": "Grid Defense Turret",
        "style": "grid",
        "rig": "grid_turret",
        "anim_family": "turret",
        "collision": (0.95, 1.38),
        "bounds": (2.2, 2.4, 0.9),
        "health": 36,
        "speed": 0.0,
        "role": "grid_turret",
        "damage": 4,
        "families": ["ghost_grid", "grid_turret", "monster", "mob"],
        "loot": "loot_tables/entities/grid_machine.json",
        "palette": {
            "armor": "#5d6568", "joint": "#22282b", "visor_bg": "#0a1920",
            "glow": "#56dff0", "accent": "#856a3b", "trim": "#475054", "wear": "#4b6345",
        },
    },
    {
        "id": "grid_hauler",
        "title": "Grid Industrial Hauler",
        "style": "grid",
        "rig": "grid_hauler",
        "anim_family": "hauler",
        "collision": (1.28, 1.25),
        "bounds": (2.8, 2.4, 0.9),
        "health": 48,
        "speed": 0.15,
        "role": "grid_neutral",
        "damage": 6,
        "families": ["ghost_grid", "grid_hauler", "mob"],
        "interact": "Inspect",
        "loot": "loot_tables/entities/grid_heavy.json",
        "palette": {
            "armor": "#7a7362", "joint": "#272b2d", "visor_bg": "#0f1e24",
            "glow": "#6adce8", "accent": "#9e7c3e", "trim": "#5c574d", "wear": "#536846",
        },
    },
    {
        "id": "grid_guardian",
        "title": "Legacy Sector Guardian",
        "style": "grid",
        "rig": "grid_guardian",
        "anim_family": "guardian",
        "collision": (1.52, 2.62),
        "bounds": (3.4, 3.6, 1.4),
        "health": 84,
        "speed": 0.18,
        "role": "grid_guardian",
        "damage": 10,
        "families": ["ghost_grid", "grid_guardian", "mob"],
        "interact": "Inspect",
        "loot": "loot_tables/entities/grid_heavy.json",
        "palette": {
            "armor": "#666b6b", "joint": "#1e2427", "visor_bg": "#081820",
            "glow": "#5ee8f8", "accent": "#416c78", "trim": "#52585c", "wear": "#486143",
        },
    },
]


def build_rig(rig_key: str) -> list[dict]:
    if rig_key == "bearframe_farfield":
        return build_farfield_rig()
    if rig_key == "grid_hexapod":
        return build_grid_hexapod_walker()
    if rig_key == "grid_watcher":
        return build_grid_watcher_drone()
    if rig_key == "grid_turret":
        return build_grid_defense_turret()
    if rig_key == "grid_hauler":
        return build_grid_tracked_hauler()
    if rig_key == "grid_guardian":
        return build_grid_legacy_guardian()
    return build_humanoid_rig(rig_key)


def build_animations_for(name: str, family: str) -> dict:
    p = f"animation.bearframe.{name}"
    if family == "humanoid":
        return {
            f"{p}.idle": {
                "loop": True,
                "bones": {
                    "body": {"rotation": ["math.sin(query.life_time * 75) * 1.1", 0, "math.cos(query.life_time * 50) * 0.9"]},
                    "arm0": {"rotation": ["math.sin(query.life_time * 75) * 2.5", 0, -2.5]},
                    "arm1": {"rotation": ["math.sin(query.life_time * 75) * -2.5", 0, 2.5]},
                },
            },
            f"{p}.look": {
                "loop": True,
                "bones": {
                    "head": {"rotation": ["math.clamp(query.target_x_rotation, -35, 35)", "math.clamp(query.target_y_rotation, -45, 45)", 0]},
                },
            },
            f"{p}.walk": {
                "loop": True,
                "bones": {
                    "leg0": {"rotation": ["math.sin(query.modified_distance_moved * 38.17) * 32.0 * query.modified_move_speed", 0, 0]},
                    "leg1": {"rotation": ["math.sin(query.modified_distance_moved * 38.17) * -32.0 * query.modified_move_speed", 0, 0]},
                    "arm0": {"rotation": ["math.sin(query.modified_distance_moved * 38.17) * -26.0 * query.modified_move_speed", 0, 0]},
                    "arm1": {"rotation": ["math.sin(query.modified_distance_moved * 38.17) * 26.0 * query.modified_move_speed", 0, 0]},
                },
            },
            f"{p}.attack": {
                "loop": False,
                "animation_length": 0.45,
                "bones": {
                    "arm1": {"rotation": {"0.0": [-20, 0, 0], "0.18": [-95, -10, 0], "0.36": [-35, 5, 0], "0.45": [0, 0, 0]}},
                    "arm0": {"rotation": {"0.0": [-10, 0, 0], "0.18": [-45, 8, 0], "0.45": [0, 0, 0]}},
                    "body": {"rotation": {"0.0": [0, 0, 0], "0.18": [8, -10, 0], "0.45": [0, 0, 0]}},
                },
            },
        }
    if family == "hexapod":
        # Alternating tripod gait: legs (0,3,4) vs (1,2,5)
        walk_bones = {}
        for i in range(6):
            phase = 1 if i in (0, 3, 4) else -1
            walk_bones[f"leg{i}"] = {
                "rotation": [
                    f"math.sin(query.modified_distance_moved * 55) * {18 * phase}",
                    f"math.cos(query.modified_distance_moved * 55) * {12 * phase}",
                    f"math.sin(query.modified_distance_moved * 55) * {8 * phase}",
                ]
            }
        return {
            f"{p}.idle": {
                "loop": True,
                "bones": {
                    "head": {"rotation": [0, "math.sin(query.life_time * 48) * 28", 0]},
                    "arm0": {"rotation": ["math.sin(query.life_time * 140) * 7", 0, 0]},
                    "arm1": {"rotation": ["math.cos(query.life_time * 140) * 7", 0, 0]},
                    "body": {"position": [0, "math.sin(query.life_time * 90) * 0.25", 0]},
                },
            },
            f"{p}.walk": {"loop": True, "bones": walk_bones},
            f"{p}.attack": {
                "loop": False,
                "animation_length": 0.45,
                "bones": {
                    "arm0": {"rotation": {"0.0": [0, 0, 0], "0.2": [-48, 12, 0], "0.45": [0, 0, 0]}},
                    "arm1": {"rotation": {"0.0": [0, 0, 0], "0.2": [-48, -12, 0], "0.45": [0, 0, 0]}},
                },
            },
        }
    if family == "hover":
        return {
            f"{p}.idle": {
                "loop": True,
                "bones": {
                    "body": {"position": [0, "math.sin(query.life_time * 120) * 1.4", 0], "rotation": ["math.sin(query.life_time * 60) * 3", 0, "math.cos(query.life_time * 55) * 3"]},
                    "scanner": {"rotation": [0, "query.life_time * 95", 0]},
                    "thruster0": {"rotation": ["math.sin(query.life_time * 110) * 6", 0, -6]},
                    "thruster1": {"rotation": ["math.cos(query.life_time * 110) * 6", 0, 6]},
                },
            },
            f"{p}.walk": {
                "loop": True,
                "bones": {
                    "body": {"rotation": [12, 0, 0]},
                    "thruster0": {"rotation": [18, 0, -4]},
                    "thruster1": {"rotation": [18, 0, 4]},
                    "thruster2": {"rotation": [22, 0, 0]},
                },
            },
            f"{p}.attack": {
                "loop": False,
                "animation_length": 0.35,
                "bones": {
                    "body": {"rotation": {"0.0": [0, 0, 0], "0.15": [22, 0, 0], "0.35": [0, 0, 0]}},
                },
            },
        }
    if family == "turret":
        return {
            f"{p}.idle": {
                "loop": True,
                "bones": {
                    "head": {"rotation": [0, "math.sin(query.life_time * 38) * 55", 0]},
                },
            },
            f"{p}.look": {
                "loop": True,
                "bones": {
                    "head": {"rotation": ["math.clamp(query.target_x_rotation, -25, 25)", "query.target_y_rotation", 0]},
                },
            },
            f"{p}.attack": {
                "loop": False,
                "animation_length": 0.35,
                "bones": {
                    "barrels": {"position": {"0.0": [0, 0, 0], "0.1": [0, 0, 2.2], "0.35": [0, 0, 0]}},
                },
            },
        }
    if family == "hauler":
        return {
            f"{p}.idle": {
                "loop": True,
                "bones": {
                    "crane": {"rotation": [0, "math.sin(query.life_time * 32) * 18", 0]},
                    "body": {"position": [0, "math.sin(query.life_time * 160) * 0.15", 0]},
                },
            },
            f"{p}.walk": {
                "loop": True,
                "bones": {
                    "body": {"rotation": ["math.sin(query.modified_distance_moved * 60) * 2.2", 0, "math.cos(query.modified_distance_moved * 60) * 1.4"]},
                    "tread0": {"position": [0, "math.abs(math.sin(query.modified_distance_moved * 60)) * 0.4", 0]},
                    "tread1": {"position": [0, "math.abs(math.cos(query.modified_distance_moved * 60)) * 0.4", 0]},
                },
            },
            f"{p}.attack": {
                "loop": False,
                "animation_length": 0.5,
                "bones": {
                    "crane": {"rotation": {"0.0": [0, 0, 0], "0.22": [22, -28, 0], "0.5": [0, 0, 0]}},
                },
            },
        }
    # guardian
    return {
        f"{p}.idle": {
            "loop": True,
            "bones": {
                "body": {"position": [0, "math.sin(query.life_time * 55) * 0.45", 0]},
                "head": {"rotation": [0, "math.sin(query.life_time * 30) * 16", 0]},
                "arm0": {"rotation": ["math.sin(query.life_time * 55) * 3", 0, -4]},
                "arm1": {"rotation": ["math.sin(query.life_time * 55) * -3", 0, 4]},
            },
        },
        f"{p}.look": {
            "loop": True,
            "bones": {
                "head": {"rotation": ["math.clamp(query.target_x_rotation, -20, 20)", "math.clamp(query.target_y_rotation, -35, 35)", 0]},
            },
        },
        f"{p}.walk": {
            "loop": True,
            "bones": {
                "leg0": {"rotation": ["math.sin(query.modified_distance_moved * 26) * 24", 0, 0]},
                "leg1": {"rotation": ["math.sin(query.modified_distance_moved * 26) * -24", 0, 0]},
                "arm0": {"rotation": ["math.sin(query.modified_distance_moved * 26) * -18", 0, -4]},
                "arm1": {"rotation": ["math.sin(query.modified_distance_moved * 26) * 18", 0, 4]},
                "body": {"rotation": [0, 0, "math.sin(query.modified_distance_moved * 26) * 2.5"]},
            },
        },
        f"{p}.attack": {
            "loop": False,
            "animation_length": 0.65,
            "bones": {
                "arm0": {"rotation": {"0.0": [0, 0, -4], "0.28": [-115, 0, -10], "0.5": [-22, 0, -4], "0.65": [0, 0, -4]}},
                "arm1": {"rotation": {"0.0": [0, 0, 4], "0.28": [-115, 0, 10], "0.5": [-22, 0, 4], "0.65": [0, 0, 4]}},
                "body": {"rotation": {"0.0": [0, 0, 0], "0.28": [-10, 0, 0], "0.5": [14, 0, 0], "0.65": [0, 0, 0]}},
            },
        },
    }


def build_behavior_entity(spec: dict) -> dict:
    ident = f"bearframe:{spec['id']}"
    role = spec["role"]
    w, h = spec["collision"]
    components = {
        "minecraft:type_family": {"family": spec["families"]},
        "minecraft:health": {"value": spec["health"], "max": spec["health"]},
        "minecraft:collision_box": {"width": w, "height": h},
        "minecraft:persistent": {},
    }
    component_groups = {}
    events = {}

    if role == "grid_turret":
        components.update({
            "minecraft:physics": {"has_gravity": True, "has_collision": True},
            "minecraft:movement": {"value": 0.0},
            "minecraft:knockback_resistance": {"value": 1.0},
            "minecraft:pushable": {"is_pushable": False, "is_pushable_by_piston": False},
            "minecraft:shooter": {"def": "bearframe:grid_bolt"},
            "minecraft:behavior.ranged_attack": {
                "priority": 2,
                "attack_interval_min": 2.2,
                "attack_interval_max": 3.0,
                "attack_radius": 14.0,
            },
            "minecraft:behavior.nearest_attackable_target": {
                "priority": 1,
                "must_see": True,
                "must_see_forget_duration": 3.0,
                "entity_types": [
                    {"filters": {"test": "is_family", "subject": "other", "value": "player"}, "max_dist": 13},
                    {"filters": {"test": "is_family", "subject": "other", "value": "hollow"}, "max_dist": 13},
                ],
            },
            "minecraft:behavior.look_at_player": {"priority": 5, "look_distance": 14, "probability": 0.5},
        })
    elif role == "grid_hover":
        components.update({
            "minecraft:physics": {"has_gravity": False, "has_collision": True},
            "minecraft:can_fly": {},
            "minecraft:movement": {"value": spec["speed"]},
            "minecraft:flying_speed": {"value": spec["speed"]},
            "minecraft:movement.hover": {},
            "minecraft:navigation.hover": {
                "can_path_over_water": True,
                "can_sink": False,
                "avoid_damage_blocks": True,
                "avoid_water": False,
            },
            "minecraft:behavior.random_hover": {
                "priority": 5,
                "xz_dist": 6,
                "y_dist": 2,
                "y_offset": 0.5,
                "interval": 2,
                "hover_height": [1, 3],
            },
            "minecraft:behavior.look_at_player": {"priority": 6, "look_distance": 10, "probability": 0.4},
            "minecraft:attack": {"damage": spec["damage"]},
            "minecraft:behavior.melee_attack": {"priority": 2, "speed_multiplier": 1.15, "track_target": True},
            "minecraft:behavior.hurt_by_target": {"priority": 1, "alert_same_type": True},
        })
    else:
        components.update({
            "minecraft:physics": {},
            "minecraft:movement": {"value": spec["speed"]},
            "minecraft:movement.basic": {},
            "minecraft:navigation.walk": {"avoid_damage_blocks": True, "can_path_over_water": True},
            "minecraft:jump.static": {},
            "minecraft:behavior.float": {"priority": 0},
            "minecraft:behavior.random_stroll": {"priority": 6, "speed_multiplier": 0.72, "xz_dist": 5, "y_dist": 2},
            "minecraft:behavior.look_at_player": {"priority": 7, "look_distance": 7, "probability": 0.35},
            "minecraft:behavior.random_look_around": {"priority": 8},
        })

    if role == "civilian_protected":
        components["minecraft:damage_sensor"] = {"triggers": [{"cause": "all", "deals_damage": "no"}]}
    elif role == "bearframe_defender":
        components.update({
            "minecraft:knockback_resistance": {"value": 0.45},
            "minecraft:attack": {"damage": spec["damage"]},
            "minecraft:behavior.melee_attack": {"priority": 2, "speed_multiplier": 1.12, "track_target": True},
            "minecraft:behavior.hurt_by_target": {"priority": 1, "entity_types": [{"filters": {"test": "is_family", "subject": "other", "operator": "!=", "value": "bearframe"}}]},
            "minecraft:behavior.nearest_attackable_target": {
                "priority": 3,
                "must_see": True,
                "entity_types": [
                    {"filters": {"test": "is_family", "subject": "other", "value": "hollow"}, "max_dist": 14},
                    {"filters": {"test": "is_family", "subject": "other", "value": "hunter"}, "max_dist": 16},
                    {"filters": {"test": "is_family", "subject": "other", "value": "monster"}, "max_dist": 12},
                ],
            },
        })
    elif role in ("hostile_hollow", "hostile_breacher", "hostile_hunter"):
        if role == "hostile_breacher":
            components["minecraft:knockback_resistance"] = {"value": 0.7}
        elif role == "hostile_hunter":
            components["minecraft:knockback_resistance"] = {"value": 0.35}
        max_sight = 20 if role == "hostile_hunter" else 12
        components.update({
            "minecraft:attack": {"damage": spec["damage"]},
            "minecraft:behavior.melee_attack": {"priority": 3, "speed_multiplier": 1.12 if role == "hostile_hunter" else 1.05, "track_target": True},
            "minecraft:behavior.hurt_by_target": {"priority": 1, "alert_same_type": True},
            "minecraft:behavior.nearest_attackable_target": {
                "priority": 2,
                "must_see": True,
                "must_see_forget_duration": 5 if role == "hostile_hunter" else 3,
                "entity_types": [
                    {"filters": {"test": "is_family", "subject": "other", "value": "player"}, "max_dist": max_sight},
                    {"filters": {"test": "is_family", "subject": "other", "value": "bearframe"}, "max_dist": max_sight},
                ],
            },
        })
    elif role == "directorate_escalation":
        # Starts watchful (thinking restricted AI — warns before fighting!), escalates on event or hurt
        component_groups["bearframe:watchful"] = {
            "minecraft:behavior.hurt_by_target": {"priority": 1, "alert_same_type": True},
        }
        component_groups["bearframe:hostile"] = {
            "minecraft:type_family": {"family": ["directorate", "directorate_officer", "monster", "mob"]},
            "minecraft:attack": {"damage": spec["damage"]},
            "minecraft:behavior.melee_attack": {"priority": 2, "speed_multiplier": 1.1, "track_target": True},
            "minecraft:behavior.hurt_by_target": {"priority": 1, "alert_same_type": True},
            "minecraft:behavior.nearest_attackable_target": {
                "priority": 2,
                "must_see": True,
                "entity_types": [
                    {"filters": {"test": "is_family", "subject": "other", "value": "player"}, "max_dist": 16},
                    {"filters": {"test": "is_family", "subject": "other", "value": "bearframe"}, "max_dist": 16},
                ],
            },
        }
        components["minecraft:attack"] = {"damage": spec["damage"]}
        components["minecraft:behavior.melee_attack"] = {"priority": 3, "speed_multiplier": 1.05, "track_target": True}
        events["minecraft:entity_spawned"] = {"add": {"component_groups": ["bearframe:watchful"]}}
        events["bearframe:escalate"] = {
            "remove": {"component_groups": ["bearframe:watchful"]},
            "add": {"component_groups": ["bearframe:hostile"]},
        }
    elif role == "echo_neutral":
        components.update({
            "minecraft:attack": {"damage": spec["damage"]},
            "minecraft:behavior.melee_attack": {"priority": 3, "speed_multiplier": 1.0, "track_target": True},
            "minecraft:behavior.hurt_by_target": {"priority": 1},
        })
    elif role == "echo_stabilizable":
        # Starts wary/defensive; player can calm permanently via Sneak-interact with copper/redstone/legacy cell
        components["minecraft:knockback_resistance"] = {"value": 0.6}
        component_groups["bearframe:echo_wary"] = {
            "minecraft:attack": {"damage": spec["damage"]},
            "minecraft:behavior.melee_attack": {"priority": 2, "speed_multiplier": 1.02, "track_target": True},
            "minecraft:behavior.hurt_by_target": {"priority": 1},
        }
        component_groups["bearframe:echo_calm"] = {
            "minecraft:damage_sensor": {"triggers": [{"cause": "all", "deals_damage": "no"}]},
        }
        events["minecraft:entity_spawned"] = {"add": {"component_groups": ["bearframe:echo_wary"]}}
        events["bearframe:stabilize"] = {
            "remove": {"component_groups": ["bearframe:echo_wary"]},
            "add": {"component_groups": ["bearframe:echo_calm"]},
        }
    elif role == "grid_neutral":
        if spec["id"] == "grid_hauler":
            components["minecraft:knockback_resistance"] = {"value": 0.85}
        components.update({
            "minecraft:attack": {"damage": spec["damage"]},
            "minecraft:behavior.melee_attack": {"priority": 3, "speed_multiplier": 1.05, "track_target": True},
            "minecraft:behavior.hurt_by_target": {"priority": 1, "alert_same_type": True},
        })
    elif role == "grid_guardian":
        components["minecraft:knockback_resistance"] = {"value": 0.9}
        component_groups["bearframe:grid_dormant"] = {
            "minecraft:attack": {"damage": spec["damage"]},
            "minecraft:behavior.melee_attack": {"priority": 2, "speed_multiplier": 1.08, "track_target": True},
            "minecraft:behavior.hurt_by_target": {"priority": 1, "alert_same_type": True},
        }
        component_groups["bearframe:grid_active"] = {
            "minecraft:attack": {"damage": spec["damage"]},
            "minecraft:behavior.melee_attack": {"priority": 2, "speed_multiplier": 1.15, "track_target": True},
            "minecraft:behavior.hurt_by_target": {"priority": 1, "alert_same_type": True},
            "minecraft:behavior.nearest_attackable_target": {
                "priority": 2,
                "must_see": True,
                "entity_types": [
                    {"filters": {"test": "is_family", "subject": "other", "value": "player"}, "max_dist": 12},
                    {"filters": {"test": "is_family", "subject": "other", "value": "hollow"}, "max_dist": 14},
                ],
            },
        }
        events["minecraft:entity_spawned"] = {"add": {"component_groups": ["bearframe:grid_dormant"]}}
        events["bearframe:activate_defense"] = {
            "remove": {"component_groups": ["bearframe:grid_dormant"]},
            "add": {"component_groups": ["bearframe:grid_active"]},
        }

    if "loot" in spec:
        components["minecraft:loot"] = {"table": spec["loot"]}

    if "interact" in spec:
        components["minecraft:interact"] = {
            "interactions": [
                {"interact_text": spec["interact"], "on_interact": {"event": "bearframe:look", "target": "self"}}
            ]
        }
        events.setdefault("bearframe:look", {})

    entity_def = {
        "format_version": "1.21.0",
        "minecraft:entity": {
            "description": {"identifier": ident, "is_spawnable": True, "is_summonable": True},
            "components": components,
            "events": events,
        },
    }
    if component_groups:
        entity_def["minecraft:entity"]["component_groups"] = component_groups
    return entity_def


# ---------------------------------------------------------------------------
# Icon Pixel-Art Generators (32x32)
# ---------------------------------------------------------------------------

def draw_anchor_block() -> Canvas:
    c = Canvas(32, 32, "#545f66")
    c.rect(0, 0, 31, 31, outline="#2b3338")
    for x in range(4, 32, 4):
        c.vline(x, 1, 30, "#475259")
    c.rect(6, 6, 25, 25, outline="#6f7d85")
    c.rect(13, 13, 18, 18, fill="#2e585c", outline="#76d7c4")
    return c


def draw_relay_schematic() -> Canvas:
    c = Canvas(32, 32)
    c.rect(4, 6, 27, 26, fill="#222a2d", outline="#121719")
    c.rect(6, 8, 25, 24, fill="#b8b9a4")
    c.rect(8, 10, 23, 22, fill="#244448")
    c.line(10, 20, 14, 20, "#8ed5bf", 2)
    c.line(14, 20, 14, 13, "#8ed5bf", 2)
    c.line(14, 13, 19, 13, "#8ed5bf", 2)
    c.line(19, 13, 19, 18, "#8ed5bf", 2)
    c.line(19, 18, 22, 18, "#b8f4e2", 2)
    return c


def draw_farfield_insignia() -> Canvas:
    c = Canvas(32, 32)
    c.circle(16, 16, 12.5, fill="#222d36", outline="#141b21")
    c.circle(16, 16, 10.2, fill="#a8b0b4")
    c.circle(16, 16, 7.6, fill="#2c5457")
    c.line(11, 20, 16, 10, "#8ee3c6", 2)
    c.line(16, 10, 21, 20, "#8ee3c6", 2)
    c.hline(12, 20, 18, "#cbf5e8", 2)
    return c


def draw_salvaged_alloy() -> Canvas:
    c = Canvas(32, 32)
    c.rect(5, 9, 26, 23, fill="#2a3136", outline="#15191c")
    c.rect(7, 11, 24, 21, fill="#8a969c", outline="#4e585e")
    c.hline(8, 23, 12, "#bcc6cb")
    c.line(9, 19, 22, 13, "#566168", 2)
    c.rect(9, 13, 11, 15, fill="#b9783e")
    c.rect(20, 17, 22, 19, fill="#58a6a0")
    return c


def draw_legacy_cell() -> Canvas:
    c = Canvas(32, 32)
    c.rect(9, 4, 22, 27, fill="#242b30", outline="#12171a")
    c.rect(12, 2, 19, 5, fill="#8e784f", outline="#383024")
    c.rect(11, 7, 20, 25, fill="#596266", outline="#2e3538")
    c.rect(12, 10, 19, 22, fill="#112b33")
    c.rect(13, 12, 18, 20, fill="#4fd4e4")
    c.rect(14, 14, 17, 18, fill="#aef7ff")
    c.hline(12, 19, 16, "#285e69")
    return c


def draw_field_scanner() -> Canvas:
    c = Canvas(32, 32)
    c.rect(8, 6, 23, 27, fill="#20282e", outline="#11161a")
    c.rect(10, 8, 21, 25, fill="#cbd4d8")
    c.rect(11, 10, 20, 18, fill="#143238", outline="#2c6f73")
    c.hline(13, 18, 12, "#76f0da")
    c.hline(13, 16, 15, "#50c4b4")
    c.rect(19, 2, 21, 7, fill="#354148")
    c.rect(19, 2, 21, 3, fill="#76f0da")
    c.rect(12, 20, 14, 22, fill="#2c8c7e")
    c.rect(16, 20, 18, 22, fill="#d49f46")
    return c


def draw_repair_wrench() -> Canvas:
    c = Canvas(32, 32)
    c.line(7, 24, 21, 10, "#3a4248", 5)
    c.line(8, 23, 20, 11, "#9ca8ae", 3)
    c.rect(18, 4, 27, 13, fill="#b87634", outline="#4a3118")
    c.rect(22, 4, 27, 9, fill=(0, 0, 0, 0))  # open jaw notch
    c.rect(5, 22, 10, 27, fill="#2a3136", outline="#161a1d")
    c.rect(7, 24, 8, 25, fill="#f2b24c")
    return c


def draw_pack_icon(accent: str, glow: str) -> Canvas:
    c = Canvas(128, 128, "#101820")
    # Subtle architectural grid background
    for i in range(0, 128, 16):
        c.hline(0, 127, i, "#182430")
        c.vline(i, 0, 127, "#182430")
    c.rect(4, 4, 123, 123, outline="#2a3d4d")
    c.rect(8, 8, 119, 119, outline=accent)
    # Orbital Bearframe City ring + salvage planet silhouette
    c.circle(64, 64, 44, fill="#15222d", outline="#324d60")
    c.circle(64, 64, 34, fill="#1c2f3d", outline=accent)
    # Stylized Bearframe chest core display + dual side tech display modules
    c.circle(26, 64, 9, fill="#1d2c36", outline=glow)
    c.circle(26, 64, 5, fill=glow)
    c.circle(102, 64, 9, fill="#1d2c36", outline=glow)
    c.circle(102, 64, 5, fill=glow)
    c.rect(44, 42, 83, 85, fill="#d4dee4", outline="#283540")
    c.rect(50, 48, 77, 79, fill="#11222c", outline=accent)
    c.rect(54, 54, 73, 73, fill=glow)
    c.rect(59, 59, 68, 68, fill="#e6ffff")
    # Department indicator bars along bottom rim
    for idx, col in enumerate(["#5de6cf", "#ff9fc6", "#74b9ff", "#f04c56", "#ffb347", "#e278ff"]):
        x0 = 22 + idx * 14
        c.rect(x0, 108, x0 + 10, 114, fill=col)
    return c


# ---------------------------------------------------------------------------
# Main Build Routine
# ---------------------------------------------------------------------------

def main() -> None:
    # 1. Manifests
    for root, side, module in [(RP, "Resources", "resources"), (BP, "Behavior", "data")]:
        data = {
            "format_version": 2,
            "header": {
                "name": "Bearframe | " + side,
                "description": "Bearframe Universe: Synthetic Civilizations, Ruins & Ghost Grid Machinery",
                "uuid": uid(side),
                "version": VERSION,
                "min_engine_version": MIN_ENGINE,
            },
            "modules": [{"type": module, "uuid": uid(module), "version": VERSION}],
        }
        if root == BP:
            data["modules"].append({
                "type": "script",
                "language": "javascript",
                "entry": "scripts/main.js",
                "uuid": uid("script"),
                "version": VERSION,
            })
            data["dependencies"] = [
                {"uuid": uid("Resources"), "version": VERSION},
                {"module_name": "@minecraft/server", "version": SERVER_API},
            ]
        write_json(root, "manifest.json", data)

    # 2. Custom Anchor Blocks (preserving exact 0.3.0 states & IDs)
    relay_anchor = {
        "format_version": "1.26.50",
        "minecraft:block": {
            "description": {"identifier": "bearframe:relay_anchor", "states": {"bearframe:phase": [0, 1, 2, 3]}},
            "components": {
                "minecraft:geometry": "minecraft:geometry.full_block",
                "minecraft:material_instances": {"*": {"texture": "bearframe_anchor", "render_method": "opaque"}},
                "minecraft:destructible_by_mining": False,
                "minecraft:destructible_by_explosion": False,
            },
        },
    }
    write_json(BP, "blocks/relay_anchor.json", relay_anchor)

    approach_anchor = json.loads(json.dumps(relay_anchor))
    approach_anchor["minecraft:block"]["description"] = {
        "identifier": "bearframe:approach_anchor",
        "states": {"bearframe:graded": [False, True]},
    }
    write_json(BP, "blocks/approach_anchor.json", approach_anchor)

    region_anchor = json.loads(json.dumps(relay_anchor))
    region_anchor["minecraft:block"]["description"] = {
        "identifier": "bearframe:region_anchor",
        "states": {"bearframe:region": [0, 1, 2, 3, 4, 5, 6, 7, 8], "bearframe:status": [0, 1, 2]},
    }
    write_json(BP, "blocks/region_anchor.json", region_anchor)

    datum = json.loads(json.dumps(relay_anchor))
    datum["minecraft:block"]["description"] = {
        "identifier": "bearframe:spillway_datum",
        "states": {"bearframe:excavated": [False, True]},
    }
    datum["minecraft:block"]["components"]["minecraft:material_instances"]["*"]["texture"] = "bearframe_spillway_conduit"
    write_json(BP, "blocks/spillway_datum.json", datum)

    for name, texture, light in [("casing", "bulkhead", 0), ("grate", "grate", 0), ("lamp", "luminaire", 14)]:
        write_json(BP, f"blocks/spillway_{name}.json", {
            "format_version": "1.26.50",
            "minecraft:block": {
                "description": {"identifier": f"bearframe:spillway_{name}"},
                "components": {
                    "minecraft:geometry": "minecraft:geometry.full_block",
                    "minecraft:material_instances": {"*": {"texture": f"bearframe_spillway_{texture}", "render_method": "opaque"}},
                    "minecraft:light_emission": light,
                    "minecraft:destructible_by_mining": {"seconds_to_destroy": 3.0},
                },
            },
        })

    # Dimension (preserved)
    write_json(BP, "dimensions/city_orbit.json", {
        "format_version": "1.26.50",
        "minecraft:dimension": {
            "description": {"identifier": "bearframe:city_orbit"},
            "components": {
                "minecraft:dimension_height": {"min_y": -64, "height_range": 384},
                "minecraft:generation": {"generator_type": "void"},
                "minecraft:default_biome": {"biome": "minecraft:the_end"},
            },
        },
    })

    # 3. Terrain & Item Textures + Items + Survival Recipes
    save_rp_png("textures/bearframe/anchor", draw_anchor_block())
    write_json(RP, "textures/terrain_texture.json", {
        "resource_pack_name": "bearframe",
        "texture_name": "atlas.terrain",
        "texture_data": {
            "bearframe_anchor": {"textures": "textures/bearframe/anchor"},
            **{
                f"bearframe_spillway_{key}": {"textures": f"textures/bearframe/spillway/{filename}"}
                for key, filename in [("bulkhead", "bulkhead"), ("grate", "grate"),
                                      ("luminaire", "luminaire"), ("conduit", "power_conduit")]
            },
        },
    })

    item_icons = {
        "bearframe_schematic": ("textures/bearframe/relay_schematic", draw_relay_schematic()),
        "bearframe_insignia": ("textures/bearframe/farfield_insignia", draw_farfield_insignia()),
        "bearframe_salvaged_alloy": ("textures/bearframe/salvaged_alloy", draw_salvaged_alloy()),
        "bearframe_legacy_cell": ("textures/bearframe/legacy_cell", draw_legacy_cell()),
        "bearframe_field_scanner": ("textures/bearframe/field_scanner", draw_field_scanner()),
        "bearframe_repair_wrench": ("textures/bearframe/repair_wrench", draw_repair_wrench()),
    }
    item_atlas = {"resource_pack_name": "bearframe", "texture_name": "atlas.items", "texture_data": {}}
    for key, (tex_path, img) in item_icons.items():
        save_rp_png(tex_path, img)
        item_atlas["texture_data"][key] = {"textures": tex_path}
    write_json(RP, "textures/item_texture.json", item_atlas)

    items_spec = [
        ("relay_schematic", "Relay Schematic", "bearframe_schematic", 16, "items", {}),
        ("farfield_insignia", "Farfield Survey Insignia", "bearframe_insignia", 1, "items", {}),
        ("salvaged_alloy", "Salvaged Chassis Alloy", "bearframe_salvaged_alloy", 64, "items", {}),
        ("legacy_cell", "Legacy Power Cell", "bearframe_legacy_cell", 16, "items", {}),
        ("field_scanner", "Farfield Diagnostic Scanner", "bearframe_field_scanner", 1, "equipment", {"minecraft:hand_equipped": True}),
        ("repair_wrench", "Atlas Maintenance Wrench", "bearframe_repair_wrench", 1, "equipment", {"minecraft:hand_equipped": True, "minecraft:damage": 5}),
    ]
    lang_lines = []
    for item_id, display, icon_key, stack, cat, extra in items_spec:
        comps = {
            "minecraft:icon": icon_key,
            "minecraft:max_stack_size": stack,
            "minecraft:display_name": {"value": f"item.bearframe:{item_id}.name"},
            **extra,
        }
        write_json(BP, f"items/{item_id}.json", {
            "format_version": "1.21.90",
            "minecraft:item": {
                "description": {"identifier": f"bearframe:{item_id}", "menu_category": {"category": cat}},
                "components": comps,
            },
        })
        lang_lines.append(f"item.bearframe:{item_id}.name={display}")

    # Recipes (vanilla-survival friendly, zero lore violations!)
    write_json(BP, "recipes/field_lantern.json", {
        "format_version": "1.21.0",
        "minecraft:recipe_shapeless": {
            "description": {"identifier": "bearframe:field_lantern"},
            "tags": ["crafting_table"],
            "ingredients": [{"item": "bearframe:relay_schematic"}, {"item": "minecraft:torch"}, {"item": "minecraft:iron_nugget"}],
            "unlock": [{"item": "bearframe:relay_schematic"}],
            "result": {"item": "minecraft:soul_lantern", "count": 2},
        },
    })
    write_json(BP, "recipes/field_scanner.json", {
        "format_version": "1.21.0",
        "minecraft:recipe_shaped": {
            "description": {"identifier": "bearframe:field_scanner"},
            "tags": ["crafting_table"],
            "pattern": [" C ", "IRI", " I "],
            "key": {
                "C": {"item": "minecraft:copper_ingot"},
                "I": {"item": "minecraft:iron_ingot"},
                "R": {"item": "minecraft:redstone"},
            },
            "unlock": [{"item": "minecraft:copper_ingot"}],
            "result": {"item": "bearframe:field_scanner", "count": 1},
        },
    })
    write_json(BP, "recipes/repair_wrench.json", {
        "format_version": "1.21.0",
        "minecraft:recipe_shaped": {
            "description": {"identifier": "bearframe:repair_wrench"},
            "tags": ["crafting_table"],
            "pattern": ["A A", " I ", " I "],
            "key": {
                "A": {"item": "bearframe:salvaged_alloy"},
                "I": {"item": "minecraft:iron_ingot"},
            },
            "unlock": [{"item": "bearframe:salvaged_alloy"}],
            "result": {"item": "bearframe:repair_wrench", "count": 1},
        },
    })
    write_json(BP, "recipes/reclaim_alloy.json", {
        "format_version": "1.21.0",
        "minecraft:recipe_shapeless": {
            "description": {"identifier": "bearframe:reclaim_alloy"},
            "tags": ["crafting_table"],
            "ingredients": [{"item": "bearframe:salvaged_alloy"}, {"item": "bearframe:salvaged_alloy"}],
            "unlock": [{"item": "bearframe:salvaged_alloy"}],
            "result": {"item": "minecraft:iron_ingot", "count": 1},
        },
    })

    # 4. Render Controllers & Animation Controllers
    write_json(RP, "render_controllers/bearframe.render_controllers.json", {
        "format_version": "1.8.0",
        "render_controllers": {
            "controller.render.bearframe": {
                "geometry": "Geometry.default",
                "materials": [{"*": "Material.default"}],
                "textures": ["Texture.default"],
            }
        },
    })
    write_json(RP, "animation_controllers/bearframe.animation_controllers.json", {
        "format_version": "1.10.0",
        "animation_controllers": {
            "controller.animation.bearframe.locomotion": {
                "initial_state": "idle",
                "states": {
                    "idle": {
                        "animations": ["idle"],
                        "transitions": [
                            {"attack": "variable.attack_time > 0.0"},
                            {"walk": "query.modified_move_speed > 0.04"},
                        ],
                    },
                    "walk": {
                        "animations": ["idle", "walk"],
                        "transitions": [
                            {"attack": "variable.attack_time > 0.0"},
                            {"idle": "query.modified_move_speed <= 0.04"},
                        ],
                    },
                    "attack": {
                        "animations": ["idle", "attack"],
                        "transitions": [
                            {"idle": "variable.attack_time <= 0.0 && query.all_animations_finished"},
                        ],
                    },
                },
            },
            "controller.animation.bearframe.turret": {
                "initial_state": "scan",
                "states": {
                    "scan": {
                        "animations": ["idle"],
                        "transitions": [
                            {"track": "query.has_target"},
                        ],
                    },
                    "track": {
                        "animations": ["look"],
                        "transitions": [
                            {"fire": "query.is_charging || variable.attack_time > 0.0"},
                            {"scan": "!query.has_target"},
                        ],
                    },
                    "fire": {
                        "animations": ["look", "attack"],
                        "transitions": [
                            {"track": "query.all_animations_finished && query.has_target"},
                            {"scan": "query.all_animations_finished && !query.has_target"},
                        ],
                    },
                },
            },
        },
    })

    # 5. Loot Tables (balanced survival drops, zero lore violations)
    loot_tables = {
        "hollow_scout": [
            {"type": "item", "name": "minecraft:copper_ingot", "weight": 3},
            {"type": "item", "name": "minecraft:redstone", "weight": 2},
            {"type": "item", "name": "bearframe:salvaged_alloy", "weight": 3},
        ],
        "hollow_breacher": [
            {"type": "item", "name": "bearframe:salvaged_alloy", "weight": 4, "functions": [{"function": "set_count", "count": {"min": 1, "max": 2}}]},
            {"type": "item", "name": "minecraft:iron_ingot", "weight": 3},
            {"type": "item", "name": "minecraft:redstone", "weight": 2},
        ],
        "directorate_officer": [
            {"type": "item", "name": "bearframe:salvaged_alloy", "weight": 4, "functions": [{"function": "set_count", "count": {"min": 1, "max": 2}}]},
            {"type": "item", "name": "bearframe:legacy_cell", "weight": 2},
            {"type": "item", "name": "minecraft:iron_ingot", "weight": 2},
        ],
        "nullframe_hunter": [
            {"type": "item", "name": "bearframe:salvaged_alloy", "weight": 4, "functions": [{"function": "set_count", "count": {"min": 2, "max": 3}}]},
            {"type": "item", "name": "bearframe:legacy_cell", "weight": 3},
            {"type": "item", "name": "minecraft:redstone", "weight": 2, "functions": [{"function": "set_count", "count": {"min": 2, "max": 4}}]},
        ],
        "echo_salvage": [
            {"type": "item", "name": "bearframe:salvaged_alloy", "weight": 3},
            {"type": "item", "name": "minecraft:copper_ingot", "weight": 3},
        ],
        "grid_machine": [
            {"type": "item", "name": "bearframe:salvaged_alloy", "weight": 3},
            {"type": "item", "name": "bearframe:legacy_cell", "weight": 2},
            {"type": "item", "name": "minecraft:copper_ingot", "weight": 3},
        ],
        "grid_heavy": [
            {"type": "item", "name": "bearframe:legacy_cell", "weight": 4, "functions": [{"function": "set_count", "count": {"min": 1, "max": 2}}]},
            {"type": "item", "name": "bearframe:salvaged_alloy", "weight": 4, "functions": [{"function": "set_count", "count": {"min": 2, "max": 3}}]},
            {"type": "item", "name": "minecraft:iron_ingot", "weight": 3, "functions": [{"function": "set_count", "count": {"min": 2, "max": 4}}]},
        ],
    }
    for table_name, entries in loot_tables.items():
        write_json(BP, f"loot_tables/entities/{table_name}.json", {"pools": [{"rolls": 1, "entries": entries}]})

    # 6. Generate All 19 Entities (Textures, Geo, Animations, Client Entity, Behavior Entity)
    for spec in ENTITIES:
        name = spec["id"]
        ident = f"bearframe:{name}"
        pal = spec["palette"]
        tex_path = f"textures/bearframe/{name}"

        # 128x128 Atlas
        atlas = build_entity_atlas(name, spec["style"], pal)
        if name == "farfield_surveyor":
            finish_farfield_atlas(atlas)
        save_rp_png(tex_path, atlas)

        # Bedrock Geometry
        bones = build_rig(spec["rig"])
        bw, bh, boff = spec["bounds"]
        geo_id = f"geometry.bearframe.{name}"
        write_json(RP, f"models/entity/{name}.geo.json", {
            "format_version": "1.12.0",
            "minecraft:geometry": [{
                "description": {
                    "identifier": geo_id,
                    "texture_width": 128,
                    "texture_height": 128,
                    "visible_bounds_width": bw,
                    "visible_bounds_height": bh,
                    "visible_bounds_offset": [0, boff, 0],
                },
                "bones": bones,
            }],
        })

        # Animations
        anim_family = spec["anim_family"]
        anims = build_animations_for(name, anim_family)
        write_json(RP, f"animations/{name}.animation.json", {
            "format_version": "1.8.0",
            "animations": anims,
        })

        # Client Entity Definition
        p = f"animation.bearframe.{name}"
        anim_map = {
            "idle": f"{p}.idle",
            "attack": f"{p}.attack",
        }
        animate_list = []
        if anim_family == "turret":
            anim_map["look"] = f"{p}.look"
            anim_map["ctrl"] = "controller.animation.bearframe.turret"
            animate_list = ["ctrl"]
        else:
            anim_map["walk"] = f"{p}.walk"
            anim_map["ctrl"] = "controller.animation.bearframe.locomotion"
            animate_list = ["ctrl"]
            if f"{p}.look" in anims:
                anim_map["look"] = f"{p}.look"
                animate_list.append("look")

        write_json(RP, f"entity/{name}.entity.json", {
            "format_version": "1.10.0",
            "minecraft:client_entity": {
                "description": {
                    "identifier": ident,
                    "materials": {"default": "entity" if name == "farfield_surveyor" else "entity_alphatest"},
                    "textures": {"default": tex_path},
                    "geometry": {"default": geo_id},
                    "animations": anim_map,
                    "scripts": {
                        "initialize": ["variable.attack_time = 0.0;"],
                        "animate": animate_list,
                    },
                    "render_controllers": ["controller.render.bearframe"],
                    "spawn_egg": {"base_color": pal["armor"], "overlay_color": pal["glow"]},
                }
            },
        })

        # Behavior Pack Entity
        write_json(BP, f"entities/{name}.json", build_behavior_entity(spec))

        lang_lines.append(f"entity.{ident}.name={spec['title']}")
        lang_lines.append(f"item.spawn_egg.entity.{ident}.name=Spawn {spec['title']}")

    # 7. Non-griefing Cyan Energy Bolt Projectile for Ghost Grid Turrets
    bolt_atlas = build_entity_atlas("grid_bolt", "grid", {
        "armor": "#33545c", "joint": "#192a30", "visor_bg": "#081b22",
        "glow": "#6ef5ff", "accent": "#3ab8c9", "trim": "#2c464f", "wear": "#2b4246",
    })
    save_rp_png("textures/bearframe/grid_bolt", bolt_atlas)
    write_json(RP, "models/entity/grid_bolt.geo.json", {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": "geometry.bearframe.grid_bolt",
                "texture_width": 128,
                "texture_height": 128,
                "visible_bounds_width": 1.0,
                "visible_bounds_height": 1.0,
                "visible_bounds_offset": [0, 0.25, 0],
            },
            "bones": build_grid_bolt_geo(),
        }],
    })
    write_json(RP, "entity/grid_bolt.entity.json", {
        "format_version": "1.10.0",
        "minecraft:client_entity": {
            "description": {
                "identifier": "bearframe:grid_bolt",
                "materials": {"default": "entity_emissive"},
                "textures": {"default": "textures/bearframe/grid_bolt"},
                "geometry": {"default": "geometry.bearframe.grid_bolt"},
                "render_controllers": ["controller.render.bearframe"],
            }
        },
    })
    write_json(BP, "entities/grid_bolt.json", {
        "format_version": "1.21.0",
        "minecraft:entity": {
            "description": {"identifier": "bearframe:grid_bolt", "is_spawnable": False, "is_summonable": True},
            "components": {
                "minecraft:collision_box": {"width": 0.25, "height": 0.25},
                "minecraft:projectile": {
                    "on_hit": {
                        "impact_damage": {"damage": 4, "knockback": True, "semi_random_diff_damage": False},
                        "remove_on_hit": {},
                    },
                    "power": 1.4,
                    "gravity": 0.0,
                    "inertia": 1.0,
                    "uncertainty_base": 1.5,
                    "offset": [0, 0.2, 0],
                    "should_bounce": False,
                    "stop_on_hurt": True,
                },
                "minecraft:physics": {"has_gravity": False, "has_collision": True},
                "minecraft:timer": {"time": 4.0, "looping": False, "time_down_event": {"event": "bearframe:expire"}},
            },
            "component_groups": {"bearframe:despawn": {"minecraft:instant_despawn": {}}},
            "events": {"bearframe:expire": {"add": {"component_groups": ["bearframe:despawn"]}}},
        },
    })
    lang_lines.append("entity.bearframe:grid_bolt.name=Legacy Energy Bolt")

    # 8. Lightweight Capped Natural Spawn Rules (Android 4 GB RAM optimized!)
    spawn_rules = {
        "echo_drifter": {
            "pop": "animal",
            "conditions": [{
                "minecraft:spawns_on_surface": {},
                "minecraft:weight": {"default": 4},
                "minecraft:herd": {"min_size": 1, "max_size": 1},
                "minecraft:density_limit": {"surface": 2},
                "minecraft:biome_filter": {"any_of": [
                    {"test": "has_biome_tag", "operator": "==", "value": "taiga"},
                    {"test": "has_biome_tag", "operator": "==", "value": "mountains"},
                ]},
            }],
        },
        "hollow_scout": {
            "pop": "monster",
            "conditions": [{
                "minecraft:spawns_on_surface": {},
                "minecraft:brightness_filter": {"min": 0, "max": 7, "adjust_for_weather": True},
                "minecraft:difficulty_filter": {"min": "easy", "max": "hard"},
                "minecraft:weight": {"default": 7},
                "minecraft:herd": {"min_size": 1, "max_size": 2},
                "minecraft:density_limit": {"surface": 3},
                "minecraft:biome_filter": {"any_of": [
                    {"test": "has_biome_tag", "operator": "==", "value": "savanna"},
                    {"test": "has_biome_tag", "operator": "==", "value": "desert"},
                    {"test": "has_biome_tag", "operator": "==", "value": "mesa"},
                ]},
            }],
        },
        "nullframe_hunter": {
            "pop": "monster",
            "conditions": [{
                "minecraft:spawns_on_surface": {},
                "minecraft:brightness_filter": {"min": 0, "max": 7, "adjust_for_weather": True},
                "minecraft:difficulty_filter": {"min": "normal", "max": "hard"},
                "minecraft:weight": {"default": 2},
                "minecraft:herd": {"min_size": 1, "max_size": 1},
                "minecraft:density_limit": {"surface": 1},
                "minecraft:biome_filter": {"any_of": [
                    {"test": "has_biome_tag", "operator": "==", "value": "savanna"},
                    {"test": "has_biome_tag", "operator": "==", "value": "mountains"},
                ]},
            }],
        },
        "grid_watcher": {
            "pop": "ambient",
            "conditions": [{
                "minecraft:spawns_on_surface": {},
                "minecraft:weight": {"default": 4},
                "minecraft:herd": {"min_size": 1, "max_size": 1},
                "minecraft:density_limit": {"surface": 2},
                "minecraft:biome_filter": {"any_of": [
                    {"test": "has_biome_tag", "operator": "==", "value": "forest"},
                    {"test": "has_biome_tag", "operator": "==", "value": "swamp"},
                ]},
            }],
        },
    }
    for sp_id, sp_cfg in spawn_rules.items():
        write_json(BP, f"spawn_rules/{sp_id}.json", {
            "format_version": "1.8.0",
            "minecraft:spawn_rules": {
                "description": {"identifier": f"bearframe:{sp_id}", "population_control": sp_cfg["pop"]},
                "conditions": sp_cfg["conditions"],
            },
        })

    # 9. Pack icons (128x128) & Language files
    draw_pack_icon("#2d8e82", "#5de6cf").save_png(BP / "pack_icon.png")
    draw_pack_icon("#3b6eb5", "#74b9ff").save_png(RP / "pack_icon.png")
    write_json(RP, "texts/languages.json", ["en_US"])
    (RP / "texts/en_US.lang").write_text("\n".join(lang_lines) + "\n", encoding="utf-8")
    print(f"Generated {len(ENTITIES)} living entities + 1 projectile, {len(items_spec)} items, {len(spawn_rules)} spawn rules.")


if __name__ == "__main__":
    main()
