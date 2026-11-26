import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import test from "node:test";
import nbt from "prismarine-nbt";
import {RUINS} from "../behavior_pack/scripts/ruins.js";
import {PIN,REGION_ANCHOR,SURVEY_TYPES} from "../behavior_pack/scripts/regions.js";

import {loadStructure,terminalLookup,walkableCells} from "./structure-fixture.mjs";

for(const [i,def] of RUINS.entries())if(i!==0)test(def.id+" has a traversable route to its working terminal",()=>{
 const template=loadStructure(def.id+(def.bunker?"":"_site"));
 const {position,at}=terminalLookup(template,REGION_ANCHOR,SURVEY_TYPES.length+i);
 assert.equal(at([0,0,0])?.name,def.panel);
 assert.equal(at(PIN)?.name,"minecraft:lodestone");
 assert.equal(at(def.layout.cache)?.name,"minecraft:barrel");
 for(const p of def.layout.seal)assert.equal(at(p)?.name,"minecraft:iron_bars");
 const crew=[{type:def.actor,offset:def.layout.actor},...(def.escorts??[])];
 for(const {type,offset:[x,y,z],hover} of crew){
  assert.equal(at([x,y,z])?.name,"minecraft:air",type+" feet");
  assert.equal(at([x,y+1,z])?.name,"minecraft:air",type+" head");
  if(!hover)assert(at([x,y-1,z])?.name && at([x,y-1,z]).name!=="minecraft:air",type+" floor");
 }
 const starts=template.find("bearframe:approach_anchor").map(([x,y,z])=>[x,y+3,z]);
 assert(starts.length>0,"Missing approach");
 const [x,y,z]=position;
 const visited=walkableCells(template,starts);
 assert([[x-1,y,z],[x+1,y,z],[x,y,z-1],[x,y,z+1]].some(p=>visited.has(p.join(","))),
   "Terminal unreachable from the approach");
});

import {SPILLWAY_DATUM,SPILLWAY_FLIGHT,SPILLWAY_MARKER,SPILLWAY_PANEL,SPILLWAY_SIGNS} from "../behavior_pack/scripts/spillway_layout.js";

test("Spillway generates the full facility with its entrance at surface level",()=>{
 const load=(part)=>new URL(`../behavior_pack/${part}`,import.meta.url);
 const jigsaw=JSON.parse(readFileSync(load("worldgen/structures/spillway_bunker.json")))["minecraft:jigsaw"];
 const pool=JSON.parse(readFileSync(load("worldgen/template_pools/spillway_bunker.json")))["minecraft:template_pool"];
 assert.equal(pool.elements[0].element.location,"bearframe/spillway_facility_district");
 assert.equal(jigsaw.start_height.value.absolute,-SPILLWAY_DATUM[1]-22);
});

test("Spillway preserves five-wide, unobstructed stairs and links every dry room to the entrance",()=>{
 const raw=nbt.simplify(nbt.parseUncompressed(readFileSync(new URL(
   "../behavior_pack/structures/bearframe/spillway_facility.mcstructure",import.meta.url)),"little"));
 const [sx,sy,sz]=raw.size, {block_palette:palette}=raw.structure.palette.default;
 const [indices]=raw.structure.block_indices;
 const get=(x,y,z)=>palette[indices[(x*sy+y)*sz+z]];
 const name=(x,y,z)=>get(x,y,z)?.name;
 const air=(x,y,z)=>name(x,y,z)==="minecraft:air";
 const [px,py,pz]=SPILLWAY_PANEL, def=RUINS[0];
 const local=([x,y,z])=>name(px+x,py+y,pz+z);
 assert.equal(name(...SPILLWAY_DATUM),SPILLWAY_MARKER);
 assert.equal(local([0,0,0]),def.panel);
 assert.equal(local([0,-2,0]),REGION_ANCHOR);
 assert.equal(local(def.layout.cache),"minecraft:barrel");
 assert(def.layout.seal.every(p=>local(p)==="minecraft:iron_bars"));
 assert.equal(name(40,4,7),"minecraft:water");
 for(const {pos} of SPILLWAY_SIGNS)assert.equal(name(...pos),"minecraft:spruce_standing_sign");
 for(const {x,y,stair} of SPILLWAY_FLIGHT)for(let z=16;z<=20;z++){
  assert.equal(name(x,y,z),stair?"minecraft:stone_brick_stairs":"minecraft:polished_andesite");
  if(stair)assert.equal(get(x,y,z).states.weirdo_direction,1);
  for(let h=1;h<=(x<=5?3:4);h++)assert(air(x,y+h,z),`blocked stair at ${x},${y+h},${z}`);
 }
 const queue=[[4,20,18]], visited=new Set();
 while(queue.length){
  const [x,y,z]=queue.pop(), key=[x,y,z].join(",");
  if(visited.has(key)||x<0||x>=sx||z<0||z>=sz||y<1||y+1>=sy||
     !air(x,y,z)||!air(x,y+1,z)||!name(x,y-1,z)||air(x,y-1,z)||name(x,y-1,z)==="minecraft:water")continue;
  visited.add(key);
  for(const [dx,dz] of [[1,0],[-1,0],[0,1],[0,-1]])for(const dy of [0,1,-1])
   queue.push([x+dx,y+dy,z+dz]);
 }
 for(const room of [[24,5,18],[36,5,18],[34,5,5],[34,5,25],[45,5,28]])
  assert(visited.has(room.join(",")),`unreachable room at ${room}`);
});
