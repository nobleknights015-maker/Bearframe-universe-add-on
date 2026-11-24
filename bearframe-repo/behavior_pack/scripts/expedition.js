import {isRecoverySpillway} from "./spillway.js";
import {recordSurvey,reportSurvey} from "./survey_log.js";
import {escalateNearbyDirectorate} from "./living_world.js";
import {BlockVolume,Difficulty,ItemStack,system,world} from "@minecraft/server";
import {ROTATIONS,at} from "./layout.js";
import {
  TYPES,REGION_ANCHOR,PIN,CACHE,SEAL,ACTOR,SIGNAL,LANDING,
  ORBIT,CITY_SIZE,CITY_ARRIVAL,CITY_EXIT,CITY_ROLES
} from "./regions.js";

const CITY_ORIGIN={x:0,y:99,z:-11};
const CHEST="minecraft:barrel";
const STATUS="bearframe:status";
const TRANSIT="bearframe:return_berth";
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

export function greetRegion(site){
  const {def,dim,pos,r}=site;
  const peaceful=world.getDifficulty()===Difficulty.Peaceful;
  const recovery=isRecoverySpillway(site);
  const primaryKey="bearframe:crew:"+keyAt(pos);
  if(!world.getDynamicProperty(primaryKey)){
    const isHostilePrimary=def.actor==="bearframe:hollow_scout"||def.actor==="bearframe:hollow_breacher"||def.actor==="bearframe:grid_turret";
    if(!isHostilePrimary||!peaceful){
      const loc=at(pos,recovery?[-3,0,-11]:offsets(site).actor,r);
      if(canSpawnAt(dim,loc,false)){
        const entity=dim.spawnEntity(def.actor,center(loc));
        entity.setDynamicProperty("bearframe:region_role",def.id);
        world.setDynamicProperty(primaryKey,true);
      }
    }
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

async function withArea(dim,from,to,name,task){
  const areas=world.tickingAreaManager;
  await areas.createTickingArea(name,{dimension:dim,from,to});
  try{return await task();}
  finally{areas.removeTickingArea(name);}
}

async function buildOrbit(){
  const dim=world.getDimension(ORBIT);
  const from=CITY_ORIGIN,to=at(from,[CITY_SIZE.x-1,CITY_SIZE.y-1,CITY_SIZE.z-1]);
  await withArea(dim,from,to,"bearframe-city-build",()=>{
    if(!world.getDynamicProperty(CITY_BUILT)){
      const placed=dim.getBlocks(new BlockVolume(from,to),{excludeTypes:["minecraft:air"]},true);
      if(placed.getCapacity())throw Error("Orbital dock volume is occupied.");
      world.structureManager.place("bearframe:orbital_city",dim,from,{includeEntities:false});
      world.setDynamicProperty(CITY_BUILT,true);
    }
    for(const [index,role] of CITY_ROLES.entries()){
      const key="bearframe:city_crew:"+index;
      if(world.getDynamicProperty(key))continue;
      const cell={x:Math.floor(role.pos.x),y:Math.floor(role.pos.y),z:Math.floor(role.pos.z)};
      if(!canSpawnAt(dim,cell,false))continue;
      const e=dim.spawnEntity(role.type,role.pos);
      e.nameTag=role.name;
      e.setDynamicProperty("bearframe:city_role",index);
      world.setDynamicProperty(key,true);
    }
  });
}

export function ensureCity(){
  if(!cityReady)cityReady=buildOrbit().catch(error=>{cityReady=undefined;throw error;});
  return cityReady;
}

function standing(dim,point){
  const p={x:Math.floor(point.x),y:Math.floor(point.y),z:Math.floor(point.z)};
  const feet=dims(dim,p),floor=feet?.below();
  return feet?.isAir && feet.above()?.isAir && floor && !floor.isAir && !floor.isLiquid;
}

export async function travelCity(player,site){
  if(transit.has(player.id))return;
  transit.add(player.id);
  try{
    await ensureCity();
    const dim=world.getDimension(ORBIT), origin=center(at(site.pos,LANDING,site.r));
    await withArea(dim,{x:0,y:99,z:-12},{x:10,y:107,z:12},"bearframe-dock-in-"+player.id,()=>{
      if(!player.isValid || player.dimension.id!==site.dim.id || dist(player.location,site.pos)>49)return;
      if(!standing(dim,CITY_ARRIVAL))return say(player,"The orbital arrival bay is obstructed.");
      player.setDynamicProperty(TRANSIT,JSON.stringify(origin));
      if(!player.tryTeleport(CITY_ARRIVAL,{dimension:dim,checkForBlocks:true})){
        player.setDynamicProperty(TRANSIT,undefined);
        return say(player,"Docking failed. Try the camp terminal again.");
      }
      say(player,"Bearframe City. All six department bays are active. Use the Return Desk in the arrival bay to go back.");
    });
  }finally{transit.delete(player.id);}
}

export async function travelSurface(player){
  if(transit.has(player.id))return;
  const berth=player.getDynamicProperty(TRANSIT);
  if(typeof berth!=="string")return say(player,"No surface berth recorded.");
  const point=JSON.parse(berth), dim=world.getDimension("overworld");
  transit.add(player.id);
  try{
    await withArea(dim,{...point,x:point.x-3,z:point.z-3},{...point,x:point.x+3,z:point.z+3},"bearframe-dock-out-"+player.id,()=>{
      if(!player.isValid || player.dimension.id!==ORBIT)return;
      let safe;
      for(const [x,z] of [[0,0],[1,0],[-1,0],[0,1],[0,-1],[2,0],[-2,0],[0,2],[0,-2]]){
        const p={...point,x:point.x+x,z:point.z+z};
        if(standing(dim,p)){safe=p;break;}
      }
      if(!safe)return say(player,"Surface berth is blocked. The station will hold your departure.");
      if(player.tryTeleport(safe,{dimension:dim,checkForBlocks:true})){
        player.setDynamicProperty(TRANSIT,undefined);
        say(player,"Surface berth reached.");
      }
    });
  }finally{transit.delete(player.id);}
}

export function interactRegion(player,site,kind,spend){
  const {def}=site;
  if(def.id==="farfield_camp"){
    if(player.isSneaking)return travelCity(player,site);
    return say(player,"Farfield checked you in. Sneak-interact here to board for Bearframe City. The city return desk brings you back.");
  }
  if(kind===CHEST)return claim(player,site);
  if(def.id==="intrusion_checkpoint"||def.id==="saltline_town"){
    escalateNearbyDirectorate(site.dim,site.pos,16);
  }
  if(phase(site)>=1)return say(player,def.note??def.name+" is running. Check the stores beyond the gate.");
  const {seal,signal}=offsets(site);
  const parts=[...seal,signal].map(p=>local(site,p));
  if(parts.slice(0,2).some(b=>!b||!MOORINGS.includes(b.typeId))||parts[2]?.typeId!=="minecraft:coal_block")
    return say(player,"This site's hardware is blocked, altered, or outside loaded terrain.");
  const [item,n]=def.cost;
  return say(player,spend(player,item,n,()=>restoreSite(site,parts))
    ?def.repair:`${def.name} needs ${n} ${item.slice(10).replaceAll("_"," ")}.`);
}

export function installExpedition({validPlayer,spend,attempt}){
  world.beforeEvents.playerInteractWithBlock.subscribe(event=>{
    const {player,block}=event;
    const isExit=block.dimension.id===ORBIT && block.typeId==="minecraft:lodestone" && keyAt(block.location)===keyAt(CITY_EXIT);
    if(!isExit&&!matchRegionDevice(block))return;
    event.cancel=true;
    if(!event.isFirstEvent)return;
    const {dimension,location}=block;
    system.run(()=>attempt(()=>{
      if(!validPlayer(player)||player.dimension.id!==dimension.id||dist(player.location,location)>49)return;
      if(isExit){travelSurface(player).catch(promiseError);return;}
      const current=dims(dimension,location),site=matchRegionDevice(current);
      if(site){
        if(current.typeId===site.def.panel)recordSurvey(player,site.def.id);
        Promise.resolve(interactRegion(player,site,current.typeId,spend)).catch(promiseError);
      }
    }));
  });
  world.beforeEvents.playerInteractWithEntity.subscribe(event=>{
    const {player,target}=event;
    const staff=target.getDynamicProperty("bearframe:city_role");
    if(typeof staff!=="number" && target.typeId!=="bearframe:ward_resident")return;
    // Allow Atlas Rigger trade in city when sneaking with alloy
    if(target.typeId==="bearframe:atlas_rigger" && player.isSneaking)return;
    event.cancel=true;
    system.run(()=>attempt(()=>{
      if(!validPlayer(player)||!target.isValid||player.dimension.id!==target.dimension.id||dist(player.location,target.location)>49)return;
      if(staff===0&&player.isSneaking){reportSurvey(player);return;}
      say(player,typeof staff==="number"?CITY_ROLES[staff]?.line??"Mind the airlock."
        :"I remember the auxiliary lamps. Leave my memory housing as it is—damage doesn't mean I'm not still here.");
    }));
  });
  world.beforeEvents.playerBreakBlock.subscribe(event=>{
    if(event.block.dimension.id===ORBIT)event.cancel=true;
  });
}
