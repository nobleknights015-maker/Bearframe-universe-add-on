from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from io import BytesIO
import json,re
from PIL import ImageDraw

exec(compile(Path('rebuild.py').read_text().split('\nmodels = ')[0],'rebuild.py','exec'))
folder=Path('deliverables')
old=ZipFile(folder/'Bearframe_Bedrock_0.7.8.mcaddon')
rp='Bearframe_Resources/'
bp='Bearframe_Behavior/'
updates={}
original=palette.copy()
profiles={
 'witch':('Echo Chemist',(116,109,119),(184,108,225),(73,47,85)),
 'iron_golem':('Ghost Grid Protector',(135,143,131),(77,208,222),(77,98,61)),
 'enderman':('Longstride Echo',(76,71,88),(189,109,241),(56,44,70)),
 'vex':('Nullframe Drone',(139,143,144),(247,64,75),(85,49,54)),
 'allay':('Blue Utility Drone',(139,143,144),(70,173,255),(53,78,99)),
 'warden':('Deep Grid Sentinel',(70,87,87),(89,226,210),(46,74,71)),
 'creaking':('Rootbound Echo',(114,92,69),(235,162,64),(92,79,55)),
 'ravager':('Nullframe Siege Beast',(117,119,118),(241,65,65),(64,51,55)),
}
def enc(d):return (json.dumps(d,indent=2)+'\n').encode()
def ref(name,suffix):
    text=Path('vanilla_client',name+'.'+suffix).read_text()
    return json.loads(re.sub(r'^\s*//.*$','',text,flags=re.M))
def native_bones(key):
    raw=ref('villager' if key=='witch' else key,'geo.json')
    d=next(iter(raw.get('minecraft:geometry',[v for k,v in raw.items() if k.startswith('geometry.')])))
    return d['bones']

