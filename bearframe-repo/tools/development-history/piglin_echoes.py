from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from io import BytesIO
from copy import deepcopy
import json

exec(compile(Path('rebuild.py').read_text().split('\nmodels = ')[0],'rebuild.py','exec'))
base=Path('deliverables')
old=ZipFile(base/'Bearframe_Bedrock_0.7.6.mcaddon')
rp='Bearframe_Resources/'
bp='Bearframe_Behavior/'
updates={}
def encode(data):return (json.dumps(data,indent=2)+'\n').encode()
profiles={
 'piglin':('Foundry Salvager',(139,115,94),(246,184,81),(87,66,54),True),
 'piglin_brute':('Vault Warden',(89,81,75),(248,156,73),(51,41,40),False),
 'zombie_pigman':('Scorched Salvager',(116,99,84),(217,85,66),(67,74,61),True),
}
colors=palette.copy()

class Salvager(Model):
    def __init__(self,key,alloy,glow,wrap):
        self.name=key
        self.geo={'description':dict(identifier='geometry.bearframe.vanilla_'+key,texture_width=256,texture_height=256,
                                     visible_bounds_width=2.25,visible_bounds_height=3.0,visible_bounds_offset=[0,1,0]),'bones':[]}
        self.bones={}
        self.atlas=Image.new('RGBA',(256,256))
        self.cache={}
        self.x=self.y=self.row=0
        self.rng=Random(key)
        palette.update(colors)
        palette.update(plate=alloy, edge=tuple(min(v+34,255) for v in alloy), cloth=wrap, cyan=glow, bezel=(144,101,54))
        self.bone('waist',None,[0,12,0])
        self.bone('body','waist',[0,24,0])
        self.bone('head','body',[0,24,0])
        for side,sign in (('right',-1),('left',1)):
            arm=side+'arm'
            self.bone(arm,'body',[6*sign,22,0])
            self.bone(side+'leg','body',[2*sign,12,0])
            hand=side+'Item'
            self.bone(hand,arm,[6*sign,15,1])
            self.bones[hand]['neverRender']=True

    def build(self):
        c=self.cube
        t=self.name
        brute=t=='piglin_brute'; gone=t=='zombie_pigman'
        c('body',(-3.8,12.0,-2),(7.6,12,4),'frame')
        c('body',(-3.65,18,-2.6),(7.3,4.9,.96),'plate')
        c('body',(-3.5,12.85,-2.35),(7,2.0,.75),'bezel')
        c('body',(-2.38,18.85,-3.07),(4.76,2.7,.72),'dark',north='slit')
        c('head',(-3.95,24,-3.85),(7.9,8,7.7),'frame')
        c('head',(-3.8,29,-3.98),(7.6,3.0,7.92),'plate')
        c('head',(-3.53,26.62,-4.02),(7.06,2.16,.57),'dark')
        for x in (-2.65,1.05):
            c('head',(x,27.24,-4.18),(1.64,.84,.42),'cyan')
        c('head',(-3.24 if not gone else -.28,24.3,-3.96),(6.48 if not gone else 3.55,1.94,.59),'plate')
        for x,side in ((-4.43,'west'),(3.83,'east')):
            c('head',(x,26.66,-.96),(.61,2.32,2.86),'bezel',**{side:'cyan'})
        for i,(side,sign) in enumerate((('right',-1),('left',1))):
            arm=side+'arm';leg=side+'leg'
            x=-8 if sign<0 else 4
            lx=-4 if sign<0 else 0
            c(arm,(x+.15,12,-1.7),(3.7,12,3.4),'frame')
            c(leg,(lx+.24,0,-1.81),(3.52,12,3.62),'frame')
            if not gone or i==0:
                c(arm,(x-.15,20.4,-2.21),(4.3,3.2,4.42),'plate')
                c(arm,(x+.25,13.0,-2.27),(3.5,3.65,.78),'plate')
            else:
                c(arm,(x+.94,13.32,-1.98),(.75,7.1,.57),'rust')
                c(arm,(x+.9,16.0,-2.17),(.81,1.36,.63),'cyan')
            c(leg,(lx+.21,.55,-2.38),(3.58,4.32,.82),'plate')
            c(leg,(lx+.25,7.07,-2.18),(3.5,3.49,.65),'plate' if not gone or i==0 else 'frame')
            c(leg,(lx+.09,0,-2.45),(3.82,1.22,4.35),'rubber')
            if brute:
                c(arm,(x-.55,20.2,-2.47),(5.1,3.85,4.94),'frame')
                c(arm,(x-.28,22.0,-2.59),(4.55,1.27,5.18),'edge')
        if brute:
            c('body',(-3.77,13.9,1.97),(7.54,8.91,.84),'cloth',south='hazard')
            c('body',(-3.45,20.8,-3.13),(6.9,1.27,.8),'bezel')
        elif gone:
            c('body',(2.65,15.1,-2.87),(1.11,4.74,.94),'rust')
            c('body',(-3.42,14.6,-2.53),(1.03,6.12,.61),'cloth')
            c('head',(-3.75,25.5,-4.15),(1.22,2.96,.61),'edge')
        else:
            c('body',(-3.22,14.2,1.78),(6.44,7.57,2.13),'cloth',south='vent')
            c('body',(-2.96,16.4,3.57),(2.1,4.08,.79),'bezel')
            c('body',(1.17,13.82,-2.81),(2.44,3.39,.96),'cloth',north='badge')
            c('body',(-3.25,20.9,-2.47),(6.5,1.4,4.85),'cloth')
        return self

