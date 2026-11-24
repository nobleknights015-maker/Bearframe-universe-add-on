import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import test from "node:test";
import nbt from "prismarine-nbt";
import {RUINS,BUNKER_SIZE,BUNKER_TERMINAL,TOWN_SIZE,TOWN_TERMINAL} from "../behavior_pack/scripts/ruins.js";
import {REGION_ANCHOR,SURVEY_TYPES} from "../behavior_pack/scripts/regions.js";

for(const [i,def] of RUINS.entries())if(i!==0)test(def.id+" has a traversable route to its working terminal",()=>{
 const bunker=i<2, size=bunker?BUNKER_SIZE:TOWN_SIZE;
 const terminal=bunker?BUNKER_TERMINAL:TOWN_TERMINAL;
 const path=new URL(`../behavior_pack/structures/bearframe/${def.id}${bunker?"":"_site"}.mcstructure`,import.meta.url);
 const raw=nbt.simplify(nbt.parseUncompressed(readFileSync(path),"little"));
 assert.deepEqual(raw.size,[size.x,size.y,size.z]);
 const n=raw.structure.palette.default.block_palette;
 const keys=raw.structure.block_indices[0];
 const cell=(x,y,z)=>n[keys[(x*size.y+y)*size.z+z]];
 const local=([x,y,z])=>cell(x+terminal[0],y+terminal[1],z+terminal[2]);
 assert.equal(local([0,-2,0]).name,REGION_ANCHOR);
 assert.equal(local([0,-2,0]).states["bearframe:region"],SURVEY_TYPES.length+i);
 assert.equal(local([0,0,0]).name,def.panel);
 assert.equal(local(def.layout.cache).name,"minecraft:barrel");
 assert(def.layout.seal.every(p=>local(p).name==="minecraft:iron_bars"));
 assert.equal(local(def.layout.actor).name,"minecraft:air");
 for(const escort of def.escorts||[]){
  const [ex,ey,ez]=escort.offset;
  assert.equal(local([ex,ey,ez]).name,"minecraft:air",`${def.id} escort ${escort.type} feet blocked`);
  assert.equal(local([ex,ey+1,ez]).name,"minecraft:air",`${def.id} escort ${escort.type} head blocked`);
  if(!escort.hover){
   assert.notEqual(local([ex,ey-1,ez]).name,"minecraft:air",`${def.id} escort ${escort.type} lacks floor`);
  }
 }
 const air=(x,y,z)=>cell(x,y,z)?.name==="minecraft:air";
 const valid=(x,y,z)=>x>=0&&x<size.x&&z>=0&&z<size.z&&y>0&&y+1<size.y
   &&air(x,y,z)&&air(x,y+1,z)&&cell(x,y-1,z)&&!air(x,y-1,z);
 const queue=[bunker?[0,21,11]:[0,14,15]],visited=new Set();
 assert(valid(...queue[0]),"blocked outer approach");
 while(queue.length){
  const [x,y,z]=queue.pop(),key=[x,y,z].join(",");
  if(visited.has(key)||!valid(x,y,z))continue;
  visited.add(key);
  for(const [dx,dz] of [[1,0],[-1,0],[0,1],[0,-1]])for(const dy of [0,1,-1])queue.push([x+dx,y+dy,z+dz]);
 }
 assert(visited.has([terminal[0]-1,terminal[1],terminal[2]].join(",")),"terminal unreachable from outside");
 if(bunker){
  for(let x=5;x<=16;x++){
    const y=20-(x-5);
    assert.equal(cell(x,y,11).name,"minecraft:stone_brick_stairs");
    assert.equal(cell(x,y,11).states.weirdo_direction,1);
  }
 }else{
  assert(visited.has("18,14,0")&&visited.has("18,14,30")&&visited.has("36,14,15"),"roads must connect all four edges");
 }
});

import {SPILLWAY_DATUM,SPILLWAY_FLIGHT,SPILLWAY_MARKER,SPILLWAY_PANEL,SPILLWAY_SIGNS} from "../behavior_pack/scripts/spillway_layout.js";

test("Spillway starts as a one-block datum with no jigsaw terrain sculpting",()=>{
 const load=(part)=>new URL(`../behavior_pack/${part}`,import.meta.url);
 const jigsaw=JSON.parse(readFileSync(load("worldgen/structures/spillway_bunker.json")))[ "minecraft:jigsaw" ];
 const beacon=nbt.simplify(nbt.parseUncompressed(readFileSync(load("structures/bearframe/spillway_bunker.mcstructure")),"little"));
 assert.deepEqual(beacon.size,[1,1,1]);
 assert.equal(beacon.structure.palette.default.block_palette[0].name,SPILLWAY_MARKER);
 assert.equal(jigsaw.terrain_adaptation,"none");
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
