"""Build the original Bedrock boss rigs, texture atlases and animation sets."""
import json
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BP, RP = ROOT / "behavior_pack", ROOT / "resource_pack"
SIZE = 256


def write(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def bone(name, pivot, *cubes, parent="body"):
    return name, parent, pivot, cubes


def cube(x, y, z, w, h, d, material="metal"):
    return [x, y, z], [w, h, d], material


def chassis(*cubes):
    return bone("body", [0, 16, 0], *cubes, parent="root")


def spider_legs():
    for row, z in enumerate((-9, 0, 9)):
        for side in (-1, 1):
            suffix = f"{row}_{'l' if side < 0 else 'r'}"
            yield bone("leg_" + suffix, [side*8, 14, z],
                       cube(-17 if side < 0 else 7, 12, z-2, 10, 4, 4),
                       cube(-20 if side < 0 else 15, 7, z-2, 5, 8, 5, "rust"))
            yield bone("foot_" + suffix, [side*17, 9, z],
                       cube(-23 if side < 0 else 16, 0, z-2, 7, 11, 4),
                       cube(-24 if side < 0 else 16, 0, z-3, 8, 3, 6, "rust"),
                       parent="leg_" + suffix)


def echo_rig(regent):
    return [
        chassis(cube(-5, 12, -2, 10, 13, 5), cube(-5, 16, -3, 10, 8, 6, "cloth"),
                cube(-2, 19, -4, 4, 3, 1, "glow")),
        bone("head", [0, 25, 0], cube(-4, 25, -4, 8, 8, 8, "cloth"),
             cube(-3, 26, -5, 6, 4, 2, "dark"),
             cube(-4 if regent else 1, 27, -5.2, 3, 1, 1, "glow"),
             cube(-6, 29, -1, 2, 3, 3, "rust"),
             cube(4, 29, -1, 2, 2, 3, "glow"),
             *([cube(-6, 31, 0, 2, 7, 2, "rust"), cube(3, 32, 1, 2, 5, 2, "metal")] if regent else [])),
        bone("arm_l", [-6, 23, 0], cube(-9, 13, -2, 4, 11, 4, "cloth"),
             cube(-10, 17, -3, 5, 6, 5, "rust"),
             cube(-9, 10, -2, 4, 4, 4, "metal")),
        bone("arm_r", [6, 23, 0], cube(5, 12, -2, 4, 11, 4),
             cube(5, 11, -3, 4, 6, 5, "glow"),
             *([cube(7, 0, 0, 2, 24, 2, "rust"), cube(5, 23, -2, 6, 7, 6, "metal"),
                cube(7, 25, -3, 2, 3, 1, "glow")] if regent else
               [cube(7, 5, -4, 2, 16, 2, "glow"), cube(6, 4, -4, 2, 5, 2, "metal")])),
        bone("leg_l", [-2.5, 12, 0], cube(-5, 0, -2, 4, 13, 4),
             cube(-5, 0, -4, 4, 3, 6, "rust")),
        bone("leg_r", [2.5, 12, 0], cube(1, 0, -2, 4, 13, 4, "dark"),
             cube(1, 0, -4, 4, 3, 6)),
        bone("drape", [0, 24, 3], cube(-6, 5 if regent else 10, 3, 6, 19 if regent else 14, 2, "cloth"),
             cube(0, 9 if regent else 15, 3, 6, 15 if regent else 9, 2, "cloth"),
             cube(-5, 4 if regent else 8, 5, 2, 9, 1, "rust")),
    ]


# Each tuple defines the exact strike frame and animation end in server ticks.
def attack(name, shape, radius, windup, end, damage, poses, **options):
    return dict(name=name, shape=shape, radius=radius, windup=windup, end=end,
                damage=damage, **options), poses


bosses = [
    dict(id="grid_palinode", title="Palinode-6", family="ghost_grid", health=180, speed=.22,
         width=2.2, height=1.55, color="#60e8da",
         palette=["#55594b", "#766347", "#60e8da", "#3e5137", "#292e29"],
         rig=[chassis(cube(-11, 10, -13, 22, 9, 26), cube(-9, 18, -10, 18, 5, 20, "rust"),
                      cube(-10, 20, -6, 6, 4, 16, "cloth")),
              bone("head", [0, 16, -13], cube(-7, 13, -20, 14, 7, 9),
                   cube(-5, 15, -21, 10, 2, 1, "glow")),
              bone("ram", [0, 13, -11], cube(-12, 7, -18, 24, 4, 7, "rust"),
                   cube(-11, 8, -21, 5, 5, 5), cube(6, 8, -21, 5, 5, 5)),
              *spider_legs()],
         moves=[
             attack("Piston Ram", "lane", 9, 24, 49, 9,
                    {"body": ([14, 0, 0], [-11, 0, 0], [6, 0, 0]), "ram": ([-34,0,0], [28,0,0], [10,0,0]),
                     "head": ([-18,0,0], [13,0,0], [0,0,0])}, width=1.65, drive=.85),
             attack("Tripod Quake", "ring", 6, 34, 65, 11,
                    {"body": ([-19,0,0], [22,0,0], [-5,0,0]), "ram": ([-47,0,0], [35,0,0], [10,0,0]),
                     **{f"leg_{i}_{s}": ([0,0,a*24], [0,0,-a*14], [0,0,a*5])
                        for i in range(3) for s,a in [("l",1),("r",-1)]}}, inner=2.4, minRange=2.4),
         ]),
    dict(id="grid_silt_engine", title="Silt Engine", family="ghost_grid", health=230, speed=.16,
         width=2.5, height=2.6, color="#7be8fa",
         palette=["#454c4c", "#796451", "#7be8fa", "#4c5840", "#262d31"],
         rig=[chassis(cube(-14, 4, -13, 28, 11, 26), cube(-10, 14, -10, 20, 7, 20, "rust")),
              bone("tread_l", [-14, 6, 0], cube(-20, 0, -14, 8, 10, 28, "dark")),
              bone("tread_r", [14, 6, 0], cube(12, 0, -14, 8, 10, 28, "dark")),
              bone("rotor", [0, 22, 0], cube(-10, 19, -10, 20, 15, 20),
                   cube(-7, 32, -7, 14, 6, 14, "rust"), cube(-3, 24, -11, 6, 6, 2, "glow")),
              bone("barrel", [0, 28, -7], cube(-5, 22, -23, 10, 10, 16, "rust"),
                   cube(-3, 24, -24, 6, 6, 2, "glow"), parent="rotor"),
              bone("vent_l", [-11, 26, 0], cube(-14, 26, -9, 4, 13, 18, "cloth"), parent="rotor"),
              bone("vent_r", [11, 26, 0], cube(10, 24, -9, 4, 10, 18, "metal"), parent="rotor")],
         moves=[
             attack("Discharge Beam", "lane", 15, 42, 74, 13,
                    {"rotor": ([0,0,8], [0,0,-10], [0,0,5]), "barrel": ([-13,0,0], [-35,0,0], [8,0,0]),
                     "vent_l": ([0,0,-50], [0,0,-70], [0,0,-25]), "vent_r": ([0,0,50], [0,0,70], [0,0,25])}, width=1.1),
             attack("Purge Valve", "ring", 5.4, 27, 60, 8,
                    {"rotor": ([0,-32,0], [0,38,0], [0,-8,0]), "barrel": ([-55,0,0], [-85,0,0], [-22,0,0]),
                     "vent_l": ([0,0,-70], [0,0,-87], [0,0,-30]), "vent_r": ([0,0,70], [0,0,87], [0,0,30])},
                    effect=["slowness", 70]),
         ]),
    dict(id="echo_seam_riven", title="Seam-Riven", family="echo_frame", health=150, speed=.31,
         width=.9, height=2.15, color="#f698d5",
         palette=["#645c67", "#7a624c", "#f698d5", "#373143", "#231f2b"],
         rig=echo_rig(False),
         moves=[
             attack("Seam Cut", "cone", 4.6, 19, 43, 9,
                    {"body": ([8,-53,14], [14,62,-24], [0,20,-10]), "arm_r": ([-82,-45,30], [-30,62,46], [25,15,16]),
                     "arm_l": ([32,15,-30], [-30,-20,-38], [8,0,0]), "drape": ([19,-24,8], [-37,42,12], [13,0,0])}, dot=.35),
             attack("Frame Skip", "lane", 10, 29, 55, 8,
                    {"body": ([-12,30,-20], [24,0,15], [-8,9,0]), "arm_r": ([66,0,20], [-104,0,10], [-42,0,20]),
                     "head": ([18,-40,19], [-24,0,-22], [6,0,0]), "drape": ([-12,0,25], [57,0,-16], [15,0,0])},
                    width=1.2, drive=1.2),
         ]),
    dict(id="echo_veil_regent", title="Veil Regent", family="echo_frame", health=195, speed=.20,
         width=1.0, height=2.45, color="#f7ca79",
         palette=["#635956", "#927747", "#f7ca79", "#4b3834", "#28242b"],
         rig=echo_rig(True),
         moves=[
             attack("Anchor Sigil", "mark", 13, 43, 75, 10,
                    {"body": ([-11,22,0], [19,-17,-8], [0,10,6]), "arm_l": ([-92,0,-38], [-125,0,-24], [-53,0,-19]),
                     "arm_r": ([-160,10,18], [-50,-10,32], [-24,0,17]), "drape": ([22,0,0], [43,0,-16], [6,0,0])}, width=2.35),
             attack("Broken Court", "cone", 6, 31, 62, 8,
                    {"body": ([-9,-30,14], [19,52,-14], [6,13,-4]), "arm_l": ([-70,20,-25], [20,0,-44], [7,0,0]),
                     "arm_r": ([-58,-66,36], [-82,47,54], [-32,0,18]), "drape": ([-14,-34,8], [29,23,12], [5,0,0])},
                    dot=.1, effect=["weakness", 90]),
         ]),
]


def crane_rig():
    rig = [chassis(cube(-10, 10, -9, 20, 7, 18, "rust"),
                   cube(-7, 17, -7, 14, 6, 14), cube(-4, 19, -8, 8, 3, 1, "glow")),
           bone("boom", [0, 21, 2], cube(-3, 20, -20, 6, 6, 24),
                cube(-4, 18, -18, 8, 3, 14, "cloth")),
           bone("claw", [0, 20, -18], cube(-8, 13, -22, 5, 10, 4, "rust"),
                cube(3, 13, -22, 5, 10, 4, "rust"), cube(-7, 12, -21, 14, 3, 3, "glow"),
                parent="boom")]
    for side, x in (("l", -13), ("r", 8)):
        for row, z in (("f", -10), ("b", 6)):
            rig.append(bone("leg_" + side + row, [x+2, 13, z+2],
                       cube(x, 0, z, 5, 15, 5), cube(x-1, 0, z-2, 7, 3, 7, "rust")))
    return rig


def spindle_rig():
    rig = [chassis(cube(-7, 8, -7, 14, 17, 14, "rust"),
                   cube(-5, 17, -8, 10, 4, 1, "glow"), cube(-4, 3, -4, 8, 7, 8, "dark")),
           bone("crown", [0, 23, 0], cube(-11, 23, -11, 22, 4, 22),
                cube(-6, 26, -6, 12, 3, 12, "cloth"), cube(-2, 28, -2, 4, 5, 4, "glow"))]
    for name, x, z, w, d in (("north",-3,-17,6,10), ("south",-3,7,6,10),
                            ("west",-17,-3,10,6), ("east",7,-3,10,6)):
        rig.append(bone(name, [0, 15, 0], cube(x, 13, z, w, 5, d),
                        cube(x, 11, z, w, 2, d, "glow")))
    return rig


def variant_echo(rook):
    rig = echo_rig(False)
    if rook:
        rig.extend([
            bone("shield", [-9, 14, -2], cube(-15, 5, -5, 13, 20, 3, "rust"),
                 cube(-16, 15, -6, 5, 9, 2), cube(-13, 8, -6, 10, 2, 1, "glow"), parent="arm_l"),
            bone("collar", [0, 22, 0], cube(-10, 20, 1, 19, 5, 5, "cloth")),
        ])
    else:
        rig.extend([
            bone("counterweight", [8, 16, 0], cube(9, 3, -2, 2, 16, 2, "dark"),
                 cube(7, 2, -4, 6, 5, 6, "rust"), cube(8, 3, -5, 3, 2, 1, "glow"), parent="arm_r"),
            bone("hood_tail", [-4, 29, 3], cube(-8, 16, 3, 4, 15, 3, "cloth"),
                 cube(-7, 9, 4, 2, 9, 2, "rust"), parent="head"),
        ])
    return rig


bosses.extend([
    dict(id="grid_gantry_marrow", title="Gantry Marrow", family="ghost_grid", health=215, speed=.19,
         width=2.0, height=1.9, color="#a5f8a3",
         palette=["#4f5b52","#786352","#a5f8a3","#415b3b","#293331"], rig=crane_rig(),
         moves=[
            attack("Load Drop", "mark", 11, 38, 70, 13,
                   {"boom": ([-47,-14,0], [23,0,0], [-12,8,0]),
                    "claw": ([32,0,-9], [-44,0,0], [21,0,0]), "body": ([-13,0,0],[13,0,0],[-4,0,0])}, width=2.7),
            attack("Gantry Rake", "cone", 6.4, 31, 63, 10,
                   {"boom": ([-19,-65,14], [7,69,-8], [-17,19,0]),
                    "claw": ([-28,0,-24], [24,0,21], [-6,0,0]), "body": ([0,-18,9],[0,22,-10],[0,0,0])},
                   dot=.05),
         ]),
    dict(id="grid_cinder_spindle", title="Cinder Spindle", family="ghost_grid", health=178, speed=.27,
         width=1.8, height=2.1, color="#ffa964",
         palette=["#565052","#78503d","#ffa964","#3a4d43","#282d2d"], rig=spindle_rig(),
         moves=[
            attack("Flywheel Burst", "ring", 6.2, 32, 59, 10,
                   {"crown": ([20,-95,0],[0,114,0],[0,183,0]), "body": ([0,-26,11],[0,56,-8],[0,105,0]),
                    **{side: ([0,0,21],[0,0,-27],[0,0,8]) for side in ("north","south","east","west")}},
                   inner=1.8, minRange=1.8),
            attack("Induction Lance", "lane", 12, 34, 64, 9,
                   {"crown": ([-37,0,0],[45,75,0],[13,100,0]),
                    "body": ([-24,0,0],[16,0,0],[6,0,0]), "north": ([-46,0,0],[14,0,0],[-9,0,0])},
                   width=1.35, effect=["slowness",55]),
         ]),
    dict(id="echo_rubble_rook", title="Rubble Rook", family="echo_frame", health=218, speed=.19,
         width=1.1, height=2.1, color="#a0c8ff",
         palette=["#544f63","#816954","#a0c8ff","#464749","#292733"], rig=variant_echo(True),
         moves=[
            attack("Barricade Rush", "lane", 7.0, 26, 57, 11,
                   {"arm_l": ([-76,-16,-40],[-98,16,-13],[-44,-12,-12]),
                    "shield": ([0,38,0],[0,-10,0],[11,15,0]), "body": ([-7,0,5],[27,0,-10],[-6,0,2])},
                   width=1.8, drive=.75),
            attack("Fallen Parapet", "ring", 4.6, 33, 66, 10,
                   {"arm_l": ([-165,18,-38],[45,-24,24],[12,0,0]),
                    "shield": ([-24,0,14],[31,0,0],[0,0,0]), "body": ([-17,0,-17],[31,0,15],[8,0,0]),
                    "head": ([-16,25,0],[23,-17,-15],[-8,0,0])}),
         ]),
    dict(id="echo_hush_pendulum", title="Hush Pendulum", family="echo_frame", health=162, speed=.26,
         width=.95, height=2.15, color="#b9f5ac",
         palette=["#5d6658","#7b6952","#b9f5ac","#343b35","#252b29"], rig=variant_echo(False),
         moves=[
            attack("Deadweight Arc", "cone", 5.8, 28, 60, 12,
                   {"body": ([-17,-45,-15],[22,68,9],[-4,19,-9]),
                    "arm_r": ([-126,-31,33],[63,44,31],[26,0,11]),
                    "counterweight": ([-46,29,0],[47,-32,24],[-25,0,0]),
                    "hood_tail": ([32,0,0],[-33,0,15],[5,0,0])}, dot=.42),
            attack("Missing Beat", "mark", 12, 36, 63, 8,
                   {"body": ([13,0,-22],[-27,0,19],[4,0,-7]), "head": ([-19,-35,18],[19,32,-24],[2,0,9]),
                    "arm_r": ([41,25,14],[-146,-31,19],[-67,15,0]),
                    "counterweight": ([36,-14,0],[-37,23,-16],[19,0,0])},
                   width=2.05, effect=["weakness",80]),
         ]),
])


def texture_and_geometry(spec):
    rng = random.Random(spec["id"])
    atlas = Image.new("RGBA", (SIZE, SIZE))
    x = y = row = 0
    bones = [{"name": "root", "pivot": [0, 0, 0]}]
    colors = dict(zip(("metal", "rust", "glow", "cloth", "dark"), spec["palette"]))
    for name, parent, pivot, cubes in spec["rig"]:
        mesh = []
        for origin, size, material in cubes:
            w, h, d = size
            width, height = 2*(w+d), h+d
            if x + width > SIZE:
                x, y, row = 0, y + row, 0
            assert y + height <= SIZE, spec["id"]
            base = tuple(bytes.fromhex(colors[material][1:]))
            for dy in range(height):
                for dx in range(width):
                    edge = dx in (0, d, d+w, 2*d+w, width-1) or dy in (0, d, height-1)
                    shade = (10 if edge else 0) + rng.choice((-15, -8, -2, 0, 2, 6))
                    if material == "glow":
                        shade = -35 if edge else 16
                    elif material in ("metal", "rust") and rng.random() < .07:
                        shade -= 22
                    atlas.putpixel((x+dx, y+dy), tuple(max(0,min(255,c+shade)) for c in base)+(255,))
            mesh.append(dict(origin=origin, size=size, uv=[x, y]))
            x += width
            row = max(row, height)
        bones.append(dict(name=name, parent=parent, pivot=pivot, cubes=mesh))
    return atlas, bones


def animation_set(spec):
    sector = spec["id"]
    rig = {entry[0] for entry in spec["rig"]}
    echo = spec["family"] == "echo_frame"
    gait = {"echo_veil_regent": 1.1, "echo_rubble_rook": 1.28, "echo_hush_pendulum": .88}.get(
        sector, .67 if echo else 1.25)
    idle_body = ({"0.0":[0,0,0], "0.8":[2,0,-3], "1.0":[-3,8,5], "1.18":[1,-4,-2], "2.4":[0,0,0]}
                 if echo else [0,0,"math.sin(query.anim_time * 110) * 2"])
    idle = {"body":{"rotation":idle_body}}
    if echo:
        idle["head"] = {"rotation":{"0.0":[0,0,0], "1.0":[-6,11,8], "1.12":[6,-7,-4], "2.4":[0,0,0]}}
    walk = {"body":{"position":[0, f"math.abs(math.sin(query.anim_time * {360/gait})) * 1.2",0]}}
    if echo:
        for side, sign in (("l",1),("r",-1)):
            walk["leg_"+side] = {"rotation":[f"math.sin(query.anim_time * {360/gait}) * {29*sign}",0,0]}
            walk["arm_"+side] = {"rotation":[f"math.sin(query.anim_time * {360/gait} + 35) * {-19*sign}",0,sign*7]}
        walk["drape"] = {"rotation":[18,"math.sin(query.anim_time * 310) * 12",0]}
    elif sector == "grid_palinode":
        for i in range(3):
            for side, offset in (("l",0),("r",1)):
                phase = (i+offset)%2*180
                wave = f"math.sin(query.anim_time * 320 + {phase})"
                # The middle actuator overshoots and briefly catches during its recovery.
                walk[f"leg_{i}_{side}"] = {"rotation":[0, f"{wave} * 19", 0],
                    "position":[0,f"math.max(0, {wave}) * {4 if i==1 else 2.7}",0]}
                foot_wave = f"math.sin(query.anim_time * 640 + {phase}) * 6" if i==1 else "0"
                walk[f"foot_{i}_{side}"] = {"rotation":[f"{wave} * 13 + {foot_wave}",0,0]}
    elif sector == "grid_gantry_marrow":
        idle["boom"] = {"rotation": ["math.sin(query.anim_time * 150) * 5",0,0]}
        walk["boom"] = {"rotation": [-12,"math.sin(query.anim_time * 280) * 7",0]}
        for leg, sign in (("lf",1),("lb",-1),("rf",-1),("rb",1)):
            walk["leg_"+leg] = {"rotation": [f"math.sin(query.anim_time * 288) * {23*sign}",0,0]}
    elif sector == "grid_cinder_spindle":
        idle["crown"] = {"rotation":[0,"query.anim_time * 150",0]}
        walk["crown"] = {"rotation":[0,"query.anim_time * 288",0]}
        walk["body"] = {"position":[0,2,0],"rotation":[12,0,"math.sin(query.anim_time * 288) * 7"]}
    else:
        walk["body"]["rotation"] = [0,0,"math.sin(query.anim_time * 225) * 4"]
        walk["rotor"] = {"rotation":[-4,"math.sin(query.anim_time * 170) * 6",0]}
        for side, sign in (("l",1),("r",-1)):
            walk["tread_"+side] = {"position":[0,0,f"math.sin(query.anim_time * 230 + {90*sign}) * 0.7"]}
    if sector == "echo_rubble_rook":
        walk["arm_l"] = {"rotation":[-39,-8,-14]}
        walk["body"]["rotation"] = [13,0,"math.sin(query.anim_time * 281) * 8"]
    if sector == "echo_hush_pendulum":
        walk["counterweight"] = {"rotation":["math.sin(query.anim_time * 409) * 46",0,12]}
        walk["head"] = {"rotation":["math.sin(query.anim_time * 818) * 8",-13,17]}
    animations = {"idle":dict(loop=True, animation_length=2.4,bones=idle),
                  "walk":dict(loop=True, animation_length=gait,bones=walk)}
    for idx, (move, poses) in enumerate(spec["moves"]):
        impact, end = move["windup"]/20, move["end"]/20
        keys = {}
        for name, (coil, strike, recoil) in poses.items():
            assert name in rig, name
            keys[name] = {"rotation":{
                "0.0":[0,0,0], str(round(impact*.42,3)):[round(n*.58,2) for n in coil],
                str(round(impact-.12,3)):list(coil), str(impact):list(strike),
                str(round(impact+.24,3)):list(recoil), str(end):[0,0,0]}}
        animations[f"attack{idx}"] = dict(animation_length=end, loop="hold_on_last_frame", bones=keys)
    animations["death"] = dict(animation_length=1, loop="hold_on_last_frame", bones={
        "root":{"rotation":{"0.0":[0,0,0],"0.2":[-7,0,11],"1.0":[0,0,62 if echo else -17]},
                "position":{"0.0":[0,0,0],"1.0":[0,-7 if echo else -4,0]}}})
    return {f"animation.bearframe.{sector}.{name}":value for name,value in animations.items()}


def build(spec):
    name = spec["id"]
    identifier = "bearframe:" + name
    atlas, bones = texture_and_geometry(spec)
    atlas.save(RP / f"textures/bearframe/{name}.png")
    geom = f"geometry.bearframe.{name}"
    write(RP / f"models/entity/{name}.geo.json", {"format_version":"1.12.0", "minecraft:geometry":[{
        "description":{"identifier":geom,"texture_width":SIZE,"texture_height":SIZE,
                       "visible_bounds_width":6,"visible_bounds_height":5,"visible_bounds_offset":[0,1,0]},
        "bones":bones}]})
    write(RP / f"animations/{name}.animation.json",
          {"format_version":"1.8.0","animations":animation_set(spec)})
    controller = "controller.animation.bearframe.boss"
    write(RP / f"entity/{name}.entity.json", {"format_version":"1.10.0","minecraft:client_entity":{"description":{
        "identifier":identifier,"materials":{"default":"entity_alphatest"},
        "textures":{"default":f"textures/bearframe/{name}"},"geometry":{"default":geom},
        "animations":{**{key:f"animation.bearframe.{name}.{key}"
                         for key in ("idle","walk","attack0","attack1","death")},"boss":controller},
        "scripts":{"animate":["boss"]},"render_controllers":["controller.render.bearframe"],
        "spawn_egg":{"base_color":spec["palette"][0],"overlay_color":spec["color"]}}}})
    loot = "grid_heavy" if spec["family"] == "ghost_grid" else "echo_salvage"
    hold_group = "bearframe:boss_hold"
    write(BP / f"entities/{name}.json", {"format_version":"1.21.0","minecraft:entity":{
        "description":{"identifier":identifier,"is_spawnable":True,"is_summonable":True,
                       "properties":{"bearframe:boss_move":{"type":"int","range":[0,2],"default":0,"client_sync":True}}},
        "components":{
            "minecraft:type_family":{"family":[spec["family"],"bearframe_boss","mob","monster"]},
            "minecraft:health":{"value":spec["health"],"max":spec["health"]},
            "minecraft:boss":{"name":spec["title"],"hud_range":30,"should_darken_sky":False},
            "minecraft:collision_box":{"width":spec["width"],"height":spec["height"]},
            "minecraft:persistent":{},"minecraft:physics":{},
            "minecraft:pushable":{"is_pushable":False,"is_pushable_by_piston":False},
            "minecraft:knockback_resistance":{"value":.75},
            "minecraft:movement":{"value":spec["speed"]},"minecraft:movement.basic":{},
            "minecraft:navigation.walk":{"avoid_damage_blocks":True,"can_path_over_water":True},
            "minecraft:jump.static":{},
            "minecraft:behavior.float":{"priority":0},
            "minecraft:behavior.nearest_attackable_target":{"priority":1,"must_see":True,
                "entity_types":[{"filters":{"test":"is_family","subject":"other","value":"player"},"max_dist":24}]},
            "minecraft:behavior.move_towards_target":{"priority":3,"speed_multiplier":1,"within_radius":3},
            "minecraft:loot":{"table":f"loot_tables/entities/{loot}.json"}},
        "component_groups":{hold_group:{"minecraft:movement":{"value":0}}},
        "events":{
            "bearframe:boss_idle":{"remove":{"component_groups":[hold_group]},
                                   "set_property":{"bearframe:boss_move":0}},
            **{f"bearframe:boss_attack{i}":{"add":{"component_groups":[hold_group]},
                                           "set_property":{"bearframe:boss_move":i+1}} for i in range(2)}
        }}})


def main():
    for spec in bosses:
        build(spec)
    active = [{"death":"!query.is_alive"},{"attack0":"query.property('bearframe:boss_move') == 1"},
              {"attack1":"query.property('bearframe:boss_move') == 2"}]
    write(RP / "animation_controllers/bearframe.boss.animation_controllers.json", {
        "format_version":"1.10.0","animation_controllers":{"controller.animation.bearframe.boss":{"states":{
            "default":{"animations":["idle"],"transitions":[*active,{"walk":"query.is_moving"}],"blend_transition":.1},
            "walk":{"animations":["walk"],"transitions":[*active,{"default":"!query.is_moving"}],"blend_transition":.1},
            **{f"attack{i}":{"animations":[f"attack{i}"],"transitions":[active[0],{"default":"query.property('bearframe:boss_move') == 0"}]}
               for i in range(2)},
            "death":{"animations":["death"]}
        }}}})
    catalog = {"bearframe:"+spec["id"]:[move for move,_ in spec["moves"]] for spec in bosses}
    (BP/"scripts/boss_moves.js").write_text("// Generated by tools/build_bosses.py.\nexport const BOSS_MOVES = "
                                           + json.dumps(catalog, indent=2) + ";\n")
    lang = RP/"texts/en_US.lang"
    lines = lang.read_text().splitlines()
    for spec in bosses:
        key = "entity.bearframe:" + spec["id"]
        egg = "item.spawn_egg.entity.bearframe:" + spec["id"]
        lines = [line for line in lines if not line.startswith((key+".name=",egg+".name="))]
        lines.extend([f"{key}.name={spec['title']}", f"{egg}.name=Spawn {spec['title']}"])
    lang.write_text("\n".join(lines)+"\n")


if __name__ == "__main__":
    main()
