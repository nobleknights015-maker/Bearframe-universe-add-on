from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from io import BytesIO
from collections import Counter
import re,json
from PIL import Image

base=Path('deliverables')
old=ZipFile(base/'Bearframe_Bedrock_0.7.2.mcaddon')
rp='Bearframe_Resources/'
bp='Bearframe_Behavior/'
refs=Path('vanilla_client')
updates={}
targets={
 'zombie':('echo_lost','Lost Echo',(235,103,87),'humanoid'),
 'husk':('echo_lost','Dustbound Echo',(220,157,83),'humanoid'),
 'drowned':('echo_drifter','Submerged Echo',(86,191,195),'humanoid'),
 'zombie_villager':('ward_resident','Fractured Ward Echo',(233,101,111),'humanoid'),
 'zombie_villager_v2':('ward_resident','Fractured Ward Echo',(233,101,111),'humanoid'),
 'skeleton':('echo_sentinel','Echo Marksman',(183,190,226),'humanoid'),
 'stray':('echo_sentinel','Frostbound Echo',(105,174,237),'humanoid'),
 'bogged':('echo_drifter','Marsh Echo',(141,195,96),'humanoid'),
 'villager':('ward_resident','Echo Villager',(229,184,105),'villager'),
 'villager_v2':('ward_resident','Echo Villager',(229,184,105),'villager'),
 'wandering_trader':('echo_route_trader','Echo Wayfarer',(88,205,198),'villager'),
 'pillager':('directorate_guard','Nullframe Raider',(220,46,53),'humanoid'),
 'vindicator':('nullframe_hunter','Nullframe Breacher',(248,79,62),'vindicator'),
 'evocation_illager':('directorate_officer','Nullframe Signal Officer',(241,62,97),'evoker'),
}
def enc(data):return (json.dumps(data,indent=2)+'\n').encode()
def recolor(im,accent,kind):
    out=im.copy()
    pixels=out.load()
    for y in range(out.height):
        for x in range(out.width):
            r,g,b,a=pixels[x,y]
            # Change the emissive cluster, while preserving ivory armor
            # and low-saturation wear and mechanical seams.
            pink=max(r,b)>157 and abs(r-g)>30 and b>g+23
            teal=g>120 and b>110 and min(g,b)>r+35
            amber=r>165 and 80<g<222 and 30<b<147 and r>b+75 and g>b+26
            red=r>155 and r>max(g,b)+65 and max(g,b)<126
            if pink or teal or amber or red:
                factor=.87 if max(r,g,b)<207 else 1
                pixels[x,y]=tuple(int(v*factor) for v in accent)+(a,)
    return out
def png(img):
    io=BytesIO();img.save(io,'PNG')
    return io.getvalue()

