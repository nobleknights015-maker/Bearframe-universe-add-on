// Bedrock little-endian template serialization follows the original Frontier tool.
import fs from "node:fs";
import {fileURLToPath} from "node:url";
import nbt from "prismarine-nbt";
import {SIZE,DECK,DIRECTION,BREAKER,GATE,RECOVERY,BULKHEAD,POWER_LIGHTS,at} from "../behavior_pack/scripts/layout.js";
const root=fileURLToPath(new URL("../behavior_pack/",import.meta.url));
const origin={x:10,y:DECK+1,z:8};
const id="maintenance_relay";
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
const palette=new Map(), data=Array(SIZE.x*SIZE.y*SIZE.z).fill(-1);
for(const {x,y,z,name,states} of blocks.values()){
 const key=JSON.stringify([name,states]);
 if(!palette.has(key))palette.set(key,palette.size);
 data[(x*SIZE.y+y)*SIZE.z+z]=palette.get(key);
}
const tag=nbt.comp({format_version:nbt.int(1),size:nbt.list(nbt.int([SIZE.x,SIZE.y,SIZE.z])),
 structure:nbt.comp({
 block_indices:{type:"list",value:{type:"list",value:[{type:"int",value:data},{type:"int",value:data.map(()=>-1)}]}},
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
const format_version="1.26.50", identifier=`bearframe:${id}`;
file(`worldgen/structures/${id}.json`,{format_version,"minecraft:jigsaw":{description:{identifier},
 step:"surface_structures",terrain_adaptation:"beard_box",start_pool:identifier,max_depth:1,
 start_height:{type:"constant",value:{absolute:-(DECK+1)}},heightmap_projection:"ocean_floor",
 biome_filters:[{test:"has_biome_tag",operator:"==",value:"plains"}]}});
file(`worldgen/template_pools/${id}.json`,{format_version,"minecraft:template_pool":{description:{identifier},
 elements:[{element:{element_type:"minecraft:single_pool_element",location:`bearframe/${id}`},weight:1}]}});
file(`worldgen/structure_sets/${id}.json`,{format_version,"minecraft:structure_set":{description:{identifier},
 placement:{type:"minecraft:random_spread",salt:681147,spacing:22,separation:10,spread_type:"linear"},
 structures:[{structure:identifier,weight:1}]}});
