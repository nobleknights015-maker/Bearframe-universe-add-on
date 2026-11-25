from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image, ImageDraw
from io import BytesIO
from math import ceil
from random import Random
import json

folder = Path('deliverables')
source = folder/'Bearframe_Bedrock_0.4.8.mcaddon'
prefix = 'Bearframe_Resources/'
styles = {
    'echo_drifter': ((67,55,79),(104,80,121), 'echo', 'long'),
    'echo_sentinel': ((38,69,65),(69,115,102), 'echo', 'mantle'),
    'ward_resident': ((85,69,51),(131,107,73), 'echo', 'short'),
    'farfield_surveyor': ((45,91,79),(100,155,135), 'farfield', 'scarf'),
    'field_researcher': ((67,72,109),(126,139,181), 'farfield', 'poncho'),
}
def encode(data):
    return (json.dumps(data, indent=2)+'\n').encode()

class Cloth:
    def __init__(self,key,geo,atlas,main,trim,weathered):
        self.bones={b['name']:b for b in geo['bones']}
        self.atlas=atlas
        self.main=main
        self.trim=trim
        self.weathered=weathered
        self.rng=Random(key)
        self.cache={}
        self.x=0
        self.y=2+max(f['uv'][1]+f['uv_size'][1] for b in geo['bones'] for c in b.get('cubes',[]) for f in c['uv'].values())
        self.row=0

    def tile(self,w,h,style):
        key=(w,h,style)
        if key in self.cache:
            return self.cache[key]
        if self.x+w+2>256:
            self.x=0
            self.y+=self.row
            self.row=0
        assert self.y+h+2<=256
        tile=Image.new('RGBA',(w,h))
        for y in range(h):
            for x in range(w):
                color=self.trim if style=='binding' or (style=='hem' and y>=h-2) else self.main
                fold=([6,2,-9,-5,0,3][x*6//w])
                shift=fold+((-12) if y==h-1 else 0)+self.rng.randint(-5,5)
                if self.weathered and self.rng.randrange(9)==0:
                    shift-=14
                tile.putpixel((x,y),tuple(max(0,min(255,c+shift)) for c in color)+(255,))
        if style=='hem' and w>=5 and h>=5:
            pen=ImageDraw.Draw(tile)
            for x in range(1,w,3):
                pen.point((x,h-3),fill=tuple(min(255,c+20) for c in self.trim)+(255,))
        for y in range(-1,h+1):
            for x in range(-1,w+1):
                self.atlas.putpixel((self.x+x+1,self.y+y+1),tile.getpixel((min(w-1,max(0,x)),min(h-1,max(0,y)))))
        uv={'uv':[self.x+1,self.y+1],'uv_size':[w,h]}
        self.cache[key]=uv
        self.x+=w+2
        self.row=max(self.row,h+2)
        return uv

    def add(self,bone,x,y,z,w,h,d,style='fold'):
        uv={}
        for name,a,b in [('north',w,h),('south',w,h),('west',d,h),('east',d,h),('up',w,d),('down',w,d)]:
            uv[name]=self.tile(max(2,ceil(a*2)),max(2,ceil(b*2)),style if name not in ('up','down') else 'fold')
        self.bones[bone].setdefault('cubes',[]).append(dict(origin=[x,y,z],size=[w,h,d],uv=uv))

def hood(c,look):
    a=c.add
    a('head',-4.48,31.55,-4.62,8.96,1.49,9.03)
    a('head',-3.95,32.9,-3.93,7.9,.49,8.03)
    a('head',-4.21,30.22,-4.6,8.42,1.52,.62,'binding')
    a('head',-4.56,24.07,-3.64,.98,7.88,7.8)
    a('head',3.59,25.07,-3.48,.98,6.9,7.68)
    a('head',-4.08,24.56,3.91,8.16,7.58,.78,'hem')
    # The front stays open around the frame's optics.
    a('head',-4.45,25.2,-4.52,1.03,5.68,1.15)
    a('head',3.38,26.1,-4.52,1.07,4.91,1.24)
    a('head',-4.27 if look!='mantle' else 3.52,23.93,-3.92,.74,2.3,.71,'hem')

def poncho(c,look):
    a=c.add
    a('body',-3.88,21.81,-2.16,7.76,2.15,4.38)
    a('body',-3.79,18.35,1.98,7.58,4.46,.88)
    a('body',-3.92,17.25,-2.83,1.86,5.31,.84)
    a('body',2.24,19.12,-2.86,1.45,3.44,.87)
    for arm,x in (('arm0',-7.75),('arm1',4.0)):
        a(arm,x,22.81,-2.71,3.69,1.31,5.09)
        a(arm,x+.27,19.86,-2.81,3.17,3.14,.62,'hem')
        a(arm,x+.37,20.21,2.10,3.0,2.91,.67,'hem')
    if look=='mantle':
        strips=[(-3.8,12.6,2.1,6.5),(-1.73,13.6,2.28,5.55),(.53,14.35,1.69,4.68),(2.2,15.7,1.58,3.32)]
    elif look=='short':
        strips=[(-3.82,16.0,2.45,3.2),(-1.4,14.7,2.15,4.48),(.7,15.0,1.42,4.25),(2.1,16.9,1.67,2.32)]
    else:
        strips=[(-3.82,15.0,2.0,4.2),(-1.85,13.35,2.73,5.84),(.85,15.0,2.89,4.15)]
    for x,y,w,h in strips:
        a('body',x,y,2.59,w,h,.59,'hem')
    if look!='poncho':
        cutoff={'short':14.1,'mantle':12.8,'long':11.55}[look]
        a('body',-3.7,cutoff,-2.87,1.65,18.6-cutoff,.76,'hem')
        a('body',-2.1,cutoff+1.5,-2.72,.77,3.55,.69,'hem')
    else:
        a('body',2.38,15.17,-3.12,1.48,5.12,.81,'hem')
        a('body',-3.8,15.95,-3.07,1.35,4.43,.78,'hem')
        a('body',-3.77,14.45,2.88,1.64,5.55,.64,'hem')
        a('body',2.20,15.55,2.88,1.54,4.45,.64,'hem')

def scarf(c):
    a=c.add
    a('body',-3.82,22.71,-2.77,7.64,1.2,5.45)
    a('body',-3.64,22.22,-3.06,7.02,.78,1.08,'binding')
    a('body',2.35,21.12,1.39,1.71,2.0,1.37)
    a('body',2.25,17.4,2.72,1.52,4.45,.54,'hem')
    a('body',1.22,19.17,3.02,1.11,2.62,.49,'hem')
    a('body',-3.65,17.56,-3.22,1.16,5.15,.54,'hem')
    a('body',-2.71,20.41,-3.35,1.14,2.42,.48,'hem')

classic=Path('source/Bearframe_Bedrock_0.4.4.mcaddon')
output=folder/'Bearframe_Bedrock_0.4.9.mcaddon'
updates={}
with ZipFile(classic) as origin, ZipFile(source) as current:
    for path in origin.namelist():
        if not path.startswith(prefix+'models/entity/') or not path.endswith('.geo.json'):
            continue
        key=Path(path).name.removesuffix('.geo.json')
        if key.startswith('grid_'):
            continue
        tex=prefix+'textures/bearframe/'+key+'.png'
        model,texture=origin.read(path),origin.read(tex)
        if key in styles:
            main,trim,group,look=styles[key]
            data=json.loads(model)
            geo=data['minecraft:geometry'][0]
            pictured=Image.open(BytesIO(texture)).convert('RGBA')
            assert pictured.size==(256,128)
            atlas=Image.new('RGBA',(256,256))
            atlas.paste(pictured,(0,0))
            cloth=Cloth(key,geo,atlas,main,trim,group=='echo')
            cloth.y=130
            geo['description']['texture_height']=256
            if group=='echo':
                hood(cloth,look)
            if look=='scarf':
                scarf(cloth)
            else:
                poncho(cloth,look)
            for bone in geo['bones']:
                for cube in bone.get('cubes',[]):
                    for face in cube['uv'].values():
                        x,y=face['uv']
                        w,h=face['uv_size']
                        assert 0<=x and x+w<=256 and 0<=y and y+h<=256
            buffer=BytesIO()
            atlas.save(buffer,'PNG')
            model,texture=encode(data),buffer.getvalue()
            assert atlas.crop((0,0,256,128)).tobytes()==pictured.tobytes()
        updates[path]=model
        updates[tex]=texture
    for pack in ('Bearframe_Behavior','Bearframe_Resources'):
        path=pack+'/manifest.json'
        data=json.loads(current.read(path))
        for entry in [data['header'],*data['modules'],*data.get('dependencies',[])]:
            if entry.get('version')==[0,4,8]:
                entry['version']=[0,4,9]
        updates[path]=encode(data)
    assert len(updates)==36
    with ZipFile(output,'w',ZIP_DEFLATED) as release:
        for name in current.namelist():
            release.writestr(name,updates[name] if name in updates else current.read(name))
    with ZipFile(output) as release:
        assert release.testzip() is None
        assert len(release.namelist())==237
        assert {name for name in release.namelist() if release.read(name)!=current.read(name)}==updates.keys()
        for path in updates:
            if '/models/entity/' not in path:
                continue
            key=Path(path).name.removesuffix('.geo.json')
            geo=json.loads(release.read(path))['minecraft:geometry'][0]
            old_geo=json.loads(origin.read(path))['minecraft:geometry'][0]
            for b,old in zip(geo['bones'],old_geo['bones'],strict=True):
                assert {k:v for k,v in b.items() if k!='cubes'}=={k:v for k,v in old.items() if k!='cubes'}
                count=len(old.get('cubes',[]))
                assert b.get('cubes',[])[:count]==old.get('cubes',[])
print('Verified original armor cubes and UVs for 17 humanoids, with five clothing overlays.')
