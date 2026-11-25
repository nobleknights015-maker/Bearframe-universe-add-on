from pathlib import Path
from random import Random
from math import ceil, cos, sin, radians
import json, zipfile
from PIL import Image, ImageDraw

rp = Path('pack/Bearframe_Resources')
bp = Path('pack/Bearframe_Behavior')
def load(path):
    return json.loads(path.read_text())
def save(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')

palette = {
    'plate': (137,133,116), 'edge': (178,171,148), 'frame': (61,62,55),
    'rubber': (40,42,40), 'rust': (152,100,52), 'hazard': (176,128,55),
    'cloth': (69,90,99), 'moss': (81,94,39), 'leaf': (111,124,49),
    'dark': (25,37,38), 'cyan': (62,198,211), 'lens': (21,44,49),
    'slit': (22,43,47), 'vent': (49,50,46), 'badge': (70,86,88)
}
faces = dict(north=(0,1),south=(0,1),east=(2,1),west=(2,1),up=(0,2),down=(0,2))

class Model:
    def __init__(self, name):
        self.name = 'grid_' + name
        self.path = rp / 'models/entity' / (self.name + '.geo.json')
        self.data = load(self.path)
        self.geo = self.data['minecraft:geometry'][0]
        self.geo['bones'] = []
        self.bones = {}
        self.atlas = Image.new('RGBA',(256,256))
        self.cache = {}
        self.x = self.y = self.row = 0
        self.rng = Random(name)
        self.bone('root', None, (0,0,0))

    def bone(self, name, parent, pivot):
        b = dict(name=name,pivot=pivot)
        if parent:
            b['parent'] = parent
        self.geo['bones'].append(b)
        self.bones[name] = b

    def tile(self, material, w, h):
        key = (material,w,h)
        if key in self.cache:
            return self.cache[key]
        if self.x + w + 2 > 256:
            self.x = 0
            self.y += self.row
            self.row = 0
        assert self.y+h+2 <= 256, (self.name, key)
        tex = Image.new('RGBA',(w,h))
        base = palette[material]
        for y in range(h):
            for x in range(w):
                shift = self.rng.choice((-16,-9,-4,0,0,4,8,15))
                color = base
                border = min(x,y,w-x-1,h-y-1)
                if material in ('plate','edge','frame','cloth'):
                    if border == 0:
                        shift += 17 if x == 0 or y == 0 else -23
                    if material in ('plate','edge') and self.rng.randrange(12) < (3 if border <= 1 else 1):
                        color = self.rng.choice(((126,79,45),(101,79,57),(85,85,76)))
                    if w >= 6 and h >= 5 and x in (1,w-2) and y in (1,h-2):
                        color = (54,52,44)
                if material == 'hazard' and ((x+y)//2)%2:
                    color = (56,53,44)
                if material in ('vent','rubber') and y%3 == 1:
                    shift -= 19
                if material == 'cloth' and w >= 5 and x in (1,w-2):
                    shift -= 21
                if material == 'badge' and (x == y or x+y == w-1):
                    color = (121,174,176)
                tex.putpixel((x,y),tuple(max(0,min(255,c+shift)) for c in color)+(255,))
        pen = ImageDraw.Draw(tex)
        if material in ('slit','lens'):
            if material == 'slit':
                y = h//2
                pen.line((1,y,w-2,y),fill=(43,213,228,255))
                pen.line((w//3,y,2*w//3,y),fill=(195,255,251,255))
                if h > 3:
                    pen.line((2,y+1,w-3,y+1),fill=(32,104,114,255))
            else:
                m = 1 if min(w,h) >= 5 else 0
                pen.ellipse((m,m,w-1-m,h-1-m),fill=(32,95,105,255))
                pen.ellipse((m+1,m+1,w-2-m,h-2-m),outline=(61,215,226,255))
                pen.point((w//2,h//2),fill=(209,255,252,255))
        # A one-pixel gutter keeps adjacent tiles out of filtered edges.
        for y in range(-1,h+1):
            for x in range(-1,w+1):
                self.atlas.putpixel((self.x+x+1,self.y+y+1),tex.getpixel((min(w-1,max(0,x)),min(h-1,max(0,y)))))
        uv = dict(uv=[self.x+1,self.y+1],uv_size=[w,h])
        self.cache[key] = uv
        self.x += w+2
        self.row = max(self.row,h+2)
        return uv

    def cube(self, bone, origin, size, material, **overrides):
        uv = {}
        for face, axes in faces.items():
            w,h = (max(1,ceil(size[a])) for a in axes)
            uv[face] = self.tile(overrides.get(face,material),w,h)
        self.bones[bone].setdefault('cubes',[]).append(dict(origin=origin,size=size,uv=uv))

    def moss(self, bone, x, y, z, w, d, trails=()):
        for i in range(ceil(w*d/9)):
            u = round(self.rng.uniform(x,x+w-1),1)
            v = round(self.rng.uniform(z,z+d-1),1)
            self.cube(bone,(u,y,v),(min(2,w),self.rng.choice((.4,.65,1)),min(2,d)),self.rng.choice(('moss','leaf')))
        for u, v, height in trails:
            for i in range(0,height,2):
                self.cube(bone,(u+self.rng.choice((-.35,0,.3)),y-i-2,v),(self.rng.choice((.65,1.05,1.4)),2,.65),self.rng.choice(('moss','leaf')))

    def beacon(self, bone, x, y, z):
        self.cube(bone,(x-.85,y,z-.85),(1.7,.7,1.7),'frame')
        self.cube(bone,(x-.36,y+.7,z-.36),(.72,2,.72),'rubber')
        self.cube(bone,(x-.65,y+2.7,z-.65),(1.3,1.25,1.3),'cyan')

    def finish(self):
        self.geo['description'].update(texture_width=256,texture_height=256)
        save(self.path,self.data)
        self.atlas.save(rp/'textures/bearframe'/(self.name+'.png'))
        return self

def humanoid(guardian):
    m = Model('guardian' if guardian else 'protocol_keeper')
    s = 1 if guardian else .72
    def cube(bone, origin, size, color, **sides):
        m.cube(bone,tuple(round(x*s,3) for x in origin),tuple(round(x*s,3) for x in size),color,**sides)
    def bone(name,parent,pivot):
        m.bone(name,parent,[round(x*s,3) for x in pivot])
    bone('body','root',(0,17,0))
    bone('head','body',(0,34,0))
    cube('body',(-5,13,-3.2),(10,8,6.4),'frame')
    cube('body',(-8,20,-5),(16,12,10),'frame')
    cube('body',(-7,21,-6.1),(14,10,1.5),'edge')
    if guardian:
        cube('body',(-5,22,-6.7),(10,8,1),'dark',north='lens')
        cube('body',(-6,21,4.8),(12,10,2),'frame',south='badge')
    else:
        cube('body',(-3,21,-6.5),(6,9,1),'dark')
        cube('body',(-.75,22,-6.8),(1.5,6,.7),'cyan')
        cube('body',(-4,8,-4.3),(8,11,.85),'cloth')
        cube('body',(-2,10,-4.75),(4,4,.5),'badge')
        for x in (-6.4,5):
            cube('body',(x,8,-3),(1.4,11,6),'cloth')
    cube('head',(-1.8,31,-1.8),(3.6,4,3.6),'rubber')
    cube('head',(-5,34,-4.1),(10,6,8.2),'plate')
    cube('head',(-4.25,35.05,-4.6),(8.5,3.8,.85),'dark',north='slit')
    for i,sign in enumerate((-1,1)):
        ax = sign*(11 if guardian else 10.75)
        lx = sign*(4.8 if guardian else 4)
        arm,leg = 'arm'+str(i),'leg'+str(i)
        bone(arm,'body',(ax,29,0))
        bone(leg,'root',(lx,16,0))
        for name,origin,size,material in [
            (arm,(ax-3.6,24,-3.8),(7.2,8,7.6),'plate'),
            (arm,(ax-2,17,-2.1),(4,8,4.2),'rubber'),
            (arm,(ax-2.9,11,-3),(5.8,8,6),'plate'),
            (arm,(ax-2,9,-2.2),(4,3,4.4),'frame'),
            (leg,(lx-2.5,3,-2.4),(5,14,4.8),'frame'),
            (leg,(lx-3,3,-3.2),(6,7,6.4),'plate'),
            (leg,(lx-3.25,0,-4),(6.5,3,7),'rubber')
        ]:
            cube(name,origin,size,material)
        if guardian:
            cube(arm,(ax-1.6,12,-3.5),(3.2,5,.9),'cyan')
        m.moss(arm,(ax-3.4)*s,32*s,-3.6*s,6*s,6*s,(((ax+sign*1.9)*s,-4*s,6 if i==0 else 4),))
    m.moss('head',-4.7*s,40*s,-3.8*s,9*s,7*s,((2.5*s,3.9*s,5),))
    m.moss('body',-7*s,32*s,-4*s,14*s,8*s,((-6*s,6.6*s,10 if guardian else 7),))
    return m.finish()

def hauler():
    m = Model('hauler')
    m.bone('body','root',(0,6,0))
    m.cube('body',(-7,3,-10),(14,6,20),'frame',north='hazard')
    m.cube('body',(-7,8,-9),(14,2,18),'edge')
    m.cube('body',(-6,10,-8),(12,6,9),'plate')
    m.cube('body',(-5,11,-8.6),(10,4,.9),'dark',north='slit')
    for y,z in ((5,-10.35),(8,-9.4)):
        m.cube('body',(-4,y,z),(8,1.8,.7),'dark',north='slit')
    m.cube('body',(-5,10,1),(10,5,6),'rust',south='hazard')
    for x in (-4,3):
        m.cube('body',(x,10,1),(1,5.2,6.2),'frame')
    for i,x in enumerate((-8.4,8.4)):
        name='tread'+str(i)
        m.bone(name,'root',(x,3,0))
        m.cube(name,(x-2.5,0,-10),(5,5.5,20),'rubber',east='hazard',west='hazard')
        for z in range(-9,10,3):
            m.cube(name,(x-2.65,.25,z),(5.3,5.15,1.1),'frame')
    m.bone('crane','body',(4,14,5))
    m.cube('crane',(4,11,1),(1.5,4,6),'rust')
    m.beacon('body',1,16,0)
    m.moss('body',-5.8,16,-7.7,11,8,((-5.8,-8.4,7),(4.1,7.35,6)))
    return m.finish()

def turret():
    m = Model('turret')
    m.bone('body','root',(0,0,0))
    m.bone('head','body',(0,13,0))
    m.bone('barrels','head',(0,15,-4))
    m.cube('body',(-2,3,-2),(4,10,4),'frame',north='hazard')
    for x,z in ((-5,-4),(5,-4),(0,5)):
        ix,iz = x*.5,z*.5
        m.cube('body',(ix-1.8,5,iz-1.8),(3.6,3,3.6),'frame')
        m.cube('body',(min(x,ix)-1.5,3,min(z,iz)-1.5),(abs(x-ix)+3,3,abs(z-iz)+3),'plate')
        m.cube('body',(x-1.65,0,z-1.65),(3.3,3.5,3.3),'plate')
        m.cube('body',(x-2,0,z-2),(4,1.25,4),'rubber')
    m.cube('head',(-4.5,11,-4),(9,7,8),'frame',south='badge',east='hazard',west='hazard')
    m.cube('head',(-5,17.5,-4.5),(10,1.3,9),'edge')
    m.cube('barrels',(-2.2,13,-8.8),(4.4,3.8,5.4),'frame')
    m.cube('barrels',(-1.45,13.5,-9.2),(2.9,2.8,.75),'cyan',north='lens')
    m.beacon('head',0,18.8,0)
    m.moss('head',-4.5,18.8,-4,9,8,((-4,-4.45,5),(3.7,4.2,6)))
    return m.finish()

def arthropod(walker):
    m = Model('walker' if walker else 'repair_crawler')
    width,depth,height,y = (10,13,5.4,5.5) if walker else (9,11,3,3.1)
    m.bone('body','root',(0,y,0))
    for i in range(6):
        side = (-1 if i%2==0 else 1) if walker else (-1 if i<3 else 1)
        # The crawler uses four walking legs. Retain the spare animation targets.
        slot = i//2 if walker else i%3
        z = (slot-1)*(4.45 if walker else 3.5)
        x = side*(5.35 if walker else 4.1)
        name = 'leg'+str(i)
        m.bone(name,'root',(x,y+1,z))
        if not walker and slot==1:
            continue
        foot = x + side*(1.9 if walker else 2.1)
        m.cube(name,(min(x,foot)-1.3,y-.4,z-1.25),(abs(foot-x)+2.6,2.2,2.5),'frame')
        m.cube(name,(foot-1.35,1,z-1.35),(2.7,y,2.7),'plate')
        m.cube(name,(foot-1.55,0,z-1.65),(3.1,1.5,3.3),'rubber')
        if walker:
            m.cube(name,(foot-1.05,y+.35,z-1.5),(2.1,.65,3),'cyan')
        if i in (0,5):
            m.moss(name,foot-1.2,y+1,z-1.3,2.5,2.5,((foot-.8,z-1.55,3),))
    m.cube('body',(-width/2,y,-depth/2),(width,height,depth),'frame',south='vent')
    m.cube('body',(-width/2-.3,y+height,-depth/2-.1),(width+.6,1.2,depth+.2),'edge')
    m.bone('head','body',(0,y+height,-depth/2))
    m.cube('head',(-3.8,y+.1,-depth/2-1),(7.6,height-.2,1.3),'edge')
    m.cube('head',(-2.9,y+.55,-depth/2-1.25),(5.8,height-1.1,.8),'dark',north='slit')
    for i,sign in enumerate((-1,1)):
        name = 'arm'+str(i)
        x = sign*3.2
        m.bone(name,'body',(x,y,-depth/2))
        m.cube(name,(x-1,y-.9,-depth/2-1),(2,2,1.8),'frame',north='cyan' if walker else 'plate')
    if walker:
        m.cube('body',(-3.7,y+height+1,-depth/2+1),(7.4,2.8,4),'plate',north='slit')
        m.beacon('body',1,y+height+3.8,-1.5)
    else:
        m.cube('body',(-3.2,y+height+1,-3),(6.4,1.3,6),'hazard')
        for x in (-2,0,2):
            m.cube('body',(x-.55,y+height+2,-2),(1.1,1.15,4),'frame')
    m.moss('body',-width/2,y+height+1.2,-depth/2,width,depth,((-width/2+.2,-depth/2-.4,4),(2,depth/2-.1,5)))
    return m.finish()

def watcher():
    m = Model('watcher')
    m.bone('body','root',(0,11,0))
    m.bone('scanner','body',(0,6,0))
    m.cube('body',(-4.4,6,-4.3),(8.8,9,8.6),'plate',east='badge',west='badge',south='vent')
    m.cube('body',(-3.5,7,-4.75),(7,7,.75),'dark',north='lens')
    m.cube('scanner',(-1.45,4.65,-1.45),(2.9,1.55,2.9),'cyan')
    for i,x in enumerate((-5.7,5.7,0)):
        z = 3.8 if i==2 else 0
        name='thruster'+str(i)
        m.bone(name,'body',(x,10,z))
        m.cube(name,(x-1.35,8,z-1.8),(2.7,4.2,3.6),'frame',east='badge',west='badge')
    m.beacon('body',0,15,0)
    m.moss('body',-4,15,-4,8,8,((-4.4,-4.7,5),(3.1,4.2,7)))
    return m.finish()

models = [humanoid(True), humanoid(False), arthropod(False), watcher(), hauler(), turret(), arthropod(True)]

def convert_keeper():
    path = bp/'entities/grid_protocol_keeper.json'
    data = load(path)
    c = data['minecraft:entity']['components']
    for key in ('can_fly','flying_speed','movement.hover','navigation.hover','behavior.random_hover'):
        del c['minecraft:'+key]
    c['minecraft:physics']['has_gravity'] = True
    c['minecraft:collision_box']['height'] = 1.84
    c['minecraft:movement.basic'] = {}
    c['minecraft:navigation.walk'] = dict(avoid_water=True,avoid_damage_blocks=True)
    c['minecraft:behavior.random_stroll'] = dict(priority=5,speed_multiplier=.8)
    save(path,data)
    keeper = rp/'animations/grid_protocol_keeper.animation.json'
    guard = rp/'animations/grid_guardian.animation.json'
    keeper.write_text(guard.read_text().replace('grid_guardian','grid_protocol_keeper'))
    entity = rp/'entity/grid_protocol_keeper.entity.json'
    data = load(entity)
    desc = data['minecraft:client_entity']['description']
    desc['animations']['ctrl'] = 'controller.animation.bearframe.locomotion'
    desc['animations']['walk'] = 'animation.bearframe.grid_protocol_keeper.walk'
    save(entity,data)

convert_keeper()
crawler_animation = rp/'animations/grid_repair_crawler.animation.json'
data = load(crawler_animation)
legs = data['animations']['animation.bearframe.grid_repair_crawler.walk']['bones']
legs['leg2'], legs['leg5'] = legs['leg1'], legs['leg0']
save(crawler_animation,data)
for folder in (rp,bp):
    path=folder/'manifest.json'
    data=load(path)
    for record in [data['header'],*data['modules'],*data.get('dependencies',[])]:
        if record.get('version') == [0,4,4]:
            record['version']=[0,4,5]
    save(path,data)

for m in models:
    animation = load(rp/'animations'/(m.name+'.animation.json'))['animations']
    requested = set().union(*(entry.get('bones',{}).keys() for entry in animation.values()))
    assert requested <= m.bones.keys(), (m.name,requested-m.bones.keys())
    assert m.atlas.getbbox() is not None

output=Path('/mnt/data/Bearframe_Bedrock_0.4.5.mcaddon')
output.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED) as archive:
    for file in sorted(Path('pack').rglob('*')):
        if file.is_file():
            archive.write(file,file.relative_to('pack'))

with zipfile.ZipFile(output) as archive, zipfile.ZipFile(next(Path('source').glob('*.mcaddon'))) as original:
    assert archive.testzip() is None and set(archive.namelist()) == set(original.namelist())
    changed = {name for name in archive.namelist() if archive.read(name)!=original.read(name)}
    expected = {str(m.path.relative_to('pack')) for m in models}
    expected.update(str((rp/'textures/bearframe'/(m.name+'.png')).relative_to('pack')) for m in models)
    expected.update(str(path.relative_to('pack')) for path in (
        rp/'manifest.json',bp/'manifest.json',bp/'entities/grid_protocol_keeper.json',
        rp/'animations/grid_protocol_keeper.animation.json',crawler_animation))
    assert changed == expected, changed ^ expected
    for name in archive.namelist():
        if name.endswith('.json'):
            json.loads(archive.read(name))
    print(f'Validated {len(archive.namelist())} entries and {len(changed)} intentional changes')
