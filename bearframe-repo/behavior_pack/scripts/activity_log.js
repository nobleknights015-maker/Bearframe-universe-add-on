import {openCharts} from "./route_charts.js";
import {system,world} from "@minecraft/server";
import {ActionFormData} from "@minecraft/server-ui";
import {read as readCampaign} from "./campaign_state.js";
import {MAIN,SIDES,CONTRACTS,EVIDENCE} from "./campaign_data.js";
import {goalCount,standing,LEADS,itemName,rpgState,inventoryCount} from "./rpg_progress.js";
import {localRows} from "./local_rpg.js";
import {specialty} from "./rpg_training.js";
import {BOSS_DOSSIERS} from "./boss_dossiers.js";
const TERMINAL="bearframe:field_log";
const OPEN_PAD="bearframe:open_field_log";
const SAVE="bearframe:activity:";
const loaded=new Map();
const dirty=new Set();
const moving=new Map();
const inventory=new Map();
const forms=new Set();
const containers=new Set(["chest","trapped_chest","barrel","ender_chest","shulker_box","hopper","dispenser","dropper","crafter","decorated_pot"]);
const benches=new Set(["crafting_table","smithing_table","enchanting_table","anvil","stonecutter","furnace","blast_furnace","smoker","brewing_stand","loom","grindstone","cartography_table"]);
const clean=id=>String(id??"").replace(/^\w+:/,"").replaceAll("_"," ");
const dimension=id=>id==="bearframe:city_orbit"?"Bearframe Station":clean(id);
const coords=p=>[Math.floor(p.x),Math.floor(p.y),Math.floor(p.z)];
const sum=(s,k,n=1)=>{s.totals[k]=(s.totals[k]??0)+n;};
const defaultLog=()=>({totals:{},recent:[],checkpoints:{},types:{}});
function record(id){
  if(!loaded.has(id)){
    const raw=world.getDynamicProperty(SAVE+id);
    loaded.set(id,typeof raw==="string"?JSON.parse(raw):defaultLog());
  }
  return loaded.get(id);
}
function flush(id){
  if(!dirty.has(id))return;
  world.setDynamicProperty(SAVE+id,JSON.stringify(record(id)));
  dirty.delete(id);
}
function append(stats,kind,detail,dim,place){
  const previous=stats.recent.at(-1);
  if(previous?.kind===kind&&previous.detail===detail&&previous.dim===dim&&system.currentTick-previous.tick<100){
    previous.count=(previous.count??1)+1;
    previous.tick=system.currentTick;
    return;
  }
  stats.recent.push({kind,detail,dim,at:place?coords(place):null,tick:system.currentTick});
  if(stats.recent.length>64)stats.recent.shift();
}
export function noteActivity(player,kind,detail,at=player.location,dim=player.dimension.id){
  if(!player?.isValid)return;
  const id=player.id,s=record(id);
  sum(s,kind);
  append(s,kind,detail,dim,at);
  if(kind==="Travel"||kind==="Death")s.checkpoints[kind]={dim,at:coords(at)};
  dirty.add(id);
}
function countBlock(player,key,type){
  const s=record(player.id), name=clean(type);
  sum(s,key);
  const table=s.types[key]??(s.types[key]={});
  const group=name in table||Object.keys(table).length<24?name:"other blocks";
  table[group]=(table[group]??0)+1;
  dirty.add(player.id);
}
function netItems({player,beforeItemStack,itemStack}){
  const batch=inventory.get(player.id)??new Map();
  for(const [item,sign] of [[beforeItemStack,-1],[itemStack,1]]){
    if(item)batch.set(item.typeId,(batch.get(item.typeId)??0)+sign*item.amount);
  }
  inventory.set(player.id,batch);
}
function drainInventory(id){
  const batch=inventory.get(id);
  if(!batch)return;
  inventory.delete(id);
  for(const [type,change] of batch){
    if(!change)continue;
    const stats=record(id);
    sum(stats,change>0?"Items added":"Items removed",Math.abs(change));
    const types=stats.types.Inventory??(stats.types.Inventory={});
    const item=clean(type);
    const group=item in types||Object.keys(types).length<24?item:"other items";
    types[group]=(types[group]??0)+change;
    dirty.add(id);
  }
}
function snapshotMovement(){
  const now=system.currentTick;
  for(const player of world.getAllPlayers()){
    const {x,y,z}=player.location;
    const old=moving.get(player.id),dim=player.dimension.id;
    moving.set(player.id,{x,y,z,dim,now});
    if(old?.dim!==dim||now-old.now>100)continue;
    const distance=Math.hypot(x-old.x,y-old.y,z-old.z);
    const stats=record(player.id);
    // Large discontinuities include teleports and spawn displacement.
    if(distance<28&&distance>.1)sum(stats,"Estimated blocks traveled",Math.round(distance*10)/10);
    sum(stats,"Session seconds",(now-old.now)/20);
    dirty.add(player.id);
  }
  for(const id of inventory.keys())drainInventory(id);
  for(const id of dirty)flush(id);
}
function activityText(stats){
  return stats.recent.length?stats.recent.slice(-18).reverse().map(e=>{
    const count=e.count>1?" ×"+e.count:"";
    return e.kind+" · "+e.detail+count+"\n"+dimension(e.dim)+(e.at?" · "+e.at.join(", "):"");
  }).join("\n\n"):"No recent events yet.";
}
const count=(stats,key)=>Math.round(stats.totals[key]??0);
function totalsText(stats){
  const keys=["Blocks placed","Blocks broken","Defeat","Death","Travel","Container","Workbench","Talk","Field entry","Repair","Campaign","Side case","Contract","Items added","Items removed","Estimated blocks traveled","Session seconds"];
  return keys.map(k=>k+": "+count(stats,k)).join("\n")+
    "\n\nInventory totals represent net changes, including pickups, storage, crafting, trades and use. Travel distance is sampled.";
}
function materialsText(stats){
  const lines=[];
  for(const key of ["Blocks placed","Blocks broken","Inventory"]){
    const entries=Object.entries(stats.types[key]??{}).sort((a,b)=>Math.abs(b[1])-Math.abs(a[1])).slice(0,10);
    lines.push(key,entries.length?entries.map(([name,n])=>name+" · "+(key==="Inventory"&&n>0?"+":"")+n).join("\n"):"No entries.","");
  }
  return lines.join("\n");
}
function fieldText(stats,state){
  const lines=Object.entries(state.sites).map(([id,at])=>(EVIDENCE[id]?.name??(id.startsWith("boss:")?BOSS_DOSSIERS[id.slice(5)]?.name:undefined)??clean(id))+" · "+at.join(", "));
  for(const [key,value] of Object.entries(stats.checkpoints))
    lines.unshift("Last "+key.toLowerCase()+" · "+dimension(value.dim)+" · "+value.at.join(", "));
  return lines.join("\n")||"Field and travel records will appear here.";
}
function storyText(state,player){
  const q=MAIN[state.chapter];
  const s=q?[q.title,q.intro,...q.goals.map(g=>Math.min(g.count,state.facts[g.key]??0)+"/"+g.count+" · "+g.label),"Debrief with "+q.speaker]:
    [state.chapter<0?"Speak to Mira in the Farfield Annex to begin.":"The Last Dispatch complete."];
  for(const side of SIDES)if(state.side[side.id]===1){s.push("\nAssignment · "+side.title+" · "+side.speaker,...side.goals.map(g=>Math.min(g.count,goalCount(side,state,g))+"/"+g.count+" · "+g.label));for(const [id,n] of side.delivery??[])s.push(Math.min(n,inventoryCount(player.getComponent("minecraft:inventory")?.container,id))+"/"+n+" · Deliver "+itemName(id));}
  for(const c of CONTRACTS)if(state.contracts[c.id]?.active)s.push("Contract · "+c.title+" · "+state.contracts[c.id].progress+"/"+c.count);
  const raw=player.getDynamicProperty("bearframe:field_requests");
  if(typeof raw==="string")s.push(...localRows(JSON.parse(raw)));
  const sp=specialty(state);if(sp)s.push("\nSpecialization · "+sp.name+" · Rank "+sp.rank);
  return s.join("\n");
}
function menu(title,body,labels){
  const form=new ActionFormData().title(title).body(body);
  for(const label of labels)form.button(label);
  return form;
}
async function logForm(player){
  if(forms.has(player.id))return;
  forms.add(player.id);
  try{
    drainInventory(player.id);
    flush(player.id);
    const options=["Recent activity","Lifetime totals","Block and inventory details","Exploration and coordinates","Active quest dossier","Treasure charts","Completed assignments","Department standing"];
    const selection=await menu("Field Log","Personal record for this world",options).show(player);
    if(selection.canceled||!player.isValid)return;
    if(selection.selection===5){await openCharts(player);return;}
    const stats=record(player.id),campaign=readCampaign(player);
    const pages=[activityText,totalsText,materialsText,s=>fieldText(s,campaign),()=>storyText(campaign,player),null,()=>SIDES.filter(q=>campaign.side[q.id]===2).map(q=>{const outcome=q.outcomes?.find(o=>o.id===rpgState(campaign).decisions[q.id]);return q.title+" · "+q.speaker+"\n"+q.report+(outcome?"\nRecommendation: "+outcome.label:"");}).join("\n\n")||"No completed assignments.",()=>LEADS.map(name=>{const r=standing(campaign,name);return name+" · "+r.tier+" ("+r.points+")";}).join("\n")];
    if(pages[selection.selection])await menu(options[selection.selection],pages[selection.selection](stats),["Close"]).show(player);
  }catch(error){console.warn("[Bearframe Field Log] "+error);}
  finally{forms.delete(player.id);}
}

