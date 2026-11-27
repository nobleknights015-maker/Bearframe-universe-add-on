import {populateBuriedSite,retainResident,fieldInteraction} from "./ecology.js";
import {FIELD_SIGNS} from "./field_signs.js";
import {fieldSound} from "./field_audio.js";
import {placeFieldLog,noteActivity} from "./activity_log.js";
import {campaignSignal,campaignDialogue,ensureDispatchBench,relayDebrief,stationReport} from "./campaign.js";
import {isRecoverySpillway} from "./spillway.js";
import {recordSurvey,reportSurvey} from "./survey_log.js";
import {escalateNearbyDirectorate} from "./living_world.js";
import {BlockVolume,Difficulty,ItemStack,SignSide,system,world} from "@minecraft/server";
import {ROTATIONS,at} from "./layout.js";
import {
  TYPES,REGION_ANCHOR,PIN,CACHE,SEAL,ACTOR,SIGNAL,LANDING,
  ORBIT,CITY_SIZE,CITY_ARRIVAL,CITY_EXIT,CITY_ROLES
} from "./regions.js";

import {CITY_ORIGIN,DOCK_ROLES,STATION_WINGS} from "./station_layout.js";
import {ASTRO} from "./astro_layout.js";
import {inspectPlacedSection,liftLanding} from "./astro_recovery.js";
import {withTemporaryArea} from "./temporary_area.js";
import {GATEWAY_CREW,GATEWAY_PARTS} from "./gateway_layout.js";
const CHEST="minecraft:barrel";
const STATUS="bearframe:status";
const TRANSIT="bearframe:return_berth";
const STATION_ARRIVAL=ASTRO?.arrival??CITY_ARRIVAL;
const CITY_BUILT="bearframe:city_built";
const MOORINGS=["minecraft:air","minecraft:iron_bars"];
const dims=(dim,p)=>dim.isChunkLoaded(p)?dim.getBlock(p):undefined;
const keyAt=({x,y,z})=>[x,y,z].join(",");
const dist=(a,b)=>(a.x-b.x)**2+(a.y-b.y)**2+(a.z-b.z)**2;
const panels=new Set(TYPES.map(s=>s.panel));
const center=({x,y,z})=>({x:x+.5,y,z:z+.5});
const say=(p,s)=>p.sendMessage("§3[Bearframe]§r "+s);
const transit=new Set();
let cityReady;
const DOCK_PRELOAD="bearframe_station_preload";
let dockUsers=0;
let dockPreloaded=false;
const promiseError=error=>console.warn("[Bearframe travel] "+error);
const phase=site=>Number(site.anchor.permutation.getState(STATUS));
const setStatus=(site,n)=>site.anchor.setPermutation(site.anchor.permutation.withState(STATUS,n));
const local=(site,offset)=>dims(site.dim,at(site.pos,offset,site.r));
const offsets=(site)=>site.def.layout??{cache:CACHE,seal:SEAL,signal:SIGNAL,actor:ACTOR};
const cacheOffsets=[...new Map(TYPES.filter(def=>def.loot).map(def=>{
  const point=def.layout?.cache??CACHE;
  return [point.join(","),point];
})).values()];

export function regionAt(dim,pos){
  const anchor=dims(dim,at(pos,[0,-2,0]));
  if(anchor?.typeId!==REGION_ANCHOR)return;
  const def=TYPES[Number(anchor.permutation.getState("bearframe:region"))];
  if(!def||dims(dim,pos)?.typeId!==def.panel)return;
  const r=ROTATIONS.findIndex((_,index)=>dims(dim,at(pos,PIN,index))?.typeId==="minecraft:lodestone");
  if(r>=0)return {dim,pos,def,r,anchor};
}

export function matchRegionDevice(block){
  if(!block||block.dimension.id!=="minecraft:overworld")return;
  const {dimension:dim,location:pos,typeId}=block;
  if(panels.has(typeId))return regionAt(dim,pos);
  if(typeId!==CHEST)return;
  for(const offset of cacheOffsets) for(let r=0;r<4;r++){
    const s=regionAt(dim,at(pos,offset.map(n=>-n),r));
    if(s?.r===r&&s.def.loot&&offsets(s).cache.join(",")===offset.join(","))return s;
  }
}

