from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from io import BytesIO
from colorsys import rgb_to_hsv,hsv_to_rgb
import json
from PIL import Image,ImageDraw
from subprocess import run
from bedrock_nbt import Site

base=Path('deliverables')
old=ZipFile(base/'Bearframe_Bedrock_0.7.0.mcaddon')
sf=ZipFile('structure_source/Starbound_Frontier.mcaddon')
sfp=ZipFile(BytesIO(sf.read('Starbound_Frontier_Resources.mcpack')))
bp='Bearframe_Behavior/'
rp='Bearframe_Resources/'
updates={}
def enc(data):return (json.dumps(data,indent=2)+'\n').encode()
def replace(s,a,b):
    assert a in s,a
    return s.replace(a,b,1)
def js(name,modify):
    path=bp+'scripts/'+name
    updates[path]=modify(old.read(path).decode()).encode()

source=json.loads(sfp.read('models/blocks/sf_return_pad.geo.json'))
source['minecraft:geometry'][0]['description']['identifier']='geometry.bearframe.field_log'
updates[rp+'models/blocks/field_log.geo.json']=enc(source)
terrain=json.loads(old.read(rp+'textures/terrain_texture.json'))
for token,path,hue in [('bearframe_field_log','return_pad',.75),('bearframe_field_log_display','return_pad_display_live',.47)]:
    raw=sfp.read('textures/sf/blocks/'+path+'.png')
    im=Image.open(BytesIO(raw)).convert('RGBA')
    for y in range(im.height):
        for x in range(im.width):
            r,g,b,a=im.getpixel((x,y))
            orig,sat,val=rgb_to_hsv(r/255,g/255,b/255)
            if sat>.11:im.putpixel((x,y),tuple(round(c*255) for c in hsv_to_rgb(hue,sat,val))+(a,))
    if path.endswith('live'):
        draw=ImageDraw.Draw(im)
        draw.rectangle((4,3,11,12),fill='#182637')
        for y,x2 in ((5,10),(7,9),(9,10)):
            draw.line((5,y,x2,y),fill='#80e5cf')
    buffer=BytesIO();im.save(buffer,'PNG')
    tex='textures/bearframe/log/'+token
    updates[rp+tex+'.png']=buffer.getvalue()
    terrain['texture_data'][token]={'textures':tex}
updates[rp+'textures/terrain_texture.json']=enc(terrain)

bp_source=ZipFile(BytesIO(sf.read('Starbound_Frontier_Behavior.mcpack')))
block=json.loads(bp_source.read('blocks/return_pad.json'))
b=block['minecraft:block']
b['description']['identifier']='bearframe:field_log'
b['description'].pop('states')
b.pop('permutations')
c=b['components']
c['minecraft:geometry']='geometry.bearframe.field_log'
c['minecraft:material_instances']['*']['texture']='bearframe_field_log'
c['minecraft:material_instances']['front']['texture']='bearframe_field_log_display'
c['minecraft:light_emission']=4
updates[bp+'blocks/field_log.json']=enc(block)
updates[bp+'recipes/field_log.json']=enc({
  'format_version':'1.21.0',
  'minecraft:recipe_shaped':{
    'description':{'identifier':'bearframe:field_log'},
    'tags':['crafting_table'],
    'pattern':['IRI','ICI','III'],
    'key':{'I':{'item':'minecraft:iron_ingot'},'R':{'item':'minecraft:redstone'},'C':{'item':'minecraft:copper_ingot'}},
    'result':{'item':'bearframe:field_log','count':1}
}})
path=rp+'texts/en_US.lang'
updates[path]=old.read(path)+b'\ntile.bearframe:field_log.name=Field Log Terminal\n'

