"""Build the original Bedrock boss rigs, texture atlases and animation sets."""
import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image

from boss_reference import motion_profile

ROOT = Path(__file__).resolve().parents[1]
BP, RP = ROOT / "behavior_pack", ROOT / "resource_pack"
SIZE = 512


def write(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def bone(name, pivot, *cubes, parent="body"):
    return name, parent, pivot, cubes


def cube(x, y, z, w, h, d, material="metal", rotation=None):
    return [x, y, z], [w, h, d], material, rotation


def chassis(*cubes):
    return bone("body", [0, 16, 0], *cubes, parent="root")


# Each tuple defines the exact strike frame and animation end in server ticks.
def attack(name, shape, radius, windup, end, damage, poses, **options):
    return dict(name=name, shape=shape, radius=radius, windup=windup, end=end,
                damage=damage, **options), poses


bosses = [
    dict(id="grid_palinode", title="Palinode-6", family="ghost_grid", health=180, speed=.22,
         width=2.2, height=1.55, color="#60e8da",
         palette=["#55594b", "#766347", "#60e8da", "#3e5137", "#292e29"],
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
         width=1.05, height=2.45, color="#f698d5",
         palette=["#645c67", "#7a624c", "#f698d5", "#373143", "#231f2b"],
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
         width=1.1, height=2.75, color="#f7ca79",
         palette=["#635956", "#927747", "#f7ca79", "#4b3834", "#28242b"],
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


bosses.extend([
    dict(id="grid_gantry_marrow", title="Gantry Marrow", family="ghost_grid", health=215, speed=.19,
         width=2.0, height=1.9, color="#a5f8a3",
         palette=["#4f5b52","#786352","#a5f8a3","#415b3b","#293331"],
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
         palette=["#565052","#78503d","#ffa964","#3a4d43","#282d2d"],
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
         width=2.1, height=1.9, color="#a0c8ff",
         palette=["#544f63","#816954","#a0c8ff","#464749","#292733"],
         moves=[
            attack("Harrowing Rush", "lane", 7.0, 26, 57, 11,
                   {"arm_l": ([-19,4,-10],[21,-5,5],[-6,0,0]),
                    "arm_r": ([-19,-4,10],[21,5,-5],[-6,0,0]),
                    "brace_l": ([0,-35,-16],[0,24,9],[0,10,4]),
                    "brace_r": ([0,35,16],[0,-24,-9],[0,-10,-4]),
                    "body": ([-8,0,0],[13,0,-3],[-4,0,2])},
                   width=1.8, drive=.75),
            attack("Fourfold Slam", "ring", 4.6, 33, 66, 10,
                   {"arm_l": ([-25,8,-8],[12,-8,4],[4,0,0]),
                    "arm_r": ([-25,-8,8],[12,8,-4],[4,0,0]),
                    "brace_l": ([-45,0,-14],[46,0,16],[11,0,4]),
                    "brace_r": ([-45,0,14],[46,0,-16],[11,0,-4]),
                    "body": ([-13,0,-4],[13,0,5],[3,0,0]),
                    "head": ([-16,25,0],[23,-17,-15],[-8,0,0])}),
         ]),
    dict(id="echo_hush_pendulum", title="Hush Pendulum", family="echo_frame", health=162, speed=.26,
         width=1.05, height=2.6, color="#b9f5ac",
         palette=["#5d6658","#7b6952","#b9f5ac","#343b35","#252b29"],
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


def silt_rig():
    c = cube
    yield chassis(c(-12,4,-13,24,8,30,"dark"),c(-10,11,2,20,6,14),
                  c(-9,16,7,15,3,8,"moss"),c(-9,7,-19,18,4,8,"rust"))
    for side,x in (("l",-18),("r",11)):
        yield bone("tread_"+side,[x+3,5,0],c(x,0,-15,7,9,31,"dark"),
                   *(c(x-1,1,z,9,2,2,"metal") for z in range(-14,16,5)))
    yield bone("rotor",[0,15,1],c(-3,13,-2,6,13,7,"rust"),
               c(-8,23,0,16,7,11),c(-7,29,5,9,3,5,"moss"),
               c(-5,24,10,10,4,2,"dark"))
    yield bone("barrel",[0,23,1],c(-2,19,-16,4,5,20,"dark"),
               c(-8,17,-22,3,10,12,"metal",[0,12,0]),
               c(5,17,-22,3,10,12,"metal",[0,-12,0]),
               c(-4,19,-22,8,6,3,"dark"),c(-3,20,-23,6,4,1,"glow"),parent="rotor")
    for side,x in (("l",-11),("r",7)):
        yield bone("vent_"+side,[x+2,23,7],c(x,22,2,4,12,13,"rust"),
                   c(x,33,4,4,2,8,"moss"),c(x+1,29,1,2,2,2,"glow"),parent="rotor")


def gantry_rig():
    c = cube
    yield chassis(c(-10,12,-6,20,5,16,"dark"),c(-10,17,4,20,4,7),
                  c(-3,18,8,9,2,4,"moss"))
    for side,x in (("l",-13),("r",10)):
        for end,z in (("f",-8),("b",9)):
            sign = -1 if side=="l" else 1
            yield bone("leg_"+side+end,[x+1,15,z],
                       c(x,5,z-2,4,12,4,"metal",[0,0,sign*24]),
                       c(x+2*sign,0,z-3,3,8,5,"dark",[0,0,-sign*19]),
                       c(x+3*sign-1,0,z-4,6,2,8,"rust"))
    yield bone("boom",[0,20,7],c(-3,21,5,6,17,5,"metal",[14,0,0]),
               c(-3,33,-20,6,5,29,"metal",[-9,0,0]),
               c(-5,35,1,9,3,8,"moss"),c(-2,28,-12,4,2,18,"dark",[-16,0,0]),
               c(-2,30,-20,4,2,2,"glow"))
    yield bone("claw",[0,35,-18],c(-1,21,-18,2,15,2,"dark"),
               c(-6,17,-23,4,8,5,"metal",[0,0,-29]),
               c(2,17,-23,4,8,5,"metal",[0,0,29]),
               c(-4,15,-23,8,2,4,"rust"),parent="boom")


def cinder_rig():
    c = cube
    yield chassis(c(-5,5,-5,10,22,10,"dark"),c(-3,2,-3,6,7,6,"rust"),
                  c(-5,15,-6,10,7,2),c(-3,17,-7,6,2,1,"glow"))
    yield bone("crown",[0,19,0],c(-8,21,-8,16,4,16,"metal",[0,45,0]),
               c(-3,17,-23,6,6,46,"dark"),c(-23,17,-3,46,6,6,"dark"),
               c(-5,23,-4,7,2,6,"moss"))
    for name,x,z,angle in (("north",0,-19,0),("south",0,19,180),("west",-19,0,90),("east",19,0,-90)):
        yield bone(name,[0,18,0],c(x-4,15,z-4,8,10,8,"metal",[12,angle,0]),
                   c(x-2,16,z-3,4,3,6,"glow"),c(x-3,24,z-2,5,1,4,"moss"),parent="crown")


def rook_rig():
    c = cube

    def strut(start, end, width, depth, material):
        """Place a rectangular segment between two points."""
        dx,dy,dz = (b-a for a,b in zip(start,end))
        length = round(math.sqrt(dx*dx+dy*dy+dz*dz))
        x,y,z = ((a+b)/2 for a,b in zip(start,end))
        pitch = math.degrees(math.atan2(dz, math.hypot(dx,dy)))
        roll = math.degrees(math.atan2(-dx,dy))
        return c(x-width/2,y-length/2,z-depth/2,width,length,depth,material,[pitch,0,roll])

    yield chassis(strut((0,13,13),(0,23,-10),10,7,"dark"),
                  c(-9,18,-11,18,7,9,"dark"),c(-5,17,-13,10,4,2,"glow"),
                  c(-8,14,8,16,6,10,"rust"))
    yield bone("head",[0,23,-11],
               c(-5,18,-16,10,9,7,"dark"),c(-4,20,-17,8,4,2,"dark"),
               c(-2,21,-18,4,2,1,"glow"),c(-6,25,-16,11,3,7,"metal",[0,0,-9]),
               c(-6,18,-15.75,3,8,5,"metal",[0,0,-12]),
               c(4,20,-15.7,2,6,4,"metal",[0,0,16]))
    # Broken halo above the face. The absent arc leaves the profile open.
    yield bone("relay_l",[0,25,-10],*(
        c(round(11*math.cos(t))-2,round(25+11*math.sin(t))-1,-11,4,3,3,
          "metal" if index%2 else "glow",[0,0,math.degrees(t)+90])
        for index,t in enumerate(map(math.radians,(32,57,84,112,144,171)))),parent="head")
    yield bone("drape",[0,23,1],
               c(-9,20,-6,18,2,20,"cloth",[-9,0,0]),
               c(8,9,-1,2,14,11,"cloth",[6,0,-15]),
               c(8,5,6,2,11,4,"cloth",[14,0,-10]),
               c(-10,10,3,2,13,10,"cloth",[9,0,15]),
               c(-11,8,6,1,10,3,"moss",[7,0,12]))
    for tag,sign in (("l",-1),("r",1)):
        shoulder=(7*sign,22,-8)
        elbow=(12*sign,12,-11)
        palm=(15*sign,2,-18)
        hip=(6*sign,15,11)
        hock=(9*sign,8,17)
        yield bone("arm_"+tag,list(shoulder),
                   strut(elbow,shoulder,5,5,"dark"),
                   strut((11*sign,14,-11),(8*sign,21,-8),6,6,"metal"))
        yield bone("paw_"+tag,list(elbow),
                   strut(palm,elbow,4,4,"dark"),
                   strut((14*sign,4,-17),(12*sign,11,-12),6,5,"metal"),
                   c(palm[0]-3,1,-20,6,3,6,"metal"),
                   *(c(palm[0]+i,0,-23,1,2,5,"rust",[9,0,i*4]) for i in (-3,0,3)),
                   parent="arm_"+tag)
        yield bone("leg_"+tag,list(hip),
                   strut(hock,hip,5,5,"metal"),
                   strut((11*sign,2,19),hock,4,4,"dark"),
                   c(11*sign-3,0,16,6,3,7,"metal"))
        joint=(17*sign,28,4)
        yield bone("brace_"+tag,[6*sign,23,4],
                   strut(joint,(6*sign,23,4),4,4,"dark"),
                   strut((14*sign,27,4),(8*sign,24,4),5,5,"metal"))
        yield bone("hook_"+tag,list(joint),
                   strut((23*sign,22,-2),joint,4,4,"metal"),
                   strut((24*sign,16,-5),(23*sign,22,-2),3,3,"dark"),
                   c(24*sign-2,15,-6,4,3,3,"metal"),
                   *(c(24*sign+i,12,-7,1,4,2,"rust",[18,0,i*7]) for i in (-2,1)),
                   parent="brace_"+tag)


def tall_echo_rig(kind):
    """Three separate legacy chassis, with weapons carried by their actual joints."""
    c = cube
    cleaver = kind == "echo_seam_riven"
    regent = kind == "echo_veil_regent"
    h = 0 if cleaver else 3 if regent else 1
    shoulder = 30+h
    yield chassis(c(-3,18,-2,6,13+h,5,"dark"), c(-5,22,-3,10,7+h,6,"dark"),
                  c(-3,23+h,-4,6,4,2,"rust"),c(-2,24+h,-5,4,3,1,"glow"),
                  c(-6,27+h,-2,5,4,5,"metal",[0,0,23]),
                  c(2,26+h,-2,5,4,5,"metal",[0,0,-26]),
                  c(-5,17,-1,10,4,4,"dark"),
                  c(-7,16,-2,4,3,4,"metal",[0,0,-12]),
                  c(3,17,-1,4,3,4,"metal",[0,0,11]),
                  c(-5,29+h,0,6,2,4,"cloth",[0,0,-12]),
                  c(0,27+h,-4,6,2,5,"cloth",[0,0,16]))
    y = 33+h
    mask = [c(-3,y-1,-3,6,7,6,"dark"),c(-4,y+4,-4,8,2,8,"cloth"),
            c(-5,y,-4,2,5,6,"cloth",[0,0,-18]),c(3,y+1,-4,2,4,6,"cloth",[0,0,21])]
    if cleaver:
        mask += [c(-4,y+1,-5,4,5,2,"metal",[0,0,-24]),c(0,y,-5,3,5,2,"metal",[0,0,17]),
                 c(-1,y+1,-6,1,4,1,"glow"),c(4,y+1,-2,2,3,3,"dark"),
                 c(5,y+1,-3,1,2,1,"glow")]
    elif regent:
        mask += [c(-3,y+1,-4,6,4,1,"dark"),c(-1,y+1,-5,2,4,1,"glow"),
                 c(-3,y+3,-5.1,6,1,1,"glow")]
        for dx in (-6,-3,0,3,6):
            mask.extend((c(dx,y+5,0,1,6-abs(dx)//3,2,"rust",[0,0,-dx*5]),
                         c(dx,y+9-abs(dx)//3,-.1,1,2,2,"glow",[0,0,-dx*5])))
    else:
        mask += [c(-3,y+1,-5,3,6,2,"metal",[0,0,-16]),
                 c(0,y,-5,3,6,2,"metal",[0,0,16]),c(-.5,y+1,-6,1,4,1,"glow")]
    yield bone("head",[0,y,0],*mask)
    for tag,side in (("l",-1),("r",1)):
        x = side*(8 if cleaver else 7)
        elbow = 20+h+(2 if regent and tag=="r" else 0)
        yield bone("arm_"+tag,[x,shoulder,0],
                   c(x-1,elbow-1,-1,3,shoulder-elbow+2,3,"dark",[0,0,side*9]),
                   c(x-3,shoulder-5,-2,5,6,5,"metal",[0,0,-side*20]),
                   c(x-2,shoulder,-1,3,1,3,"moss"))
        if regent and tag == "r":
            yield bone("forearm_r",[x,elbow,-1],
                       c(6,22,-8,4,4,8,"dark",[8,0,-8]),
                       c(6,23,-7,4,4,5,"metal"),parent="arm_r")
            yield bone("grip",[9,23,-9],
                       c(7,21,-10,2,5,4,"dark"),
                       c(8,22,-11,4,1,2,"metal"),
                       c(8,24,-11,4,1,2,"metal"),
                       c(11,21,-10,1,4,3,"rust"),parent="forearm_r")
        else:
            yield bone("forearm_"+tag,[x,elbow,-1],
                       c(x-1,elbow-8,-2,3,8,3,"dark"),
                       c(x-2,elbow-7,-3,4,6,4,"metal",[0,0,side*12]),
                       c(x-1,elbow-10,-2,3,3,3,"rust"),parent="arm_"+tag)
        hip = side*(4 if regent else 5)
        yield bone("leg_"+tag,[hip,18,0],
                   c(hip-1,9,-1,3,10,3,"dark",[0,0,side*9]),
                   c(hip-2,11,-3,4,6,4,"metal",[0,0,side*16]))
        boot = hip+side
        yield bone("shin_"+tag,[boot,9,0],
                   c(boot-1,1,0,3,9,3,"dark"),c(boot-2,2,-2,4,6,3,"metal",[0,0,-side*9]),
                   c(boot-2,0,-4,5,2,7,"metal"),c(boot,0,-4.5,2,1,3,"rust"),parent="leg_"+tag)

    if cleaver:
        yield bone("cleaver",[8,11,-2],c(8,7,-3,3,7,3,"dark"),
                   c(9,0,-4,7,10,3,"rust",[0,0,22]),c(12,1,-5,3,11,2,"metal",[0,0,22]),
                   c(9,7,-5,4,3,2,"metal"),c(9,2,-5,3,2,2,"metal"),
                   c(8,9,-5,2,4,1,"glow"),parent="forearm_r")
    elif regent:
        yield bone("staff",[9,23,-9],c(9,2,-9,2,38,2,"dark"),
                   *(c(8,k,-10,4,2,4,"metal") for k in (3,13,30,36)),
                   c(4,36,-10,2,7,4,"metal",[0,0,-28]),
                   c(14,36,-10,2,7,4,"metal",[0,0,28]),
                   c(7,42,-10,6,2,4,"rust"),c(8,38,-11,4,4,4,"glow"),
                   parent="grip")
    else:
        yield bone("counterweight",[7,11,-2],c(8,4,-3,1,9,1,"rust"),
                   c(6,0,-5,6,6,5,"metal",[0,0,11]),c(7,2,-6,4,2,1,"glow"),
                   parent="forearm_r")
        for tag,start in (("l",105),("r",-50)):
            plates = []
            for angle in range(start,start+121,24):
                t = math.radians(angle)
                x,y = round(14*math.cos(t)),round(29+14*math.sin(t))
                plates += [c(x-3,y-2,7,6,4,4,"metal",[0,0,angle+90]),
                           c(x-2,y-1,6,4,2,2,"glow",[0,0,angle+90])]
            yield bone("relay_"+tag,[0,29,7],*plates)
        yield bone("hood_tail",[-3,36,2],c(-6,25,3,3,14,1,"cloth",[20,0,-12]),
                   c(-5,22,5,2,11,1,"moss",[23,0,14]),parent="head")
    top = shoulder - (3 if cleaver else 1)
    yield bone("drape",[0,top,3],
               c(-7,top-(13 if cleaver else 23),3,6,13 if cleaver else 23,2,"cloth",[17,0,-14]),
               c(1,4 if regent else 9,4,5,top-(4 if regent else 9),1,"cloth",[12,0,12]),
               c(-5,5 if regent else 12,6,2,15,1,"cloth",[20,0,9]),
               c(3,top-12,5,2,11,1,"moss",[23,0,-11]))


def texture_and_geometry(spec):
    rng = random.Random(spec["id"])
    atlas = Image.new("RGBA", (SIZE, SIZE))
    x = y = row = 0
    bones = [{"name": "root", "pivot": [0, 0, 0]}]
    colors = dict(zip(("metal", "rust", "glow", "cloth", "dark"), spec["palette"]))
    colors["moss"] = "#536c42"
    for name, parent, pivot, cubes in spec["rig"]:
        mesh = []
        for origin, size, material, rotation in cubes:
            w, h, d = size
            width, height = 2*(w+d), h+d
            if x + width > SIZE:
                x, y, row = 0, y + row, 0
            assert y + height <= SIZE, spec["id"]
            base = tuple(bytes.fromhex(colors[material][1:]))
            for dy in range(height):
                for dx in range(width):
                    borders = (0, d, d+w, 2*d+w)
                    local_x = dx - max(boundary for boundary in borders if boundary <= dx)
                    local_y = dy if dy < d else dy-d
                    edge = dx in borders or dy in (0,d)
                    shade = rng.choice((-5,-3,-1,0,2,3,5))
                    tint = base
                    if material == "glow":
                        shade = -40 if edge else 22 if local_y % 4 == 1 else 4
                    elif material in ("metal","rust","dark"):
                        shade += 16 if edge else -16 if local_y % 9 == 7 else 0
                        if local_x % 9 == 2 and local_y % 9 in (2,3):
                            shade -= 30
                        if (local_x * 7 + local_y * 3 + x) % 31 < 4 and material != "dark":
                            tint = (128,74,42)
                    else:
                        shade += (8 if local_x % 3 == 0 else -4) - (9 if local_y % 5 == 0 else 0)
                        if material == "cloth" and local_y > h-4 and local_x % 5 < 2:
                            shade -= 37
                    atlas.putpixel((x+dx,y+dy),tuple(max(0,min(255,k+shade)) for k in tint)+(255,))
            piece = dict(origin=origin, size=size, uv=[x, y])
            if rotation:
                piece.update(rotation=rotation, pivot=[origin[i]+size[i]/2 for i in range(3)])
            mesh.append(piece)
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
        for side,phase in (("l",0),("r",180)):
            walk["arm_"+side] = {"rotation":[f"math.sin(query.anim_time * 281 + {phase}) * 15",0,0]}
            walk["leg_"+side] = {"rotation":[f"math.sin(query.anim_time * 281 + {180-phase}) * 13",0,0]}
        walk["body"]["rotation"] = [0,0,"math.sin(query.anim_time * 281) * 3"]
    if sector == "echo_hush_pendulum":
        walk["counterweight"] = {"rotation":["math.sin(query.anim_time * 409) * 46",0,12]}
        walk["head"] = {"rotation":["math.sin(query.anim_time * 818) * 8",-13,17]}
    for side,sign in (("l",1),("r",-1)):
        if "relay_"+side in rig:
            idle["relay_"+side] = {"rotation":[0,sign*9,"math.sin(query.anim_time * 150) * 4"]}
        if "brace_"+side in rig:
            walk["brace_"+side] = {"rotation":[f"math.sin(query.anim_time * 281) * {17*sign}",0,0]}
    if "forearm_l" in rig:
        for side,phase in (("l",0),("r",180)):
            walk["shin_"+side] = {"rotation":[f"math.max(0, math.sin(query.anim_time * {360/gait} + {phase})) * 26",0,0]}
            walk["forearm_"+side] = {"rotation":[f"math.sin(query.anim_time * {360/gait} + {phase}) * 9",0,0]}
        if "staff" in rig:
            walk["arm_r"] = {"rotation":[-5,0,-6]}
            walk["forearm_r"] = {"rotation":[4,0,4]}
    animations = {"idle":dict(loop=True, animation_length=2.4,bones=idle),
                  "walk":dict(loop=True, animation_length=gait,bones=walk)}
    for idx, (move, poses) in enumerate(spec["moves"]):
        impact, end = move["windup"]/20, move["end"]/20
        keys = {}
        if "forearm_l" in rig:
            wrist = {
                "echo_seam_riven": ([34,0,0],[-21,0,0],[9,0,0]),
                "echo_veil_regent": ([52,0,-14],[-15,0,8],[22,0,0]),
                "echo_hush_pendulum": ([19,0,-15],[-28,0,12],[11,0,0]),
            }[sector]
            poses = {**poses,"forearm_r":wrist}
        for name, (coil, strike, recoil) in poses.items():
            assert name in rig, name
            keys[name] = {"rotation":{
                "0.0":[0,0,0], str(round(impact*.42,3)):[round(n*.58,2) for n in coil],
                str(round(impact-.12,3)):list(coil), str(impact):list(strike),
                str(round(impact+.24,3)):list(recoil), str(end):[0,0,0]}}
        # Add a short original follow-through; reference density controls its spacing.
        settle = min(.27, max(.09, 2 / spec["pose_density"]))
        for channel in keys.values():
            rotation = channel["rotation"]
            recoil = rotation[str(round(impact+.24,3))]
            rotation[str(round(impact+.24+settle,3))] = [round(n*.42,2) for n in recoil]
        animations[f"attack{idx}"] = dict(animation_length=end, loop="hold_on_last_frame", bones=keys)
    animations["death"] = dict(animation_length=1, loop="hold_on_last_frame", bones={
        "root":{"rotation":{"0.0":[0,0,0],"0.2":[-7,0,11],"1.0":[0,0,62 if echo else -17]},
                "position":{"0.0":[0,0,0],"1.0":[0,-7 if echo else -4,0]}}})
    return {f"animation.bearframe.{sector}.{name}":value for name,value in animations.items()}


def palinode_ram_rig():
    """A low rail-clearance machine built around an exposed reciprocating ram."""
    c = cube
    yield chassis(c(-3,10,-11,6,5,25,"dark"), c(-8,13,1,16,4,16,"metal"),
                  c(-7,17,6,14,4,11,"metal"), c(-5,20,10,9,2,6,"moss"),
                  c(-7,15,-9,3,4,12,"metal"), c(4,15,-9,3,4,12,"metal"))
    yield bone("head", [-6,17,-5], c(-9,17,-9,6,4,6,"metal"),
               c(-8,18,-10,4,2,2,"dark"), c(-7,18,-11,2,1,1,"glow"),
               c(-9,21,-7,4,1,3,"moss"))
    yield bone("ram", [0,12,-4], c(-2,9,-18,4,5,21,"dark"),
               c(-4,9,-21,8,7,8,"metal"), c(-9,6,-25,18,3,7,"metal",[22,0,0]),
               c(-10,7,-24,4,5,6,"rust",[0,-17,0]),
               c(6,7,-24,4,5,6,"rust",[0,17,0]), c(-5,12,-22,10,1,2,"glow"))
    for index, z in enumerate((-10, 0, 12)):
        for side, tag in ((-1,"l"),(1,"r")):
            suffix = f"{index}_{tag}"
            hip = (6 + (index == 2)) * side
            reach = (15 + (index == 1) * 3) * side
            left = min(hip,reach)
            yield bone("leg_"+suffix, [hip,14,z],
                       c(left,12,z-2,abs(hip-reach),4,4,"dark",[0,side*(index-1)*18,0]),
                       c(reach-3,10,z-3,6,6,6,"metal"),
                       c(reach-2,16,z-1,3,1,3,"moss"))
            broken = index == 1 and side == -1
            yield bone("foot_"+suffix, [reach,11,z],
                       c(reach-2,2,z-2,4,10,4,"rust" if broken else "metal",[0,0,side*-23]),
                       c(reach-3,0,z-4,6,3,8,"dark"),
                       c(reach-2,1,z-5,4,2,4,"metal"), parent="leg_"+suffix)


def build(spec):
    name = spec["id"]
    identifier = "bearframe:" + name
    atlas, bones = texture_and_geometry(spec)
    atlas.save(RP / f"textures/bearframe/{name}.png")
    geom = f"geometry.bearframe.{name}"
    write(RP / f"models/entity/{name}.geo.json", {"format_version":"1.12.0", "minecraft:geometry":[{
        "description":{"identifier":geom,"texture_width":atlas.width,"texture_height":atlas.height,
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-jar", type=Path, help="Local Mowzie's Mobs Java JAR")
    args = parser.parse_args()
    profile = motion_profile(args.reference_jar) if args.reference_jar else None
    density = profile["poses_per_second"] if profile else 12
    if profile:
        print(f"Reference: {profile['clips']} clips, median {density} distinct keyframe times/second")
    for spec in bosses:
        spec["pose_density"] = density
        machine_rigs = {"grid_palinode": palinode_ram_rig, "grid_silt_engine": silt_rig,
                        "grid_gantry_marrow": gantry_rig, "grid_cinder_spindle": cinder_rig}
        if spec["id"] in machine_rigs:
            spec["rig"] = list(machine_rigs[spec["id"]]())
            spec["palette"] = ["#b9b7a1","#925d37","#54d8f0","#5b7135","#282d30"]
        else:
            spec["rig"] = list(rook_rig() if spec["id"] == "echo_rubble_rook" else tall_echo_rig(spec["id"]))
            glow = {"echo_seam_riven":"#49d6e3","echo_veil_regent":"#ce73fa",
                    "echo_rubble_rook":"#ae5df0","echo_hush_pendulum":"#f47755"}[spec["id"]]
            spec["palette"] = ["#bdb4a9","#865c40",glow,"#65404e","#2b272b"]
            spec["color"] = glow
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
