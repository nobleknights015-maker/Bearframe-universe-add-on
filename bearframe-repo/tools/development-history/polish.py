from pathlib import Path
import runpy, math, io, copy, zipfile
from PIL import Image, ImageDraw
import numpy as np

# Load the original model-building routines without running its release build.
base = Path('rebuild.py').read_text().split('\nmodels = ')[0]
exec(compile(base, 'rebuild.py', 'exec'))

profiles = {
    'city_engineer': ('bear','#eeb052','tool'),
    'city_steward': ('bear','#70d4bb','satchel'),
    'city_watch': ('bear','#ef626b','watch'),
    'atlas_rigger': ('bear','#f2a835','rig'),
    'atlas_vanguard': ('bear','#efc97d','shield'),
    'farfield_surveyor': ('bear','#5ed0be','survey'),
    'field_researcher': ('bear','#9facf2','instrument'),
    'vera_artisan': ('bear','#e58ac9','artisan'),
    'directorate_guard': ('null','#e33c40','guard'),
    'directorate_officer': ('null','#f04a48','officer'),
    'nullframe_hunter': ('null','#fa5058','hunter'),
    'hollow_line': ('hollow','#ef383d','line'),
    'hollow_scout': ('hollow','#ef383d','scout'),
    'hollow_breacher': ('hollow','#fa403d','breach'),
    'echo_drifter': ('echo','#bd87f0','drifter'),
    'echo_sentinel': ('echo','#79e0ca','sentinel'),
    'ward_resident': ('echo','#e3b473','resident'),
}
def rgb(hex):
    return tuple(bytes.fromhex(hex.lstrip('#')))