// Native terrain can leave water inside a sealed tunnel. Drain the authored
// corridor once near first discovery. Do not change the surrounding terrain.
export function prepareBunker(site){
  if(!site.def.bunker||site.def.flooded||isRecoverySpillway(site))return;
  const key="bearframe:bunker_drain:"+keyAt(site.pos);
  if(world.getDynamicProperty(key))return;
  const tunnel=[];
  for(let x=-17;x<=-6;x++){
    const stair=11-(x+17);
    for(let z=-1;z<=1;z++)for(let y=stair;y<=stair+3;y++){
      const block=local(site,[x,y,z]);
      if(!block)return;
      tunnel.push(block);
    }
  }
  for(let x=-7;x<=11;x++)for(let z=-7;z<=7;z++)for(let y=0;y<=4;y++){
    const block=local(site,[x,y,z]);
    if(!block)return;
    tunnel.push(block);
  }
  for(const block of tunnel){
    if(block.typeId==="minecraft:water"||block.typeId==="minecraft:flowing_water")block.setType("minecraft:air");
    if(block.isWaterlogged&&(block.isAir||block.typeId==="minecraft:stone_brick_stairs"))block.setWaterlogged(false);
  }
  world.setDynamicProperty(key,true);
}

function canSpawnAt(dim,loc,hover=false){
  const feet=dims(dim,loc);
  if(!feet?.isAir||!feet.above()?.isAir)return false;
  if(hover)return true;
  const floor=feet.below();
  return Boolean(floor&&!floor.isAir&&!floor.isLiquid);
}

function prepareFieldSigns(site){
  const signs=FIELD_SIGNS[site.def.id];
  if(!signs)return;
  const key="bearframe:field_signs:"+keyAt(site.pos);
  if(world.getDynamicProperty(key))return;
  let loadedAll=true;
  for(const {offset,type,text} of signs){
    const block=local(site,offset);
    if(!block){loadedAll=false;continue;}
    if(!block.isAir)continue;
    const floor=block.below();
    if(!floor||floor.isAir||floor.isLiquid)continue;
    block.setType(type);
    const sign=block.getComponent("minecraft:sign");
    if(!sign)continue;
    const label=site.def.id==="grid_hub"&&phase(site)>0?onlineSwitchLabel(text):text;
    sign.setText(label);
    sign.setText(label,SignSide.Back);
    sign.setWaxed(true);
  }
  if(loadedAll)world.setDynamicProperty(key,true);
}

const onlineSwitchLabel=text=>text.split("\n").slice(0,2).concat("Carrier online").join("\n");

function bindSwitchyardWalker(site,walker){
  const key=keyAt(site.pos);
  walker.setDynamicProperty("bearframe:switchyard_terminal",key);
  walker.triggerEvent(phase(site)<1?"bearframe:relay_offline":"bearframe:switch_a");
  world.setDynamicProperty("bearframe:switchyard_bound:"+key,true);
}

