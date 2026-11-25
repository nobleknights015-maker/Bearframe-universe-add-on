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


import zipfile,io
zip_path=Path('deliverables/Bearframe_Bedrock_0.4.9.mcaddon')
groups=[
    ('Bearframe Labs', '#7dd7ce', 'city_steward city_engineer city_watch atlas_rigger atlas_vanguard farfield_surveyor field_researcher vera_artisan'),
    ('Nullframe Directorate', '#ef7778', 'directorate_guard directorate_officer nullframe_hunter hollow_line hollow_scout hollow_breacher'),
    ('Echo Frames', '#bf9be1', 'echo_drifter echo_sentinel ward_resident'),
    ('Ghost Grid', '#94c2a3', 'grid_guardian grid_protocol_keeper grid_hauler grid_turret grid_repair_crawler grid_walker grid_watcher'),
]
sheet=Image.new('RGB',(1610,2800),'#141b20')
draw=ImageDraw.Draw(sheet)
draw.text((34,22),'Bearframe Bedrock 0.4.9',font=ImageFont.truetype(font+'-Bold.ttf',55),fill='#ecf3f4')
draw.text((36,93),'24 ENTITY MODELS   /   FRONT AND REAR   /   VIEWS SCALED TO FIT',font=ImageFont.truetype(font+'.ttf',22),fill='#aec4c8')
top=145
with zipfile.ZipFile(zip_path) as z:
    lang=z.read('Bearframe_Resources/texts/en_US.lang').decode()
    labels=dict(line.split('=',1) for line in lang.splitlines() if '=' in line)
    for group,accent,keys in groups:
        keys=keys.split()
        draw.text((36,top),group,font=ImageFont.truetype(font+'-Bold.ttf',31),fill=accent)
        top+=49
        for i,key in enumerate(keys):
            x=32+(i%4)*389
            y=top+(i//4)*338
            draw.rounded_rectangle((x,y,x+379,y+325),radius=12,fill='#243038',outline='#415156',width=2)
            label=labels[f'entity.bearframe:{key}.name']
            title=ImageFont.truetype(font+'-Bold.ttf',20)
            draw.text((x+13,y+12),label,font=title,fill='#e7eff0')
            path='Bearframe_Resources/'
            geometry=json.loads(z.read(path+'models/entity/'+key+'.geo.json'))['minecraft:geometry'][0]
            cubes=[cube for b in geometry['bones'] for cube in b.get('cubes',[])]
            atlas=np.array(Image.open(io.BytesIO(z.read(path+'textures/bearframe/'+key+'.png'))).convert('RGBA'))
            for j,yaw in enumerate((30,214)):
                pic=render(cubes,atlas,yaw)
                pic=pic.crop(pic.getbbox())
                pic.thumbnail((175,242),Image.Resampling.LANCZOS)
                px=x+96+j*187-pic.width//2
                py=y+155-pic.height//2
                sheet.paste(pic,(px,py),pic)
                draw.text((x+96+j*187,y+285),'FRONT' if j==0 else 'REAR',anchor='mt',font=ImageFont.truetype(font+'.ttf',16),fill='#b2c5c6')
        top+=((len(keys)+3)//4)*338+12
sheet=sheet.crop((0,0,sheet.width,top))
sheet.save('deliverables/Bearframe_0.4.9_Model_Preview.png')
sheet.thumbnail((800,1300))
sheet.save('classic_contact.png')