class FactionModel(Model):
    def __init__(self, key, faction, color):
        # Keep the packaged model and animation identifiers and original rig.
        self.name = key
        self.path = rp/'models/entity'/(key+'.geo.json')
        self.data = load(self.path)
        self.geo = self.data['minecraft:geometry'][0]
        self.bones = {b['name']:b for b in self.geo['bones']}
        for bone in self.bones.values():
            bone.pop('cubes',None)
        self.atlas=Image.new('RGBA',(256,256))
        self.cache={}
        self.x=self.y=self.row=0
        self.rng=Random(key)
        self.faction=faction
        self.acc=rgb(color)

    def tile(self, kind, w, h):
        if (kind,w,h) in self.cache:
            return self.cache[kind,w,h]
        if self.x+w+2>256:
            self.x=0
            self.y+=self.row
            self.row=0
        assert self.y+h+2<=256
        silver = {'bear':(194,207,211),'null':(209,213,206),'hollow':(181,187,181),'echo':(129,129,119)}[self.faction]
        acc=self.acc
        colors={
            'silver':silver,'dark':(30,36,42),'steel':(74,89,96),
            'light':acc,'tint':tuple(int(c*.58) for c in acc),
            'rib':(44,53,57),'glass':(18,26,34),'bear':(26,41,50),
            'optic':(17,24,30),'rank':(31,34,37),'crack':silver,
            'panel':(40,48,53),'hazard':(185,129,53),'fabric':(53,63,74),
            'scan':(22,35,40),
        }
        tile=Image.new('RGBA',(w,h))
        for y in range(h):
            for x in range(w):
                col=colors[kind]
                edge=min(x,y,w-1-x,h-1-y)
                shift=0
                if kind in ('silver','steel','crack','tint','panel'):
                    if edge==0:
                        shift=22 if min(x,y)==0 else -27
                    elif w>=6 and h>=6 and x in (1,w-2) and y in (1,h-2):
                        col=(69,79,81)
                    elif kind in ('silver','crack'):
                        shift=5 if y<h*.42 else -6
                if kind in ('rib','fabric') and y%3==1:
                    shift=-14
                if kind=='hazard' and (x+y)//3%2:
                    col=(49,47,45)
                if self.faction=='echo' and kind in ('crack','silver','steel') and self.rng.random()<.16:
                    col=self.rng.choice(((99,77,60),(108,86,69),(74,77,70)))
                tile.putpixel((x,y),tuple(max(0,min(255,c+shift)) for c in col)+(255,))
        d=ImageDraw.Draw(tile)
        rgba=lambda c: (*c,255)
        if kind in ('optic','scan','rank') and w>=3:
            offsets=[0] if kind=='optic' else [-1,1]
            for off in offsets:
                y=max(0,min(h-1,h//2+off))
                d.line((1,y,w-2,y),fill=rgba(acc))
                d.point((w//2,y),fill=rgba(tuple((c+255)//2 for c in acc)))
        if kind=='bear' and w>=7 and h>=7:
            cx,cy=w//2,h//2
            d.rectangle((cx-2,cy-1,cx+2,cy+1),fill=rgba(acc))
            d.point([(cx-2,cy-2),(cx+2,cy-2)],fill=rgba(acc))
            d.line((cx-1,cy+2,cx+1,cy+2),fill=rgba(acc))
            d.point([(cx-1,cy),(cx+1,cy)],fill=rgba((21,33,40)))
        if kind=='crack':
            x=max(1,w//2)
            d.line([(x,0),(x-1,h//3),(min(w-1,x+1),2*h//3),(x,h-1)],fill=rgba((33,37,36)))
        if kind=='light':
            d.line((0,max(0,h//2-1),w-1,max(0,h//2-1)),fill=rgba(tuple((c+255)//2 for c in acc)))
        for y in range(-1,h+1):
            for x in range(-1,w+1):
                self.atlas.putpixel((self.x+x+1,self.y+y+1),tile.getpixel((max(0,min(w-1,x)),max(0,min(h-1,y)))))
        uv=dict(uv=[self.x+1,self.y+1],uv_size=[w,h])
        self.cache[kind,w,h]=uv
        self.x+=w+2
        self.row=max(self.row,h+2)
        return uv

def humanoid_polish(name, faction, color, role):
    m=FactionModel(name,faction,color)
    c=m.cube
    bf=faction=='bear'
    echo=faction=='echo'
    null=faction=='null'
    hollow=faction=='hollow'
    heavy=role in ('shield','guard','breach','sentinel')
    skin='crack' if echo else 'silver'
    c('body',(-4,12,-2),(8,12,4),'dark',east='rib',west='rib')
    c('head',(-4,24,-4),(8,8,8),'dark')
    c('head',(-3.8,29.9,-3.9),(7.6,2.4,8.02),skin if role!='hunter' else 'steel')
    c('head',(-3.75,26.35,-4.27),(7.5,2.45,.54),'glass',north='optic')
    c('head',(-3.1 if not echo else -.1,24.3,-4.13),(6.2 if bf else 3.15,1.5,.65),skin)
    c('head',(-3.65,24.45,3.86),(7.3,4.8,.55),'steel',south='panel')
    if bf or (null and role!='hunter'):
        for x in (-3.98,3.46):
            c('head',(x,24.45,-3.63),(.52,5.6,7.32),'silver',north='steel')
        c('head',(-3.57,28.22,3.92),(7.14,2.11,.54),'silver',south='panel')
    if bf or null or echo:
        for x,side in ((-4.65,'west'),(3.92,'east')):
            c('head',(x,26.15,-1.35),(.73,3.35,3.25),'steel')
            c('head',(x-.10 if side=='west' else x+.65,26.73,-.8),(.18,2.13,2.15),'glass',**{side:'light'})
    if echo:
        c('head',(-3.85,25.2,-4.55),(2.55,4.65,.6),'steel',north='crack')
        c('head',(-3.2,27.1,-4.65),(1.2,.45,.35),'light')
    c('body',(-3.83,17.05,-2.6),(7.66,6.1,.92),skin)
    c('body',(-3.5,19.65,-2.75),(7.0,2.9,.56),'steel' if null or hollow else skin)
    c('body',(-2.18,17.95,-3.02),(4.36,2.8,.65),'glass',north='bear' if bf else 'rank' if null else 'scan' if echo else 'panel')
    # The bear icon needs more texels than the thin display's world-space dimensions.
    if bf:
        m.bones['body']['cubes'][-1]['uv']['north']=m.tile('bear',13,9)
    c('body',(-3.5,12.8,-2.3),(7,1.45,.75),'steel',north='panel')
    if bf:
        c('body',(-3.48,19.1,1.88),(6.96,3.72,.72),'silver',south='panel')
        c('body',(-2.14,15.6,1.92),(4.28,3.55,.53),'steel',south='rib')
        m.bones['body']['cubes'][-2]['uv']['south']=m.tile('bear',15,9)
    if echo:
        c('body',(-3.64,14.04,-3.0),(1.25,6.4,.65),'steel',north='crack')
        c('body',(-3.09,14.57,-3.14),(.42,3.8,.28),'light')
        c('body',(1.62,14.6,1.9),(1.1,6.7,1.48),'steel',south='rib')
    if null or hollow:
        c('body',(-2.95,16.1,1.92),(5.9,6.8,1.08),'dark',south='rib')
        c('body',(-3.45,21.8,-2.95),(6.9,.7,.8),'silver')
        if role=='officer':
            c('body',(-3.5,13.05,2.76),(7,8.65,.84),'fabric',south='rank')
            c('head',(-3.15,31.9,1.46),(6.3,1.04,2.3),'steel')
        if role=='hunter':
            for x in (-3.25,2.65):
                c('head',(x,30.85,2.25),(.6,2.4,1.05),'steel')
            c('body',(-2.7,15.2,2.83),(5.4,6.6,1.09),'dark',south='rank')
    for i in range(2):
        arm,leg='arm'+str(i),'leg'+str(i)
        ax,lx=(-8,-4) if i==0 else (4,0)
        c(arm,(ax,12,-2),(4,12,4),'dark',east='rib',west='rib')
        c(leg,(lx,0,-2),(4,12,4),'dark',east='rib',west='rib')
        missing=echo and i==(1 if role!='resident' else 0)
        if not missing:
            extra=.69 if heavy or role=='hunter' else .17
            c(arm,(ax-extra,20.18,-2.38),(4+2*extra,3.55,4.9),skin)
            c(arm,(ax-.06,22.8,-2.06),(4.12,1.25,4.0),'tint' if bf else 'steel')
            c(arm,(ax+.26,13.55,-2.45),(3.48,3.85,.97),skin,north='silver' if not echo else 'crack')
        else:
            c(arm,(ax+.44,16.7,-2.27),(2.87,4.55,.55),'steel',north='rib')
            c(arm,(ax+1.28,13.15,-2.43),(.44,4.18,.35),'light')
        c(arm,(ax+.36,12.0,-2.14),(3.28,1.43,3.96),'steel')
        c(leg,(lx+.29,1.03,-2.60),(3.42,4.1,.98),skin if not missing else 'steel')
        c(leg,(lx+.23,0,-2.73),(3.54,1.48,4.76),'steel')
        if not missing:
            c(leg,(lx+.38,1.15,1.8),(3.24,4.05,.68),'steel' if echo else skin,south='panel')
            c(arm,(ax+.33,13.8,1.89),(3.34,3.82,.67),'steel' if hollow or echo else skin,south='panel')
        c(leg,(lx+.41,5.3,-2.31),(3.18,1.52,.63),'tint' if bf else 'steel',north='rank' if hollow else 'panel')
        if heavy:
            c(leg,(lx+.13,7.5,-2.37),(3.74,3,.68),skin)
    # Duty equipment is attached to the bone that actually carries it.
    if role in ('survey','instrument','tool','rig'):
        c('body',(-2.68,15.55,1.85),(5.36,6.65,2.12),'steel',south='panel')
        c('body',(-2.28,16.15,3.79),(4.56,5.45,.77),'silver',south='scan' if role in ('survey','instrument') else 'hazard')
    if role=='survey':
        c('body',(1.7,21.0,3.05),(.58,5.2,.58),'steel')
        c('body',(1.58,25.78,2.94),(.82,.73,.82),'light')
        c('arm1',(4.22,13.18,-3.16),(3.22,3.93,1.04),'glass',north='scan')
    elif role=='instrument':
        for x in (-3.24,2.39):
            c('body',(x,15.1,2.09),(.85,6.03,1.45),'tint')
        c('arm0',(-7.83,14.21,-3.23),(3.65,2.55,1.22),'glass',north='scan')
    elif role=='rig':
        c('arm0',(-9.06,12.6,-2.6),(2.65,5.5,4.95),'steel',west='hazard',north='hazard')
        c('arm0',(-9.03,11.18,-1.65),(1.3,2.2,.84),'steel')
        c('arm0',(-9.03,11.18,.34),(1.3,2.2,.84),'steel')
    elif role=='shield':
        c('arm0',(-8.67,12.88,-3.38),(5.22,6.8,1.35),'steel')
        c('arm0',(-8.36,13.15,-3.82),(4.60,6.25,.62),'silver',north='tint')
        m.bones['arm0']['cubes'][-1]['uv']['north']=m.tile('bear',12,14)
    elif role=='satchel':
        c('body',(-4.02,13.72,-2.83),(2.42,3.76,1),'fabric',north='tint')
        c('body',(2.08,14.45,1.98),(1.63,3.47,1.14),'fabric',south='panel')
    elif role=='artisan':
        c('arm1',(4.18,12.99,-3.06),(3.7,4.15,1.12),'steel',north='scan')
        c('body',(-2.75,14.7,2.0),(5.5,4.18,1.12),'tint',south='panel')
    elif role=='watch':
        c('body',(-3.21,14.2,2.06),(6.42,7.3,1),'steel',south='rank')
        c('head',(2.9,29.1,3.0),(.59,4,.62),'steel')
        c('head',(2.78,32.52,2.9),(.82,.65,.83),'light')
    elif role=='guard':
        c('arm0',(-8.38,14,-3.31),(4.62,5.55,1.25),'silver',north='rank')
    elif role=='hunter':
        for ax in (-8,4):
            bone='arm0' if ax<0 else 'arm1'
            c(bone,(ax+.48,20.7,1.88),(2.9,3.7,1.52),'steel',south='rank')
        c('arm1',(4.08,13.3,-3.24),(3.84,4.65,1.42),'steel',north='rank')
    elif role=='breach':
        c('arm0',(-8.93,12.9,-3.2),(5.17,6.85,2.27),'steel',north='hazard')
        c('arm0',(-8.65,14.63,-3.78),(4.48,3.04,.88),'silver',north='rank')
    elif role=='scout':
        c('body',(-2.08,18.2,2.0),(4.16,5.2,1.57),'steel',south='scan')
        c('body',(1.2,22.4,2.65),(.51,3.2,.51),'steel')
    elif role=='line':
        c('body',(-3.4,16.45,-2.72),(6.8,1.5,.75),'steel',north='rank')
    elif role=='drifter':
        c('leg1',(1.93,1.1,1.95),(1.22,7.3,.89),'steel',south='rib')
        c('body',(1.82,19.1,2.2),(1.33,4.08,.78),'crack')
    elif role=='sentinel':
        c('arm0',(-8.72,13.25,-3.14),(4.71,6.35,1.15),'crack')
        c('body',(-2.7,16.4,2.02),(4.1,5.66,1.2),'steel',south='scan')
    elif role=='resident':
        c('body',(-2.65,13.1,2.0),(4.76,5.15,1.41),'fabric',south='panel')
        c('body',(1.85,13.45,-2.58),(1.4,5.2,.75),'tint')
    return m.finish()

models=[humanoid_polish(name,*profile) for name,profile in profiles.items()]

def grid_finish(m):
    key=m.name.removeprefix('grid_')
    c=m.cube
    if key=='guardian':
        c('body',(-6,26,5.78),(2.0,5.05,1.15),'frame',south='vent')
        c('body',(3.75,26,5.78),(2.25,5.05,1.15),'frame',south='vent')
        c('body',(-4.5,17,-3.92),(9,1.7,1.09),'frame',north='vent')
        m.moss('leg0',-7.1,9.9,-3.05,3,2,((-6.3,-3.25,6),))
    elif key=='protocol_keeper':
        c('head',(-3.68,25.4,-1.72),(.74,2.25,3.44),'frame',west='vent')
        c('head',(2.94,25.4,-1.72),(.74,2.25,3.44),'frame',east='vent')
        c('body',(-.63,13.65,-3.25),(1.26,.73,.52),'rust',north='hazard')
    elif key=='repair_crawler':
        c('arm0',(-4.08,2.75,-8.75),(1.52,.87,2.6),'edge')
        c('arm0',(-4.15,2.7,-9.1),(.58,.98,.64),'frame')
        c('arm0',(-3.0,2.7,-9.1),(.58,.98,.64),'frame')
        c('arm1',(2.75,2.62,-8.3),(1.2,1.12,2.1),'frame',north='cyan')
        c('body',(-2.25,4.1,5.49),(4.5,1.6,.44),'hazard')
    elif key=='walker':
        c('body',(-3.8,6.15,6.47),(7.6,3.7,.8),'plate',south='vent')
        c('body',(-2.5,6.4,7.16),(5,1.05,.35),'dark',south='slit')
        c('body',(-4.82,10.88,2.6),(2.8,1.31,2.8),'hazard')
    elif key=='hauler':
        for i,x in enumerate((-8.4,8.4)):
            c('tread'+str(i),(x-2.28,1.26,-10.31),(4.56,3.7,.67),'frame',north='vent')
        c('body',(-5.25,9.7,6.85),(10.5,1.15,.88),'edge',south='hazard')
        c('body',(-5.22,14.75,1.44),(10.44,1,5.38),'rust')
    elif key=='turret':
        c('head',(-4.75,13.56,-3.02),(.68,2.95,5.92),'dark',west='vent')
        c('head',(4.07,13.56,-3.02),(.68,2.95,5.92),'dark',east='vent')
        c('barrels',(-2.47,12.84,-6.73),(4.94,4.12,1.05),'plate')
        c('body',(-2.22,9.25,-2.22),(4.44,1.62,4.44),'plate',north='hazard')
    elif key=='watcher':
        c('body',(-3.79,6.8,4.25),(7.58,7.17,.68),'dark',south='vent')
        c('body',(-3.72,6.75,4.79),(7.44,1.02,.49),'hazard')
        c('thruster0',(-6.95,8.6,-1.91),(2.51,2.3,.36),'dark',north='slit')
        c('thruster1',(4.44,8.6,-1.91),(2.51,2.3,.36),'dark',north='slit')

    # Tighten the palette and cluster weathering so it reads at normal mob scale.
    for (material,w,h),rect in m.cache.items():
        x,y=rect['uv']
        tile=np.array(m.atlas.crop((x,y,x+w,y+h)))
        light=np.array([.96,1.01,1.04])
        if material in ('plate','edge'):
            rust=(tile[:,:,0]>tile[:,:,1]+14) & (tile[:,:,1]>tile[:,:,2]+8)
            tile[:,:,:3]=np.clip(tile[:,:,:3]*light,0,255)
            tile[rust,:3]=(126,77,40)
        elif material in ('moss','leaf'):
            tile[:,:,:3]=np.clip(tile[:,:,:3]*[.89,1.08,.81],0,255)
        elif material=='cyan':
            tile[:,:,:3]=np.clip(tile[:,:,:3]*[.84,1.10,1.10],0,255)
        for row in range(-1,h+1):
            for col in range(-1,w+1):
                m.atlas.putpixel((x+col,y+row),tuple(tile[max(0,min(h-1,row)),max(0,min(w-1,col))]))
    return original_finish(m)

original_finish=Model.finish
Model.finish=grid_finish
# grid_finish delegates to the original writer, while the builders dispatch to the polish.
models.extend([humanoid(True),humanoid(False),arthropod(False),watcher(),hauler(),turret(),arthropod(True)])
Model.finish=original_finish

# Refresh the effect model too, keeping the projectile's entity and movement intact.
bolt=FactionModel('grid_bolt','bear','#70eaff')
bolt.cube('body',(-.85,1.15,-2.65),(1.7,1.7,5.3),'light')
bolt.cube('body',(-.36,1.64,-3.4),(.72,.72,6.8),'light')
bolt.cube('body',(-1.2,1.78,-1.3),(2.4,.44,2.6),'light')
bolt.finish()

for folder in (rp,bp):
    path=folder/'manifest.json'
    data=load(path)
    for entry in [data['header'],*data['modules'],*data.get('dependencies',[])]:
        if entry.get('version')==[0,4,5]:
            entry['version']=[0,4,6]
    save(path,data)

pack=rp.parent
before=Path('baseline045')
changes={p.relative_to(pack).as_posix() for p in pack.rglob('*') if p.is_file() and p.read_bytes()!=(before/p.relative_to(pack)).read_bytes()}
assert len(changes)==52 and all(p.endswith(('geo.json','.png','manifest.json')) for p in changes),changes
for m in [*models,bolt]:
    geom=m.geo
    names={b['name'] for b in geom['bones']}
    for b in geom['bones']:
        assert 'parent' not in b or b['parent'] in names
        for c in b.get('cubes',[]):
            for face in c['uv'].values():
                x,y=face['uv']; w,h=face['uv_size']
                assert x>=0 and y>=0 and x+w<=256 and y+h<=256
                assert m.atlas.getpixel((x,y))[3]==255
    view=load(rp/'entity'/(m.name+'.entity.json'))['minecraft:client_entity']['description']
    assert geom['description']['identifier']==view['geometry']['default']
    assert (rp/(view['textures']['default']+'.png')).exists()
    animated=rp/'animations'/(m.name+'.animation.json')
    if animated.exists():
        for a in load(animated)['animations'].values():
            assert a.get('bones',{}).keys()<=names
out=Path('deliverables')
out.mkdir(exist_ok=True)
with zipfile.ZipFile(out/'Bearframe_Bedrock_0.4.6.mcaddon','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(pack.rglob('*')):
        if p.is_file():
            z.write(p,p.relative_to(pack).as_posix())
with zipfile.ZipFile(out/'Bearframe_Bedrock_0.4.6.mcaddon') as z:
    assert z.testzip() is None
    assert len(z.namelist())==237
    for p in z.namelist():
        if p.endswith('.json'):
            json.loads(z.read(p))
print('Validated 24 units, 1 projectile, 237 archive entries and 52 intended file changes.')
