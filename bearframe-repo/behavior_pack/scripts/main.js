import {ARCHIVE_SITE_IDS} from "./campaign_data.js";
import {fieldSound} from "./field_audio.js";
import {offerRelayLead,registerChartSite,installRouteCharts} from "./route_charts.js";
import {installEcology,retainResident} from "./ecology.js";
import {installActivityLog} from "./activity_log.js";
import {campaignSignal,installCampaign} from "./campaign.js";
import {buildSurfaceSite,surveyRoamingSite} from "./surface_sites.js";
import {SURFACE_DATUM,EXTENDED_SURFACE_DATUM,SURFACE_DONE,LEGACY_DATUM} from "./surface_layout.js";
import {buildSpillway} from "./spillway.js";
import {SPILLWAY_BUILT,SPILLWAY_MARKER} from "./spillway_layout.js";
import {recordSurvey} from "./survey_log.js";
import {greetRegion,installExpedition,prepareBunker,regionAt} from "./expedition.js";
import {installLivingWorld} from "./living_world.js";
import {REGION_ANCHOR,ORBIT} from "./regions.js";
import {APPROACH_MARKER,gradeApproach} from "./approaches.js";
import {BlockTypes,BlockVolume,Difficulty,GameMode,ItemStack,system,world} from "@minecraft/server";
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
    if(paid)attempt(()=>dim.playSound("random.click",terminal,{volume:.65,pitch:.75}));
    return info(player,paid?"Breaker seated. Follow the copper line to the rubble, clear it, then bring one redstone dust back here.":"The breaker is missing its contact plates. Bring two copper ingots.");
  }
  if(state===1){
    const debris=loaded(dim,at(terminal,BULKHEAD,rotation));
    if(!debris?.isAir)return info(player,"Clear the cobblestone at the end of the copper service line.");
    const {gate,lights,breaker}=powerParts(site);
    if(gate.some(b=>!b || !["minecraft:air","minecraft:iron_bars"].includes(b.typeId)) ||
      lights.some(b=>!b || !["minecraft:coal_block","minecraft:sea_lantern"].includes(b.typeId)) ||
      breaker?.typeId!=="minecraft:waxed_cut_copper")return info(player,"Station hardware is obstructed or outside loaded terrain.");
    const paid=spend(player,"minecraft:redstone",1,()=>restorePower(site));
    if(!paid)return info(player,"The line is clear. Bring one redstone dust to bridge the signal contact.");
    campaignSignal(player,"repair","maintenance_relay",terminal);
    announceRelayPower(site);
    return;
  }
  campaignSignal(player,"repair","maintenance_relay",terminal);
  return info(player,"The service wing has power. The relay keeps repeating: Keep one bunk warm. Reservation still open.");
}

function announceRelayPower(site){
  const {dim,terminal}=site;
  for(const walker of dim.getEntities({type:ACTOR_TYPES.walker,location:terminal,maxDistance:12})){
    if(walker.getDynamicProperty("bearframe:relay_walker")===relayKey(terminal))
      attempt(()=>walker.triggerEvent("bearframe:relay_online"));
  }
  fieldSound(dim,"relay",at(terminal,GATE[0],site.rotation));
  system.runTimeout(()=>attempt(()=>{
    if(!dim.isChunkLoaded(terminal))return;
    attempt(()=>dim.playSound("random.orb",terminal,{volume:.55,pitch:.65}));
    for(const listener of dim.getPlayers({location:terminal,maxDistance:16}))
      info(listener,"Relay transmission: Keep one bunk warm. Reservation still open.");
  }),14);
}

const relayKey=({x,y,z})=>[x,y,z].join(",");

function activateSite(site){
  const {dim,terminal,rotation}=site;
  for(const [role,offset] of Object.entries(ACTORS)){
    const pos=at(terminal,offset,rotation);
    if(!loaded(dim,pos)?.isAir || !loaded(dim,{...pos,y:pos.y+1})?.isAir)continue;
    if(role==="scout"&&world.getDifficulty()===Difficulty.Peaceful)continue;
    const key=`bearframe:resident:${terminal.x},${terminal.y},${terminal.z}:${role}`;
    if(world.getDynamicProperty(key))continue;
    const resident=dim.spawnEntity(ACTOR_TYPES[role],{x:pos.x+.5,y:pos.y,z:pos.z+.5});
    world.setDynamicProperty(key,true);
    retainResident(resident);
    if(role==="walker"){
      resident.setDynamicProperty("bearframe:relay_walker",relayKey(terminal));
      if(phase(site)<2)resident.triggerEvent("bearframe:relay_offline");
    }
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
      if(now.typeId===PANEL){
        recordSurvey(player,"maintenance_relay");
        campaignSignal(player,"read","maintenance_relay",location);
      }
      useRelay(player,site,now.typeId);
    }
  }));
});

