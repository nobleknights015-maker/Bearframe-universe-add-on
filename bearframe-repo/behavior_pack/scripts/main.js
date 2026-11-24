import {buildSpillway} from "./spillway.js";
import {SPILLWAY_BUILT,SPILLWAY_MARKER} from "./spillway_layout.js";
import {recordSurvey} from "./survey_log.js";
import {greetRegion,installExpedition,prepareBunker,regionAt} from "./expedition.js";
import {installLivingWorld} from "./living_world.js";
import {REGION_ANCHOR,ORBIT} from "./regions.js";
import {APPROACH_MARKER,gradeApproach} from "./approaches.js";
import {BlockVolume,Difficulty,GameMode,ItemStack,system,world} from "@minecraft/server";
import {ACTORS,BREAKER,BULKHEAD,DIRECTION,GATE,POWER_LIGHTS,RECOVERY,ROTATIONS,at} from "./layout.js";

const ANCHOR="bearframe:relay_anchor";
const PHASE="bearframe:phase";
const PANEL="minecraft:lectern";
const CRATE="minecraft:barrel";
const PART="bearframe:relay_schematic";
const ACTOR_TYPES={engineer:"bearframe:farfield_surveyor",walker:"bearframe:grid_walker",scout:"bearframe:hollow_scout"};
const info=(player,text)=>player.sendMessage("§b[Farfield]§r "+text);
const dist=(a,b)=>(a.x-b.x)**2+(a.y-b.y)**2+(a.z-b.z)**2;
const same=(a,b)=>a.x===b.x&&a.y===b.y&&a.z===b.z;
const loaded=(dim,p)=>dim.isChunkLoaded(p)?dim.getBlock(p):undefined;
const attempt=(make)=>{try{make();}catch(error){console.warn("[Bearframe] "+error);}};
const validPlayer=p=>p.isValid && [GameMode.Survival,GameMode.Adventure,GameMode.Creative].includes(p.getGameMode());

function resolveSite(dim,terminal){
  const marker=loaded(dim,at(terminal,[0,-2,0]));
  if(marker?.typeId!==ANCHOR || loaded(dim,terminal)?.typeId!==PANEL)return;
  const rotation=ROTATIONS.findIndex((_,r)=>loaded(dim,at(terminal,DIRECTION,r))?.typeId==="minecraft:lodestone");
  if(rotation<0)return;
  return {dim,terminal,marker,rotation};
}

function findLinked(block){
  if(block.typeId===PANEL)return resolveSite(block.dimension,block.location);
  if(block.typeId!==CRATE)return;
  const reverse=RECOVERY.map(n=>-n);
  for(let r=0;r<ROTATIONS.length;r++){
    const site=resolveSite(block.dimension,at(block.location,reverse,r));
    if(site?.rotation===r)return site;
  }
}

const phase=site=>Number(site.marker.permutation.getState(PHASE));
const advance=(site,value)=>site.marker.setPermutation(site.marker.permutation.withState(PHASE,value));
const component=p=>p.getComponent("minecraft:inventory")?.container;

function spend(player,id,amount,commit){
  const bag=component(player);
  if(!bag)return false;
  const changes=[];
  let remaining=amount;
  for(let i=0;i<bag.size && remaining;i++){
    const stack=bag.getItem(i);
    if(stack?.typeId!==id||stack.nameTag)continue;
    const removed=Math.min(stack.amount,remaining);
    const next=removed===stack.amount?undefined:stack.clone();
    if(next)next.amount-=removed;
    changes.push({i,stack,next});
    remaining-=removed;
  }
  if(remaining)return false;
  const applied=[];
  try {
    for(const change of changes){
      bag.setItem(change.i,change.next);
      applied.push(change);
    }
    commit();
  } catch(error) {
    for(const {i,stack} of applied)bag.setItem(i,stack);
    throw error;
  }
  return true;
}

