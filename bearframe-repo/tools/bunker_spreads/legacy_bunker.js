import {BlockTypes,BlockVolume,Difficulty,system,world} from "@minecraft/server";
import {withTemporaryArea} from "./temporary_area.js";
import {PARTS} from "./legacy_bunker_layout.js";
export const LEGACY_BUNKER_MARKER="bearframe:legacy_bunker_datum";
export const LEGACY_BUNKER_ENCOUNTER="bearframe:legacy_bunker_encounter";
// A naturally placed surface datum starts a resumable, one-at-a-time construction.
// Only fresh natural terrain is eligible. Existing non-terrain blocks stop placement.
const naturalNames=`air stone deepslate dirt grass_block grass_path dirt_path coarse_dirt rooted_dirt podzol mycelium moss_block mud clay gravel sand red_sand sandstone red_sandstone tuff calcite andesite granite diorite bedrock snow snow_layer snow_block ice packed_ice water flowing_water lava flowing_lava coal_ore iron_ore copper_ore redstone_ore lit_redstone_ore gold_ore lapis_ore diamond_ore emerald_ore deepslate_coal_ore deepslate_iron_ore deepslate_copper_ore deepslate_redstone_ore lit_deepslate_redstone_ore deepslate_gold_ore deepslate_lapis_ore deepslate_diamond_ore deepslate_emerald_ore dripstone_block pointed_dripstone glow_lichen cave_vines cave_vines_body_with_berries cave_vines_head_with_berries moss_carpet azalea_leaves azalea_leaves_flowered oak_leaves spruce_leaves birch_leaves jungle_leaves acacia_leaves dark_oak_leaves cherry_leaves oak_log spruce_log birch_log jungle_log acacia_log dark_oak_log cherry_log short_grass tall_grass fern large_fern deadbush dead_bush dandelion poppy blue_orchid allium azure_bluet red_tulip orange_tulip white_tulip pink_tulip oxeye_daisy cornflower lily_of_the_valley brown_mushroom red_mushroom amethyst_block budding_amethyst small_amethyst_bud medium_amethyst_bud large_amethyst_bud amethyst_cluster basalt smooth_basalt terracotta hardened_clay white_terracotta orange_terracotta yellow_terracotta red_terracotta brown_terracotta light_gray_terracotta`.split(/\s+/).filter(n=>n!=="bedrock").map(n=>"minecraft:"+n);
let allowed,sequence=0,active;
const retry=new Map();
const add=(p,a)=>({x:p.x+a[0],y:p.y+a[1],z:p.z+a[2]});
const tick=()=>new Promise(resolve=>system.run(resolve));
const inside=(p,a,b)=>p.x>=a.x&&p.x<b.x+1&&p.y>=a.y&&p.y<b.y+1&&p.z>=a.z&&p.z<b.z+1;
const key=p=>`${p.x},${p.y},${p.z}`;
function tell(p,s){if(p?.isValid)p.sendMessage("§b[Farfield]§r "+s);}
async function area(dim,from,to,task){
 const name="legacy-bunker-"+(++sequence).toString(36);
 return withTemporaryArea({areas:world.tickingAreaManager,dimension:dim,from,to,name,task,
  scheduleTimeout:fn=>system.runTimeout(fn,300),cancelTimeout:id=>system.clearRun(id)});
}
function bounds(anchor,part){const a=add(anchor,part.offset),b=add(a,part.size.map(n=>n-1));return [a,b];}
function occupied(dim,a,b){
 return dim.getBlocks(new BlockVolume(a,b),{excludeTypes:allowed},true).getCapacity()>0;
}
function dryEntrance(dim,p){
 const floor=dim.getBlock({x:p.x,y:p.y-1,z:p.z});
 return !!floor&&!floor.isAir&&!floor.isLiquid&&!floor.isWaterlogged&&allowed.includes(floor.typeId);
}
async function build(dim,anchor,player,claim){
 let progress=Number(world.getDynamicProperty(claim)??0);
 const count=PARTS.length;
 if(progress===-1||progress>=count+1)return;
 if(anchor.y<64||anchor.y>180){world.setDynamicProperty(claim,-1);return;}
 allowed??=naturalNames.filter(id=>BlockTypes.get(id));
 // Preflight every section before changing any blocks. Avoid structures, containers,
 // non-natural terrain, and sites where the surface entrance is underwater.
 if(progress===0){
  const d=await area(dim,anchor,anchor,()=>dryEntrance(dim,anchor));
  if(!d){world.setDynamicProperty(claim,-1);return;}
  tell(player,"Ancient bunker signal detected. Surveying the underground facility.");
  for(const part of PARTS){
   const [a,b]=bounds(anchor,part);
   if(a.y<dim.heightRange.min+3||b.y>=dim.heightRange.max){world.setDynamicProperty(claim,-1);return;}
   const blocked=await area(dim,a,b,()=>occupied(dim,a,b));
   if(blocked){world.setDynamicProperty(claim,-1);console.warn("[Bearframe bunker] Site rejected: occupied "+part.id+" at "+key(anchor));return;}
   await tick();
  }
  // Distinguish a surveyed, not-yet-placed facility from an unsurveyed datum.
  world.setDynamicProperty(claim,1);progress=1;
 }
 for(let i=progress-1;i<count;i++){
  const part=PARTS[i],[a,b]=bounds(anchor,part);
  const status=await area(dim,a,b,()=>{
   if(dim.getPlayers({location:a,maxDistance:200}).some(p=>inside(p.location,a,b)))return "player";
   if(occupied(dim,a,b))return "blocked";
   const template=world.structureManager.get("bearframe:"+part.id);
   if(!template)throw Error("Missing bunker template "+part.id);
   world.structureManager.place("bearframe:"+part.id,dim,a,{includeEntities:false});
   world.setDynamicProperty(claim,i+2);
   return "placed";
  });
  if(status!=="placed"){
   // Never overwrite unexpected edits or a possibly interrupted placement.
   // The entrance is built last; a failed partial facility stays inaccessible.
   if(status==="blocked"){world.setDynamicProperty(claim,-1);console.warn("[Bearframe bunker] Stopped at "+part.id+"; existing blocks preserved");}
   return;
  }
  await tick();
 }
 tell(player,"Ancient bunker discovered. Explore the entrance near the survey marker.");
}
export function discoverLegacyBunker(marker,player){
 const {dimension:dim,location:anchor}=marker;
 if(dim.id!=="minecraft:overworld"||active)return;
 const claim="bearframe:legacy_bunker:"+key(anchor);
 const progress=Number(world.getDynamicProperty(claim)??0);
 if(progress===-1||progress>=PARTS.length+1||system.currentTick<(retry.get(claim)??0))return;
 if(retry.size>128)retry.clear();retry.set(claim,system.currentTick+400);
 active=claim;
 build(dim,anchor,player,claim).catch(e=>console.warn("[Bearframe bunker] "+e)).finally(()=>{active=undefined;});
}