world.beforeEvents.playerInteractWithEntity.subscribe(event=>{
  const {player,target}=event;
  if(target.typeId!==ACTOR_TYPES.engineer||target.dimension.id===ORBIT)return;
  event.cancel=true;
  system.run(()=>attempt(()=>{
    if(!validPlayer(player)||!target.isValid||dist(player.location,target.location)>49)return;
    if(!player.isSneaking)return info(player,"I'm with Farfield. Start at the lectern. Sneak-interact to trade 2 charcoal for a torch kit.");
    const bag=component(player);
    if(!bag || bag.emptySlotsCount===0)return info(player,"Free one slot for four torches.");
    if(spend(player,"minecraft:charcoal",2,()=>{bag.addItem(new ItemStack("minecraft:torch",4));}))
      info(player,"Four torches. Light the floor before you reconnect anything.");
    else info(player,"A kit costs 2 charcoal.");
  }));
});

const cells=new Map();
const siteMarkers=[ANCHOR,APPROACH_MARKER,REGION_ANCHOR,SPILLWAY_MARKER,SURFACE_DATUM,EXTENDED_SURFACE_DATUM,LEGACY_DATUM];
let registeredSiteMarkers;
world.afterEvents.playerLeave.subscribe(({playerId})=>cells.delete(playerId));
system.runInterval(()=>{
  for(const p of world.getAllPlayers())attempt(()=>{
    if(p.dimension.id!=="minecraft:overworld")return cells.delete(p.id);
    const {dimension:dim,location:loc}=p;
    registeredSiteMarkers??=siteMarkers.filter(id=>BlockTypes.get(id));
    const key=[loc.x,loc.y,loc.z].map(n=>Math.floor(n/12)).join(",");
    const last=cells.get(p.id);
    if(last?.key===key && (!last.pending || system.currentTick-last.tick<240)){
      if(surveyRoamingSite(p,system.currentTick))cells.delete(p.id);
      offerRelayLead(p);
      return;
    }
    let pending=false;
    const top=dim.isChunkLoaded(loc)?dim.getTopmostBlock(loc)?.y:undefined;
    const y=Math.floor(top!==undefined&&loc.y>top+18?top:loc.y);
    const a={x:Math.floor(loc.x)-40,y:Math.max(dim.heightRange.min,y-24),z:Math.floor(loc.z)-40};
    const b={x:Math.floor(loc.x)+40,y:Math.min(dim.heightRange.max-1,y+19),z:Math.floor(loc.z)+40};
    if(!registeredSiteMarkers.length)return;
    for(const p of dim.getBlocks(new BlockVolume(a,b),{includeTypes:registeredSiteMarkers},true).getBlockLocationIterator()){
      const marker=loaded(dim,p);
      if(marker?.typeId===SURFACE_DATUM||marker?.typeId===EXTENDED_SURFACE_DATUM||marker?.typeId===LEGACY_DATUM){
        if(!marker.permutation.getState(SURFACE_DONE) && !buildSurfaceSite(marker))pending=true;
        continue;
      }
      if(marker?.typeId===SPILLWAY_MARKER){
        registerChartSite("spillway_bunker",dim.id,marker.location,"beacon");
        if(!marker.permutation.getState(SPILLWAY_BUILT) && !buildSpillway(marker))pending=true;
        continue;
      }
      if(marker?.typeId===APPROACH_MARKER){gradeApproach(marker);continue;}
      if(marker?.typeId===REGION_ANCHOR){
        const region=regionAt(dim,at(p,[0,2,0]));
        if(region){registerChartSite(region.def.id,dim.id,region.pos);prepareBunker(region);greetRegion(region);}
        continue;
      }
      const site=resolveSite(dim,at(p,[0,2,0]));
      if(site){registerChartSite("maintenance_relay",dim.id,at(p,[0,2,0]));activateSite(site);}
    }
    cells.set(p.id,{key,pending,tick:system.currentTick});
    if(surveyRoamingSite(p,system.currentTick))cells.delete(p.id);
    offerRelayLead(p);
  });
},60);

world.afterEvents.playerSpawn.subscribe(({player,initialSpawn})=>{
  if(!initialSpawn||!validPlayer(player)||player.getDynamicProperty("bearframe:farfield_intro"))return;
  player.setDynamicProperty("bearframe:farfield_intro",true);
  info(player,"Farfield is taking volunteers. Find a Survey Camp and sneak-use its map table, or craft a Teleport Tablet at a crafting table. Ask Mira for your first assignment aboard Bearframe Station.");
});

installExpedition({validPlayer,spend,attempt});
installLivingWorld({validPlayer,spend,attempt});

installCampaign(ARCHIVE_SITE_IDS);

installActivityLog();

installEcology();

installRouteCharts();