function powerParts(site){
  const blocks=(offsets)=>offsets.map(p=>loaded(site.dim,at(site.terminal,p,site.rotation)));
  return {gate:blocks(GATE),lights:blocks(POWER_LIGHTS),breaker:blocks([BREAKER])[0]};
}

function restorePower(site){
  const {gate,lights,breaker}=powerParts(site);
  if(gate.some(b=>!b || !["minecraft:air","minecraft:iron_bars"].includes(b.typeId)) ||
    lights.some(b=>!b || !["minecraft:coal_block","minecraft:sea_lantern"].includes(b.typeId)) ||
    breaker?.typeId!=="minecraft:waxed_cut_copper")return false;
  const saved=[...gate,...lights].map(b=>[b,b.permutation]);
  try{
    gate.forEach(b=>b.setType("minecraft:air"));
    lights.forEach(b=>b.setType("minecraft:sea_lantern"));
    advance(site,2);
  }catch(error){
    for(const [block,permutation] of saved)block.setPermutation(permutation);
    throw error;
  }
  return true;
}

function useRelay(player,site,kind){
  const {dim,terminal,rotation}=site;
  const state=phase(site);
  if(kind===CRATE){
    if(state<2)return info(player,"The recovery locker is offline.");
    if(state>=3)return info(player,"This station's schematic was already recovered.");
    const bag=component(player);
    if(!bag)return;
    let slot=0;
    while(slot<bag.size && bag.getItem(slot))slot++;
    if(slot>=bag.size)return info(player,"Free one inventory slot for the relay schematic.");
    bag.setItem(slot,new ItemStack(PART));
    try{advance(site,3);}catch(error){bag.setItem(slot,undefined);throw error;}
    player.playSound("random.levelup",{volume:.35});
    return info(player,"Relay schematic recovered. Use it with a torch and an iron nugget to craft two field lanterns.");
  }
  if(state===0){
    const breaker=loaded(dim,at(terminal,BREAKER,rotation));
    if(breaker?.typeId!=="minecraft:cut_copper")return info(player,"Find an intact unpowered breaker beside the terminal.");
    const paid=spend(player,"minecraft:copper_ingot",2,()=>{
      const former=breaker.permutation;
      try{breaker.setType("minecraft:waxed_cut_copper");advance(site,1);}
      catch(error){breaker.setPermutation(former);throw error;}
    });
    return info(player,paid?"Breaker fitted. Clear the cobblestone at the copper service line and return with 1 redstone dust.":"Breaker open. Bring 2 copper ingots to repair it.");
  }
  if(state===1){
    const debris=loaded(dim,at(terminal,BULKHEAD,rotation));
    if(!debris?.isAir)return info(player,"Clear the cobblestone at the end of the copper service line.");
    const {gate,lights,breaker}=powerParts(site);
    if(gate.some(b=>!b || !["minecraft:air","minecraft:iron_bars"].includes(b.typeId)) ||
      lights.some(b=>!b || !["minecraft:coal_block","minecraft:sea_lantern"].includes(b.typeId)) ||
      breaker?.typeId!=="minecraft:waxed_cut_copper")return info(player,"Station hardware is obstructed or outside loaded terrain.");
    const paid=spend(player,"minecraft:redstone",1,()=>restorePower(site));
    return info(player,paid?"Circuit restored. The service wing is open. Check the recovery locker.":"Bring 1 redstone dust to reconnect the circuit.");
  }
  return info(player,"Power stable. The locker is in the service wing beyond the bars.");
}

function activateSite(site){
  const {dim,terminal,rotation}=site;
  for(const [role,offset] of Object.entries(ACTORS)){
    const pos=at(terminal,offset,rotation);
    if(!loaded(dim,pos)?.isAir || !loaded(dim,{...pos,y:pos.y+1})?.isAir)continue;
    if(role==="scout"&&world.getDifficulty()===Difficulty.Peaceful)continue;
    const key=`bearframe:resident:${terminal.x},${terminal.y},${terminal.z}:${role}`;
    if(world.getDynamicProperty(key))continue;
    dim.spawnEntity(ACTOR_TYPES[role],{x:pos.x+.5,y:pos.y,z:pos.z+.5});
    world.setDynamicProperty(key,true);
  }
}

