"""Render actual packaged held geometry and mapped textures into a contact sheet."""
import io
import json
import math
import sys
from zipfile import ZipFile

import numpy as np
from PIL import Image,ImageDraw,ImageFont

from finish_arsenal import ATLAS,MODELS,ROOT

faces={
    "north":((1,1,0),(0,1,0),(1,0,0)), "south":((0,1,1),(1,1,1),(0,0,1)),
    "west":((0,1,0),(0,1,1),(0,0,0)), "east":((1,1,1),(1,1,0),(1,0,1)),
    "up":((0,1,0),(1,1,0),(0,1,1)), "down":((0,0,1),(1,0,1),(0,0,0)),
}
normals=[(0,0,-1),(0,0,1),(-1,0,0),(1,0,0),(0,1,0),(0,-1,0)]


def render(pack,item,draw,cx,cy):
    atlas=Image.open(io.BytesIO(pack.read(ATLAS+item+".png")))
    model=json.loads(pack.read(MODELS+item+".geo.json"))["minecraft:geometry"][0]
    camera=np.array([.92,.17,.32] if item!="field_cutter" else [.3,.17,.92])
    camera/=np.linalg.norm(camera)
    right=np.cross([0,1,0],camera)
    right/=np.linalg.norm(right)
    up=np.cross(camera,right)
    turn=math.radians(-24)
    screen_x=right*math.cos(turn)-up*math.sin(turn)
    screen_y=right*math.sin(turn)+up*math.cos(turn)
    center=np.array([0,13 if not item.startswith("cyber_katana") else 15,0.5])
    scale=7 if item.startswith("cyber_katana") else 8
    def project(p):
        q=p-center
        return cx+scale*(screen_x@q),cy-scale*(screen_y@q)
    tiles=[]
    for bone in model["bones"]:
        for cube in bone.get("cubes",[]):
            origin,size=np.array(cube["origin"]),np.array(cube["size"])
            pivot=np.array(cube.get("pivot",bone.get("pivot",[0,0,0])))
            rotation=np.eye(3)
            for axis,angle in enumerate(cube.get("rotation",[0,0,0])):
                a,b=(axis+1)%3,(axis+2)%3
                matrix=np.eye(3)
                c,s=math.cos(math.radians(angle)),math.sin(math.radians(angle))
                matrix[a,a]=matrix[b,b]=c
                matrix[a,b],matrix[b,a]=-s,s
                rotation=matrix@rotation
            for (face,corners),normal in zip(faces.items(),normals):
                direction=rotation@normal
                if direction@camera<=0:
                    continue
                start,end,lower=[pivot+rotation@(point-pivot) for point in origin+size*np.array(corners)]
                if face not in cube["uv"]:
                    continue
                u,v=cube["uv"][face]["uv"]
                du,dv=cube["uv"][face]["uv_size"]
                u,v,du,dv=map(int,(u,v,du,dv))
                if du==0 or dv==0:
                    continue
                horiz,vert=(end-start)/abs(du),(lower-start)/abs(dv)
                shade=.72+.28*max(0,direction@np.array([.54,.75,.45]))
                for y in range(abs(dv)):
                    for x in range(abs(du)):
                        rgba=atlas.getpixel((u+x if du>0 else u-x-1,v+y if dv>0 else v-y-1))
                        if not rgba[3]:
                            continue
                        p=start+x*horiz+y*vert
                        points=[project(q) for q in (p,p+horiz,p+horiz+vert,p+vert)]
                        depth=camera@(p+(horiz+vert)*.5)
                        tiles.append((depth,points,tuple(round(value*shade) for value in rgba[:3])))
    for _,points,color in sorted(tiles,key=lambda tile:tile[0]):
        draw.polygon(points,fill=color)