export function greetRegion(site){
  const {def,dim,pos,r}=site;
  const peaceful=world.getDifficulty()===Difficulty.Peaceful;
  const recovery=isRecoverySpillway(site);
  populateBuriedSite(site,at);
  prepareFieldSigns(site);
  const primaryKey="bearframe:crew:"+keyAt(pos);
  if(!world.getDynamicProperty(primaryKey)){
    const isHostilePrimary=def.actor==="bearframe:hollow_scout"||def.actor==="bearframe:hollow_breacher"||def.actor==="bearframe:grid_turret";
    if(!isHostilePrimary||!peaceful){
      const loc=at(pos,recovery?[-3,0,-11]:offsets(site).actor,r);
      if(canSpawnAt(dim,loc,false)){
        const entity=dim.spawnEntity(def.actor,center(loc));
        entity.setDynamicProperty("bearframe:region_role",def.id);
        retainResident(entity);
        if(def.id==="grid_hub")bindSwitchyardWalker(site,entity);
        world.setDynamicProperty(primaryKey,true);
      }
    }
  }
  if(def.id==="grid_hub"&&world.getDynamicProperty(primaryKey)&&
    !world.getDynamicProperty("bearframe:switchyard_bound:"+keyAt(pos))){
    const legacy=dim.getEntities({type:def.actor,location:pos,maxDistance:14}).find(entity=>
      entity.getDynamicProperty("bearframe:region_role")===def.id&&
      !entity.getDynamicProperty("bearframe:switchyard_terminal"));
    if(legacy)bindSwitchyardWalker(site,legacy);
  }
  // Spawn additional contextual site squad members (multiplayer-safe via per-slot dynamic properties)
  const escorts=recovery?[
    {type:"bearframe:grid_watcher",offset:[3,3,-10],hover:true},
    {type:"bearframe:farfield_surveyor",offset:[-2,0,11]},
  ]:def.escorts;
  if(Array.isArray(escorts)){
    for(const [idx,escort] of escorts.entries()){
      if(escort.hostile&&peaceful)continue;
      const eKey=`bearframe:escort:${keyAt(pos)}:${idx}`;
      if(world.getDynamicProperty(eKey))continue;
      const loc=at(pos,escort.offset,r);
      if(!canSpawnAt(dim,loc,Boolean(escort.hover)))continue;
      const entity=dim.spawnEntity(escort.type,center(loc));
      entity.setDynamicProperty("bearframe:region_role",def.id);
        retainResident(entity);
      world.setDynamicProperty(eKey,true);
    }
  }
}

function restoreSite(site,parts){
  const old=parts.map(b=>[b,b.permutation,b.isWaterlogged]);
  try{
    for(const block of parts.slice(0,2)){
      if(block.isWaterlogged)block.setWaterlogged(false);
      block.setType("minecraft:air");
    }
    parts[2].setType("minecraft:sea_lantern");
    setStatus(site,1);
  }catch(error){
    for(const [block,permutation,wet] of old){
      block.setPermutation(permutation);
      if(wet)block.setWaterlogged(true);
    }
    throw error;
  }
}

function respondToRepair(site){
  const {dim,pos,def}=site;
  if(def.id==="grid_hub"){
    for(const walker of dim.getEntities({type:"bearframe:grid_walker",location:pos,maxDistance:20}))
      if(walker.getDynamicProperty("bearframe:switchyard_terminal")===keyAt(pos))
        walker.triggerEvent("bearframe:switch_a");
    for(const {offset,type,text} of FIELD_SIGNS.grid_hub){
      const block=local(site,offset);
      const sign=block?.typeId===type&&block.getComponent("minecraft:sign");
      if(sign&&sign.getText(SignSide.Front)===text){
        sign.setWaxed(false);
        sign.setText(onlineSwitchLabel(text));
        sign.setText(onlineSwitchLabel(text),SignSide.Back);
        sign.setWaxed(true);
      }
    }
    fieldSound(dim,"switchyard",pos);
  }else if(def.id==="spillway_bunker"){
    const sign=local(site,[1,0,-1])?.getComponent("minecraft:sign");
    if(sign){
      sign.setWaxed(false);
      for(const side of [SignSide.Front,SignSide.Back])
        sign.setText("AUXILIARY PUMP\nPressure stable\nTest bench in workshop",side);
      sign.setWaxed(true);
    }
    fieldSound(dim,"pump",pos);
  }else fieldSound(dim,"relay",pos);
}

function claim(player,site){
  if(phase(site)<1)return say(player,"Restore this site's systems before opening the stores.");
  if(phase(site)>1)return say(player,"The site's supplies have already been recovered.");
  const bag=player.getComponent("minecraft:inventory")?.container;
  if(!bag)return;
  const vacancies=[];
  for(let i=0;i<bag.size&&vacancies.length<site.def.loot.length;i++)if(!bag.getItem(i))vacancies.push(i);
  if(vacancies.length<site.def.loot.length)return say(player,`Free ${site.def.loot.length} inventory slots for the stores.`);
  let count=0;
  try{
    for(const [item,amount] of site.def.loot){
      bag.setItem(vacancies[count],new ItemStack(item,amount));
      count++;
    }
    setStatus(site,2);
  }catch(error){
    for(let i=0;i<count;i++)bag.setItem(vacancies[i],undefined);
    throw error;
  }
  return say(player,"Site stores recovered.");
}

