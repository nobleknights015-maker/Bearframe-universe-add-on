from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from io import BytesIO
import json
from PIL import Image
from bedrock_nbt import Site

folder=Path('deliverables')
source=ZipFile(folder/'Bearframe_Bedrock_0.7.9.mcaddon')
odyssey=ZipFile(Path('upload/bbc730fb4d9311a9737b6f49667b4f55.mcpack'))
out=folder/'Bearframe_Bedrock_0.8.0_Star_Odyssey.mcaddon'
rp='Bearframe_Resources/'
bp='Bearframe_Behavior/'
header=json.loads(odyssey.read('manifest.json'))['header']
source_atlas=json.loads(odyssey.read('textures/terrain_texture.json'))
current=json.loads(source.read(rp+'textures/terrain_texture.json'))
materials={
    'bearframe_anchor':'lodestone_side',
    'bearframe_spillway_bulkhead':'iron_block',
    'bearframe_spillway_grate':'blast_furnace_side',
    'bearframe_spillway_luminaire':'sea_lantern',
    'bearframe_spillway_conduit':'oxidized_cut_copper',
    'bearframe_frontier_bulkhead':'iron_block',
    'bearframe_frontier_brace':'netherite_block',
    'bearframe_frontier_deck':'stone_slab_top',
    'bearframe_frontier_marking':'concrete_yellow',
    'bearframe_frontier_lift_conduit':'redstone_lamp_off',
    'bearframe_frontier_slag':'basalt_side',
    'bearframe_frontier_rime':'ice_packed',
    'bearframe_frontier_loam':'dirt_with_roots',
    'bearframe_frontier_dust':'end_stone',
}
updates={}
def enc(obj):return (json.dumps(obj,indent=2)+'\n').encode()
for token,texture in materials.items():
    assert token in current['texture_data']
    path='textures/blocks/'+texture
    im=Image.open(BytesIO(odyssey.read(path+'.png'))).convert('RGBA')
    assert im.size==(16,16) and im.getchannel('A').getextrema()==(255,255)
    current['texture_data'][token]={'textures':path}
# Keep Star Odyssey's own terrain variations reachable in the top atlas,
# including terrain keys beyond those referenced by Bearframe's blocks.
assert not current['texture_data'].keys() & source_atlas['texture_data'].keys()
current['texture_data']={**source_atlas['texture_data'],**current['texture_data']}
updates[rp+'textures/terrain_texture.json']=enc(current)

for root in (bp,rp):
    name=root+'manifest.json'
    data=json.loads(source.read(name))
    for row in [data['header'],*data['modules'],*data.get('dependencies',[])]:
        if row.get('version')==[0,7,9]:row['version']=[0,8,0]
    if root==rp:
        data['header']['name']='Bearframe | Resources (Star Odyssey Edition)'
        data['header']['description']='Bearframe structural materials for the Star Odyssey resource pack.'
        data.setdefault('dependencies',[]).append({'uuid':header['uuid'],'version':header['version']})
    updates[name]=enc(data)

def verify_refs(value):
    if isinstance(value,str) and value.startswith('textures/'):
        assert any(value+ext in odyssey.namelist() or rp+value+ext in source.namelist()
                   for ext in ('.png','.tga','.jpg','.jpeg')) ,value
    elif isinstance(value,dict):
        for v in value.values():verify_refs(v)
    elif isinstance(value,list):
        for v in value:verify_refs(v)
verify_refs(current['texture_data'])
with ZipFile(out,'w',ZIP_DEFLATED) as z:
    for name in source.namelist():z.writestr(name,updates[name] if name in updates else source.read(name))
with ZipFile(out) as z:
    assert z.testzip() is None
    assert set(z.namelist())==set(source.namelist())
    assert {p for p in z.namelist() if z.read(p)!=source.read(p)}==updates.keys()
    templates=[p for p in z.namelist() if p.endswith('.mcstructure') and Site(z.read(p)).w>1]
    print('Full templates retained:',len(templates))
    print('Texture aliases linked:',len(materials))
    print('Star Odyssey terrain definitions linked:',len(source_atlas['texture_data']))
    print('No Star Odyssey texture image files copied.')
