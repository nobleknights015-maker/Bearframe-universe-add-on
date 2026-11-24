import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import test from "node:test";
import nbt from "prismarine-nbt";
import {ACTOR,CACHE,CITY_ARRIVAL,CITY_EXIT,CITY_ROLES,CITY_SIZE,LANDING,ORBIT,REGION_ANCHOR,SEAL,SURVEY_TYPES} from "../behavior_pack/scripts/regions.js";
const bp=new URL("../behavior_pack/",import.meta.url);
function voxelLookup(name){
 const path=new URL(`structures/bearframe/${name}.mcstructure`,bp);
 const n=nbt.simplify(nbt.parseUncompressed(readFileSync(path),"little"));
 const [,sy,sz]=n.size,{block_palette:p}=n.structure.palette.default;
 return {size:n.size,cell:(x,y,z)=>p[n.structure.block_indices[0][(x*sy+y)*sz+z]]};
}
for(const [i,d] of SURVEY_TYPES.entries())test(d.id+" has anchored hardware, approach markers and clear primary + escort spawns",()=>{
 const {cell}=voxelLookup(d.id), at=([x,y,z])=>cell(x+10,y+14,z+8);
 const anchor=at([0,-2,0]);
 assert.equal(anchor.name,REGION_ANCHOR);
 assert.equal(anchor.states["bearframe:region"],i);
 assert.equal(at([0,0,0]).name,d.panel);
 assert.equal(at(ACTOR).name,"minecraft:air");
 assert.equal(at(LANDING).name,"minecraft:air");
 for(const escort of d.escorts||[]){
  const [ex,ey,ez]=escort.offset;
  assert.equal(at([ex,ey,ez]).name,"minecraft:air",`${d.id} escort ${escort.type} feet blocked`);
  assert.equal(at([ex,ey+1,ez]).name,"minecraft:air",`${d.id} escort ${escort.type} head blocked`);
  if(!escort.hover){
   assert.notEqual(at([ex,ey-1,ez]).name,"minecraft:air",`${d.id} escort ${escort.type} lacks floor`);
  }
 }
 for(const [x,z] of [[0,8],[20,8],[10,0],[10,16]])assert.equal(cell(x,11,z).name,"bearframe:approach_anchor");
 if(d.loot){
  assert.equal(at(CACHE).name,"minecraft:barrel");
  for(const part of SEAL)assert.equal(at(part).name,"minecraft:iron_bars");
 }
 const rule=JSON.parse(readFileSync(new URL(`worldgen/structures/${d.id}.json`,bp)));
 assert.equal(rule["minecraft:jigsaw"].biome_filters[0].value,d.biome);
});
test("orbital arrival bay, return desk and all 7 canonical department staff resolve",()=>{
 const {size,cell}=voxelLookup("orbital_city");
 assert.deepEqual(size,[CITY_SIZE.x,CITY_SIZE.y,CITY_SIZE.z]);
 const at=({x,y,z})=>cell(Math.floor(x),y-99,Math.floor(z)+11).name;
 assert.equal(CITY_ROLES.length,7);
 for(const p of [CITY_ARRIVAL,...CITY_ROLES.map(r=>r.pos)]){
  assert.equal(at(p),"minecraft:air");
  assert.notEqual(at({...p,y:p.y-1}),"minecraft:air");
  assert.equal(at({...p,y:p.y+1}),"minecraft:air");
 }
 assert.equal(at(CITY_EXIT),"minecraft:lodestone");
 const dim=JSON.parse(readFileSync(new URL("dimensions/city_orbit.json",bp)))["minecraft:dimension"];
 assert.equal(dim.description.identifier,ORBIT);
 assert.equal(dim.components["minecraft:generation"].generator_type,"void");
});