class Frame(Model):
    def __init__(self,key,alloy,optics,cloth):
        self.name=key
        self.geo={'description':dict(identifier='geometry.bearframe.vanilla_'+key,texture_width=256,texture_height=256,
            visible_bounds_width=6 if key=='ravager' else 3,visible_bounds_height=4,visible_bounds_offset=[0,1.4,0]),'bones':[]}
        self.bones={}
        self.atlas=Image.new('RGBA',(256,256))
        self.cache={}
        self.x=self.y=self.row=0
        self.rng=Random('drone' if key in ('vex','allay') else key)
        palette.update(original)
        palette.update(plate=alloy,edge=tuple(min(235,c+36) for c in alloy),cyan=optics,cloth=cloth)
        if key in ('vex','allay'): palette.update(cloth=(49,56,64))
        for b in native_bones(key):
            self.bone(b['name'],b.get('parent'),b.get('pivot',[0,0,0]))
            for attr in ('rotation','binding','neverRender','locators'):
                if attr in b:self.bones[b['name']][attr]=b[attr]

    def tile(self,material,w,h):
        fresh=(material,w,h) not in self.cache
        uv=super().tile(material,w,h)
        if fresh and material in ('slit','lens'):
            x,y=uv['uv']
            for a in range(x-1,x+w+1):
                for b in range(y-1,y+h+1):
                    r,g,blue,alpha=self.atlas.getpixel((a,b))
                    if g>75 and blue>80 and blue>r+30:
                        level=max(g,blue)/245
                        self.atlas.putpixel((a,b),tuple(min(255,round(value*level)) for value in palette['cyan'])+(alpha,))
        return uv

    def drone(self,blue):
        c=self.cube
        top='look_at' if blue else 'head'
        arms=('right_arm','left_arm') if blue else ('rightArm','leftArm')
        wings=('right_wing','left_wing') if blue else ('rightWing','leftWing')
        c(top,(-1.8,5.7,-1.8),(3.6,2.45,3.25),'plate')
        c(top,(-1.48,6.14,-2),(2.96,1.3,.51),'dark',north='slit')
        for x in (-1.77,1.44):c(top,(x,6.21,-.57),(.36,1.28,1.54),'cyan')
        c('body',(-1.5,2.35,-1.07),(3.0,3.33,2.20),'frame')
        c('body',(-1.18,3.16,-1.38),(2.36,2.04,.59),'plate')
        c('body',(-.69,3.66,-1.64),(1.38,1.02,.36),'cyan')
        c('body',(-1.33,1.6,-.81),(2.66,.76,1.61),'plate')
        for i,arm in enumerate(arms):
            x=-2.32 if i==0 else 1.38
            c(arm,(x,3.08,-.58),(.94,2.49,1.1),'plate')
            c(arm,(x+.05,2.68,-.54),(.84,.71,.96),'frame')
        for i,wing in enumerate(wings):
            x=-4.7 if i==0 else .68
            c(wing,(x,4.28,1.03),(4.02,.68,1.27),'frame')
            c(wing,(x+.19,4.72,1.12),(3.63,.33,1.08),'cyan')
            c(wing,(x+.45,4.08,2.17),(3.15,.56,.48),'plate')

    def chemist(self):
        c=self.cube
        for side,x in (('rightarm',-6),('leftarm',6)):
            self.bone(side,'body',[x,22,0])
            c(side,(x-1.83,12,-1.78),(3.66,12,3.56),'frame')
            c(side,(x-2.04,20.26,-2.14),(4.08,3.48,4.24),'cloth')
            c(side,(x-1.62,13.55,-2.22),(3.24,3.39,.75),'plate')
        c('body',(-4,12,-2),(8,12,4),'frame')
        c('body',(-3.6,15.3,-2.45),(7.2,7.44,.75),'cloth')
        c('body',(-2,19.6,-3.03),(4,2.42,.68),'frame',north='slit')
        for x in (-3.03,2.04):
            c('body',(x,13.1,-2.91),(1.08,3.08,1.05),'cyan')
            c('body',(x-.08,15.89,-3.02),(1.24,.6,1.17),'rust')
        c('body',(-3.76,9.5,1.97),(7.52,12.7,.72),'cloth')
        c('head',(-3.9,24,-3.85),(7.8,8,7.7),'plate')
        c('head',(-3.62,27,-4.10),(7.24,2.26,.63),'dark',north='slit')
        c('head',(-4.56,30.55,-4.5),(9.12,1.75,9.02),'cloth')
        for x in (-4.53,3.83):c('head',(x,26.02,-3.22),(.70,5.14,6.94),'cloth')
        for i,leg in enumerate(('leg0','leg1')):
            x=-4.0 if i==0 else .17
            c(leg,(x,0,-1.85),(3.67,12,3.7),'frame')
            c(leg,(x+.12,1,-2.26),(3.38,4.35,.75),'plate')

    def golem(self):
        c=self.cube
        c('body',(-9.3,15,-4.9),(18.6,17.3,9.8),'frame')
        c('body',(-8.47,20,-6.22),(16.94,11.1,1.64),'plate')
        c('body',(-4.1,22,-6.94),(8.2,7,1.22),'frame',north='lens')
        c('body',(-6.7,16.6,4.7),(13.4,12.51,1.25),'vent')
        c('head',(-4.8,32,-5.75),(9.6,7,8.8),'plate')
        c('head',(-4.06,34.28,-6.10),(8.12,3.2,.86),'dark',north='slit')
        for i,ax in enumerate((-12,12)):
            arm='arm'+str(i);leg='leg'+str(i)
            c(arm,(ax-3.32,21.8,-3.6),(6.64,10.4,7.2),'plate')
            c(arm,(ax-2.11,13.75,-2.74),(4.22,9.7,5.5),'frame')
            c(arm,(ax-3,7,-3.25),(6,8.84,6.5),'plate')
            m=-4 if i==0 else 4
            c(leg,(m-3,0,-3.1),(6,14.9,6.2),'plate')
            c(leg,(m-3.45,0,-3.7),(6.9,2.4,7.2),'rubber')
        self.moss('body',-8.4,32.31,-4.2,16,8,((-7,-5.1,7),(6,5.3,5)))

    def longstride(self):
        c=self.cube
        c('body',(-3.1,25,-1.95),(6.2,13.3,3.9),'frame')
        c('body',(-3.38,34,-2.27),(6.76,4.55,4.38),'plate')
        c('body',(-1.02,25,-2.31),(2.04,10.47,.77),'edge')
        for y in (28,30.4,32.8):
            c('body',(-2.86,y,-2.24),(5.72,.65,.9),'plate')
        c('head',(-3.8,39,-3.2),(7.6,7.4,6.4),'plate')
        c('head',(-3.28,41.58,-3.56),(6.56,1.8,.65),'dark',north='slit')
        for i,side in enumerate(('right','left')):
            ax=-4.7 if i==0 else 4.7;lx=-2 if i==0 else 2
            arm=side+'Arm';leg=side+'Leg'
            c(arm,(ax-.96,13,-.94),(1.92,23,1.88),'frame')
            c(arm,(ax-1.3,27,-1.16),(2.6,7.67,2.32),'plate')
            c(arm,(ax-1.18,13,-1.08),(2.36,3.1,2.16),'edge')
            c(leg,(lx-.9,0,-.85),(1.8,26,1.7),'frame')
            c(leg,(lx-1.08,2,-1.13),(2.16,7.6,1.65),'plate')
            c(leg,(lx-1.24,0,-1.47),(2.48,1.65,2.73),'edge')

    def deep(self):
        c=self.cube
        c('body',(-9,16,-5),(18,21,10),'frame')
        c('body',(-8.8,28,-5.7),(17.6,7.95,1.38),'plate')
        c('body',(-4.4,18,-5.45),(8.8,12,1.29),'dark')
        c('body',(-1.92,22.18,-6.31),(3.84,4.8,1.16),'cyan')
        for right,side in ((True,-1),(False,1)):
            pre='right' if right else 'left'
            for i,y in enumerate((19,22,25,28)):
                x=-8 if right else 1.5
                c(pre+'_ribcage',(x,y,-6.37),(6.5,1.28,2.02),'edge')
            x=-14 if right else 9
            c(pre+'_arm',(x,20,-3.77),(5,15,8.04),'plate')
            c(pre+'_arm',(x-.45,11,-4.1),(5.9,10.7,8.75),'frame')
            c(pre+'_arm',(x,11.2,-4.86),(5,4.38,1.34),'edge')
            x=-7.75 if right else 2.3
            c(pre+'_leg',(x,0,-3.3),(5.45,17,6.6),'plate')
            c(pre+'_leg',(x-.32,0,-4),(6.1,3.01,7.25),'rubber')
            x=-8.32 if right else 7.05
            c(pre+'_tendril',(x,41.52,-1.25),(1.26,6.8,2.5),'frame')
            c(pre+'_tendril',(x-.18,47.45,-1.51),(1.62,1.17,3.0),'cyan')
        c('head',(-7.63,34,-5.24),(15.26,11.73,10.48),'plate')
        c('head',(-6.85,36.23,-5.74),(13.7,4.8,1.11),'vent')

    def rootbound(self):
        c=self.cube
        c('body',(-4.3,18,-2.7),(7.5,13.4,6.04),'frame')
        c('body',(-5.1,26.7,-3.15),(10.1,3.85,5.9),'cloth')
        c('body',(-2,20.1,-3.2),(2.2,8.59,1.04),'rust')
        c('head',(-7,30,-3.3),(6.3,7,6.4),'cloth')
        c('head',(-6.43,32.7,-3.73),(4.97,1.3,.86),'dark')
        for x in (-6.26,-4.8,-3.22):c('head',(x,33.05,-3.94),(.83,.55,.51),'cyan')
        c('head',(-6.8,36.65,.4),(2.15,2.1,2.19),'edge')
        for arm,x,low in (('rightArm',-8.5,12.4),('leftArm',4.27,15.15)):
            c(arm,(x,low,-.88),(2.02,28.3-low,2.93),'frame')
            c(arm,(x-.25,23.2,-1.45),(2.53,4.7,3.8),'cloth')
            c(arm,(x+.37,low+1.75,-1.16),(1.28,5.11,.6),'edge')
        for leg,x in (('leftLeg',.66),('rightLeg',-2.6)):
            c(leg,(x,0,-1.09),(1.94,18.8,2.06),'frame')
            c(leg,(x-.29,0,-1.79),(2.47,2.6,3.26),'cloth')
            c(leg,(x+.2,6.6,-1.38),(1.52,6.33,.83),'plate')

    def siege(self):
        c=self.cube
        c('body',(-7.1,12,-3),(14.2,14.3,22),'frame')
        c('body',(-7.65,23.1,-3.5),(15.3,4.55,22.9),'plate')
        c('body',(-5.17,27,-.4),(10.34,2.2,17.5),'edge')
        for side,x in (('west',-7.89),('east',7.46)):
            for z in (0,7,14):c('body',(x,18.5,z),(.44,4.84,4.2),'cloth',**{side:'cyan'})
        c('neck',(-5.3,21,-12),(10.6,9.5,16.4),'frame')
        c('neck',(-6,23.2,-12.2),(12,5.18,3.25),'plate')
        c('head',(-7.6,15.89,-23.45),(15.2,16.6,15.2),'plate')
        c('head',(-6.76,22.55,-24.28),(13.52,4.11,1.2),'dark',north='slit')
        c('mouth',(-6.6,13.8,-23.39),(13.2,3.45,13.15),'frame')
        c('mouth',(-6.0,14,-23.97),(12,2.0,.73),'vent')
        for x in (-9,7):
            c('horns',(x,26.65,-19.32),(2,9.7,3.2),'frame')
            c('horns',(x+.1,34.8,-20.4),(1.77,1.9,3.01),'edge')
        for i,(x,z) in enumerate(((-11,17),(4,17),(-11,-8),(4,-8))):
            leg='leg'+str(i)
            c(leg,(x,3,z),(6.95,25.1,7.02),'frame')
            c(leg,(x-.39,11.0,z-.37),(7.75,8.89,7.76),'plate')
            c(leg,(x-.64,0,z-.82),(8.21,4.32,8.57),'rubber')
            c(leg,(x+.40,11.38,z-.74),(6.19,1.08,.78),'cyan')