// Converted Java mob-spawner positions become one-shot Bearframe encounters.
export function discoverBunkerEncounter(marker,player){
 if(active||!player?.isValid)return;
 const {dimension:dim,location:p}=marker;
 if(dim.id!=="minecraft:overworld")return;
 const claim="bearframe:legacy_bunker_resident:"+key(p);
 if(world.getDynamicProperty(claim))return;
 const roles=["grid_breach_guard","grid_repair_crawler","echo_lost","echo_drifter","grid_protocol_keeper"];
 const h=(Math.imul(p.x,73856093)^Math.imul(p.y,19349663)^Math.imul(p.z,83492791))>>>0;
 const role=world.getDifficulty()===Difficulty.Peaceful?"echo_drifter":roles[h%roles.length];
 const offsets=[[0,1,0],[1,0,0],[-1,0,0],[0,0,1],[0,0,-1],[2,0,0],[-2,0,0],[0,0,2],[0,0,-2]];
 for(const offset of offsets){
  const q=add(p,offset);if(!dim.isChunkLoaded(q))continue;
  const b=dim.getBlock(q),floor=b?.below();
  if(!b?.isAir||!b.above()?.isAir||!floor||floor.isAir||floor.isLiquid||floor.isWaterlogged)continue;
  const pos={x:q.x+.5,y:q.y,z:q.z+.5};
  if(dim.getPlayers({location:pos,maxDistance:6}).length||dim.getEntities({location:pos,maxDistance:2}).length)continue;
  const e=dim.spawnEntity("bearframe:"+role,pos);
  try{e.setDynamicProperty("bearframe:region_role","legacy_bunker");world.setDynamicProperty(claim,true);}
  catch(error){if(e.isValid)e.remove();throw error;}
  return;
 }
}