render={'format_version':'1.8.0','render_controllers':{}}
labels={}
professions=[
 (126,179,153),(198,184,108),(161,172,187),(214,155,115),(143,205,226),
 (180,129,215),(224,191,95),(92,173,218),(226,126,124),(120,189,172),
 (209,166,226),(181,201,103),(223,163,93),(191,195,178),(149,183,218),
]
models=[]
for vanilla,(base_model,label,accent,kind) in targets.items():
    d=json.loads((refs/(vanilla+'.entity.json')).read_text())
    client=d['minecraft:client_entity']['description']
    assert client['identifier']=='minecraft:'+vanilla
    geometry=json.loads(old.read(rp+'models/entity/'+base_model+'.geo.json'))
    g=geometry['minecraft:geometry'][0]
    g['description']['identifier']='geometry.bearframe.vanilla_'+vanilla
    source=Image.open(BytesIO(old.read(rp+'textures/bearframe/'+base_model+'.png'))).convert('RGBA')
    limb0,limb1=('leg0','leg1') if kind in ('villager','vindicator') else ('rightleg','leftleg')
    rename={'root':'waist','arm0':'rightarm','arm1':'leftarm','leg0':limb0,'leg1':limb1}
    bones={b['name']:b for b in g['bones']}
    # The vanilla animation channels continue to drive body, look, riding,
    # spellcasting and held weapons. Original armor meshes use those channels.
    for b in bones.values():
        b['name']=rename.get(b['name'],b['name'])
        if 'parent' in b:b['parent']=rename.get(b['parent'],b['parent'])
    bones['root']['pivot']=[0,12,0]
    for i,(bone,item,x) in enumerate((('rightarm','rightItem',-6),('leftarm','leftItem',6))):
        g['bones'].append({'name':item,'parent':bone,'pivot':[x,15,1],'neverRender':True})
    folded=kind in ('villager','vindicator','evoker')
    if folded:
        # This is original armor, with the original arm UVs reused on a
        # compact, crossed-arm pose driven by the vanilla 'arms' channel.
        uv=bones['arm0']['cubes'][0]['uv']
        g['bones'].append({'name':'arms','parent':'body','pivot':[0,22,0],'cubes':[
            {'origin':[-5.8,14.8,-3.0],'size':[2.5,6.2,2.5],'uv':uv},
            {'origin':[3.3,14.8,-3.0],'size':[2.5,6.2,2.5],'uv':uv},
            {'origin':[-3.65,15,-4.8],'size':[7.3,2.6,2.6],'uv':bones['arm0']['cubes'][-1]['uv']},
        ]})
    # Preserve animation definitions and spawn-egg appearance from the
    # matching vanilla client. Single custom textures replace overlay stacks.
    client['materials']={'default':'entity_alphatest'}
    client['geometry']={'default':g['description']['identifier']}
    client['textures']={'default':'textures/bearframe/vanilla/'+vanilla}
    client['render_controllers']=['controller.render.bearframe.vanilla_'+vanilla]
    client['scripts']=client.get('scripts',{})
    if '2.0' in str(client['scripts'].get('scale','')):
        client['scripts']['scale']='0.9375' if kind=='villager' else '1.0'
    controllers={'geometry':'Geometry.default','materials':[{'*':'Material.default'}],'textures':['Texture.default']}
    if kind=='villager':
        controllers['part_visibility']=[{'leftarm':False},{'rightarm':False}]
    elif kind=='vindicator':
        controllers['part_visibility']=[{'arms':'!query.is_angry'},{'leftarm':'query.is_angry'},{'rightarm':'query.is_angry'}]
    if vanilla=='villager_v2':
        # Vanilla profession variant stays visible as distinct trim colors.
        values=[]
        for slot,color in enumerate(professions):
            name='trade_'+str(slot)
            tex=client['textures']['default']+'_'+str(slot)
            client['textures'][name]=tex
            updates[rp+tex+'.png']=png(recolor(source,color,kind))
            values.append('Texture.'+name)
        controllers['arrays']={'textures':{'Array.professions':values}}
        controllers['textures']=['Array.professions[math.clamp(query.variant, 0, 14)]']
    tex=client['textures']['default']
    updates[rp+tex+'.png']=png(recolor(source,accent,kind))
    updates[rp+'entity/'+vanilla+'.entity.json']=enc(d)
    updates[rp+'models/entity/vanilla_'+vanilla+'.geo.json']=enc(geometry)
    render['render_controllers'][client['render_controllers'][0]]=controllers
    labels[vanilla]=label
    models.append((vanilla,label,geometry,tex))
updates[rp+'render_controllers/vanilla_bearframe.render_controllers.json']=enc(render)

for pack in ('Bearframe_Behavior','Bearframe_Resources'):
    p=pack+'/manifest.json'
    data=json.loads(old.read(p))
    for obj in [data['header'],*data['modules'],*data.get('dependencies',[])]:
        if obj.get('version')==[0,7,2]:obj['version']=[0,7,3]
    updates[p]=enc(data)
out=base/'Bearframe_Bedrock_0.7.3.mcaddon'
with ZipFile(out,'w',ZIP_DEFLATED) as z:
    for path in sorted(set(old.namelist())|updates.keys()):
        z.writestr(path,updates[path] if path in updates else old.read(path))
with ZipFile(out) as z:
    assert z.testzip() is None
    for path in old.namelist():
        if path not in updates: assert z.read(path)==old.read(path)
    for vanilla,label,model,tex in models:
        g=model['minecraft:geometry'][0]
        names={b['name'].lower() for b in g['bones']}
        assert len(names)==len(g['bones'])
        assert all('parent' not in b or b['parent'].lower() in names for b in g['bones'])
        assert {'head','rightarm','leftarm','rightitem','leftitem'}<=names
        img=Image.open(BytesIO(z.read(rp+tex+'.png')))
        assert img.size==(g['description']['texture_width'],g['description']['texture_height'])
        client=json.loads(z.read(rp+'entity/'+vanilla+'.entity.json'))['minecraft:client_entity']['description']
        own=json.loads((refs/(vanilla+'.entity.json')).read_text())['minecraft:client_entity']['description']
        assert client['animations']==own['animations']
        for png_path in client['textures'].values():assert rp+png_path+'.png' in z.namelist()
print('Validated 14 visual overrides, 15 villager profession trims, and unchanged vanilla behavior sources.')
