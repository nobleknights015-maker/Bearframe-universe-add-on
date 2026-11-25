from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from io import BytesIO
import json

# Reuse the existing Bedrock box UV and pixel material builder.
helpers=Path('rebuild.py').read_text().split('\nmodels = ')[0]
exec(compile(helpers,'rebuild.py','exec'))
folder=Path('deliverables')
source=ZipFile(folder/'Bearframe_Bedrock_0.7.4.mcaddon')
rp='Bearframe_Resources/'
bp='Bearframe_Behavior/'
updates={}
names={
 'skeleton':('Echo Marksman',(147,151,141),(201,179,242)),
 'stray':('Frostbound Echo',(143,169,178),(103,204,248)),
 'bogged':('Marsh Echo',(115,130,102),(157,218,92)),
 'parched':('Dustline Echo',(173,149,104),(242,179,75)),
 'wither_skeleton':('Cinder Echo',(73,66,74),(229,91,82)),
}
original=palette.copy()
reference=json.loads(source.read(rp+'models/entity/vanilla_skeleton.geo.json'))['minecraft:geometry'][0]
def enc(data):return (json.dumps(data,indent=2)+'\n').encode()

class EchoRig(Model):
    def __init__(self,key,alloy,optics):
        self.name=key
        self.geo={'description':dict(reference['description']),'bones':[]}
        self.geo['description'].update(identifier='geometry.bearframe.vanilla_'+key,texture_width=256,texture_height=256)
        self.bones={}
        self.atlas=Image.new('RGBA',(256,256))
        self.cache={}
        self.x=self.y=self.row=0
        self.rng=Random(key)
        palette.update(original)
        palette.update(plate=alloy,edge=tuple(min(242,x+33) for x in alloy),cyan=optics)
        palette['optic']=optics
        taller=key=='wither_skeleton'
        factor=1.12 if taller else 1
        for b in reference['bones']:
            name=b['name'];pivot=[round(y*factor,3) if i==1 else y for i,y in enumerate(b['pivot'])]
            self.bone(name,b.get('parent'),pivot)
            if b.get('neverRender'):self.bones[name]['neverRender']=True
        self.height=factor

    def part(self,bone,origin,size,material,**faces):
        x,y,z=origin;w,h,d=size
        self.cube(bone,(x,round(y*self.height,3),z),(w,round(h*self.height,3),d),material,**faces)
    def build(self):
        c=self.part
        c('body',(-1.15,12.1,-1.22),(2.3,11.6,2.4),'frame')
        c('body',(-2.7,12,-1.53),(5.4,2.35,3.05),'edge')
        c('body',(-2.45,15.1,-1.5),(4.9,.63,3.1),'plate')
        c('body',(-3.3,17.6,-1.66),(6.6,.73,3.35),'plate')
        c('body',(-3.65,19.9,-1.75),(7.3,.8,3.5),'edge')
        c('body',(-3.85,22.1,-1.9),(7.7,1.65,3.8),'plate')
        c('body',(-1.13,19.25,-2.04),(2.26,2.62,.65),'dark')
        c('body',(-.52,20.15,-2.24),(1.04,.82,.43),'optic')
        c('body',(-.45,14.1,1.12),(.9,8.0,.72),'rust')
        for x in (-2.68,2.05):
            c('body',(x,16.45,-1.61),(.63,5.75,.75),'frame')
        c('head',(-3.8,28,-3.54),(7.6,3.9,7.02),'plate')
        c('head',(-3.44,25.2,-1.0),(6.88,3.2,4.26),'frame')
        c('head',(-3.56,27.5,-3.69),(7.12,1.6,.84),'dark')
        for x in (-2.71,1.05):
            c('head',(x,27.82,-3.90),(1.66,.73,.43),'optic')
        c('head',(-3.02,24.4,-3.62),(6.04,.88,3.85),'edge')
        c('head',(-3.61,24.9,-3.36),(.62,2.73,2.68),'plate')
        c('head',(2.9,25.6,-3.33),(.64,2.25,2.7),'plate')
        c('head',(-.42,23.6,-.87),(.84,1.85,1.6),'frame')
        for i in (-1,1):
            arm='rightarm' if i<0 else 'leftarm'
            leg='rightleg' if i<0 else 'leftleg'
            ax=5.72*i; lx=2*i
            c(arm,(ax-1.21,20.85,-1.12),(2.42,2.1,2.32),'plate')
            c(arm,(ax-.59,16.65,-.61),(1.18,4.5,1.23),'frame')
            c(arm,(ax-.88,15.72,-.91),(1.76,1.45,1.82),'rust')
            c(arm,(ax-.54,12.6,-.63),(1.08,3.35,1.22),'edge')
            c(arm,(ax-.90,11.65,-.94),(1.8,1.26,1.83),'frame')
            c(leg,(lx-.71,7.15,-.71),(1.42,4.95,1.42),'edge')
            c(leg,(lx-.99,5.6,-1.05),(1.98,1.95,2.09),'frame')
            c(leg,(lx-.5,1.55,-.56),(1,4.45,1.15),'plate')
            c(leg,(lx-1.04,0,-1.47),(2.08,1.63,2.31),'frame')

        if self.name=='skeleton':
            c('rightarm',(-7.02,20.56,-1.58),(1.54,2.8,3.2),'edge')
            c('head',(3.57,26.62,-1.85),(.61,2.72,2.8),'frame',east='optic')
            c('body',(-2.39,17.65,1.48),(1.08,4.75,1.21),'vent')
        elif self.name=='stray':
            palette['cloth']=(59,85,108)
            c('body',(-3.4,21.1,-2.21),(6.8,1.87,4.6),'cloth')
            c('body',(-3.49,14.6,1.72),(3.1,7.1,.69),'cloth')
            c('body',(-.37,17.3,1.79),(3.62,4.2,.71),'cloth')
            c('head',(-3.51,29.9,-3.78),(6.67,2.6,7.47),'cloth')
            c('head',(-3.96,27,1.0),(.65,4.55,2.55),'edge')
        elif self.name=='bogged':
            palette['moss']=(73,108,59);palette['leaf']=(111,145,59);palette['hazard']=(135,66,56)
            self.bone('fungi','head',(0,24,0))
            for x,y,z,w in ((-2.5,31.68,1.4,2.6),(1.4,32.1,-.4,2.2)):
                c('fungi',(x+w/2-.35,y,z),(.7,.86,.7),'rust')
                c('fungi',(x,y+.78,z-.5),(w,1.08,2.03),'hazard')
            c('body',(-3.9,21.9,-1.91),(2.6,1.7,3.83),'moss')
            c('body',(-2.85,17.19,-1.77),(.72,5.05,.68),'leaf')
            c('leftleg',(1.55,3.2,-.72),(1.57,2.8,1.62),'moss')
        elif self.name=='parched':
            palette['cloth']=(126,88,60)
            c('head',(-4.02,29.75,-3.71),(8.04,2.9,7.56),'cloth')
            c('head',(-3.94,27.08,.64),(1.28,4.12,2.99),'cloth')
            c('head',(2.68,26.2,.92),(1.37,5.11,2.81),'cloth')
            c('body',(1.85,13.36,1.69),(1.42,9.61,.77),'cloth')
            c('body',(-3.1,20.84,-1.97),(6.2,1.31,.52),'edge')
            c('rightleg',(-2.92,1.77,-.66),(1.78,2.02,1.37),'cloth')
        else:
            c('body',(-4.04,20.78,-1.86),(8.08,2.31,3.87),'frame')
            c('head',(-3.81,27.4,-3.48),(7.62,1.65,1.13),'frame')
            for x in (-2.52,1.03):c('head',(x,27.81,-3.76),(1.49,.65,.53),'optic')
            c('head',(-3.5,31.8,1.6),(1.1,1.8,1.4),'edge')
            c('rightarm',(-7.18,20.0,-1.31),(2.75,3.09,2.67),'plate')
            c('leftarm',(4.42,20.0,-1.31),(2.75,3.09,2.67),'plate')
        return self

