"""Convert the owner-provided Java world to sparse Bedrock bunker tiles.
Run extract.py and mask.py first, and bed_palette.py against the base pack.
No Java entities, player data, or Java item NBT are imported.
"""
from pathlib import Path
import zipfile, json, struct, collections, hashlib, sys, os
import numpy as np
ROOT=Path(__file__).parent
BP='Bearframe_Behavior/'; RP='Bearframe_Resources/'
BASE=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT.parent/'Bearframe_The_Last_Dispatch_0.11.19_Integrated_Cities.mcaddon'
OUT=Path(sys.argv[2]) if len(sys.argv)>2 else ROOT.parent/'Bearframe_The_Last_Dispatch_0.11.20_Bunker_Test.mcaddon'
X0,Z0,Y0=-128,-128,-56; VERSION=18168865; ANCHOR=(8,66,53)
# NBT writer: exact numeric types for block states and chunk indices.
class Byte(int):pass
class Long(int):pass
class L(list):
 def __init__(self,t,values=()):super().__init__(values);self.t=t

def st(s):b=s.encode('utf8');return struct.pack('<H',len(b))+b
def kind(v):return 1 if isinstance(v,Byte) else 4 if isinstance(v,Long) else 3 if isinstance(v,int) else 8 if isinstance(v,str) else 9 if isinstance(v,L) else 10 if isinstance(v,dict) else None
def enc(v,t=None):
 t=t or kind(v)
 if t in (1,3,4):return struct.pack('<'+{1:'b',3:'i',4:'q'}[t],v)
 if t==8:return st(v)
 if t==9:
  if v.t==3:return b'\x03'+struct.pack('<i',len(v))+np.asarray(v,dtype='<i4').tobytes()
  return bytes([v.t])+struct.pack('<i',len(v))+b''.join(enc(x,v.t) for x in v)
 if t==10:return b''.join(bytes([kind(x)])+st(k)+enc(x) for k,x in v.items())+b'\0'
 raise ValueError((v,t))
def nbt(d):return b'\x0a\0\0'+enc(d)
def block(name,states=None):
 s=states or {};return {'name':name,'states':{k:Byte(v) if isinstance(v,int) and (k.endswith('_bit') or k in ('hanging','persistent_bit','update_bit','in_wall_bit')) else v for k,v in s.items()},'version':VERSION}
def js(d):return (json.dumps(d,indent=2)+'\n').encode()
basepal=json.loads((ROOT/'bed_palette.json').read_text()); src=json.loads((ROOT/'palette.json').read_text()); w=np.load(ROOT/'central.npz')['world']; mask=np.load(ROOT/'mask.npy'); authored=np.load(ROOT/'auth.npy')
# Keep only source internal water, not the surrounding lake at the entrance.
waterids=[i for i,a in enumerate(src) if a['Name']=='minecraft:water'];water=np.isin(w,waterids);mask[:,90:,:]&=~water[:,90:,:] # source y >=34: preserve dry shaft, do not transplant lake
# original shaft's south ladder connects through a low covered surface room;
# extend it six blocks and open its adjacent floor/headspace to the dry surface.
def setsrc(x,y,z,name,props=None):
 d={'Name':name};
 if props:d['Properties']=props
 if d not in src:src.append(d)
 i=(x-X0,y-Y0,z-Z0);w[i]=src.index(d);mask[i]=True
for y in range(62,67):
 setsrc(8,y,46,'minecraft:ladder',{'facing':'north','waterlogged':'false'});setsrc(8,y,47,'minecraft:stone_bricks');setsrc(8,y,45,'minecraft:air')
# Open external approach from south, preserve original round structure.
for x in [7,8,9]:
 for z in [48,49,50]:
  setsrc(x,65,z,'minecraft:smooth_stone');setsrc(x,66,z,'minecraft:air');setsrc(x,67,z,'minecraft:air')
# Entry to the round room via an opening through its original south ring.
for y in [63,64,66]:
 for x in [8,9]:setsrc(x,y,48,'minecraft:air')
