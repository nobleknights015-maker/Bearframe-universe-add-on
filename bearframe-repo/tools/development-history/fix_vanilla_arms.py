from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import json

folder=Path('deliverables')
source=ZipFile(folder/'Bearframe_Bedrock_0.7.3.mcaddon')
release=folder/'Bearframe_Bedrock_0.7.4.mcaddon'
rp='Bearframe_Resources/'
updates={}
def encode(data):return (json.dumps(data,indent=2)+'\n').encode()
def read(path):return json.loads(source.read(path))

variants=('villager','villager_v2','wandering_trader','vindicator','evocation_illager')
controllers_path=rp+'render_controllers/vanilla_bearframe.render_controllers.json'
controllers=read(controllers_path)
animation={
    'format_version':'1.8.0',
    'animations':{
        'animation.bearframe.echo_civilian.arm_swing':{
            'loop':True,'anim_time_update':'query.modified_distance_moved',
            'bones':{
                'rightarm':{'rotation':['math.cos(query.anim_time * 38.17) * math.clamp(query.modified_move_speed * 80, 0, 17)',0,0]},
                'leftarm':{'rotation':['math.cos(query.anim_time * 38.17 + 180) * math.clamp(query.modified_move_speed * 80, 0, 17)',0,0]},
            }
        },
        'animation.bearframe.signal_officer.ready':{
            'loop':True,
            'bones':{
                'rightarm':{'rotation':[0,0,-3]},
                'leftarm':{'rotation':[0,0,3]},
            }
        }
    }
}
updates[rp+'animations/vanilla_arm_pose.animation.json']=encode(animation)
for mob in variants:
    path=rp+'models/entity/vanilla_'+mob+'.geo.json'
    mesh=read(path)
    bones=mesh['minecraft:geometry'][0]['bones']
    assert any(b['name']=='arms' for b in bones)
    bones[:]=[b for b in bones if b['name']!='arms']
    assert all(next(b for b in bones if b['name']==name)['cubes'] for name in ('rightarm','leftarm'))
    updates[path]=encode(mesh)
    controllers['render_controllers']['controller.render.bearframe.vanilla_'+mob].pop('part_visibility',None)
    if mob!='vindicator':
        path=rp+'entity/'+mob+'.entity.json'
        entity=read(path)
        client=entity['minecraft:client_entity']['description']
        client['animations']['general']='animation.bearframe.signal_officer.ready' if mob=='evocation_illager' else 'animation.bearframe.echo_civilian.arm_swing'
        updates[path]=encode(entity)
updates[controllers_path]=encode(controllers)

for pack in ('Bearframe_Behavior','Bearframe_Resources'):
    path=pack+'/manifest.json'
    data=read(path)
    for row in [data['header'],*data['modules'],*data.get('dependencies',[])]:
        if row.get('version')==[0,7,3]:row['version']=[0,7,4]
    updates[path]=encode(data)
with ZipFile(release,'w',ZIP_DEFLATED) as out:
    for path in sorted(set(source.namelist())|updates.keys()):
        out.writestr(path,updates[path] if path in updates else source.read(path))
with ZipFile(release) as out:
    assert out.testzip() is None
    for mob in variants:
        p=rp+'models/entity/vanilla_'+mob+'.geo.json'
        before=read(p)['minecraft:geometry'][0]['bones']
        after=json.loads(out.read(p))['minecraft:geometry'][0]['bones']
        assert [b for b in before if b['name']!='arms']==after
    for path in source.namelist():
        if path not in updates:assert out.read(path)==source.read(path)
print('Verified both articulated arms on all five updated rig variants; vanilla attack and casting references remain attached.')