export function placeFieldLog(dim,key,positions){
  if(world.getDynamicProperty(key))return;
  const found=positions.map(p=>dim.isChunkLoaded(p)?dim.getBlock(p):undefined);
  if(found.some(b=>b?.typeId===TERMINAL)){
    world.setDynamicProperty(key,true);return;
  }
  const target=found.find(b=>b?.isAir&&b.above()?.isAir&&b.below()&&!b.below().isAir&&!b.below().isLiquid);
  if(target){target.setType(TERMINAL);world.setDynamicProperty(key,true);}
}
export function installActivityLog(){
  system.beforeEvents.startup.subscribe(({itemComponentRegistry})=>{
    itemComponentRegistry.registerCustomComponent(OPEN_PAD,{
      onUse:({source})=>system.run(()=>{if(source.isValid)logForm(source);})
    });
  });
  world.beforeEvents.playerInteractWithBlock.subscribe(event=>{
    if(event.block.typeId!==TERMINAL)return;
    event.cancel=true;
    const {player}=event;
    if(event.isFirstEvent)system.run(()=>logForm(player));
  });
  world.afterEvents.playerPlaceBlock.subscribe(({player,block})=>countBlock(player,"Blocks placed",block.typeId));
  world.afterEvents.playerBreakBlock.subscribe(({player,brokenBlockPermutation})=>countBlock(player,"Blocks broken",brokenBlockPermutation.type.id));
  world.afterEvents.playerInventoryItemChange?.subscribe(netItems);
  world.afterEvents.playerInteractWithBlock?.subscribe(({player,block,isFirstEvent})=>{
    if(isFirstEvent===false)return;
    const id=block.typeId;
    if(containers.has(id.split(":")[1])||id.endsWith("_shulker_box"))noteActivity(player,"Container",clean(id),block.location);
    else if(benches.has(id.split(":")[1]))noteActivity(player,"Workbench",clean(id),block.location);
  });
  world.afterEvents.playerInteractWithEntity?.subscribe(({player,target})=>{
    if(target.typeId==="minecraft:villager"||target.typeId==="minecraft:villager_v2")noteActivity(player,"Talk","villager",target.location);
  });
  world.afterEvents.playerDimensionChange?.subscribe(({player,toDimension,toLocation})=>{
    moving.delete(player.id);
    noteActivity(player,"Travel","Entered "+dimension(toDimension.id),toLocation,toDimension.id);
    flush(player.id);
  });
  world.afterEvents.entityDie.subscribe(({deadEntity,damageSource})=>{
    if(deadEntity.typeId==="minecraft:player")noteActivity(deadEntity,"Death",clean(damageSource.cause),deadEntity.location);
    const source=damageSource.damagingEntity;
    if(source?.typeId==="minecraft:player")noteActivity(source,"Defeat",clean(deadEntity.typeId),deadEntity.location);
  });
  world.afterEvents.playerLeave.subscribe(({playerId})=>{
    drainInventory(playerId);
    flush(playerId);
    loaded.delete(playerId);moving.delete(playerId);forms.delete(playerId);
  });
  system.runInterval(snapshotMovement,40);
}