# Use actual palette definitions from existing Bedrock templates. Explicit
# aliases/fallbacks cover edition-specific names and source mod ores.
DIRE={'north':2,'south':3,'west':4,'east':5,'up':1,'down':0};STAIR={'east':0,'west':1,'south':2,'north':3};DIR={'south':0,'west':1,'north':2,'east':3}
alias={ 'cave_air':'air','void_air':'air','bubble_column':'water','magma_block':'magma','cobweb':'web','redstone_wall_torch':'redstone_torch','soul_wall_torch':'soul_torch','repeater':'unpowered_repeater','powered_rail':'golden_rail','spawner':'legacy_bunker_encounter','tnt':'iron_block','quartz_pillar':'quartz_block','waxed_oxidized_cut_copper':'oxidized_cut_copper','waxed_oxidized_cut_copper_slab':'waxed_exposed_cut_copper_slab','waxed_oxidized_cut_copper_stairs':'waxed_exposed_cut_copper_stairs','smooth_sandstone_slab':'smooth_quartz_slab','cobblestone_slab':'normal_stone_slab','andesite_slab':'polished_andesite_slab','granite_slab':'polished_diorite_slab','polished_granite_slab':'polished_diorite_slab','andesite_stairs':'polished_andesite_stairs','granite_stairs':'polished_granite_stairs','birch_stairs':'spruce_stairs','dark_prismarine_stairs':'polished_blackstone_stairs','prismarine_wall':'polished_deepslate_wall','jungle_wall_sign':'jungle_wall_sign','jungle_sign':'standing_sign','gray_bed':'bed','yellow_bed':'bed','damaged_anvil':'anvil','skeleton_skull':'skull','yellow_wall_banner':'wall_banner','piston_head':'air','cave_vines_plant':'cave_vines','stripped_oak_wood':'stripped_oak_log','oak_wood':'oak_log'}
# These vanilla IDs are modern Bedrock blocks, absent only from base structures.
plain=set('clay black_concrete red_concrete yellow_concrete orange_stained_glass spruce_planks birch_planks jungle_planks soul_sand note_block dark_prismarine wet_sponge iron_block tuff dripstone_block budding_amethyst raw_iron_block raw_copper_block snow_layer'.split())
plain|={a['Name'].split(':')[1] for a in src if a['Name'].startswith('minecraft:') and a['Name'].endswith('_ore')}
# Remove Java-only hazards and unsupported mod blocks rather than importing their IDs.
sub=collections.Counter();unknown=collections.Counter();state_counts=collections.Counter();used=np.bincount(w[mask],minlength=len(src))
def convert(a,n):
 old=a['Name']; p=a.get('Properties',{}); name=old.split(':')[1]
 if not old.startswith('minecraft:'):
  name={'limestone':'smooth_stone','scoria':'deepslate','asurine':'tuff','crimsite':'granite','veridium':'andesite','ochrum':'diorite','deepslate_zinc_ore':'deepslate_iron_ore','zinc_ore':'iron_ore','plastic_ore':'coal_ore'}.get(name,'stone')
 else:name=alias.get(name,name)
 full=('bearframe:' if name=='legacy_bunker_encounter' else 'minecraft:')+name; f=p.get('facing','north');b=lambda k:int(p.get(k)=='true'); states={}
 if name.endswith('_stairs'):states={'weirdo_direction':STAIR.get(f,0),'upside_down_bit':int(p.get('half')=='top')};
 elif name.endswith('_slab'):
  if p.get('type')=='double':
   dbl=name.removesuffix('_slab')+'_double_slab'; full='minecraft:'+dbl
   if full not in basepal:full='minecraft:'+{'stone_brick':'stone_bricks','normal_stone':'stone'}.get(name.removesuffix('_slab'),name.removesuffix('_slab'))
  else:states={'minecraft:vertical_half':p.get('type','bottom')}
 elif name.endswith('_door'):states={'door_hinge_bit':int(p.get('hinge')=='right'),'minecraft:cardinal_direction':f,'open_bit':b('open'),'upper_block_bit':int(p.get('half')=='upper')}
 elif name.endswith('_trapdoor'):states={'direction':STAIR.get(f,0),'open_bit':b('open'),'upside_down_bit':int(p.get('half')=='top')}
 elif name.endswith('_wall'):states={**{'wall_connection_type_'+d:('short' if p.get(d)=='low' else p.get(d,'none')) for d in ['north','east','south','west']},'wall_post_bit':b('up')}
 elif name in ('ladder','barrel','dispenser','dropper','piston','sticky_piston','wall_banner','jungle_wall_sign','skull'):states={'facing_direction':DIRE.get(f,2)}
 elif name=='chest':states={'minecraft:cardinal_direction':f}
 elif name=='bed':states={'direction':DIR.get(f,2),'head_piece_bit':int(p.get('part')=='head'),'occupied_bit':0}
 elif name in ('redstone_torch','soul_torch'):states={'torch_facing_direction':p.get('facing','top')}
 elif name=='redstone_wire':states={'redstone_signal':int(p.get('power',0))}
 elif name=='unpowered_repeater':states={'minecraft:cardinal_direction':f,'repeater_delay':int(p.get('delay',1))-1}
 elif name=='stone_button':states={'button_pressed_bit':b('powered'),'facing_direction':1 if p.get('face')=='floor' else 0 if p.get('face')=='ceiling' else DIRE.get(f,2)}
 elif name=='lever':states={'lever_direction':f if p.get('face')=='wall' else ('up_' if p.get('face')=='floor' else 'down_')+('east_west' if f in ('east','west') else 'north_south'),'open_bit':b('powered')}
 elif name=='rail' or name=='golden_rail':states={'rail_direction':{'north_south':0,'east_west':1,'ascending_east':2,'ascending_west':3,'ascending_north':4,'ascending_south':5,'south_east':6,'south_west':7,'north_west':8,'north_east':9}.get(p.get('shape'),0)};states.update({'rail_data_bit':b('powered')} if name=='golden_rail' else {})
 elif name=='observer':states={'minecraft:facing_direction':f,'powered_bit':0}
 elif name=='lantern':states={'hanging':b('hanging')}
 elif name=='standing_sign':states={'ground_sign_direction':int(p.get('rotation',0))}
 elif name=='farmland':states={'moisturized_amount':int(p.get('moisture',0))}
 elif name in ('carrots','nether_wart'):states={'growth':int(p.get('age',0))}
 elif name=='quartz_block' and 'axis' in p:states={'pillar_axis':p['axis']}
 elif 'axis' in p:states={'pillar_axis':p['axis']}
 elif name=='redstone_lamp' and b('lit'):full='minecraft:sea_lantern'
 # Resolve actual known state schemas, preserving orientation rather than choosing arbitrary variants.
 candidates=basepal.get(full,[])
 if candidates:
  chosen=min(candidates,key=lambda a:sum(4 if k in ('weirdo_direction','minecraft:cardinal_direction','facing_direction','direction','upper_block_bit','upside_down_bit','minecraft:vertical_half') else 1 for k,v in states.items() if a['states'].get(k)!=v)+sum(k not in states for k in a['states'])*.05)
  actual=dict(chosen['states']);
  # Known state domains are stable; all combinations for stairs/doors are valid.
  for k,v in states.items():
   if k in actual and any(c['states'].get(k)==v for c in candidates):actual[k]=v
  states=actual
 elif name=='legacy_bunker_encounter':states={}
 elif name in plain or name in ('redstone_wire','carrots','nether_wart','soul_torch','dispenser','dropper','piston','sticky_piston','jungle_wall_sign','skull','stripped_oak_log','oak_log','birch_fence','cave_vines','glow_lichen','lily_pad','bubble_column'):
  if name in ('cave_vines','glow_lichen','lily_pad'): # vines can spread and destabilize during bulk placement
   full='minecraft:air';states={}
  elif name in ('piston','sticky_piston','dispenser','dropper'): # keep industrial machinery appearance but avoid cross-edition circuit malfunctions
   full='minecraft:observer';states={'minecraft:facing_direction':f,'powered_bit':0}
  elif name=='skull':full='minecraft:air';states={}
  elif name=='jungle_wall_sign':full='minecraft:jungle_wall_sign';states={'facing_direction':DIRE.get(f,2)}
  elif name=='birch_fence':full='minecraft:oak_fence';states={}
  elif name=='note_block':full='minecraft:noteblock';states={}
  elif name=='dark_prismarine':full='minecraft:prismarine';states={'prismarine_block_type':'dark'}
  elif name=='soul_torch':full='minecraft:soul_lantern';states={'hanging':0}
 else:
  unknown[old]+=int(n);full='minecraft:stone' if old not in ('minecraft:snow','minecraft:grass','minecraft:azalea_leaves') else 'minecraft:air';states={}
 if full!=old:sub[(old,full)]+=int(n)
 return block(full,states)
