from pathlib import Path
from copy import deepcopy
from zipfile import ZipFile,ZIP_DEFLATED
from collections import deque
import json
from subprocess import run
from bedrock_nbt import Site

base=Path('deliverables')
old=ZipFile(base/'Bearframe_Bedrock_0.6.4.mcaddon')
bp='Bearframe_Behavior/'
updates={}
def enc(data):return (json.dumps(data,indent=2)+'\n').encode()
def replace(s,a,b):
    assert a in s,a
    return s.replace(a,b,1)
def js(path,modify):
    key=bp+'scripts/'+path
    updates[key]=modify(old.read(key).decode()).encode()

archive_ids=[
    'relay_nine','frontier_ruin','crashed_skiff','sealed_archive_bunker',
    'collapsed_transit_bunker','rootbound_service_bunker','flooded_pump_bunker',
    'overgrown_colony','lost_waystation','nivalis_lab','shattered_array',
]
block=json.loads(old.read(bp+'blocks/surface_survey.json'))
definition=block['minecraft:block']
definition['description']={'identifier':'bearframe:field_archive','states':{'bearframe:record':list(range(len(archive_ids)))}}
definition['components']['minecraft:material_instances']['*']['texture']='bearframe_frontier_marking'
definition['components']['minecraft:light_emission']=5
updates[bp+'blocks/field_archive.json']=enc(block)
lang='Bearframe_Resources/texts/en_US.lang'
updates[lang]=old.read(lang)+b'\ntile.bearframe:field_archive.name=Farfield Record Reader\n'

