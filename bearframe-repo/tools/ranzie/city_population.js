import {BlockTypes,BlockVolume,Difficulty,GameMode,system,world} from "@minecraft/server";
const MARKER="bearframe:overgrown_city_marker";
const ROLE_POOLS=["echo_drifter","echo_route_trader","echo_lost","grid_repair_crawler","grid_breach_guard","directorate_guard","farfield_surveyor"];
const HOSTILE=new Set(["echo_lost","grid_breach_guard","directorate_guard"]);
const cache=new Map();
function hash(x,z){return (Math.imul(x,73856093)^Math.imul(z,19349663))>>>0;}
function roleAt(x,z){const n=hash(x,z)%100;return ROLE_POOLS[n<38?0:n<52?1:n<70?2:n<82?3:n<89?4:n<97?5:6];}
function safe(dim,p){
 if(!dim.isChunkLoaded(p))return false;
 const b=dim.getBlock(p),floor=b?.below();
 return Boolean(b?.isAir&&!b.isWaterlogged&&b.above()?.isAir&&floor&&!floor.isAir&&!floor.isLiquid&&!floor.isWaterlogged);
}
function populate(dim,p){
 const gx=Math.floor(p.x/48),gz=Math.floor(p.z/48),key=`bearframe:overgrown_city:${gx},${gz}`;
 if(world.getDynamicProperty(key))return;
 let role=roleAt(gx,gz);
 if(HOSTILE.has(role)&&world.getDifficulty()===Difficulty.Peaceful)role="echo_drifter";
 const candidates=[[0,1,0],[2,1,0],[-2,1,0],[0,1,2],[0,1,-2]];
 for(const [x,y,z] of candidates){
  const point={x:p.x+x,y:p.y+y,z:p.z+z};
  if(!safe(dim,point))continue;
  const loc={x:point.x+.5,y:point.y,z:point.z+.5};
  if(dim.getPlayers({location:loc,maxDistance:6}).length||dim.getEntities({location:loc,maxDistance:2}).length)continue;
  const entity=dim.spawnEntity("bearframe:"+role,loc);
  try{
   entity.setDynamicProperty("bearframe:region_role","overgrown_city");
   entity.setDynamicProperty("bearframe:city_cell",key);
   // The district claim is persisted before another player can trigger it.
   world.setDynamicProperty(key,true);
  }catch(error){if(entity.isValid)entity.remove();throw error;}
  return;
 }
}
world.afterEvents.playerLeave.subscribe(({playerId})=>cache.delete(playerId));
system.runInterval(()=>{
 if(!BlockTypes.get(MARKER))return;
 for(const player of world.getAllPlayers()){
  if(!player.isValid||player.dimension.id!=="minecraft:overworld"||![GameMode.Survival,GameMode.Adventure,GameMode.Creative].includes(player.getGameMode()))continue;
  const dim=player.dimension,loc=player.location,now=system.currentTick;
  const cell=[loc.x,loc.y,loc.z].map(n=>Math.floor(n/16)).join(",");
  const previous=cache.get(player.id);if(previous?.cell===cell&&now-previous.tick<240)continue;
  cache.set(player.id,{cell,tick:now});
  try{
   const y=Math.floor(loc.y),a={x:Math.floor(loc.x)-24,y:Math.max(dim.heightRange.min,y-12),z:Math.floor(loc.z)-24},b={x:Math.floor(loc.x)+24,y:Math.min(dim.heightRange.max-1,y+12),z:Math.floor(loc.z)+24};
   for(const p of dim.getBlocks(new BlockVolume(a,b),{includeTypes:[MARKER]},true).getBlockLocationIterator())populate(dim,p);
  }catch(error){console.warn("[Bearframe city population] "+error);}
 }
},80);
