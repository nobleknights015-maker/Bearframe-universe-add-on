import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import test from "node:test";
import {ACTOR,CACHE,CITY_ARRIVAL,CITY_EXIT,CITY_ROLES,CITY_SIZE,LANDING,ORBIT,PIN,REGION_ANCHOR,SEAL,SURVEY_TYPES} from "../behavior_pack/scripts/regions.js";
import {GATEWAY_CREW,GATEWAY_PARTS} from "../behavior_pack/scripts/gateway_layout.js";
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
 const station={cell(x,y,z){
  for(const {template,origin} of parts){
   const block=template.cell(x-origin.x,y-origin.y,z-origin.z);
   if(block)return block;
  }
 }};
 const paths=walkableCells(station,[[Math.floor(CITY_ARRIVAL.x),CITY_ARRIVAL.y,Math.floor(CITY_ARRIVAL.z)]]);
 for(const {name,pos} of CITY_ROLES)
  assert(paths.has([Math.floor(pos.x),pos.y,Math.floor(pos.z)].join(",")),name+" reachable from the dock");
 assert(paths.has([CITY_EXIT.x+1,CITY_EXIT.y,CITY_EXIT.z].join(",")),"return desk reachable");
 const gateway=GATEWAY_PARTS.map(({id,origin})=>({origin,template:loadStructure(id)}));
 const imported={cell(x,y,z){
  for(const {origin,template} of gateway){
   const block=template.cell(x-origin.x,y-origin.y,z-origin.z);
   if(block)return block;
  }
 }};
 const floors=walkableCells(imported,[[Math.floor(CITY_ARRIVAL.x),CITY_ARRIVAL.y,Math.floor(CITY_ARRIVAL.z)]]);
 assert.equal(GATEWAY_CREW.length,CITY_ROLES.length);
 for(const [i,pos] of GATEWAY_CREW.entries())
  assert(floors.has([Math.floor(pos.x),pos.y,Math.floor(pos.z)].join(",")),CITY_ROLES[i].name);
 assert.equal(imported.cell(CITY_EXIT.x,CITY_EXIT.y,CITY_EXIT.z)?.name,"minecraft:lodestone");
 const dim=JSON.parse(readFileSync(new URL("dimensions/city_orbit.json",bp)))["minecraft:dimension"];
 assert.equal(dim.description.identifier,ORBIT);
 assert.equal(dim.components["minecraft:generation"].generator_type,"void");
});

import {EXTENDED_SURFACE_DATUM,SURFACE_DATUM,SURFACE_SITES} from "../behavior_pack/scripts/surface_layout.js";
for(const [index,site] of SURFACE_SITES.entries())test(site.id+" is backed by a full template at native generation height",()=>{
 const marker=loadStructure(site.id);
 assert.deepEqual(marker.size,[1,1,1]);
 const datum=index<16?SURFACE_DATUM:EXTENDED_SURFACE_DATUM;
 assert.equal(marker.cell(0,0,0).name,datum);
 assert.equal(marker.cell(0,0,0).states["bearframe:site"],index);
 const jigsaw=JSON.parse(readFileSync(new URL(`worldgen/structures/${site.id}.json`,bp)))["minecraft:jigsaw"];
 assert.equal(jigsaw.start_height.value.absolute,-site.deck);
 const pool=JSON.parse(readFileSync(new URL(`worldgen/template_pools/${site.id}.json`,bp)))["minecraft:template_pool"];
 assert.equal(pool.elements[0].element.location,`bearframe/${site.id}_site_district`);
 const district=loadStructure(site.id+"_site_district");
 assert.deepEqual(district.size,[site.size.x+64,Math.max(site.size.y,site.deck+25),site.size.z+88]);
 assert.equal(district.cell(19,site.deck+1,21)?.name,"bearframe:field_lantern");
 const core=loadStructure(site.id+"_site");
 for(let x=0;x<site.size.x;x++)for(let z=0;z<site.size.z;z++)for(let y=0;y<site.size.y;y++)
   assert.deepEqual(district.cell(x+32,y,z+44),core.cell(x,y,z),`Quest core changed at ${x},${y},${z}`);
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

test("compact exploration sites preserve authored terminals and supported light blocks",()=>{
 for(const [i,site] of SURVEY_TYPES.entries()){
  const template=loadStructure(site.id+"_field");
  const {position,at}=terminalLookup(template,REGION_ANCHOR,i);
  assert.deepEqual(template.size,[21,19,17]);
  assert.deepEqual(position,[10,14,8]);
  assert.equal(at([0,0,0])?.name,site.panel);
  assert.equal(at(PIN)?.name,"minecraft:lodestone");
  assert.equal(template.find("minecraft:lantern").length,0);
 }
 const relay=loadStructure("maintenance_relay_field");
 assert.equal(relay.find("bearframe:spillway_lamp").length,5);
});

test("all surface landmarks share one native spacing grid and use full templates",()=>{
 const worldgen=new URL("worldgen/",bp);
 const data=JSON.parse(readFileSync(new URL("structure_sets/farfield_landmarks.json",worldgen)))["minecraft:structure_set"];
 assert.equal(data.structures.length,28);
 assert.equal(new Set(data.structures.map(row=>row.structure)).size,28);
 assert(data.placement.spacing>=30);
 assert(data.placement.separation<data.placement.spacing/2);
 for(const row of data.structures){
  const id=row.structure.split(":")[1];
  const pool=JSON.parse(readFileSync(new URL(`template_pools/${id}.json`,worldgen)))["minecraft:template_pool"];
  const district=loadStructure(pool.elements[0].element.location.split("/")[1]);
  const [width,,depth]=district.size;
  assert(district.size.every(n=>n>1),id);
  const jigsaw=JSON.parse(readFileSync(new URL(`structures/${id}.json`,worldgen)))["minecraft:jigsaw"];
  const feet=1-jigsaw.start_height.value.absolute;
  if(id.endsWith("_bunker")){
   const base=loadStructure(pool.elements[0].element.location.split("/")[1].replace(/_district$/,""));
   for(let x=0;x<base.size[0];x++)for(let z=0;z<base.size[2];z++)for(let y=0;y<base.size[1];y++)
    assert.deepEqual(district.cell(x+32,y+22,z+44),base.cell(x,y,z),id+" original bunker");
   const below=feet-16, cross=depth>>1;
   const paths=walkableCells(district,[[23,feet,cross-28]]);
   assert(paths.has([21,below,cross+22].join(",")),id+" lower room accessible from street");
   assert(district.find("minecraft:chest").some(([x,y])=>x<28&&y===below),id+" lower bunker loot");
   if(id==="collapsed_transit_bunker"){
    for(const block of ["golden_rail","rail","quartz_block","glowstone","redstone_torch"])
     assert(district.find("minecraft:"+block).some(([x,y])=>x<28&&y>below-2&&y<below+6),block+" from Lost Cities");
   }
  }
  const routes=walkableCells(district,[[23,feet,1],[width-24,feet,1]]);
  for(const [side,x] of [[0,15],[1,width-16]]){
   for(let plot=0;plot<4;plot++){
    const approach=15+Math.floor(plot*(depth-47)/3);
    for(const lane of [7,8])
     assert(routes.has([x,feet,approach+lane].join(",")),`${id}, side ${side}, plot ${plot}, lane ${lane}`);
   }
  }
 }
});