def half(seq):return [round(v*.5,4) for v in seq]
controller=rp+'render_controllers/vanilla_bearframe.render_controllers.json'
renders=json.loads(old.read(controller))
for key,(label,alloy,glow,wrap,baby) in profiles.items():
    m=Salvager(key,alloy,glow,wrap).build()
    geometries=[m.geo]
    path=rp+'models/entity/vanilla_'+key+'.geo.json'
    if baby:
        mini=deepcopy(m.geo)
        mini['description']['identifier']+='_baby'
        for b in mini['bones']:
            if 'pivot' in b:b['pivot']=half(b['pivot'])
            for cube in b.get('cubes',[]):
                for name in ('origin','size','pivot'):
                    if name in cube:cube[name]=half(cube[name])
        geometries.append(mini)
    updates[path]=encode({'format_version':'1.12.0','minecraft:geometry':geometries})
    path=rp+'entity/'+key+'.entity.json'
    client=json.loads(Path('vanilla_client',key+'.entity.json').read_bytes())
    d=client['minecraft:client_entity']['description']
    d['materials']={'default':'entity_alphatest'}
    d['geometry']={'default':m.geo['description']['identifier']}
    tex='textures/bearframe/vanilla/'+key
    d['textures']={'default':tex}
    key_r='controller.render.bearframe.vanilla_'+key
    d['render_controllers']=[key_r]
    render={'geometry':'Geometry.default','materials':[{'*':'Material.default'}],'textures':['Texture.default']}
    if baby:
        d['geometry']['baby']=mini['description']['identifier']
        render['arrays']={'geometries':{'Array.bearframe_age':['Geometry.default','Geometry.baby']}}
        render['geometry']='Array.bearframe_age[query.is_baby ? 1 : 0]'
    renders['render_controllers'][key_r]=render
    updates[path]=encode(client)
    buf=BytesIO();m.atlas.save(buf,'PNG')
    updates[rp+tex+'.png']=buf.getvalue()
updates[controller]=encode(renders)
for pack in ('Bearframe_Behavior','Bearframe_Resources'):
    path=pack+'/manifest.json'
    data=json.loads(old.read(path))
    for row in [data['header'],*data['modules'],*data.get('dependencies',[])]:
        if row.get('version')==[0,7,6]:row['version']=[0,7,7]
    updates[path]=encode(data)
output=base/'Bearframe_Bedrock_0.7.7.mcaddon'
with ZipFile(output,'w',ZIP_DEFLATED) as out:
    for path in sorted(set(old.namelist())|updates.keys()):
        out.writestr(path,updates[path] if path in updates else old.read(path))
with ZipFile(output) as out:
    assert out.testzip() is None
    for key,(_,_,_,_,baby) in profiles.items():
        p=rp+'entity/'+key+'.entity.json'
        desc=json.loads(out.read(p))['minecraft:client_entity']['description']
        vanilla=json.loads(Path('vanilla_client',key+'.entity.json').read_bytes())['minecraft:client_entity']['description']
        for prop in ('scripts','animations','enable_attachables'):assert desc[prop]==vanilla[prop]
        g=json.loads(out.read(rp+'models/entity/vanilla_'+key+'.geo.json'))['minecraft:geometry']
        assert len(g)==(2 if baby else 1)
        assert ('baby' in desc['geometry'])==baby
        for shape in g:
            bones={b['name']:b for b in shape['bones']}
            assert all('parent' not in b or b['parent'] in bones for b in bones.values())
            assert bones['leftarm']['cubes'] and bones['rightarm']['cubes']
    assert all(out.read(path)==old.read(path) for path in old.namelist() if path not in updates)
print('Verified Piglin, Piglin Brute, and Zombified Piglin client replacements, including both baby forms.')
