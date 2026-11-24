import {RUINS,BUNKER_SIZE,TOWN_SIZE,BUNKER_ENTRY} from "../behavior_pack/scripts/ruins.js";
import {stampBunker,stampTown} from "./ruin_layouts.mjs";
// Bedrock little-endian template serialization follows the original Frontier tool.
import fs from "node:fs";
import {fileURLToPath} from "node:url";
import nbt from "prismarine-nbt";
import {SIZE,DECK,DIRECTION,BREAKER,GATE,RECOVERY,BULKHEAD,POWER_LIGHTS,at} from "../behavior_pack/scripts/layout.js";
const root=fileURLToPath(new URL("../behavior_pack/",import.meta.url));
import {SURVEY_TYPES,REGION_ANCHOR,PIN,ACTOR,CACHE,SEAL,SIGNAL,LANDING,CITY_EXIT} from "../behavior_pack/scripts/regions.js";
const origin={x:10,y:DECK+1,z:8};
const blocks=new Map();
const put=(x,y,z,name,states={})=>blocks.set(`${x},${y},${z}`,{x,y,z,name,states});
function fill(x1,y1,z1,x2,y2,z2,name){
 for(let x=x1;x<=x2;x++) for(let y=y1;y<=y2;y++) for(let z=z1;z<=z2;z++) put(x,y,z,name);
}
function local(location,name,states){
 const {x,y,z}=at(origin,location);
 put(x,y,z,name,states);
}
const air="minecraft:air", deck="minecraft:polished_andesite", masonry="minecraft:cracked_deepslate_tiles";
const trim="minecraft:polished_deepslate", plate="minecraft:iron_block";
fill(0,0,0,20,DECK-1,16,"minecraft:stone");
fill(0,DECK,0,20,DECK,16,deck);
fill(0,DECK+1,0,20,DECK+4,16,air);
// Main hall with two opposite approaches, a loading alcove, and a sealable east wing.
fill(3,DECK+1,3,17,DECK+4,13,masonry);
fill(4,DECK+1,4,16,DECK+3,12,air);
fill(4,DECK+1,3,6,DECK+3,3,air);
fill(4,DECK+1,13,6,DECK+3,13,air);
fill(3,DECK+1,7,3,DECK+2,9,air);
fill(14,DECK+1,4,14,DECK+3,12,trim);
fill(0,DECK,7,8,DECK,9,"minecraft:stone_bricks");
fill(4,DECK,0,6,DECK,16,"minecraft:stone_bricks");
for(const [x,z] of [[4,4],[9,4],[13,12],[5,12],[15,8]]) put(x,DECK+3,z,"minecraft:lantern");
for(const [x,z] of [[4,2],[11,13],[12,4],[17,12]]) {
 put(x,DECK+1,z,"minecraft:moss_block");
 put(x,DECK+2,z,"minecraft:moss_carpet");
}
for(const [x,z] of [[7,3],[8,3],[12,13],[13,13]])put(x,DECK+2,z,"minecraft:glass");
for(const [x,z] of [[4,5],[5,5],[7,11],[11,11]])put(x,DECK+1,z,"minecraft:oxidized_cut_copper");
fill(8,DECK+4,5,12,DECK+4,8,air);
for(const [x,z] of [[1,5],[1,11],[18,4],[18,12]]) {
 put(x,DECK+1,z,trim);
 put(x,DECK+2,z,"minecraft:sea_lantern");
}
local([0,-2,0],"bearframe:relay_anchor",{"bearframe:phase":0});
local(DIRECTION,"minecraft:lodestone");
local([0,0,0],"minecraft:lectern");
local(BREAKER,"minecraft:cut_copper");
local(BULKHEAD,"minecraft:cobblestone");
local([2,-1,0],"minecraft:copper_block");
local([3,-1,0],"minecraft:copper_block");
local(RECOVERY,"minecraft:barrel");
for(const p of GATE)local(p,"minecraft:iron_bars");
for(const p of POWER_LIGHTS)local(p,"minecraft:coal_block");
local([6,0,2],"minecraft:crafting_table");
local([6,0,-2],plate);
for(const [x,z,dx,dz] of [[0,8,-1,0],[5,0,0,-1],[5,16,0,1]]){
 put(x,DECK-2,z,"bearframe:approach_anchor",{"bearframe:graded":false});
 put(x-dx,DECK-2,z-dz,"minecraft:polished_deepslate");
}
emit("maintenance_relay",SIZE,"plains",22,681147);
for(const [index,region] of SURVEY_TYPES.entries()){
 blocks.clear();
 buildRegion(index,region);
 emit(region.id,SIZE,region.biome,region.spacing,region.salt);
}
for(const [i,def] of RUINS.entries()){
 blocks.clear();
 const index=SURVEY_TYPES.length+i;
 if(i<2)stampBunker({put,fill},def,index,i===1);
 else stampTown({put,fill},def,index,i===3);
 emit(def.id,i<2?BUNKER_SIZE:TOWN_SIZE,def.biome,def.spacing,def.salt,
   i<2?BUNKER_ENTRY[1]:DECK,"world_surface",true);
}
blocks.clear();
buildCity();
emit("orbital_city",{x:44,y:8,z:23});

