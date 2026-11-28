"""Offline orthographic renders of the converted UV-mapped Bedrock cuboids."""
import io
import json
import sys
from zipfile import ZipFile
import numpy as np
from PIL import Image, ImageDraw

root = "Bearframe_Resources/"
with ZipFile(sys.argv[1]) as pack:
    atlas = Image.open(io.BytesIO(pack.read(root+"textures/bearframe/held/field_cutter.png")))
    geo = json.loads(pack.read(root+"models/entity/held_field_cutter.geo.json"))
    cubes = geo["minecraft:geometry"][0]["bones"][1]["cubes"]

faces = {
    "north":((1,1,0),(0,1,0),(1,0,0)), "south":((0,1,1),(1,1,1),(0,0,1)),
    "west":((0,1,0),(0,1,1),(0,0,0)), "east":((1,1,1),(1,1,0),(1,0,1)),
    "up":((0,1,0),(1,1,0),(0,1,1)), "down":((0,0,1),(1,0,1),(0,0,0)),
}
normals = [(0,0,-1),(0,0,1),(-1,0,0),(1,0,0),(0,1,0),(0,-1,0)]
sheet=Image.new("RGB",(1120,400),"#142126")
draw=ImageDraw.Draw(sheet)
for col,(label,direction) in enumerate([
    ("FRONT",(0,0,1)),("SIDE",(1,0,0)),("THREE-QUARTER",(0.55,0.4,1)),
    ("GRIP STUDY",(0.7,-0.3,1))
]):
    camera=np.array(direction,dtype=float)
    camera/=np.linalg.norm(camera)
    right=np.cross([0,1,0],camera)
    right/=np.linalg.norm(right)
    up=np.cross(camera,right)
    angle=np.deg2rad(-33 if col==3 else 0)
    pose=np.array([[np.cos(angle),-np.sin(angle),0],[np.sin(angle),np.cos(angle),0],[0,0,1]])
    center=np.array([140+col*280,245])
    def project(p):
        p=pose@p
        return tuple(center+11*np.array([right@p,-up@p]))
    tiles=[]
    for cube in cubes:
        origin=np.array(cube["origin"])
        size=np.array(cube["size"])
        for (face,corners),normal in zip(faces.items(),normals):
            if camera@(pose@normal)<=1e-6:
                continue
            start,end,down=origin+size*np.array(corners)
            hori,vert=end-start,down-start
            u,v=cube["uv"][face]["uv"]
            du,dv=cube["uv"][face]["uv_size"]
            shade=0.77+0.22*max(0,np.array([.4,.75,.45])@(pose@normal))
            for y in range(abs(dv)):
                for x in range(abs(du)):
                    color=atlas.getpixel((u+x if du>0 else u-x-1,v+y if dv>0 else v-y-1))
                    if not color[3]:
                        continue
                    a=start+hori*x/abs(du)+vert*y/abs(dv)
                    b=hori/abs(du)
                    c=vert/abs(dv)
                    tiles.append((camera@(pose@(a+(b+c)/2)),[project(p) for p in (a,a+b,a+b+c,a+c)],tuple(round(k*shade) for k in color[:3])))
    for _,points,color in sorted(tiles,key=lambda item:item[0]):
        draw.polygon(points,fill=color)
    if col==3:
        x,y=project(np.zeros(3))
        draw.ellipse((x-8,y-8,x+8,y+8),outline="#ffcd83",width=2)
        draw.text((x+14,y+8),"Grip pivot",fill="#ffcd83")
    draw.text((col*280+22,350),label,fill="#e4eeed")
    if col:
        draw.line((col*280,55,col*280,360),fill="#334750")
draw.text((22,19),"FIELD CUTTER  /  0.11.46  /  OFFLINE MODEL RENDER",fill="#e4eeed")
sheet.save(sys.argv[2])
