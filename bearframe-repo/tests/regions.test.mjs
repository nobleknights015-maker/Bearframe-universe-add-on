import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import test from "node:test";
import {ACTOR,CACHE,CITY_ARRIVAL,CITY_EXIT,CITY_ROLES,CITY_SIZE,LANDING,ORBIT,PIN,REGION_ANCHOR,SEAL,SURVEY_TYPES} from "../behavior_pack/scripts/regions.js";
import {CITY_ORIGIN,DOCK_ROLES,STATION_WINGS} from "../behavior_pack/scripts/station_layout.js";
import {loadStructure,terminalLookup} from "./structure-fixture.mjs";
const bp=new URL("../behavior_pack/",import.meta.url);
for(const [i,d] of SURVEY_TYPES.entries())test(d.id+" has anchored hardware, approach markers and clear primary + escort spawns",()=>{
 const template=loadStructure(d.id+"_site");
 const {at}=terminalLookup(template,REGION_ANCHOR,i);
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
 assert.equal(at(PIN)?.name,"minecraft:lodestone");
 assert.equal(template.find("bearframe:approach_anchor").length,4);
 if(d.loot){
  assert.equal(at(CACHE).name,"minecraft:barrel");
  for(const part of SEAL)assert.equal(at(part).name,"minecraft:iron_bars");
 }
 const rule=JSON.parse(readFileSync(new URL(`worldgen/structures/${d.id}.json`,bp)));
 const filter=rule["minecraft:jigsaw"].biome_filters[0];
 assert((filter.any_of??[filter]).some(f=>f.value===d.biome));
});
test("orbital arrival, return desk, and every assigned staff slot resolve",()=>{
 const dock=loadStructure("orbital_city");
 assert.deepEqual(dock.size,[CITY_SIZE.x,CITY_SIZE.y,CITY_SIZE.z]);
 const parts=[{template:dock,origin:CITY_ORIGIN,roles:DOCK_ROLES},
   ...STATION_WINGS.map(w=>({template:loadStructure(w.id),origin:w.origin,roles:w.roleIds}))];
 assert.deepEqual(parts.flatMap(p=>p.roles).sort((a,b)=>a-b),CITY_ROLES.map((_,i)=>i));
 for(const [i,part] of parts.entries()){
  const {template,origin,roles}=part;
  const at=p=>template.cell(Math.floor(p.x)-origin.x,p.y-origin.y,Math.floor(p.z)-origin.z)?.name;
  if(i===0)assert.equal(at(CITY_EXIT),"minecraft:lodestone");
  for(const p of [...roles.map(r=>CITY_ROLES[r].pos),...(i===0?[CITY_ARRIVAL]:[])]){
   assert.equal(at(p),"minecraft:air",JSON.stringify(p));
   const floor=at({...p,y:p.y-1});
   assert(floor&&floor!=="minecraft:air",JSON.stringify(p));
   assert.equal(at({...p,y:p.y+1}),"minecraft:air",JSON.stringify(p));
  }
 }
 const dim=JSON.parse(readFileSync(new URL("dimensions/city_orbit.json",bp)))["minecraft:dimension"];
 assert.equal(dim.description.identifier,ORBIT);
 assert.equal(dim.components["minecraft:generation"].generator_type,"void");
});

import {EXTENDED_SURFACE_DATUM,SURFACE_DATUM,SURFACE_SITES} from "../behavior_pack/scripts/surface_layout.js";
for(const [index,site] of SURFACE_SITES.entries())test(site.id+" requires dry-grade placement before the building loads",()=>{
 const marker=loadStructure(site.id);
 assert.deepEqual(marker.size,[1,1,1]);
 const datum=index<16?SURFACE_DATUM:EXTENDED_SURFACE_DATUM;
 assert.equal(marker.cell(0,0,0).name,datum);
 assert.equal(marker.cell(0,0,0).states["bearframe:site"],index);
 const jigsaw=JSON.parse(readFileSync(new URL(`worldgen/structures/${site.id}.json`,bp)))["minecraft:jigsaw"];
 assert.equal(jigsaw.terrain_adaptation,"none");
 const {cell,size}=loadStructure(site.id+"_site");
 assert.deepEqual(size,[site.size.x,site.size.y,site.size.z]);
 for(let x=0;x<site.size.x;x++)for(let z=0;z<site.size.z;z++)assert.equal(cell(x,site.deck-3,z),undefined);
});

test("the Frontier roles are assigned to authored habitats",()=>{
 const habitat=id=>SURVEY_TYPES.find(site=>site.id===id);
 const placements={
  farfield_camp:"field_researcher",grid_hub:"grid_protocol_keeper",foundry_annex:"grid_repair_crawler",
 };
 for(const [site,id] of Object.entries(placements))
  assert(habitat(site).escorts.some(actor=>actor.type==="bearframe:"+id));
 const checkpoint=habitat("intrusion_checkpoint");
 assert.equal(checkpoint.actor,"bearframe:directorate_guard");
 assert(checkpoint.escorts.some(actor=>actor.type==="bearframe:hollow_line"&&actor.hostile));
});

import {FIELD_SIGNS} from "../behavior_pack/scripts/field_signs.js";
import {walkableCells} from "./structure-fixture.mjs";

test("field signage fits authored floors and both Switchyard points are reachable",()=>{
 for(const [id,signs] of Object.entries(FIELD_SIGNS)){
  const template=loadStructure(id+"_site");
  const index=SURVEY_TYPES.findIndex(site=>site.id===id);
  const {position,at}=terminalLookup(template,REGION_ANCHOR,index);
  for(const {offset:[x,y,z]} of signs){
   assert.equal(at([x,y,z])?.name,"minecraft:air",id+" sign slot");
   const floor=at([x,y-1,z])?.name;
   assert(floor&&floor!=="minecraft:air"&&floor!=="minecraft:water",id+" sign floor");
  }
  if(id==="grid_hub"){
   const absolute=offset=>position.map((p,i)=>p+offset[i]);
   const routes=walkableCells(template,[absolute(ACTOR)],SEAL.map(absolute));
   for(const {offset} of signs)assert(routes.has(absolute(offset).join(",")));
  }
 }
});