let areaSequence=0;
async function withArea(dim,from,to,name,task){
  const ticket=name+"-"+(++areaSequence).toString(36);
  return withTemporaryArea({areas:world.tickingAreaManager,dimension:dim,from,to,name:ticket,task,
    scheduleTimeout:fn=>system.runTimeout(fn,200),cancelTimeout:id=>system.clearRun(id)});
}

function clearDockPreload(dim){
  try{dim.runCommand("tickingarea remove "+DOCK_PRELOAD);}catch{}
}

// A transient ticket alone may wait indefinitely when the orbital dimension
// has no players. Keep one shared preload until all arrivals release it.
async function withDockPreload(dim,task){
  if(dockUsers===0){
    clearDockPreload(dim);
    if(!dim.isChunkLoaded(STATION_ARRIVAL)){
      const x=Math.floor(STATION_ARRIVAL.x/16)*16,z=Math.floor(STATION_ARRIVAL.z/16)*16,y=STATION_ARRIVAL.y;
      const result=dim.runCommand(`tickingarea add ${x} ${y-2} ${z} ${x+15} ${y+5} ${z+15} ${DOCK_PRELOAD} true`);
      if(!result.successCount)throw Error("Could not preload the station dock");
      dockPreloaded=true;
    }
  }
  dockUsers++;
  try{return await task();}
  finally{
    dockUsers--;
    if(dockUsers===0&&dockPreloaded){
      clearDockPreload(dim);
      dockPreloaded=false;
    }
  }
}

function ensureCityCrew(dim,index,pos=CITY_ROLES[index].pos) {
  const role=CITY_ROLES[index];
  const key="bearframe:city_crew:"+index;
  if(world.getDynamicProperty(key))return;
  const cell={x:Math.floor(pos.x),y:Math.floor(pos.y),z:Math.floor(pos.z)};
  if(!canSpawnAt(dim,cell,false))return;
  const e=dim.spawnEntity(role.type,pos);
  e.nameTag=role.name;
  e.setDynamicProperty("bearframe:city_role",index);
  world.setDynamicProperty(key,true);
}

async function buildStationWings(dim) {
  for(const wing of STATION_WINGS){
    const [w,h,d]=wing.size;
    const {origin:from}=wing;
    const to=at(from,[w-1,h-1,d-1]);
    const key="bearframe:station_wing:"+wing.id;
    const built=world.getDynamicProperty(key);
    if(!built || wing.roleIds.some(index=>!world.getDynamicProperty("bearframe:city_crew:"+index))){
      await withArea(dim,from,to,"bearframe-build-"+wing.id,()=>{
        if(!built){
          const occupied=dim.getBlocks(new BlockVolume(from,to),{excludeTypes:["minecraft:air"]},true);
          if(occupied.getCapacity())throw Error("Orbital expansion volume is occupied: "+wing.id);
          world.structureManager.place("bearframe:"+wing.id,dim,from,{includeEntities:false});
          world.setDynamicProperty(key,true);
        }
        for(const index of wing.roleIds)ensureCityCrew(dim,index);
      });
    }
    const linkKey="bearframe:station_link:"+wing.id;
    if(!world.getDynamicProperty(linkKey)){
      const first=at(CITY_ORIGIN,[0,0,0]);
      const last=at(first,[CITY_SIZE.x-1,CITY_SIZE.y-1,CITY_SIZE.z-1]);
      await withArea(dim,first,last,"bearframe-connect-"+wing.id,()=>{
        const blocks=wing.link.map(([x,y,z])=>dim.getBlock({x,y,z}));
        const safe=new Set(["minecraft:air","minecraft:tinted_glass","minecraft:polished_blackstone","minecraft:polished_deepslate","minecraft:smooth_quartz"]);
        if(blocks.some(block=>!block||!safe.has(block.typeId)))throw Error("Orbital passage is obstructed: "+wing.id);
        for(const block of blocks)if(!block.isAir)block.setType("minecraft:air");
        world.setDynamicProperty(linkKey,true);
      });
    }
  }
}

const GATEWAY_BUILT="bearframe:gateway_built";