world.beforeEvents.playerInteractWithBlock.subscribe(event=>{
  const block=event.block;
  if(!findLinked(block))return;
  event.cancel=true;
  if(!event.isFirstEvent)return;
  const {player}=event,{dimension,location}=block;
  system.run(()=>attempt(()=>{
    if(!validPlayer(player)||player.dimension.id!==dimension.id||dist(player.location,location)>49)return;
    const now=loaded(dimension,location),site=now&&findLinked(now);
    if(site){
      if(now.typeId===PANEL)recordSurvey(player,"maintenance_relay");
      useRelay(player,site,now.typeId);
    }
  }));
});

world.beforeEvents.playerInteractWithEntity.subscribe(event=>{
  const {player,target}=event;
  if(target.typeId!==ACTOR_TYPES.engineer)return;
  event.cancel=true;
  system.run(()=>attempt(()=>{
    if(!validPlayer(player)||!target.isValid||dist(player.location,target.location)>49)return;
    if(target.dimension.id===ORBIT)return;
    if(!player.isSneaking)return info(player,"I'm with Farfield. Start at the lectern. Sneak-interact to trade 2 charcoal for a torch kit.");
    const bag=component(player);
    if(!bag || bag.emptySlotsCount===0)return info(player,"Free one slot for four torches.");
    if(spend(player,"minecraft:charcoal",2,()=>{bag.addItem(new ItemStack("minecraft:torch",4));}))
      info(player,"Four torches. Light the floor before you reconnect anything.");
    else info(player,"A kit costs 2 charcoal.");
  }));
});

const cells=new Map();
world.afterEvents.playerLeave.subscribe(({playerId})=>cells.delete(playerId));
system.runInterval(()=>{
  for(const p of world.getAllPlayers())attempt(()=>{
    if(p.dimension.id!=="minecraft:overworld")return cells.delete(p.id);
    const {dimension:dim,location:loc}=p;
    const key=[loc.x,loc.y,loc.z].map(n=>Math.floor(n/12)).join(",");
    const last=cells.get(p.id);
    if(last?.key===key && (!last.pending || system.currentTick-last.tick<240))return;
    let pending=false;
    const a={x:Math.floor(loc.x)-21,y:Math.max(dim.heightRange.min,Math.floor(loc.y)-18),z:Math.floor(loc.z)-21};
    const b={x:Math.floor(loc.x)+21,y:Math.min(dim.heightRange.max-1,Math.floor(loc.y)+14),z:Math.floor(loc.z)+21};
    for(const p of dim.getBlocks(new BlockVolume(a,b),{includeTypes:[ANCHOR,APPROACH_MARKER,REGION_ANCHOR,SPILLWAY_MARKER]},true).getBlockLocationIterator()){
      const marker=loaded(dim,p);
      if(marker?.typeId===SPILLWAY_MARKER){
        if(!marker.permutation.getState(SPILLWAY_BUILT) && !buildSpillway(marker))pending=true;
        continue;
      }
      if(marker?.typeId===APPROACH_MARKER){gradeApproach(marker);continue;}
      if(marker?.typeId===REGION_ANCHOR){
        const region=regionAt(dim,at(p,[0,2,0]));
        if(region){prepareBunker(region);greetRegion(region);}
        continue;
      }
      const site=resolveSite(dim,at(p,[0,2,0]));
      if(site)activateSite(site);
    }
    cells.set(p.id,{key,pending,tick:system.currentTick});
  });
},60);

installExpedition({validPlayer,spend,attempt});
installLivingWorld({validPlayer,spend,attempt});