converted=[convert(a,used[i] if i<len(used) else 0) if i<len(used) and used[i] else block('minecraft:air') for i,a in enumerate(src)]
# Deduplicate Bedrock palette entries, keep independent water layers.
pal=[];pindex={}; cmap=[]
for v in converted:
 key=json.dumps(v,sort_keys=True)
 if key not in pindex:pindex[key]=len(pal);pal.append(v)
 cmap.append(pindex[key])
def idxblock(n,s=None):
 v=block(n,s);k=json.dumps(v,sort_keys=True)
 if k not in pindex:pindex[k]=len(pal);pal.append(v)
 return pindex[k]
waterindex=idxblock('minecraft:water',{});markerindex=idxblock('bearframe:legacy_bunker_datum');
wet=np.array([a.get('Properties',{}).get('waterlogged')=='true' for a in src]);mapped=np.array(cmap)[w];mapped[~mask]=-1;secondary=np.where(mask & wet[w],waterindex,-1)
signs={tuple(x['pos']):x for x in json.loads((ROOT/'signs.json').read_text())}
# Explicitly preserve original chest/barrel positions and use existing Bearframe bunker loot.
# Source original item inventories, entities and redstone logic are not copied.

def structure(arr,second,origin):
 size=arr.shape; ids=sorted(set(arr.ravel())|set(second.ravel())-{-1});ids=[int(i) for i in ids if i>=0];ix={k:i for i,k in enumerate(ids)};localpal=[pal[i] for i in ids]
 remap=np.full(len(pal)+1,-1,dtype=np.int32)
 for k,i in ix.items():remap[k]=i
 a=remap[arr];b=remap[second];be={};chests=0
 for j,p in enumerate(localpal):
  if p['name'] not in ('minecraft:chest','minecraft:barrel','minecraft:bed','minecraft:standing_sign','minecraft:jungle_wall_sign'):continue
  for flat in np.flatnonzero(a.ravel()==j):
   x,y,z=np.unravel_index(flat,size);entity={'id':{'minecraft:chest':'Chest','minecraft:barrel':'Barrel','minecraft:bed':'Bed','minecraft:standing_sign':'Sign','minecraft:jungle_wall_sign':'Sign'}[p['name']],'x':int(x),'y':int(y),'z':int(z),'isMovable':Byte(1)}
   if p['name']=='minecraft:bed':
    source=src[w[x+origin[0]-X0,y+origin[1]-Y0,z+origin[2]-Z0]]['Name'];entity['color']=Byte(7 if source=='minecraft:gray_bed' else 4)
   elif p['name'] in ('minecraft:standing_sign','minecraft:jungle_wall_sign'):
    info=signs.get((int(x)+origin[0],int(y)+origin[1],int(z)+origin[2]),{});front=info.get('front','');back=info.get('back','');entity.update({'Text':front,'FrontText':{'Text':front,'IgnoreLighting':Byte(0),'PersistFormatting':Byte(1),'SignTextColor':-16777216},'BackText':{'Text':back,'IgnoreLighting':Byte(0),'PersistFormatting':Byte(1),'SignTextColor':-16777216},'IsWaxed':Byte(0)})
   else:entity.update({'LootTable':'loot_tables/chests/legacy_bunker.json','LootTableSeed':Long(0)});chests+=1
   be[str(int(flat))]={'block_entity_data':entity}
 return nbt({'format_version':1,'size':L(3,[int(v) for v in size]),'structure':{'block_indices':L(9,[L(3,a.ravel()),L(3,b.ravel())]),'entities':L(10),'palette':{'default':{'block_palette':L(10,localpal),'block_position_data':be}}},'structure_world_origin':L(3,[0,0,0])}),chests