async function buildGateway(dim){
  if(!world.getDynamicProperty(GATEWAY_BUILT)){
    for(const part of GATEWAY_PARTS){
      const {id,origin,size:[w,h,d]}=part;
      const key="bearframe:gateway_part:"+id;
      if(world.getDynamicProperty(key))continue;
      const to=at(origin,[w-1,h-1,d-1]);
      await withArea(dim,origin,to,key,()=>{
        const occupied=dim.getBlocks(new BlockVolume(origin,to),{excludeTypes:["minecraft:air"]},true);
        if(occupied.getCapacity())throw Error("Gateway hull volume is occupied: "+id);
        world.structureManager.place("bearframe:"+id,dim,origin,{includeEntities:false});
        world.setDynamicProperty(key,true);
      });
    }
    world.setDynamicProperty(GATEWAY_BUILT,true);
  }
  await withArea(dim,{x:0,y:99,z:-11},{x:48,y:106,z:11},"bearframe-gateway-crew",()=>{
    for(const [index,pos] of GATEWAY_CREW.entries())ensureCityCrew(dim,index,pos);
    placeFieldLog(dim,"bearframe:log:station",[
      {x:4,y:101,z:3},{x:5,y:101,z:3},{x:4,y:101,z:-3}
    ]);
  });
}

async function buildAstro(dim){
  const readyKey="bearframe:astro_station_ready";
  if(world.getDynamicProperty(readyKey))return;
  for(const {id,origin,size:[w,h,d]} of ASTRO.parts){
    const key="bearframe:astro_built:"+id;
    if(world.getDynamicProperty(key))continue;
    const end=at(origin,[w-1,h-1,d-1]);
    await withArea(dim,origin,end,id,async()=>{
      if(dim.getBlocks(new BlockVolume(origin,end),{excludeTypes:["minecraft:air"]},true).getCapacity()){
        const structure=world.structureManager.get("bearframe:"+id);
        if(!structure)throw Error("Missing Astro section template: "+id);
        const result=await inspectPlacedSection({structure,origin,size:[w,h,d],
          readBlock:p=>dims(dim,p),yieldTick:()=>new Promise(resolve=>system.run(resolve))});
        if(!result.ok)throw Error("Astro section "+id+" cannot be recovered ("+result.reason+
          (result.position?" at "+keyAt(result.position):"")+"). Existing blocks were preserved.");
        // An interrupted placement can have all blocks but lack its completion marker.
        // Do not place the template again; that could replace existing containers.
        world.setDynamicProperty(key,true);
        return;
      }
      world.structureManager.place("bearframe:"+id,dim,origin,{includeEntities:false});
      world.setDynamicProperty(key,true);
    });
    await new Promise(resolve=>system.run(resolve));
  }
  for(const [slot,{role,name,pos}] of ASTRO.staff.entries()){
    const key="bearframe:astro_staff:"+slot;
    if(world.getDynamicProperty(key))continue;
    const cell={x:Math.floor(pos.x),y:pos.y,z:Math.floor(pos.z)};
    await withArea(dim,cell,cell,"astro-crew-"+slot,()=>{
      if(!standing(dim,pos))throw Error("Blocked crew position at "+keyAt(cell));
      const prior=dim.getEntities({location:pos,maxDistance:2}).find(e=>e.getDynamicProperty("bearframe:astro_slot")===slot);
      if(!prior){
        const e=dim.spawnEntity(CITY_ROLES[role].type,pos);
        try{
          e.nameTag=name??CITY_ROLES[role].name;
          e.setDynamicProperty("bearframe:city_role",name&&role===0?9:role);
          e.setDynamicProperty("bearframe:astro_slot",slot);
        }catch(error){if(e.isValid)e.remove();throw error;}
      }
      world.setDynamicProperty(key,true);
    });
  }
  for(const [i,{pos,text}] of ASTRO.signs.entries()){
    await withArea(dim,pos,pos,"astro-sign-"+i,()=>{
      const sign=dim.getBlock(pos)?.getComponent("minecraft:sign");
      if(!sign)throw Error("Missing station sign "+text);
      sign.setText(text,SignSide.Front);
      sign.setText(text,SignSide.Back);
    });
  }
  const log=ASTRO.log;
  await withArea(dim,log,log,"astro-field-log",()=>placeFieldLog(dim,"bearframe:astro_field_log",[log]));
  world.setDynamicProperty(readyKey,true);
}

