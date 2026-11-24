import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import test from "node:test";
import nbt from "prismarine-nbt";
import {RUINS,BUNKER_SIZE,BUNKER_TERMINAL,TOWN_SIZE,TOWN_TERMINAL} from "../behavior_pack/scripts/ruins.js";
import {REGION_ANCHOR,SURVEY_TYPES} from "../behavior_pack/scripts/regions.js";

for(const [i,def] of RUINS.entries())test(def.id+" has a traversable route to its working terminal",()=>{
 const bunker=i<2, size=bunker?BUNKER_SIZE:TOWN_SIZE;
 const terminal=bunker?BUNKER_TERMINAL:TOWN_TERMINAL;
 const path=new URL(`../behavior_pack/structures/bearframe/${def.id}.mcstructure`,import.meta.url);
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