function room(x1,z1,x2,z2,height,wall,door){
 fill(x1,DECK+1,z1,x2,DECK+height,z2,wall);
 fill(x1+1,DECK+1,z1+1,x2-1,DECK+height-1,z2-1,air);
 if(door){
  const [x,z]=door;
  fill(x,DECK+1,z,x,DECK+2,z,air);
 }
}

function buildRegion(index,region){
 const tops=["minecraft:stone_bricks","minecraft:mossy_stone_bricks","minecraft:polished_andesite","minecraft:polished_blackstone_bricks","minecraft:cut_sandstone"];
 const walls=["minecraft:iron_block","minecraft:cracked_deepslate_tiles","minecraft:smooth_quartz","minecraft:polished_blackstone","minecraft:smooth_sandstone"];
 const accent=["minecraft:cyan_terracotta","minecraft:oxidized_cut_copper","minecraft:light_blue_terracotta","minecraft:red_terracotta","minecraft:orange_terracotta"];
 const floor=tops[index],wall=walls[index],stripe=accent[index];
 fill(0,0,0,20,DECK-1,16,"minecraft:stone");
 fill(0,DECK,0,20,DECK,16,floor);
 fill(0,DECK+1,0,20,DECK+4,16,air);
 fill(0,DECK,7,20,DECK,9,"minecraft:stone_bricks");
 fill(9,DECK,0,11,DECK,16,"minecraft:stone_bricks");
 if(index===0){
  room(3,2,9,6,4,wall,[7,6]);room(12,2,17,6,4,wall,[14,6]);
  room(4,10,8,15,3,"minecraft:weathered_cut_copper",[7,10]);
  fill(11,DECK+1,13,16,DECK+1,13,"minecraft:hay_block");
  for(const x of [3,8,13,17])put(x,DECK,8,stripe);
  put(6,DECK+1,4,"minecraft:crafting_table");
  put(13,DECK+1,4,"minecraft:barrel");
  put(15,DECK+1,4,"minecraft:furnace");
 }else{
  room(13,5,18,11,4,wall,[13,8]);
  for(const n of SEAL)local(n,"minecraft:iron_bars");
  local(CACHE,"minecraft:barrel");
  if(index===1){
   for(const [x,z] of [[3,3],[4,12],[8,3],[16,12],[16,4]]){
    put(x,DECK+1,z,"minecraft:moss_block");put(x,DECK+2,z,"minecraft:azalea_leaves");
   }
   fill(5,DECK+3,4,7,DECK+3,12,stripe);
   fill(5,DECK+1,4,5,DECK+3,4,wall);fill(7,DECK+1,12,7,DECK+3,12,wall);
   for(const x of [6,9,11])put(x,DECK,7,"minecraft:oxidized_copper");
  }else if(index===2){
   room(3,2,8,6,4,wall,[6,6]);room(3,10,8,14,4,wall,[6,10]);
   for(const [x,z] of [[4,4],[4,12]]){put(x,DECK+1,z,stripe);put(x+1,DECK+1,z,"minecraft:tinted_glass");}
   fill(7,DECK,7,13,DECK,7,stripe);
   put(15,DECK+3,8,"minecraft:chain");
  }else if(index===3){
   for(const x of [4,16])for(const z of [3,13]){
    fill(x,DECK+1,z,x+1,DECK+3,z,wall);
    put(x,DECK+4,z,stripe);
   }
   fill(4,DECK+3,6,4,DECK+4,10,"minecraft:iron_block");
   fill(4,DECK,6,4,DECK,10,stripe);
   room(6,2,11,6,3,wall,[9,6]);
   put(7,DECK+1,4,"minecraft:target");
  }else{
   room(2,4,7,12,4,wall,[7,8]);
   fill(4,DECK+3,4,4,DECK+3,12,"minecraft:cut_copper");
   for(const [x,z] of [[4,6],[4,10],[9,5],[11,11]]){
    put(x,DECK+1,z,"minecraft:blast_furnace");
    put(x,DECK+2,z,stripe);
   }
   fill(5,DECK,8,13,DECK,8,"minecraft:polished_blackstone");
  }
  local(SIGNAL,"minecraft:coal_block");
 }
 local([0,-2,0],REGION_ANCHOR,{"bearframe:region":index,"bearframe:status":0});
 local(PIN,"minecraft:lodestone");
 local([0,0,0],region.panel);
 for(const loc of [ACTOR,LANDING]) {
  local(loc,air);local([loc[0],loc[1]+1,loc[2]],air);
 }
 for(const [x,z,dx,dz] of [[0,8,-1,0],[20,8,1,0],[10,0,0,-1],[10,16,0,1]]){
  put(x,DECK-2,z,"bearframe:approach_anchor",{"bearframe:graded":false});
  put(x-dx,DECK-2,z-dz,"minecraft:polished_deepslate");
 }
}