async function buildOrbit(){
  const dim=world.getDimension(ORBIT);
  if(ASTRO){await buildAstro(dim);return;}
  if(!world.getDynamicProperty(CITY_BUILT)||world.getDynamicProperty(GATEWAY_BUILT)){
    await buildGateway(dim);
    return;
  }
  const from=CITY_ORIGIN,to=at(from,[CITY_SIZE.x-1,CITY_SIZE.y-1,CITY_SIZE.z-1]);
  await withArea(dim,from,to,"bearframe-city-build",()=>{
    for(const index of DOCK_ROLES)ensureCityCrew(dim,index);
    placeFieldLog(dim,"bearframe:log:station",[
      {x:4,y:101,z:3},{x:5,y:101,z:3},{x:4,y:101,z:-3}
    ]);
  });
  await buildStationWings(dim);
}

export function ensureCity(){
  if(!cityReady){
    const dim=world.getDimension(ORBIT);
    cityReady=withDockPreload(dim,buildOrbit).catch(error=>{cityReady=undefined;throw error;});
  }
  return cityReady;
}

function standing(dim,point){
  const p={x:Math.floor(point.x),y:Math.floor(point.y),z:Math.floor(point.z)};
  const feet=dims(dim,p),floor=feet?.below();
  return feet?.isAir && feet.above()?.isAir && floor && !floor.isAir && !floor.isLiquid;
}

export function travelCity(player,site){
  const origin=center(at(site.pos,LANDING,site.r));
  return dockAtStation(player,origin,()=>dist(player.location,site.pos)<=49);
}

async function dockAtStation(player,origin,canDepart){
  const surface=player.dimension;
  if(surface.id!=="minecraft:overworld")return;
  if(transit.has(player.id))return;
  transit.add(player.id);
  try{
    const dim=world.getDimension(ORBIT);
    await withDockPreload(dim,async()=>{
      await ensureCity();
      const p=STATION_ARRIVAL;
      await withArea(dim,{x:Math.floor(p.x)-3,y:p.y-2,z:Math.floor(p.z)-3},
        {x:Math.floor(p.x)+3,y:p.y+5,z:Math.floor(p.z)+3},"bearframe-dock-in-"+player.id,()=>{
        if(!player.isValid||player.dimension.id!==surface.id)return;
        if(!canDepart())return say(player,"Docking canceled. Stay near your departure point and try again.");
        const arrival=[p,...[-1,1,2].map(dz=>({...p,z:p.z+dz}))]
          .find(point=>standing(dim,point)&&player.tryTeleport(point,{dimension:dim,checkForBlocks:true}));
        if(!arrival)return say(player,"The orbital arrival bay is obstructed.");
        player.setDynamicProperty(TRANSIT,JSON.stringify(origin));
        fieldSound(dim,"dock",arrival);
        say(player,"Bearframe Station. Mira is at Farfield Dispatch. The Commons Deck Lift serves the department pods. Use the Return Desk to go back.");
      });
    });
  }finally{transit.delete(player.id);}
}

export async function useStationTablet(player){
  const dim=player.dimension;
  if(dim.id===ORBIT)return travelSurface(player);
  if(dim.id!=="minecraft:overworld")return say(player,"Use the tablet on the surface or at Bearframe Station.");
  const {x,y,z}=player.location;
  const origin=center({x:Math.floor(x),y:Math.floor(y),z:Math.floor(z)});
  if(!standing(dim,origin))return say(player,"Stand on clear, solid ground to record a return berth.");
  await dockAtStation(player,origin,()=>dist(player.location,origin)<=49&&standing(dim,origin));
}


const returnOffsets=Array.from({length:17},(_,i)=>i-8)
  .flatMap(x=>Array.from({length:17},(_,i)=>[x,i-8]))
  .sort(([ax,az],[bx,bz])=>ax*ax+az*az-bx*bx-bz*bz);
const unsafeSurface=new Set(["minecraft:magma","minecraft:campfire","minecraft:soul_campfire",
  "minecraft:cactus","minecraft:powder_snow","minecraft:fire","minecraft:soul_fire"]);