with zipfile.ZipFile(BASE) as z:files={n:z.read(n) for n in z.namelist() if not n.endswith('/')}
sections=[];chest_count=0
for x in range(0,w.shape[0],32):
 for z in range(0,w.shape[2],32):
  m=mask[x:x+32,:,z:z+32]
  if not m.any():continue
  # Trim sparse bounds and separate the surface entrance into a final section.
  for ya,yb in [(0,114),(114,w.shape[1])]:
   a=m[:,ya:yb,:];
   if not a.any():continue
   xx,yy,zz=np.where(a);lo=(x+int(xx.min()),ya+int(yy.min()),z+int(zz.min()));hi=(x+int(xx.max())+1,ya+int(yy.max())+1,z+int(zz.max())+1);sl=tuple(slice(l,h) for l,h in zip(lo,hi));o=(lo[0]+X0,lo[1]+Y0,lo[2]+Z0);size=[h-l for l,h in zip(lo,hi)]
   name='legacy_bunker_'+str(len(sections));data,c=structure(mapped[sl],secondary[sl],o);chest_count+=c;files[BP+'structures/bearframe/'+name+'.mcstructure']=data
   sections.append({'id':name,'offset':[o[i]-ANCHOR[i] for i in range(3)],'size':size,'surface':ya==114})
