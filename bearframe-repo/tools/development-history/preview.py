from pathlib import Path
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

root = Path('pack/Bearframe_Resources')
units = [
    ('guardian', 'Legacy Sector Guardian'),
    ('protocol_keeper', 'Grid Protocol Keeper'),
    ('hauler', 'Grid Industrial Hauler'),
    ('turret', 'Grid Defense Turret'),
    ('repair_crawler', 'Grid Repair Crawler'),
    ('walker', 'Legacy Hexapod Walker'),
    ('watcher', 'Grid Watcher Drone'),
]
font = '/usr/share/fonts/truetype/dejavu/DejaVuSans'
def render(cubes, atlas, yaw):
    theta = np.radians(yaw)
    pitch = np.radians(19)
    horizontal = np.array([np.cos(theta), 0, np.sin(theta)])
    toward = np.array([np.sin(theta)*np.cos(pitch),np.sin(pitch),-np.cos(theta)*np.cos(pitch)])
    vertical = np.cross(horizontal,toward)
    matrix = np.stack((horizontal,-vertical,toward))
    polygons = []
    for cube in cubes:
        lo = np.array(cube['origin'])
        hi = lo + cube['size']
        x,y,z = lo
        X,Y,Z = hi
        for name, points, normal, light in (
            ('north', [(x,Y,z),(X,Y,z),(x,y,z)],(0,0,-1),1),
            ('south', [(X,Y,Z),(x,Y,Z),(X,y,Z)],(0,0,1),.91),
            ('east', [(X,Y,z),(X,Y,Z),(X,y,z)],(1,0,0),.79),
            ('west', [(x,Y,Z),(x,Y,z),(x,y,Z)],(-1,0,0),.79),
            ('up', [(x,Y,Z),(X,Y,Z),(x,Y,z)],(0,1,0),1.12),
        ):
            if np.dot(toward,normal) > 1e-6:
                p,q,r = np.array(points) @ matrix.T
                polygons.append((p,q,r,cube['uv'][name],light))
    corners = np.array([v for p,q,r,_,_ in polygons for v in (p,q,r,q+r-p)])
    size=236
    scale = min(11, (size-18)/max(np.ptp(corners[:,0]),np.ptp(corners[:,1])))
    center = (corners[:,:2].max(axis=0)+corners[:,:2].min(axis=0))/2
    depth = np.full((size,size),-np.inf)
    rgba = np.zeros((size,size,4),dtype=np.uint8)
    for p,q,r,uv,light in polygons:
        o,a,b=(np.array([p,q,r])[:,:2]-center)*scale+size/2
        coords = np.array((o,a,b,a+b-o))
        left,top = np.maximum(0,np.floor(coords.min(axis=0)).astype(int))
        right,bottom = np.minimum(size,np.ceil(coords.max(axis=0)).astype(int))
        if right<=left or bottom<=top:
            continue
        py,px = np.mgrid[top:bottom,left:right]
        inverse = np.linalg.inv(np.column_stack((a-o,b-o)))
        u,v = inverse @ np.stack((px.ravel()+.5-o[0],py.ravel()+.5-o[1]))
        py,px = py.ravel(),px.ravel()
        d = p[2]+u*(q[2]-p[2])+v*(r[2]-p[2])
        mask = (u>=0)&(v>=0)&(u<1)&(v<1)&(d>depth[py,px])
        py,px = py[mask],px[mask]
        tx,ty=uv['uv']
        w,h=uv['uv_size']
        pixels=atlas[ty+(v[mask]*h).astype(int),tx+(u[mask]*w).astype(int)].copy()
        pixels[:,:3] = np.clip(pixels[:,:3]*light,0,255).astype(np.uint8)
        rgba[py,px] = pixels
        depth[py,px] = d[mask]
    return Image.fromarray(rgba)

sheet=Image.new('RGB',(1056,1234),'#121a1b')
draw=ImageDraw.Draw(sheet)
draw.text((30,24),'Ghost Grid',font=ImageFont.truetype(font+'-Bold.ttf',43),fill='#e4edec')
draw.text((32,82),'BEARFRAME BEDROCK 0.4.5  /  PACKAGED MODELS',font=ImageFont.truetype(font+'.ttf',20),fill='#8ac5c6')
for i,(key,label) in enumerate(units):
    left=26+(i%2)*506
    top=122+(i//2)*274
    draw.rounded_rectangle((left,top,left+498,top+264),radius=13,fill='#263133',outline='#3c5354',width=2)
    draw.text((left+16,top+12),label,font=ImageFont.truetype(font+'-Bold.ttf',22),fill='#e4edec')
    ident='grid_'+key
    geometry=json.loads((root/'models/entity'/f'{ident}.geo.json').read_text())['minecraft:geometry'][0]
    cubes=[cube for bone in geometry['bones'] for cube in bone.get('cubes',[])]
    assert all('rotation' not in cube for cube in cubes)
    atlas=np.array(Image.open(root/'textures/bearframe'/f'{ident}.png').convert('RGBA'))
    for j,yaw in enumerate((31,210)):
        pic=render(cubes,atlas,yaw)
        pic.thumbnail((216,216),Image.Resampling.LANCZOS)
        sheet.paste(pic,(left+17+j*249,top+34),pic)
        draw.text((left+125+j*249,top+244),'FRONT' if j==0 else 'REAR',anchor='mt',font=ImageFont.truetype(font+'.ttf',13),fill='#a6bbbb')
sheet.save('/mnt/data/Bearframe_0.4.5_Ghost_Grid_Preview.png')
