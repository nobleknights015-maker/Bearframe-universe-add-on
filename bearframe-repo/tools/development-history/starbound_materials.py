from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from io import BytesIO
import json
from bedrock_nbt import Site
from PIL import Image,ImageDraw,ImageFont

folder=Path('deliverables')
original=ZipFile('structure_source/Starbound_Frontier.mcaddon')
resources=ZipFile(BytesIO(original.read('Starbound_Frontier_Resources.mcpack')))
source=ZipFile(folder/'Bearframe_Bedrock_0.6.0.mcaddon')
out=folder/'Bearframe_Bedrock_0.6.1.mcaddon'
bp='Bearframe_Behavior/'
rp='Bearframe_Resources/'
materials={
 'frontier_bulkhead':('bulkhead','Frontier Bulkhead'),
 'frontier_brace':('brace','Frontier Structural Brace'),
 'frontier_deck':('deck','Frontier Deck Panel'),
 'frontier_marking':('marking','Frontier Marked Panel'),
 'frontier_lift_conduit':('power_conduit','Frontier Power Conduit'),
 'frontier_slag':('oxidized_slag','Oxidized Slag'),
 'frontier_rime':('rime_stone','Rime Stone'),
 'frontier_loam':('root_loam','Root Loam'),
 'frontier_dust':('lunar_dust','Lunar Dust'),
}
updates={}
def enc(value): return (json.dumps(value,indent=2)+'\n').encode()
terrain=json.loads(source.read(rp+'textures/terrain_texture.json'))
casing=json.loads(source.read(bp+'blocks/spillway_casing.json'))
lang=source.read(rp+'texts/en_US.lang').decode().rstrip()+'\n'
atlas={}
for key,(name,label) in materials.items():
    tex='textures/bearframe/frontier/'+name
    token='bearframe_'+key
    raw=resources.read('textures/sf/blocks/'+name+'.png')
    img=Image.open(BytesIO(raw)).convert('RGBA')
    assert img.getbbox() is not None
    atlas[key]=img
    updates[rp+tex+'.png']=raw
    terrain['texture_data'][token]={'textures':tex}
    data=json.loads(json.dumps(casing))
    entry=data['minecraft:block']
    entry['description']['identifier']='bearframe:'+key
    entry['components']['minecraft:material_instances']['*']['texture']=token
    updates[bp+'blocks/'+key+'.json']=enc(data)
    lang+='tile.bearframe:'+key+'.name='+label+'\n'
updates[rp+'textures/terrain_texture.json']=enc(terrain)
updates[rp+'texts/en_US.lang']=lang.encode()

for path in source.namelist():
    if not path.startswith(bp+'structures/bearframe/') or not path.endswith('.mcstructure'): continue
    name=Path(path).stem
    if name=='orbital_city': continue
    site=Site(source.read(path))
    if site.w<2: continue
    deck=4 if name=='spillway_facility' else 8 if name=='shelter_bunker' else 13 if name in {'rainline_town_site','saltline_town_site','farfield_camp_site','grid_hub_site','echo_ward_site','intrusion_checkpoint_site','foundry_annex_site','maintenance_relay_site'} else 3
    base=site.blocks.copy()
    labels=[site.label(b) for b in base]
    converted={}
    def material_for(x,y,z,n):
        if name.startswith('cinder_') and n in ('tuff','blackstone') and y==deck: return 'frontier_slag'
        if name.startswith('nivalis_') and n=='calcite': return 'frontier_rime'
        if name.startswith('verdantis_') and n in ('rooted_dirt','coarse_dirt'): return 'frontier_loam'
        if name.startswith('shattered_') and n in ('end_stone','tuff') and y==deck: return 'frontier_dust'
        if n=='iron_block': return 'frontier_bulkhead'
        if n=='smooth_quartz' and y>deck+1 and (x//3+z//3)%3!=0: return 'frontier_bulkhead'
        if n in ('polished_deepslate','polished_blackstone') and y>=deck+2 and (x//3+z//3)%3==0: return 'frontier_brace'
        if n in ('polished_andesite','smooth_stone') and y==deck and (x//4+z//4)%3!=0: return 'frontier_deck'
        if n in ('orange_terracotta','cyan_terracotta','yellow_terracotta') and y>deck+1: return 'frontier_marking'
        if n=='oxidized_cut_copper' and y>=deck+3 and (x//3+z//3)%2: return 'frontier_lift_conduit'
        if n=='stone_bricks' and y==deck and (x%7==0 or z%7==0): return 'frontier_deck'
    for i,n in enumerate(labels):
        if n in ('air','void') or str(i) in site.metadata: continue
        x,y,z=site.xyz(i)
        key=material_for(x,y,z,n)
        if key:
            if key not in converted: converted[key]=site.block('bearframe:'+key)
            site.blocks[i]=converted[key]
    assert sum(a!=b for a,b in zip(base,site.blocks))>0,name
    updates[path]=site.raw()

for pack in ('Bearframe_Behavior','Bearframe_Resources'):
    path=pack+'/manifest.json'
    m=json.loads(source.read(path))
    for r in [m['header'],*m['modules'],*m.get('dependencies',[])]:
        if r.get('version')==[0,6,0]:r['version']=[0,6,1]
    updates[path]=enc(m)
with ZipFile(out,'w',ZIP_DEFLATED) as archive:
    for p in sorted(set(source.namelist())|updates.keys()):
        archive.writestr(p,updates[p] if p in updates else source.read(p))
with ZipFile(out) as archive:
    assert archive.testzip() is None
    assert archive.read(bp+'structures/bearframe/orbital_city.mcstructure')==source.read(bp+'structures/bearframe/orbital_city.mcstructure')
    assert len([p for p in updates if p.endswith('.mcstructure')])==28
    for p in updates:
        if p.endswith('.json'):json.loads(archive.read(p))
        if p.endswith('.mcstructure'):
            site=Site(archive.read(p))
            assert all(len(b)==site.w*site.h*site.d and -1<=min(b)<=max(b)<len(site.palette) for _,b in site.layers)
            for idx in {i for i in site.blocks if i>=0}:
                name=site.palette[idx]['name'][1]
                if name in {'bearframe:'+key for key in materials}: assert bp+'blocks/'+name.split(':')[1]+'.json' in archive.namelist()

sheet=Image.new('RGB',(930,795),'#172024')
draw=ImageDraw.Draw(sheet)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans'
draw.text((34,25),'Starbound Frontier materials',fill='#eaf1ef',font=ImageFont.truetype(font+'-Bold.ttf',40))
draw.text((37,83),'Original texture samples used in Bearframe Bedrock 0.6.1',fill='#a8c0be',font=ImageFont.truetype(font+'.ttf',21))
for i,(key,(_,label)) in enumerate(materials.items()):
    x,y=31+(i%3)*291,128+(i//3)*215
    draw.rounded_rectangle((x,y,x+277,y+201),radius=12,fill='#263337',outline='#52696a')
    im=atlas[key].resize((136,136),Image.Resampling.NEAREST)
    sheet.paste(im,(x+70,y+16),im)
    draw.text((x+138,y+167),label,anchor='mt',font=ImageFont.truetype(font+'-Bold.ttf',17),fill='#e6f0ee')
sheet.save(folder/'Bearframe_0.6.1_Starbound_Materials.png')
print('Verified 28 updated templates, 9 original Starbound textures and block registrations, and identical Bearframe Station.')