controller=rp+'render_controllers/vanilla_bearframe.render_controllers.json'
renders=json.loads(old.read(controller))
for key,(title,alloy,accent,cloth) in profiles.items():
    m=Frame(key,alloy,accent,cloth)
    if key in ('allay','vex'):m.drone(key=='allay')
    else:
        fn={'witch':m.chemist,'iron_golem':m.golem,'enderman':m.longstride,'warden':m.deep,'creaking':m.rootbound,'ravager':m.siege}[key]
        fn()
    updates[rp+'models/entity/vanilla_'+key+'.geo.json']=enc({'format_version':'1.12.0','minecraft:geometry':[m.geo]})
    client=ref(key,'entity.json')
    d=client['minecraft:client_entity']['description']
    d['materials']={'default':'entity_alphatest'}
    d['geometry']={'default':m.geo['description']['identifier']}
    tex='textures/bearframe/vanilla/'+key
    d['textures']={'default':tex}
    rid='controller.render.bearframe.vanilla_'+key
    d['render_controllers']=[rid]
    render={'geometry':'Geometry.default','materials':[{'*':'Material.default'}],'textures':['Texture.default']}
    updates[rp+'entity/'+key+'.entity.json']=enc(client)
    buf=BytesIO();m.atlas.save(buf,'PNG')
    updates[rp+tex+'.png']=buf.getvalue()
    renders['render_controllers'][rid]=render