for index,site_id in enumerate(archive_ids):
    path=bp+'structures/bearframe/'+site_id+'_site.mcstructure'
    s=Site(old.read(path))
    w,d=s.w,s.d
    def reach(exclude=None):
        q=deque([(w//2,0),(0,d//2),(w//2,d-1),(w-1,d//2)])
        visited=set()
        while q:
            x,z=q.popleft()
            if (x,z)==exclude or (x,z) in visited or not(0<=x<w and 0<=z<d):continue
            if s.get(x,3,z) in ('air','void','water') or s.get(x,4,z)!='air' or s.get(x,5,z)!='air':continue
            visited.add((x,z))
            q.extend(((x-1,z),(x+1,z),(x,z-1),(x,z+1)))
        return visited
    points=reach()
    # An archive should be in a room or by intact structural remains, near
    # the original site center without blocking a doorway or access to loot.
    candidates=[]
    for x,z in points:
        if abs(x-w//2)<2 or abs(z-d//2)<2:continue
        if any(s.get(x+dx,4,z+dz)=='chest' for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)) if 0<=x+dx<w and 0<=z+dz<d):continue
        adjacent=sum((x+dx,z+dz) in points for dx,dz in ((1,0),(-1,0),(0,1),(0,-1)))
        roof=any(s.get(x,y,z) not in ('air','void') for y in range(6,min(11,s.h)))
        if 2<=adjacent<=3:
            candidates.append((abs(x-w//2)+abs(z-d//2)-(4 if roof else 0),x,z))
    for _,x,z in sorted(candidates):
        if reach((x,z))==points-{(x,z)}:break
    else: raise ValueError(site_id)
    pos=s.index(x,4,z)
    assert str(pos) not in s.metadata
    s.blocks[pos]=s.block('bearframe:field_archive',{'bearframe:record':(3,index)})
    updates[path]=s.raw()

console=deepcopy(block)
defn=console['minecraft:block']
defn['description']={'identifier':'bearframe:dispatch_console','states':{'bearframe:port':[0,1,2]}}
defn['components']['minecraft:material_instances']['*']['texture']='bearframe_spillway_conduit'
updates[bp+'blocks/dispatch_console.json']=enc(console)
updates[lang]+=b'tile.bearframe:dispatch_console.name=Spillway Test Bench Console\n'
path=bp+'structures/bearframe/spillway_facility.mcstructure'
s=Site(old.read(path))
for port,x in enumerate((54,58,62)):
    at=s.index(x,5,15)
    assert s.label(s.blocks[at])=='air' and s.get(x,4,15) not in ('air','void') and s.get(x,5,16)=='air'
    s.blocks[at]=s.block('bearframe:dispatch_console',{'bearframe:port':(3,port)})
updates[path]=s.raw()

def main(s):
    s='import {campaignSignal,installCampaign} from "./campaign.js";\n'+s
    s=replace(s,'if(now.typeId===PANEL)recordSurvey(player,"maintenance_relay");', '''if(now.typeId===PANEL){
        recordSurvey(player,"maintenance_relay");
        campaignSignal(player,"read","maintenance_relay",location);
      }''')
    return s+'\ninstallCampaign('+json.dumps(archive_ids)+');\n'
js('main.js',main)

def expedition(s):
    s='import {campaignSignal,campaignDialogue,ensureDispatchBench} from "./campaign.js";\n'+s
    s=replace(s,'if(current.typeId===site.def.panel)recordSurvey(player,site.def.id);\n        Promise.resolve(interactRegion(player,site,current.typeId,spend)).catch(promiseError);', '''const terminal=current.typeId===site.def.panel;
        if(terminal){
          recordSurvey(player,site.def.id);
          campaignSignal(player,"read",site.def.id,location);
        }
        const result=interactRegion(player,site,current.typeId,spend);
        if(terminal&&phase(site)>=1){
          campaignSignal(player,"repair",site.def.id,location);
          if(site.def.id==="spillway_bunker"&&isRecoverySpillway(site))
            ensureDispatchBench(site,at);
        }
        Promise.resolve(result).catch(promiseError);''')
    s=replace(s,'if(staff===0&&player.isSneaking){reportSurvey(player);return;}', '''if(staff===0&&player.isSneaking){
        reportSurvey(player);
        campaignDialogue(player,target,staff);
        return;
      }
      if(campaignDialogue(player,target,staff))return;
      if(target.typeId==="bearframe:ward_resident"&&player.dimension.id==="minecraft:overworld")
        campaignSignal(player,"echo","ward_resident");''')
    s=replace(s,'The Commons, Farfield annex, and Operations wing are open.', 'Sneak-interact with Mira in the Farfield Annex to begin The Last Dispatch.')
    return s
js('expedition.js',expedition)
def living(s):
    s='import {campaignSignal} from "./campaign.js";\n'+s
    a=s.index('// Echo Drifter: peaceful salvage exchange')
    return s[:a]+replace(s[a:],'''if(!player.isSneaking){
          return say(player,"§d[Echo Drifter]"''','''if(!player.isSneaking){
          if(player.dimension.id==="minecraft:overworld")campaignSignal(player,"echo","echo_drifter");
          return say(player,"§d[Echo Drifter]"''')
js('living_world.js',living)
for name in ('campaign.js','campaign_data.js','campaign_state.js'):
    updates[bp+'scripts/'+name]=Path('campaign_src',name).read_bytes()
for pack in ('Bearframe_Behavior','Bearframe_Resources'):
    path=pack+'/manifest.json'
    data=json.loads(old.read(path))
    for row in [data['header'],*data['modules'],*data.get('dependencies',[])]:
        if row.get('version')==[0,6,4]:row['version']=[0,7,0]
    if pack=='Bearframe_Behavior':data['dependencies'].append({'module_name':'@minecraft/server-ui','version':'2.0.0'})
    updates[path]=enc(data)
out=base/'Bearframe_Bedrock_0.7.0.mcaddon'
with ZipFile(out,'w',ZIP_DEFLATED) as z:
    for path in sorted(set(old.namelist())|updates.keys()):
        z.writestr(path,updates[path] if path in updates else old.read(path))
with ZipFile(out) as z:
    assert z.testzip() is None
    for path in z.namelist():
        if path.endswith('.js'):
            run(['node','--input-type=module','--check'],input=z.read(path),check=True)
        if path.endswith('.json'):json.loads(z.read(path))
        if path.endswith('.mcstructure') and path in updates:
            original=Site(old.read(path));site=Site(z.read(path))
            assert original.metadata==site.metadata
            expected=3 if path.endswith("/spillway_facility.mcstructure") else 1
            assert sum(a!=b for a,b in zip(original.blocks,site.blocks))==expected
            assert any(b['name'][1] in ('bearframe:field_archive','bearframe:dispatch_console') for b in site.palette)
print('11 archives packaged; existing loot and the station templates verified.')