def expedition(s):
    s='import {placeFieldLog,noteActivity} from "./activity_log.js";\n'+s
    s=replace(s,'for(const index of [0,1,2,3,4,5,6,11,15])ensureCityCrew(dim,index);','''for(const index of [0,1,2,3,4,5,6,11,15])ensureCityCrew(dim,index);
    placeFieldLog(dim,"bearframe:log:station",[
      {x:4,y:101,z:3},{x:5,y:101,z:3},{x:4,y:101,z:-3}
    ]);''')
    s=replace(s,'if(def.id==="farfield_camp"){','''if(def.id==="farfield_camp"){
    placeFieldLog(site.dim,"bearframe:log:camp:"+keyAt(site.pos),[
      at(site.pos,[-3,0,2],site.r),at(site.pos,[-3,0,-2],site.r),at(site.pos,[1,0,-2],site.r)
    ]);''')
    s=replace(s,'if(kind===CHEST)return claim(player,site);','''if(kind===CHEST){
    noteActivity(player,"Container",def.name+" service stores",site.pos);
    return claim(player,site);
  }''')
    s=replace(s,'if(staff===0&&player.isSneaking){','''noteActivity(player,"Talk",target.nameTag||target.typeId.split(":")[1].replaceAll("_"," "),target.location);
      if(staff===0&&player.isSneaking){''')
    return s
js('expedition.js',expedition)
def main(s):
    s='import {installActivityLog} from "./activity_log.js";\n'+s
    return s+'\ninstallActivityLog();\n'
js('main.js',main)
def campaign(s):
    s='import {noteActivity} from "./activity_log.js";\n'+s
    s=replace(s,'write(player,state);\n  if(type==="read"&&fresh', '''write(player,state);
  if(fresh&&type==="read")noteActivity(player,"Field entry",EVIDENCE[id]?.name??id,place);
  if(fresh&&type==="repair")noteActivity(player,"Repair",EVIDENCE[id]?.name??id,place);
  if(type==="echo"&&id==="echo_drifter")noteActivity(player,"Talk","Echo Drifter");
  if(type==="read"&&fresh''')
    s=replace(s,'tell(player,"Assignment accepted.', '''noteActivity(player,"Campaign","Accepted The Last Dispatch");
      tell(player,"Assignment accepted.''')
    s=replace(s,'    tell(player,q.report);\n    if(choice)','''    noteActivity(player,"Campaign","Debrief complete: "+q.title);
    tell(player,q.report);
    if(choice)''')
    s=replace(s,'write(player,current);tell(player,"Case accepted: "+q.title);','write(player,current);noteActivity(player,"Side case","Accepted "+q.title);tell(player,"Case accepted: "+q.title);')
    s=replace(s,'    tell(player,q.report);\n  }\n}', '    noteActivity(player,"Side case","Closed "+q.title);\n    tell(player,q.report);\n  }\n}')
    s=replace(s,'    tell(player,"Contract accepted: "+q.title);','    noteActivity(player,"Contract","Accepted "+q.title);\n    tell(player,"Contract accepted: "+q.title);')
    s=replace(s,'    }))tell(player,"Payment received. You can take another commission when ready.");','''    })){
      noteActivity(player,"Contract","Paid for "+q.title);
      tell(player,"Payment received. You can take another commission when ready.");
    }''')
    return s
js('campaign.js',campaign)
updates[bp+'scripts/activity_log.js']=Path('campaign_src/activity_log.js').read_bytes()
for pack in ('Bearframe_Behavior','Bearframe_Resources'):
    path=pack+'/manifest.json'
    data=json.loads(old.read(path))
    for row in [data['header'],*data['modules'],*data.get('dependencies',[])]:
        if row.get('version')==[0,7,0]:row['version']=[0,7,1]
    updates[path]=enc(data)
out=base/'Bearframe_Bedrock_0.7.1.mcaddon'
with ZipFile(out,'w',ZIP_DEFLATED) as z:
    for path in sorted(set(old.namelist())|updates.keys()):
        z.writestr(path,updates[path] if path in updates else old.read(path))
with ZipFile(out) as z:
    assert z.testzip() is None
    for p in updates:
        if p.endswith('.js'):run(['node','--input-type=module','--check'],input=z.read(p),check=True)
        if p.endswith('.json'):json.loads(z.read(p))
    for p in old.namelist():
        if p not in updates:assert z.read(p)==old.read(p)
    core=Site(z.read(bp+'structures/bearframe/orbital_city.mcstructure'))
    assert any(core.get(x,2,z+11)=='air' and core.get(x,3,z+11)=='air' and core.get(x,1,z+11) not in ('air','void') for x,z in ((4,3),(5,3),(4,-3)))
print('Validated recolored pad, recipe, placement, campaign hooks, texture references, and archive.')