updates[controller]=enc(renders)
for pack in ('Bearframe_Behavior','Bearframe_Resources'):
    path=pack+'/manifest.json'
    data=json.loads(old.read(path))
    for a in [data['header'],*data['modules'],*data.get('dependencies',[])]:
        if a.get('version')==[0,7,8]:a['version']=[0,7,9]
    updates[path]=enc(data)
output=folder/'Bearframe_Bedrock_0.7.9.mcaddon'
with ZipFile(output,'w',ZIP_DEFLATED) as out:
    for path in sorted(set(old.namelist())|updates.keys()):
        out.writestr(path,updates[path] if path in updates else old.read(path))
with ZipFile(output) as out:
    assert out.testzip() is None
    for key in profiles:
        p=rp+'entity/'+key+'.entity.json'
        d=json.loads(out.read(p))['minecraft:client_entity']['description']
        native=ref(key,'entity.json')['minecraft:client_entity']['description']
        for part in ('scripts','animations','animation_controllers','enable_attachables','particle_effects','sound_effects'):
            assert d.get(part)==native.get(part),(key,part)
        g=json.loads(out.read(rp+'models/entity/vanilla_'+key+'.geo.json'))['minecraft:geometry'][0]
        bones={b['name']:b for b in g['bones']}
        assert all('parent' not in b or b['parent'] in bones for b in bones.values())
        assert all(x['name'] in bones for x in native_bones(key))
        for b in bones.values():
            for c in b.get('cubes',[]):
                for uv in c['uv'].values():
                    x,y=uv['uv'];w,h=uv['uv_size']
                    assert x+w<=256 and y+h<=256
    assert all(out.read(p)==old.read(p) for p in old.namelist() if p not in updates)
print('Validated eight replacement rigs with preserved vanilla animation and particle references.')
