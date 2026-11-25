from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
from io import BytesIO
import json
import math
from PIL import Image,ImageDraw
from subprocess import run

folder=Path('deliverables')
source=ZipFile(folder/'Bearframe_Bedrock_0.8.1_Star_Odyssey.mcaddon')
bp='Bearframe_Behavior/'
rp='Bearframe_Resources/'
updates={}
def enc(d):return (json.dumps(d,indent=2)+'\n').encode()
def replace(s,a,b):
    assert a in s,a
    return s.replace(a,b,1)
def js(name,patch):
    p=bp+'scripts/'+name
    updates[p]=patch(source.read(p).decode()).encode()

def main(s):
    s='import {registerChartSite,installRouteCharts} from "./route_charts.js";\n'+s
    s=replace(s,'if(marker?.typeId===SPILLWAY_MARKER){','if(marker?.typeId===SPILLWAY_MARKER){\n        registerChartSite("spillway_bunker",dim.id,marker.location,"beacon");')
    s=replace(s,'if(region){prepareBunker(region);greetRegion(region);}', 'if(region){registerChartSite(region.def.id,dim.id,region.pos);prepareBunker(region);greetRegion(region);}')
    s=replace(s,'if(site)activateSite(site);','if(site){registerChartSite("maintenance_relay",dim.id,at(p,[0,2,0]));activateSite(site);}')
    return s+'\ninstallRouteCharts();\n'
js('main.js',main)

def surface(s):
    s='import {registerChartSite,removeChartBeacon} from "./route_charts.js";\n'+s
    s=replace(s,'  const {dimension:dim,location:loc}=marker;','  const {dimension:dim,location:loc}=marker;\n  registerChartSite(site.id,dim.id,loc,"beacon");')
    s=replace(s,'      populateRuin(dim,site.id,base);','''      removeChartBeacon(site.id,dim.id,loc);
      registerChartSite(site.id,dim.id,at(base,[site.size.x>>1,site.deck+1,site.size.z>>1]));
      populateRuin(dim,site.id,base);''')
    return s
js('surface_sites.js',surface)

def spillway(s):
    s='import {registerChartSite,removeChartBeacon} from "./route_charts.js";\n'+s
    s=replace(s,'      world.structureManager.place("bearframe:spillway_facility",dim,origin,{includeEntities:false});','''      world.structureManager.place("bearframe:spillway_facility",dim,origin,{includeEntities:false});
      removeChartBeacon("spillway_bunker",dim.id,datum.location);
      registerChartSite("spillway_bunker",dim.id,at(origin,SPILLWAY_DATUM));''')
    return s
js('spillway.js',spillway)

def campaign(s):
    s='import {archiveChart,openCharts,registerChartSite} from "./route_charts.js";\n'+s
    s=replace(s,'  fieldProgress(player,type,id,place);','''  fieldProgress(player,type,id,place);
  if(type==="read"&&place)registerChartSite(id,player.dimension.id,place);''')
    s=replace(s,'    noteActivity(player,"Campaign","Debrief complete: "+q.title);','    archiveChart(player,"main",state.chapter,q,now);\n    noteActivity(player,"Campaign","Debrief complete: "+q.title);')
    s=replace(s,'    noteActivity(player,"Side case","Closed "+q.title);','    archiveChart(player,"side",q.id,q,current);\n    noteActivity(player,"Side case","Closed "+q.title);')
    s=replace(s,'      noteActivity(player,"Contract","Paid for "+q.title);','      archiveChart(player,"contract",q.id,q,current,r.seen);\n      noteActivity(player,"Contract","Paid for "+q.title);')
    s=replace(s,'"Field directory and coordinates"]','"Field directory and coordinates","Treasure charts"]')
    s=replace(s,'    if(pick===3)await show(player,form("Field directory",journalText(read(player)),["Close"]));','    if(pick===3)await show(player,form("Field directory",journalText(read(player)),["Close"]));\n    if(pick===4)await openCharts(player);')
    return s
js('campaign.js',campaign)