function emergencySurface(dim,point){
  for(const [dx,dz] of returnOffsets){
    const column={x:Math.floor(point.x)+dx,z:Math.floor(point.z)+dz};
    const top=dim.getTopmostBlock(column);
    if(!top||top.isLiquid||unsafeSurface.has(top.typeId)||top.y+2>=dim.heightRange.max)continue;
    const candidate=center({...column,y:top.y+1});
    if(standing(dim,candidate))return candidate;
  }
}

export async function travelSurface(player){
  if(transit.has(player.id)||player.dimension.id!==ORBIT)return;
  const berth=player.getDynamicProperty(TRANSIT);
  const dim=world.getDimension("overworld");
  const spawn=world.getDefaultSpawnLocation();
  let point;
  if(typeof berth==="string"){
    try{point=JSON.parse(berth);}catch{point=undefined;}
  }
  const recorded=point&&[point.x,point.y,point.z].every(Number.isFinite)?point:undefined;
  const move=(destination,exact)=>withArea(dim,
    {...destination,x:destination.x-8,z:destination.z-8},
    {...destination,x:destination.x+8,z:destination.z+8},
    "bearframe-dock-out-"+player.id,()=>{
      if(!player.isValid||player.dimension.id!==ORBIT)return false;
      const safe=exact&&standing(dim,destination)?destination:emergencySurface(dim,destination);
      if(!safe||!player.tryTeleport(safe,{dimension:dim,checkForBlocks:true}))return false;
      player.setDynamicProperty(TRANSIT,undefined);
      say(player,exact&&safe===destination?"Surface berth reached.":
        exact?"Original berth blocked. Landed on clear ground nearby.":"Emergency descent complete near world spawn.");
      return true;
    });
  transit.add(player.id);
  try{
    if(recorded&&await move(recorded,true))return;
    if(player.isValid&&player.dimension.id===ORBIT&&!(await move(spawn,false)))
      say(player,"No clear emergency landing found. Your berth is saved. Try the Return Desk again.");
  }finally{transit.delete(player.id);}
}

export function interactRegion(player,site,kind,spend){
  const {def}=site;
  if(def.id==="farfield_camp"){
    placeFieldLog(site.dim,"bearframe:log:camp:"+keyAt(site.pos),[
      at(site.pos,[-3,0,2],site.r),at(site.pos,[-3,0,-2],site.r),at(site.pos,[1,0,-2],site.r)
    ]);
    if(player.isSneaking)return travelCity(player,site);
    return say(player,"Farfield checked you in. Sneak-interact here to board for Bearframe City. The city return desk brings you back.");
  }
  if(kind===CHEST){
    noteActivity(player,"Container",def.name+" service stores",site.pos);
    return claim(player,site);
  }
  if(def.id==="intrusion_checkpoint"||def.id==="saltline_town"){
    escalateNearbyDirectorate(site.dim,site.pos,16);
  }
  if(phase(site)>=1){
    if(def.id==="foundry_annex"&&player.isSneaking){
      const bag=player.getComponent("minecraft:inventory")?.container;
      if(!bag?.emptySlotsCount)return say(player,"Open one slot for the Annex stock.");
      const paid=spend(player,"minecraft:coal",1,()=>bag.addItem(new ItemStack("minecraft:iron_ingot",2)));
      return say(player,paid?"The handler delivered two iron ingots.":"The handler needs one coal to process two iron ingots.");
    }
    return say(player,def.note??def.name+" is running. Check the stores beyond the gate.");
  }
  const {seal,signal}=offsets(site);
  const parts=[...seal,signal].map(p=>local(site,p));
  if(parts.slice(0,2).some(b=>!b||!MOORINGS.includes(b.typeId))||parts[2]?.typeId!=="minecraft:coal_block")
    return say(player,"This site's hardware is blocked, altered, or outside loaded terrain.");
  const [item,n]=def.cost;
  if(!spend(player,item,n,()=>restoreSite(site,parts)))
    return say(player,`${def.name} needs ${n} ${item.slice(10).replaceAll("_"," ")}.`);
  try{respondToRepair(site);}catch(error){promiseError(error);}
  return say(player,def.repair);
}

