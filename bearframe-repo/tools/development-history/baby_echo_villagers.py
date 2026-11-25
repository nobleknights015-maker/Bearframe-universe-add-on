from copy import deepcopy
import json
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED

base=Path('deliverables')
old=ZipFile(base/'Bearframe_Bedrock_0.7.7.mcaddon')
rp='Bearframe_Resources/'
bp='Bearframe_Behavior/'
updates={}
mobs=('villager','villager_v2')
def encode(data):return (json.dumps(data,indent=2)+'\n').encode()
def load(path):return json.loads(old.read(path))
def half(seq):return [round(v*.5,4) for v in seq]

render=rp+'render_controllers/vanilla_bearframe.render_controllers.json'
r=load(render)
for mob in mobs:
    path=rp+'models/entity/vanilla_'+mob+'.geo.json'
    data=load(path)
    adult=data['minecraft:geometry'][0]
    child=deepcopy(adult)
    desc=child['description']
    desc['identifier']+='_baby'
    # Preserve native villager age scaling and trade and sleeping animations.
    for b in child['bones']:
        if 'pivot' in b:b['pivot']=half(b['pivot'])
        for cube in b.get('cubes',[]):
            for key in ('origin','size','pivot'):
                if key in cube:cube[key]=half(cube[key])
    data['minecraft:geometry'].append(child)
    updates[path]=encode(data)
    path=rp+'entity/'+mob+'.entity.json'
    entity=load(path)
    client=entity['minecraft:client_entity']['description']
    client['geometry']['baby']=desc['identifier']
    client['scripts']['scale']='query.is_baby ? 2.0 : 0.9375' if mob=='villager_v2' else 'query.is_baby ? 1.875 : 0.9375'
    c=r['render_controllers'][client['render_controllers'][0]]
    c.setdefault('arrays',{})['geometries']={'Array.bearframe_age':['Geometry.default','Geometry.baby']}
    c['geometry']='Array.bearframe_age[query.is_baby ? 1 : 0]'
    if mob=='villager_v2':
        c['arrays']['textures']['Array.professions'].append('Texture.default')
        c['textures']=['Array.professions[query.is_baby ? 15 : math.clamp(query.variant, 0, 14)]']
    updates[path]=encode(entity)
updates[render]=encode(r)

for pack in ('Bearframe_Behavior','Bearframe_Resources'):
    path=pack+'/manifest.json'
    data=load(path)
    for row in [data['header'],*data['modules'],*data.get('dependencies',[])]:
        if row.get('version')==[0,7,7]:row['version']=[0,7,8]
    updates[path]=encode(data)

output=base/'Bearframe_Bedrock_0.7.8.mcaddon'
with ZipFile(output,'w',ZIP_DEFLATED) as out:
    for path in old.namelist():out.writestr(path,updates[path] if path in updates else old.read(path))
with ZipFile(output) as out:
    assert out.testzip() is None
    for mob in mobs:
        p=rp+'models/entity/vanilla_'+mob+'.geo.json'
        adult,child=json.loads(out.read(p))['minecraft:geometry']
        assert adult==load(p)['minecraft:geometry'][0]
        for a,b in zip(adult['bones'],child['bones'],strict=True):
            assert a['name']==b['name'] and half(a['pivot'])==b['pivot']
            for c,d in zip(a.get('cubes',[]),b.get('cubes',[]),strict=True):
                assert c['uv']==d['uv'] and half(c['size'])==d['size']
        path=rp+'entity/'+mob+'.entity.json'
        current=json.loads(out.read(path))['minecraft:client_entity']['description']
        before=load(path)['minecraft:client_entity']['description']
        assert current['animations']==before['animations']
        assert current['geometry']['baby']==child['description']['identifier']
    assert all(out.read(path)==old.read(path) for path in old.namelist() if path not in updates)
print('Both baby Echo villager rigs verified. Adult armor and profession colors retained.')