controller=rp+'render_controllers/vanilla_bearframe.render_controllers.json'
renders=json.loads(source.read(controller))
for key,(label,alloy,optics) in names.items():
    m=EchoRig(key,alloy,optics).build()
    gpath=rp+'models/entity/vanilla_'+key+'.geo.json'
    updates[gpath]=enc({'format_version':'1.12.0','minecraft:geometry':[m.geo]})
    path=rp+'entity/'+key+'.entity.json'
    datum=json.loads(source.read(path) if path in source.namelist() else Path('vanilla_client',key+'.entity.json').read_bytes())
    d=datum['minecraft:client_entity']['description']
    d['geometry']={'default':m.geo['description']['identifier']}
    d['materials']={'default':'entity_alphatest'}
    tex='textures/bearframe/vanilla/'+key
    d['textures']={'default':tex}
    r='controller.render.bearframe.vanilla_'+key
    d['render_controllers']=[r]
    renders['render_controllers'][r]={'geometry':'Geometry.default','materials':[{'*':'Material.default'}],'textures':['Texture.default']}
    if key=='bogged':renders['render_controllers'][r]['part_visibility']=[{'fungi':'!query.is_sheared'}]
    updates[path]=enc(datum)
    f=BytesIO();m.atlas.save(f,'PNG')
    updates[rp+tex+'.png']=f.getvalue()
updates[controller]=enc(renders)

for pack in ('Bearframe_Behavior','Bearframe_Resources'):
    path=pack+'/manifest.json'
    data=json.loads(source.read(path))
    for o in [data['header'],*data['modules'],*data.get('dependencies',[])]:
        if o.get('version')==[0,7,4]:o['version']=[0,7,5]
    updates[path]=enc(data)
output=folder/'Bearframe_Bedrock_0.7.5.mcaddon'
with ZipFile(output,'w',ZIP_DEFLATED) as z:
    for path in sorted(set(source.namelist())|updates.keys()):
        z.writestr(path,updates[path] if path in updates else source.read(path))
with ZipFile(output) as z:
    assert z.testzip() is None
    for key in names:
        g=json.loads(z.read(rp+'models/entity/vanilla_'+key+'.geo.json'))['minecraft:geometry'][0]
        bones={b['name']:b for b in g['bones']}
        assert all('parent' not in b or b['parent'] in bones for b in bones.values())
        assert all(bones[k]['cubes'] for k in ('rightarm','leftarm','rightleg','leftleg'))
        assert all(item in bones for item in ('rightItem','leftItem'))
        for b in bones.values():
            for cube in b.get('cubes',[]):
                for uv in cube['uv'].values():
                    x,y=uv['uv'];w,h=uv['uv_size'];assert x+w<=256 and y+h<=256
    for path in source.namelist():
        if path not in updates:assert z.read(path)==source.read(path)
print('Verified five skeletal Echo variants, articulated limb rigs, and preserved equipment attachment points.')