export function installExpedition({validPlayer,spend,attempt}){
  system.beforeEvents.startup.subscribe(({itemComponentRegistry})=>{
    itemComponentRegistry.registerCustomComponent("bearframe:station_transit",{
      onUse:({source:player})=>system.run(()=>{
        if(!validPlayer(player))return;
        useStationTablet(player).catch(error=>{
          promiseError(error);
          if(player.isValid)say(player,String(error?.message??error).startsWith("Astro section ")?String(error.message):"Station transit failed. Try again in a moment.");
        });
      })
    });
  });
  world.beforeEvents.playerInteractWithBlock.subscribe(event=>{
    const {player,block}=event;
    const stationDevice=block.dimension.id===ORBIT&&block.typeId==="minecraft:lodestone";
    const isExit=stationDevice&&[CITY_EXIT,ASTRO?.exit].filter(Boolean).some(p=>keyAt(p)===keyAt(block.location));
    const lift=stationDevice&&ASTRO?.lifts.find(({pos})=>keyAt(pos)===keyAt(block.location));
    if(!isExit&&!lift&&!matchRegionDevice(block))return;
    event.cancel=true;
    if(!event.isFirstEvent)return;
    const {dimension,location}=block;
    system.run(()=>attempt(()=>{
      if(!validPlayer(player)||player.dimension.id!==dimension.id||dist(player.location,location)>49)return;
      if(lift){
        const p=lift.target,cell={x:Math.floor(p.x),y:p.y,z:Math.floor(p.z)};
        const isCurrent=()=>player.isValid&&player.dimension.id===dimension.id&&dist(player.location,location)<=49;
        const area="astro-lift-"+player.id;
        if(transit.has(player.id))return;
        transit.add(player.id);
        withArea(dimension,cell,cell,area,()=>{
          liftLanding({isCurrent,standing:()=>standing(dimension,p),
            teleport:()=>player.tryTeleport(p,{dimension,checkForBlocks:true}),
            notify:message=>say(player,message),label:lift.label});
        }).catch(error=>{
          promiseError(error);
          if(isCurrent())say(player,"Lift could not load its destination. Try again.");
        }).finally(()=>transit.delete(player.id));
        return;
      }
      if(isExit){
        travelSurface(player).catch(error=>{
          promiseError(error);
          if(player.isValid)say(player,"The surface could not be loaded. Try the Return Desk again.");
        });
        return;
      }
      const current=dims(dimension,location),site=matchRegionDevice(current);
      if(site){
        const terminal=current.typeId===site.def.panel;
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
        Promise.resolve(result).catch(promiseError);
      }
    }));
  });
  world.beforeEvents.playerInteractWithEntity.subscribe(event=>{
    const {player,target}=event;
    if(fieldInteraction(player,target))return;
    const staff=target.getDynamicProperty("bearframe:city_role");
    if(typeof staff!=="number" && target.typeId!=="bearframe:ward_resident")return;
    // Allow Atlas Rigger trade in city when sneaking with alloy
    if(target.typeId==="bearframe:atlas_rigger" && player.isSneaking)return;
    event.cancel=true;
    system.run(()=>attempt(()=>{
      if(!validPlayer(player)||!target.isValid||player.dimension.id!==target.dimension.id||dist(player.location,target.location)>49)return;
      noteActivity(player,"Talk",target.nameTag||target.typeId.split(":")[1].replaceAll("_"," "),target.location);
      if(staff===0&&player.isSneaking){
        reportSurvey(player);
        campaignDialogue(player,target,staff);
        return;
      }
      if(campaignDialogue(player,target,staff))return;
      if(stationReport(player,staff)||(staff===14&&relayDebrief(player)))return;
      if(target.typeId==="bearframe:ward_resident"&&player.dimension.id==="minecraft:overworld"){
        campaignSignal(player,"echo","ward_resident");
        if(target.getDynamicProperty("bearframe:region_role")==="echo_ward"){
          say(player,"You can look at the service records. Please leave the core housings closed. We keep our own names here.");
          return;
        }
      }
      say(player,typeof staff==="number"?CITY_ROLES[staff]?.line??"Mind the airlock."
        :"I remember the auxiliary lamps. Leave my memory housing as it is—damage doesn't mean I'm not still here.");
    }));
  });
  world.beforeEvents.playerBreakBlock.subscribe(event=>{
    if(event.block.dimension.id===ORBIT)event.cancel=true;
  });
}