def local(s):
    s='import {archiveChart} from "./route_charts.js";\n'+s
    return replace(s,'        }))noteActivity(player,"Side case","Closed "+entry.quest);','''        })){
          archiveChart(player,"local",key,{title:entry.quest},state,cur.seen);
          noteActivity(player,"Side case","Closed "+entry.quest);
        }''')
js('ecology.js',local)
def activity(s):
    s='import {openCharts} from "./route_charts.js";\n'+s
    s=replace(s,'"Exploration and coordinates","Quest dossier"]','"Exploration and coordinates","Quest dossier","Treasure charts"]')
    s=replace(s,'    const stats=record(player.id),campaign=readCampaign(player);','    if(selection.selection===5){await openCharts(player);return;}\n    const stats=record(player.id),campaign=readCampaign(player);')
    return s
js('activity_log.js',activity)
updates[bp+'scripts/route_charts.js']=Path('campaign_src/route_charts.js').read_bytes()

# Button icons are genuine schematic views of a direction, not invented
# topography. Relative bearing and exact coordinates are provided in text.
def chart_icon(t):
    im=Image.new('RGBA',(48,48))
    d=ImageDraw.Draw(im)
    d.polygon([(4,9),(14,4),(34,6),(42,3),(44,36),(34,43),(14,41),(6,45)],
              fill='#a37545',outline='#593924',width=2)
    d.polygon([(7,10),(15,7),(34,9),(40,6),(41,34),(33,40),(13,38),(8,41)],fill='#dbb883')
    d.line([(8,19),(19,17),(24,22),(32,17),(40,20)],fill='#b48e5b',width=1)
    d.line([(15,8),(14,38)],fill='#c59f6b')
    d.line([(34,9),(33,39)],fill='#c59f6b')
    d.line([(17,11),(24,13),(28,12),(31,14)],fill='#b48e5b')
    d.line([(10,32),(16,30),(18,32),(21,31)],fill='#b48e5b')
    d.polygon([(22,25),(24,22),(26,25),(24,27)],fill='#286b69')
    if t=='unknown':
        d.text((32,9),'?',fill='#6d4029')
        return im
    if t=='charted':dx,dz=0,-1
    else:
        i=['n','ne','e','se','s','sw','w','nw'].index(t)
        dx=math.sin(i*math.pi/4);dz=-math.cos(i*math.pi/4)
    x=round(24+dx*12);y=round(24+dz*12)
    for q in (.29,.5,.68):
        px,py=round(24+(x-24)*q),round(24+(y-24)*q)
        d.point((px,py),fill='#744d37')
    d.line((x-3,y-3,x+3,y+3),fill='#893529',width=2)
    d.line((x+3,y-3,x-3,y+3),fill='#893529',width=2)
    return im

for key in ['n','ne','e','se','s','sw','w','nw','charted','unknown']:
    buf=BytesIO()
    chart_icon(key).save(buf,'PNG')
    updates[rp+'textures/bearframe/charts/'+key+'.png']=buf.getvalue()
for pack in ('Bearframe_Behavior','Bearframe_Resources'):
    path=pack+'/manifest.json'
    data=json.loads(source.read(path))
    for r in [data['header'],*data['modules'],*data.get('dependencies',[])]:
        if r.get('version')==[0,8,1]:r['version']=[0,8,2]
    updates[path]=enc(data)
out=folder/'Bearframe_Bedrock_0.8.2_Star_Odyssey.mcaddon'
with ZipFile(out,'w',ZIP_DEFLATED) as z:
    for path in sorted(set(source.namelist())|updates.keys()):
        z.writestr(path,updates[path] if path in updates else source.read(path))
with ZipFile(out) as z:
    assert z.testzip() is None
    for path in updates:
        if path.endswith('.js'):run(['node','--input-type=module','--check'],input=z.read(path),check=True)
    for path in source.namelist():
        if path not in updates:assert source.read(path)==z.read(path)
print('Chart art, journal integration, quest archives and placement hooks verified.')
