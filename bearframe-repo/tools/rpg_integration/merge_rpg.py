import sys,zipfile,json,re,hashlib,subprocess
from pathlib import Path
B='Bearframe_Behavior/'; R='Bearframe_Resources/'; V=[0,11,21]
def read(p):
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None
  return {n:z.read(n) for n in z.namelist() if not n.endswith('/')}
def enc(x):return (json.dumps(x,indent=2,ensure_ascii=False)+'\n').encode()
def replace(s,a,b):
 assert a in s,a[:100];return s.replace(a,b)
def main(base,rarity,chest,out):
 f=read(base); old=f.copy(); rr=read(rarity); cl=read(chest)
 items={json.loads(b)['minecraft:item']['description']['identifier']:json.loads(b)['minecraft:item']['components'] for n,b in f.items() if n.startswith(B+'items/') and n.endswith('.json')}
 gear={i for i,c in items.items() if 'minecraft:damage' in c and c.get('minecraft:hand_equipped') and i!='bearframe:repair_wrench'}
 forbidden={'bearframe:'+i for i in 'field_cutter palinode_ram silt_discharge gantry_rake cinder_inductor seam_splitter veil_anchor rook_hammer hush_pendulum'.split()}
 # Keep original executable libraries; no redundant alternate copies.
 for n in ['mainLib','statsLib','skillsLib','passivesLib','divineMobs','divineStats','divineSkills','divinePassives']:
  f[B+'scripts/rarity/'+n+'.js']=rr['RARITY BP/scripts/'+n+'.js']
 s=rr['RARITY BP/scripts/main.js'].decode()
 s='import {entityThreat,classifyUnit} from "../unit_classification.js";\n'+s
 s=replace(s,'    FormCancelationReason,\n    uiManager','    FormCancelationReason')
 s=replace(s,'function parseTags(itemId = "minecraft:apple") {','const BF_GEAR = new Set('+json.dumps(sorted(gear))+');\nfunction parseTags(itemId = "minecraft:apple") {\n    if (BF_GEAR.has(itemId)) return {rarity:true,data:"sword"};\n    if(itemId.startsWith("bearframe:")) return {rarity:false};')
 s=replace(s,'function parseMaterial(itemId = "minecraft:apple") {','function parseMaterial(itemId = "minecraft:apple") {\n    if(BF_GEAR.has(itemId)) return {chance:0,maxRarity:6};')
 s=replace(s,'rarityUp = "None", upGuarant = false) {','rarityUp = "None", upGuarant = false, slot = EquipmentSlot.Mainhand) {')
 s=replace(s,'equippable?.setEquipment(EquipmentSlot.Mainhand, newItem);','equippable?.setEquipment(slot, newItem);')
 s=replace(s,'        rarityItemTest(player.getComponent("minecraft:equippable")?.getEquipment(EquipmentSlot.Mainhand), player);\n        compileBuffs(player);\n        setMainStats(player);','        try {\n            const eq=player.getComponent("minecraft:equippable");\n            if(!eq) continue;\n            for(const slot of [EquipmentSlot.Mainhand,EquipmentSlot.Offhand,EquipmentSlot.Head,EquipmentSlot.Chest,EquipmentSlot.Legs,EquipmentSlot.Feet]) rarityItemTest(eq.getEquipment(slot),player,"None",false,slot);\n            compileBuffs(player);\n            setMainStats(player);\n        } catch(error){ console.warn("[Bearframe rarity] "+error); }')
 # Don't double the vanilla hit. Avoid supplemental damage to controlled factions; preserve quest credit.
 s=replace(s,'    let damage = calculateDamage(player, ev.damage);','    if (mob.typeId === "minecraft:player" || (classifyUnit(mob.typeId) && !entityThreat(mob)) || (mob.typeId.startsWith("bearframe:") && !entityThreat(mob))) return;\n    let damage = Math.max(0, calculateDamage(player, ev.damage)-ev.damage);')
 s=replace(s,'            mob.applyDamage(damage);','            if (damage > 0) mob.applyDamage(damage);')
 s=replace(s,'    let damage = calculateDamage(player, 6);','    if (mob.typeId === "minecraft:player" || (classifyUnit(mob.typeId) && !entityThreat(mob)) || (mob.typeId.startsWith("bearframe:") && !entityThreat(mob))) return;\n    let damage = Math.max(0, calculateDamage(player, 0));')
 # Additional combat attribution is non-recursive; base melee hits must be ordinary entity attacks.
 s=replace(s,'if (!ev.damageSource.damagingEntity || ev.damageSource.damagingEntity?.typeId != "minecraft:player") return;','if (ev.damageSource.cause !== EntityDamageCause.entityAttack || ev.damageSource.damagingEntity?.typeId !== "minecraft:player") return;')
 s=s.replace('if (damage > 0) mob.applyDamage(damage);','if (damage > 0) mob.applyDamage(damage,{cause:EntityDamageCause.magic,damagingEntity:player});')
 s=replace(s,'return scoreboardValue;','return scoreboardValue ?? 0;')
 s=replace(s,'time: scoreboardValue','time: scoreboardValue ?? 0')
 s=replace(s,'if (cd >= 0) {','if (cd > 0) {')
 s=replace(s,'if (cd === 0) {','if (cd === 1) {')
 s=replace(s,'system.runTimeout(() => {initializeScoreboards()}, 50);','world.afterEvents.worldLoad.subscribe(()=>initializeScoreboards());')
 s=replace(s,'const DIM_MULT = { overworld: 1, nether: 2, end: 4 };','const DIM_MULT = { "minecraft:overworld": 1, "minecraft:nether": 2, "minecraft:the_end": 4 };\n            if (!(dimension in DIM_MULT)) continue;')
 s=replace(s,'function openSignatureWeapons(player, equipment, itemStack, loreArray, selection = 0) {','function openSignatureWeapons(player, equipment, itemStack, loreArray, selection = 0) {\n    if(BF_GEAR.has(itemStack.typeId)){player.sendMessage("Bearframe signature equipment keeps its original item identity.");return;}')
 # Reset formerly left hidden divine data behind, allowing repeated core redemption.
 s=replace(s,'function divineTransformFunction(origin) {','function divineTransformFunction(origin) {\n    system.run(()=>origin.sourceEntity?.sendMessage("Divine reset is unavailable pending transaction validation.")); return {status:CustomCommandStatus.Failure};')
 # Allow skill activation even for weapons lacking the vanilla item-use event.
 s=replace(s,'world.afterEvents.itemUse.subscribe((ev) => {\n    const player = ev.source;','function activateRaritySkill(player) {')
 start=s.index('function activateRaritySkill(player) {'); end=s.index('//=====================================INITIALIZATION',start)
 section=s[start:end]; closing=section.rfind('});');assert closing>=0
 section=section[:closing]+'}\nworld.afterEvents.itemUse.subscribe(ev=>activateRaritySkill(ev.source));\n'+section[closing+3:];s=s[:start]+section+s[end:]
 s=replace(s,'    init.customCommandRegistry.registerEnum("rrs:Rarity",','    init.customCommandRegistry.registerCommand({name:"rrs:skill",description:"Activate held equipment skill",permissionLevel:CommandPermissionLevel.Any},origin=>{system.run(()=>{if(origin.sourceEntity?.typeId==="minecraft:player") activateRaritySkill(origin.sourceEntity);});return {status:CustomCommandStatus.Success};});\n    init.customCommandRegistry.registerEnum("rrs:Rarity",')
 # Existing boss tuning and custom humanoids are not modified by random mob enhancements.
 s=replace(s,'    const entity = event.entity;\n    \n    // Check if entity type is eligible','    const entity = event.entity;\n    if(entity.typeId.startsWith("bearframe:") || classifyUnit(entity.typeId) && !entityThreat(entity)) return;\n    // Check if entity type is eligible')
 s=replace(s,'entity.getComponent("minecraft:type_family").hasTypeFamily("monster")','entity.getComponent("minecraft:type_family")?.hasTypeFamily("monster")')
 s=replace(s,'if (!shouldAffectEntity(deadEntity.typeId))','if (deadEntity.typeId === "minecraft:player" || deadEntity.typeId.startsWith("bearframe:") && !entityThreat(deadEntity) || !shouldAffectEntity(deadEntity.typeId))')
 # Limit destructive abilities and stray collateral in generated facilities.
 for fn in ['skillExplosiveMining','skillRayMiner','skillExcavator','skillShadowDash']:
  s=replace(s,'function '+fn+'(player, skill) {','function '+fn+'(player, skill) {\n    player.sendMessage("This terrain-changing skill is disabled in The Last Dispatch test build."); return;')
 s=replace(s,'event.dimension.createExplosion(event.location, passive.value);','event.dimension.createExplosion(event.location, Math.min(3,passive.value), {breaksBlocks:false,causesFire:false,source:player});')
 s=replace(s,'entity.runCommand(`setblock ${posX} ${posY - 1} ${posZ} powder_snow`);','// Preserve authored floors.')
 s=replace(s,'player.runCommand(`execute at @s positioned${pos} run fill ~ ~ ~ ~ ~ ~ fire replace air`);','// Do not ignite authored structures.')
 # Limit broad damage selectors to monster family, and avoid unbounded lightning/fire in the world.
 s=s.replace('@e[r=', '@e[family=monster,r=')
 s=replace(s,'event.dimension.spawnEntity("lightning_bolt", event.location);','event.dimension.spawnParticle("minecraft:critical_hit_emitter", event.location);')
 # Use stock UI controls instead of absent custom RP icons; give otherwise empty buttons visible labels.
 def label(m):
  name=m.group(2).split('/')[-1]; labels={'up_medium_arrow_blue':'Upgrade','smithing_icon':'Reforge','arrow_left':'Previous','arrow_right':'Next','color_plus':'Add','invisible':'Continue'}
  return '.button('+json.dumps(labels.get(name,name.replace('_button','').replace('_',' ').title()))+')'
 s=re.sub(r'\.button\((""|\'\'),\s*["\'](textures/ui/[^"\']+)["\']\)',label,s)
 s=re.sub(r',\s*["\']textures/ui/[^"\']+["\'](?=\))','',s)
 s=replace(s,".body('menu.invisible.rrs')",".body('Bearframe equipment engineering')")
 s=s.replace('.body("menu.invisible.rrs")','.body("Bearframe equipment engineering")')
 s=s.replace('SIGNATURE_WEAPONS[selection].requirements.text, SIGNATURE_WEAPONS[selection].texture','SIGNATURE_WEAPONS[selection].requirements.text')
 s=replace(s,'const loreArray = itemStack.getLore();\n    if (!itemStack || loreArray.length','const loreArray = itemStack?.getLore() ?? [];\n    if (!itemStack || loreArray.length')
 # Guard stale inventory snapshots before async form mutations.
 s='function sameHeld(player,item){try{const now=player.getComponent("minecraft:equippable")?.getEquipment(EquipmentSlot.Mainhand);return !!now&&!!item&&now.typeId===item.typeId&&now.amount===item.amount&&now.nameTag===item.nameTag&&JSON.stringify(now.getLore())===JSON.stringify(item.getLore())&&now.getComponent("minecraft:durability")?.damage===item.getComponent("minecraft:durability")?.damage;}catch{return false;}}\n'+s
 for form in ['upgradeForm','reforgeMenu','newStats','ascendingForm','newSkills','newPassives','signatureForm']:
  s=s.replace(form+'.show(player).then((r) => {',form+'.show(player).then((r) => {\n        if (!sameHeld(player,itemStack)) { player.sendMessage("Held item changed; reopen the forge."); return; }')
 f[B+'scripts/rarity/main.js']=s.encode()
 # Original upgrade items and forge, with existing Bearframe textures as fallback.
 atlas=json.loads(f[R+'textures/item_texture.json']); terrain=json.loads(f[R+'textures/terrain_texture.json']);
 for n,b in rr.items():
  if not n.startswith('RARITY BP/') or not n.endswith('.json'):continue
  p=n[len('RARITY BP/'):];
  if not p.startswith(('items/','blocks/','recipes/','loot_tables/')):continue
  d=json.loads(b)
  if p.startswith('items/'):
   c=d['minecraft:item']['components']; icon=c['minecraft:icon']; ident=d['minecraft:item']['description']['identifier'];
   # The two unfinished signature items reference unregistered custom components; don't install them.
   if 'minecraft:custom_components' in c:continue
   if isinstance(c.get('minecraft:damage'),dict):c['minecraft:damage']=c['minecraft:damage']['value']
   c.pop('minecraft:mining_speed',None)
   fallback='bearframe_legacy_cell' if 'core' in ident else 'bearframe_salvaged_alloy' if 'upgrade' in ident else 'bearframe_phase_edge'
   atlas['texture_data'][icon]=atlas['texture_data'][fallback]
  if p.startswith('blocks/'):
   c=d['minecraft:block']['components'];c['minecraft:geometry']='minecraft:geometry.full_block';c['minecraft:destructible_by_explosion']={'explosion_resistance':12};c['minecraft:material_instances']['*']['render_method']='opaque';terrain['texture_data']['rrs_heavy_anvil']=terrain['texture_data']['bearframe_frontier_bulkhead']
  if p.startswith('recipes/'):
   for k,v in d.items():
    if k.startswith('minecraft:recipe'):
     v['description']['identifier']='rrs:'+Path(p).stem.lower()
  assert B+p not in f,p;f[B+p]=enc(d)
 f[R+'textures/item_texture.json']=enc(atlas);f[R+'textures/terrain_texture.json']=enc(terrain)
 # Preserve the full Chest Loot operator editor, don't install player override or global tick hooks.
 s=cl['Chest Loot BP/scripts/main.js'].decode().replace('\r\n','\n')
 s=replace(s,'const availableItems =\n        [...lootTable.items];','const availableItems = lootTable.items.filter(item=>!BF_RESTRICTED.has(item.itemId));')
 s=replace(s,'const DB_KEY =','const BF_RESTRICTED = new Set('+json.dumps(sorted(forbidden))+');\nconst DB_KEY =')
 s=replace(s,'    debugLog(\n        `[ChestLoot DEBUG] ${message}`\n    );','    console.warn(`[ChestLoot DEBUG] ${message}`);')
 f[B+'scripts/chest_loot/main.js']=s.encode()
 f[B+'scripts/main.js']=b'import "./rarity/main.js";\nimport "./chest_loot/main.js";\n'+f[B+'scripts/main.js']
 # Apply source Chest Loot durability ranges to native world loot without rerolling player chests.
 count=0; changed=0
 for n,b in old.items():
  if not n.startswith((B+'loot_tables/chests/',B+'loot_tables/structures/')) or not n.endswith('.json'):continue
  d=json.loads(b); touched=False
  for pool in d.get('pools',[]):
   for e in pool.get('entries',[]):
    name=e.get('name');assert name not in forbidden,n
    if e.get('type')!='item' or name not in gear:continue
    funcs=e.setdefault('functions',[]);existing={fn['function'] for fn in funcs}; c=items[name]
    if 'minecraft:durability' in c and 'set_damage' not in existing:funcs.append({'function':'set_damage','damage':{'min':0.35,'max':0.85}});touched=True
    if 'minecraft:enchantable' in c and not existing.intersection({'enchant_randomly','enchant_with_levels','specific_enchants'}):funcs.append({'function':'enchant_randomly','conditions':[{'condition':'random_chance','chance':0.15}],'treasure':False});touched=True
    count+=1
  if touched:f[n]=enc(d);changed+=1
 for pre in [B,R]:
  n=pre+'manifest.json';m=json.loads(f[n]);oldver=m['header']['version'];assert oldver==[0,11,20];m['header']['version']=V
  for a in m['modules']:a['version']=V
  for a in m.get('dependencies',[]):
   if a.get('version')==oldver:a['version']=V
  f[n]=enc(m)
 assert all(f[n]==b for n,b in old.items() if n.endswith('.mcstructure'))
 for n,b in f.items():
  if n.endswith('.js') and (n not in old or b!=old[n]):subprocess.run(['node','--input-type=module','--check'],input=b,check=True,capture_output=True)
  if n.endswith('.json') and (n not in old or b!=old[n]):json.loads(b)
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
  for n,b in sorted(f.items()):z.writestr(n,b)
 with zipfile.ZipFile(out) as z:assert z.testzip() is None and all(z.read(n)==b for n,b in f.items())
 print(json.dumps({'files':len(f),'structures':sum(n.endswith('.mcstructure') for n in f),'gear':sorted(gear),'loot_entries':count,'loot_tables':changed,'added':len(set(f)-set(old)),'changed':sum(f[n]!=b for n,b in old.items()),'sha256':hashlib.sha256(Path(out).read_bytes()).hexdigest()}))
if __name__=='__main__':main(*sys.argv[1:])
