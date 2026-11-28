from pathlib import Path
import json,json5,zipfile,shutil,re,uuid,struct,hashlib,collections,subprocess
import sys,tempfile
D=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
TMP=Path(tempfile.mkdtemp(prefix='bearframe-clean-'))
O=TMP/'old'; C=TMP/'cities'; chest=TMP/'chest'; rarity=TMP/'rarity'
for name,target in [('Bearframe_The_Last_Dispatch_0.11.49_Walker_Animation_Repair.mcaddon',O),('RandS Overgrown Cities 1.3.mcpack',C),('Chest Loot.mcaddon',chest),('RARITY STATS BP v19.4.mcaddon',rarity)]:
 with zipfile.ZipFile(D/name) as archive:archive.extractall(target)
B=O/'Bearframe_Behavior'; R=O/'Bearframe_Resources'; L=chest/'Chest Loot BP'; S=rarity/'RARITY BP'; ROOT=TMP/'cleanbase'; BP=ROOT/'Bearframe_Base_BP'; RP=ROOT/'Bearframe_Base_RP'; BP.mkdir(parents=True); RP.mkdir()
def copy(src,dest):
 dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
def tree(src,dest,pred=lambda p:True):
 for p in src.rglob('*'):
  if p.is_file() and pred(p):copy(p,dest/p.relative_to(src))
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
def js(p,o):write(p,json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def read(p):
 s=p.read_text(encoding="utf-8-sig")
 try:return json.loads(s)
 except ValueError:return json5.loads(s)
# Original city geometry, never use old transformed city assets or other structures.
for name in ['structures','worldgen']:tree(C/name,BP/name)
for name in ['features','feature_rules']:tree(C/'subpacks/overgrown'/name,BP/name)
changes=0
for p in (BP/'structures').rglob('*.mcstructure'):
 data=p.read_bytes();a=b'jigsaw:air';b=b'minecraft:air';old=struct.pack('<H',len(a))+a;new=struct.pack('<H',len(b))+b;changes+=data.count(old);data=data.replace(old,new);assert a not in data;p.write_bytes(data)
assert changes==12
for p in (BP/'worldgen').rglob('*.json'):
 t=p.read_text().replace('minecraft:chiseled_deepslste','minecraft:chiseled_deepslate').replace('minecraft:deepslate_slab','minecraft:cobbled_deepslate_slab');write(p,t)
(BP/"worldgen/template_pools/village/custom/test.json").unlink()
p=BP/'worldgen/processors/house5.json';j=read(p);j['minecraft:processor_list']['description']['identifier']='jigsaw:house5';js(p,j)
for name in ['iron','gold','diamond','netherite']:copy(B/f'loot_tables/chests/{name}.json',BP/f'loot_tables/chests/{name}.json')
# Original Rarity, with targeted compatibility guards.
for name in ['items','recipes','blocks','loot_tables']:tree(S/name,BP/name)
tree(S/'scripts',BP/'scripts/rarity')
libs={'main.js','mainLib.js','statsLib.js','skillsLib.js','passivesLib.js','divineMobs.js','divineStats.js','divineSkills.js','divinePassives.js'}
for p in (BP/'scripts/rarity').glob('*.js'):
 if p.name not in libs:p.unlink()
rp=BP/'scripts/rarity/main.js';s=rp.read_text();old=(B/'scripts/rarity/main.js').read_text();s=s.replace('FormCancelationReason,\n    uiManager','FormCancelationReason')
def replace_func(s,old,name):
 pattern=rf'(?m)^function {name}\([^\n]*\) \{{[\s\S]*?^\}}';m=re.search(pattern,old);assert m,name; s,n=re.subn(pattern,lambda _:m.group(0),s,count=1);assert n==1,name;return s
for n in ['updateCooldown','equipEntity','applyEffects','applyDivineTags','applyStrongTags','handleHealthBoostStorage']:s=replace_func(s,old,n)
s=s.replace('const entity = event.entity;\n    \n    // Check if entity type is eligible', 'const entity = event.entity;\n    if (!entity.isValid || entity.typeId.startsWith("bearframe:")) return;\n    // Check if entity type is eligible').replace('entity.getComponent("minecraft:type_family").hasTypeFamily("monster")','entity.getComponent("minecraft:type_family")?.hasTypeFamily("monster")')
s=s.replace('if (!shouldAffectEntity(deadEntity.typeId))','if (deadEntity.typeId.startsWith("bearframe:") || !shouldAffectEntity(deadEntity.typeId))')
s=re.sub(r'(?m)^function getScoreboardValue\([^\n]*\) \{[\s\S]*?^\}',lambda _:'function getScoreboardValue(scoreboard, player) {\n    try {\n        const objective=world.scoreboard.getObjective(scoreboard);\n        if (!objective || !player?.isValid) return 0;\n        const identity=player.scoreboardIdentity;\n        return identity && objective.hasParticipant(identity) ? (objective.getScore(identity) ?? 0) : 0;\n    } catch { return 0; }\n}',s,count=1)
s=s.replace(".body('menu.invisible.rrs')", ".body('Choose an upgrade or reforge option.')").replace(".button('', 'textures/ui/up_medium_arrow_blue')", ".button('Upgrade stats')").replace(".button('', 'textures/ui/smithing_icon')", ".button('Reforge item')")
s=s.replace('const loreArray = itemStack.getLore();\n    if (!itemStack', 'const loreArray = itemStack?.getLore() ?? [];\n    if (!itemStack')
s=s.replace('if (entity.hasTag("recordhealth"))','if (entity.isValid && entity.hasTag("recordhealth"))')
s=s.replace('console.error("Error restoring entity health:", error);','if (entity.isValid && error?.name !== "InvalidEntityError") console.error("Error restoring entity health:", error);')
s=s.replace('console.error(`Error recording health for entity ${entity.typeId}:`, error);','if (entity.isValid && error?.name !== "InvalidEntityError") console.error(`Error recording health for entity ${entity.typeId}:`, error);')
write(rp,s)
copy(B/'blocks/rrs_heavy_anvil.json',BP/'blocks/rrs_heavy_anvil.json')
icons={};fallbacks={'divine_core':'textures/items/diamond','tier1_upgrade':'textures/items/iron_ingot','tier2_upgrade':'textures/items/gold_ingot','tier3_upgrade':'textures/items/diamond','razor_signature_weapon':'textures/items/diamond_sword','oreman_signature_weapon':'textures/items/netherite_sword','vertx_signature_weapon_mf':'textures/items/golden_sword','vertx_signature_weapon_mv':'textures/items/iron_sword'}
for p in (BP/'items').glob('*.json'):
 j=read(p);d=j['minecraft:item'];c=d['components'];key='base_'+p.stem;icons[key]={'textures':fallbacks[p.stem.removeprefix('rrs_')]};c['minecraft:icon']=key;c.pop('minecraft:custom_components',None);js(p,j)
js(RP/'textures/item_texture.json',{'resource_pack_name':'Bearframe Base','texture_name':'atlas.items','texture_data':icons});js(RP/'textures/terrain_texture.json',{'resource_pack_name':'Bearframe Base','texture_name':'atlas.terrain','texture_data':{'rrs_heavy_anvil':{'textures':'textures/blocks/anvil_base'}}})
copy(L/'scripts/main.js',BP/'scripts/chest_loot/main.js');p=BP/'scripts/chest_loot/main.js';write(p,p.read_text().replace('beast:chestloot','rrs:chestloot'))
copy(L/'loot_tables/empty.json',BP/'loot_tables/empty.json')
tree(B/'entities',BP/'entities');tree(B/'spawn_rules',BP/'spawn_rules');tree(B/'loot_tables/entities',BP/'loot_tables/entities')
for p in (BP/'loot_tables/entities').glob('*.json'):
 j=read(p)
 def fix(x):
  if isinstance(x,dict):
   if x.get('type')=='item' and x.get('name','').startswith('bearframe:'):
    name=x['name'];x['name']={'bearframe:salvaged_alloy':'minecraft:iron_ingot','bearframe:legacy_cell':'minecraft:copper_ingot'}.get(name,'minecraft:diamond')
   for v in x.values():fix(v)
  elif isinstance(x,list):
   for v in x:fix(v)
 fix(j);js(p,j)
for n in ['boss_combat','boss_moves','echo_specials','grid_specials','grid_special_plan','combat_credit']:copy(B/f'scripts/{n}.js',BP/f'scripts/{n}.js')
p=BP/'scripts/boss_combat.js';s=p.read_text();s=re.sub(r'^import \{ (campaignSignal|creditIds|defeatedClaim) \}.*\n','',s,flags=re.M);a=s.index('  world.afterEvents.entityDie.subscribe');b=s.index('  system.runInterval',a);s=s[:a]+'''  world.afterEvents.entityDie.subscribe(({deadEntity})=>{
    active.delete(deadEntity.id);participants.delete(deadEntity.id);
  });
'''+s[b:];s=s.replace('state.claim=entity.getDynamicProperty("bearframe:boss_claim");','').replace('claim:entity.getDynamicProperty("bearframe:boss_claim"), ','').replace('state.claim=hurtEntity.getDynamicProperty("bearframe:boss_claim")??state.claim;','');write(p,s)
for n in ['entity','animation_controllers','render_controllers','particles']:tree(R/n,RP/n)
tree(R/'models/entity',RP/'models/entity',lambda p:not p.name.startswith('held_'));tree(R/'animations',RP/'animations',lambda p:p.name!='bearframe.held_gear.animation.json')
for p in (R/'textures/bearframe').glob('*.png'):
 if p.stem in {x.stem for x in (BP/'entities').glob('*.json')}:copy(p,RP/'textures/bearframe'/p.name)
for n in ['vanilla','fx']:tree(R/'textures/bearframe'/n,RP/'textures/bearframe'/n)
tree(R/'textures/particle',RP/'textures/particle');tree(R/'textures/ui/bearframe',RP/'textures/ui/bearframe');copy(R/'ui/hud_screen.json',RP/'ui/hud_screen.json')
for p in (BP/'entities').glob('*.json'):
 j=read(p);d=j['minecraft:entity']['description']
 if d['identifier'].startswith('bearframe:city_'):d['is_spawnable']=True
 js(p,j)
lines=[x for x in (R/'texts/en_US.lang').read_text().splitlines() if x.startswith(('entity.','item.spawn_egg.entity.')) and '=' in x];write(RP/'texts/en_US.lang','\n'.join(lines)+'\n');copy(R/'texts/languages.json',RP/'texts/languages.json')
write(BP/'scripts/main.js','''import "./rarity/main.js";\nimport "./chest_loot/main.js";\nimport {installBossCombat} from "./boss_combat.js";\nimport {world} from "@minecraft/server";\ninstallBossCombat();\nworld.afterEvents.playerSpawn.subscribe(({player,initialSpawn})=>{if(initialSpawn)player.sendMessage("§b[Bearframe Base] Active build 0.1.0 — clean reset");});\n''')
ns=uuid.UUID('6b2b29bf-dc0d-4a31-aa42-711951cd3501');uid=lambda x:str(uuid.uuid5(ns,x));v=[0,1,0];engine=[1,26,50]
for path,label,typ in [(BP,'Behavior','data'),(RP,'Resources','resources')]:
 key=typ;manifest={'format_version':2,'header':{'name':f'Bearframe Clean Base 0.1.0 | {label}','description':'Clean city, rarity, chest loot and faction entity base','uuid':uid(key),'version':v,'min_engine_version':engine},'modules':[{'type':typ,'uuid':uid(key+'module'),'version':v}]}
 if path==BP:
  manifest['modules'].append({'type':'script','language':'javascript','entry':'scripts/main.js','uuid':uid('script'),'version':v});manifest['dependencies']=[{'uuid':uid('resources'),'version':v},{'module_name':'@minecraft/server','version':'2.10.0'},{'module_name':'@minecraft/server-ui','version':'2.2.0'}]
 js(path/'manifest.json',manifest);copy(C/'pack_icon.png',path/'pack_icon.png')
for p in ROOT.rglob('*.json'):read(p)
for p in (BP/'scripts').rglob('*.js'):
 r=subprocess.run(['node','--input-type=module','--check'],input=p.read_bytes(),capture_output=True);assert r.returncode==0,(p,r.stderr)
 for ref in re.findall(r'(?:from\s*|import\s*)[\'\"](\.[^\'\"]+)[\'\"]',p.read_text()):assert (p.parent/ref).is_file(),(p,ref)
assert len(list((BP/'structures').rglob('*.mcstructure')))==536
assert len(list((BP/'worldgen/structure_sets').glob('*.json')))==1
assert len(list((BP/'entities').glob('*.json')))==47
assert len(list((RP/'entity').glob('*.json')))==74
geom=set();anims=set();controllers=set()
for p in (RP/'models').rglob('*.json'):
 for g in read(p).get('minecraft:geometry',[]):geom.add(g['description']['identifier'])
for p in (RP/'animations').glob('*.json'):anims.update(read(p).get('animations',{}))
for p in (RP/'animation_controllers').glob('*.json'):controllers.update(read(p).get('animation_controllers',{}))
for p in (RP/'entity').glob('*.json'):
 d=read(p)['minecraft:client_entity']['description']
 for x in d.get('textures',{}).values():
  if x.startswith('textures/bearframe/'):assert (RP/(x+'.png')).exists(),(p,x)
 for x in d.get('geometry',{}).values():
  if x.startswith('geometry.bearframe.'):assert x in geom,(p,x)
 for x in d.get('animations',{}).values():
  if x.startswith('animation.bearframe.'):assert x in anims,(p,x)
  if x.startswith('controller.animation.bearframe.'):assert x in controllers,(p,x)
for p in (BP/'entities').glob('*.json'):
 j=read(p)['minecraft:entity'];d=j['components'].get('minecraft:loot',{}).get('table');assert not d or (BP/d).exists(),(p,d)
for p in (RP/'particles').glob('*.json'):
 d=read(p)['particle_effect']['description']['basic_render_parameters']['texture'];assert (RP/(d+'.png')).exists(),(p,d)
output=D/'Bearframe_Clean_Base_0.1.0.mcaddon'
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(ROOT.rglob('*')):
  if p.is_file():z.write(p,p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(output) as z:assert z.testzip() is None
print('PASS',output,output.stat().st_size,hashlib.sha256(output.read_bytes()).hexdigest(),'files',len(list(ROOT.rglob('*'))),'jigsaw fixes',changes)