# Build below-ground sections first, surface entrance last; preserve stable order.
sections.sort(key=lambda a:(a['surface'],a['offset'][1],a['offset'][0],a['offset'][2]))
# Separate native placement datum at surface; symmetric single cell, no rotation issues.
marker,_=structure(np.array([[[markerindex]]]),np.array([[[-1]]]),ANCHOR);files[BP+'structures/bearframe/legacy_bunker_datum.mcstructure']=marker
mark=json.loads(files[BP+'blocks/overgrown_city_marker.json']);mark['minecraft:block']['description']['identifier']='bearframe:legacy_bunker_datum';files[BP+'blocks/legacy_bunker_datum.json']=js(mark)
mark['minecraft:block']['description']['identifier']='bearframe:legacy_bunker_encounter';files[BP+'blocks/legacy_bunker_encounter.json']=js(mark)
loot=json.loads(files[BP+'loot_tables/chests/bearframe_bunker.json']);loot['pools'][0]['rolls']={'min':1,'max':3};loot['pools'][-1]['entries'][0]['weight']=9850;loot['pools'][-1]['entries'][1]['weight']=120;loot['pools'][-1]['entries'][2]['weight']=28;loot['pools'][-1]['entries'][3]['weight']=2;files[BP+'loot_tables/chests/legacy_bunker.json']=js(loot)
files[BP+'worldgen/template_pools/legacy_bunker.json']=js({'format_version':'1.26.50','minecraft:template_pool':{'description':{'identifier':'bearframe:legacy_bunker'},'elements':[{'element':{'element_type':'minecraft:single_pool_element','location':'bearframe/legacy_bunker_datum'},'weight':1}]}})
files[BP+'worldgen/structures/legacy_bunker.json']=js({'format_version':'1.26.50','minecraft:jigsaw':{'description':{'identifier':'bearframe:legacy_bunker'},'step':'surface_structures','start_pool':'bearframe:legacy_bunker','max_depth':1,'start_height':{'type':'constant','value':{'absolute':0}},'heightmap_projection':'world_surface','biome_filters':[{'test':'has_biome_tag','operator':'==','value':'plains'}]}})
files[BP+'worldgen/structure_sets/legacy_bunker.json']=js({'format_version':'1.26.50','minecraft:structure_set':{'description':{'identifier':'bearframe:legacy_bunker'},'placement':{'type':'minecraft:random_spread','salt':971653,'spacing':40,'separation':24,'spread_type':'linear'},'structures':[{'structure':'bearframe:legacy_bunker','weight':1}]}})
# Preserve all existing landmark entries: Signal Shelter has explicit quest dependencies.
files[BP+'scripts/legacy_bunker_layout.js']=('export const PARTS='+json.dumps(sections,separators=(',',':'))+';\n').encode();files[BP+'scripts/legacy_bunker.js']=(ROOT/'legacy_bunker.js').read_bytes()
p=BP+'scripts/main.js';s=files[p].decode();s='import {discoverLegacyBunker,discoverBunkerEncounter,LEGACY_BUNKER_MARKER,LEGACY_BUNKER_ENCOUNTER} from "./legacy_bunker.js";\n'+s;s=s.replace('SPILLWAY_MARKER,"bearframe:field_archive"]','SPILLWAY_MARKER,"bearframe:field_archive",LEGACY_BUNKER_MARKER,LEGACY_BUNKER_ENCOUNTER]');s=s.replace('      if(marker?.typeId==="bearframe:field_archive"){','      if(marker?.typeId===LEGACY_BUNKER_MARKER){discoverLegacyBunker(marker,p);continue;}\n      if(marker?.typeId===LEGACY_BUNKER_ENCOUNTER){discoverBunkerEncounter(marker,p);continue;}\n      if(marker?.typeId==="bearframe:field_archive"){');assert 'discoverLegacyBunker(marker,p)' in s;files[p]=s.encode()
for prefix in (BP,RP):
 path=prefix+'manifest.json';m=json.loads(files[path]);old=m['header']['version'];assert old==[0,11,19];m['header']['version']=[0,11,20]
 for module in m['modules']:module['version']=[0,11,20]
 for dep in m.get('dependencies',[]):
  if dep.get('version')==old:dep['version']=[0,11,20]
 files[path]=js(m)
report={'source':str(Path(os.environ['BUNKER_SOURCE'])),'source_sha256':hashlib.sha256((Path(os.environ['BUNKER_SOURCE'])).read_bytes()).hexdigest(),'base_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'parts':len(sections),'authored_blocks':int(authored.sum()),'occupied_template_cells':int(mask.sum()),'chest_barrel_count':chest_count,'substitutions':{a+' -> '+b:n for (a,b),n in sub.items()},'unknown_fallbacks':dict(unknown),'layout':sections}
(ROOT/'conversion_report.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k not in ('layout','substitutions')});print('substitutions',sorted(sub.items(),key=lambda a:-a[1])[:30]);
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for n,b in sorted(files.items()):z.writestr(n,b)
with zipfile.ZipFile(OUT) as z:assert z.testzip() is None;assert len(z.namelist())==len(files)
print(OUT,len(files),hashlib.sha256(OUT.read_bytes()).hexdigest())