function buildCity(){
 const floor="minecraft:smooth_quartz", hull="minecraft:polished_blackstone";
 fill(0,0,0,43,1,22,hull);fill(1,1,1,42,1,21,floor);
 fill(0,2,0,43,7,22,"minecraft:tinted_glass");
 fill(1,2,1,42,6,21,air);
 fill(9,1,9,42,1,13,"minecraft:cyan_terracotta");
 for(const [x1,z1,x2,z2,hue,door] of [[11,2,26,8,"cyan",[18,8]],[11,14,26,20,"pink",[18,14]],
  [28,2,41,8,"blue",[34,8]],[28,14,41,20,"red",[34,14]]]){
  fill(x1,2,z1,x2,5,z2,hull);fill(x1+1,2,z1+1,x2-1,5,z2-1,air);
  fill(x1+1,1,z1+1,x2-1,1,z2-1,`minecraft:${hue}_terracotta`);
  fill(door[0]-1,2,door[1],door[0]+1,4,door[1],air);
  for(let x=x1+2;x<x2;x+=4)put(x,5,z1+2,"minecraft:sea_lantern");
 }
 for(const x of [2,8,14,20,26,32,38,41])put(x,6,11,"minecraft:sea_lantern");
 for(const [x,z] of [[14,16],[17,16],[22,16],[24,19]]){
  put(x,2,z,"minecraft:moss_block");put(x,3,z,"minecraft:flowering_azalea");
 }
 for(const x of [30,33,37,39])put(x,2,3,"minecraft:smithing_table");
 for(const x of [12,16,21,24])put(x,2,3,"minecraft:cartography_table");
 for(const x of [29,32,35,40])put(x,2,19,"minecraft:iron_block");
 put(6,2,6,"minecraft:respawn_anchor");
 put(CITY_EXIT.x,CITY_EXIT.y-99,CITY_EXIT.z+11,"minecraft:lodestone");
}

function emit(id,size,biome,spacing,salt,surface=DECK,projection=id==="intrusion_checkpoint"?"world_surface":"ocean_floor",dry=false){
const palette=new Map(), data=Array(size.x*size.y*size.z).fill(-1);
for(const {x,y,z,name,states} of blocks.values()){
 const key=JSON.stringify([name,states]);
 if(!palette.has(key))palette.set(key,palette.size);
 data[(x*size.y+y)*size.z+z]=palette.get(key);
}
const explicitAir=palette.get(JSON.stringify([air,{}]));
const liquids=data.map(index=>dry&&index!==-1?explicitAir:-1);
const tag=nbt.comp({format_version:nbt.int(1),size:nbt.list(nbt.int([size.x,size.y,size.z])),
 structure:nbt.comp({
 block_indices:{type:"list",value:{type:"list",value:[{type:"int",value:data},{type:"int",value:liquids}]}},
 entities:nbt.list(nbt.comp([])),palette:nbt.comp({default:nbt.comp({
 block_palette:nbt.list(nbt.comp([...palette.keys()].map(key=>{
  const [name,states]=JSON.parse(key);
  return {name:nbt.string(name),states:nbt.comp(Object.fromEntries(Object.entries(states).map(([k,v])=>[k,typeof v==="boolean"?nbt.byte(Number(v)):nbt.int(v)]))),version:nbt.int(18168865)};
 }))),block_position_data:nbt.comp({})})})}),structure_world_origin:nbt.list(nbt.int([0,0,0]))});
function file(path,value){
 fs.mkdirSync(root+path.slice(0,path.lastIndexOf("/")),{recursive:true});
 fs.writeFileSync(root+path,Buffer.isBuffer(value)?value:JSON.stringify(value,null,2)+"\n");
}
file(`structures/bearframe/${id}.mcstructure`,Buffer.from(nbt.writeUncompressed(tag,"little")));
if(!biome)return;
const format_version="1.26.50", identifier=`bearframe:${id}`;
file(`worldgen/structures/${id}.json`,{format_version,"minecraft:jigsaw":{description:{identifier},
 step:"surface_structures",terrain_adaptation:"beard_box",start_pool:identifier,max_depth:1,
 start_height:{type:"constant",value:{absolute:-(surface+1)}},heightmap_projection:projection,
 biome_filters:[{test:"has_biome_tag",operator:"==",value:biome}]}});
file(`worldgen/template_pools/${id}.json`,{format_version,"minecraft:template_pool":{description:{identifier},
 elements:[{element:{element_type:"minecraft:single_pool_element",location:`bearframe/${id}`},weight:1}]}});
file(`worldgen/structure_sets/${id}.json`,{format_version,"minecraft:structure_set":{description:{identifier},
 placement:{type:"minecraft:random_spread",salt,spacing,separation:10,spread_type:"linear"},
 structures:[{structure:identifier,weight:1}]}});

}
