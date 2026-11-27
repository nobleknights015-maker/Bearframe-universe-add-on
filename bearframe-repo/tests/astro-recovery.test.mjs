import test from "node:test";
import assert from "node:assert/strict";
import {inspectPlacedSection,liftLanding} from "../behavior_pack/scripts/astro_recovery.js";
const expected={type:{id:"minecraft:quartz_block"},getAllStates:()=>({variant:0})};
const template={getBlockPermutation:({x})=>x===1?undefined:expected,getIsWaterlogged:()=>false};
const matching={permutation:{matches:(id,states)=>id==="minecraft:quartz_block"&&states.variant===0},isWaterlogged:false};
const inspect=(readBlock,structure=template)=>inspectPlacedSection({structure,origin:{x:100,y:50,z:20},size:[3,1,1],readBlock,yieldTick:async()=>{},batchSize:2});
test("recovers fully matching sparse section without reading omitted cells",async()=>{
  const seen=[];const r=await inspect(p=>{seen.push(p.x);return matching;});
  assert.deepEqual(seen,[100,102]);assert.equal(r.ok,true);assert.equal(r.checked,2);
});
test("rejects missing or obstructed authored blocks",async()=>{
  const r=await inspect(p=>p.x===102?{...matching,permutation:{matches:()=>false}}:matching);
  assert.equal(r.ok,false);assert.deepEqual(r.position,{x:102,y:50,z:20});
});
test("rejects changed waterlogged state",async()=>assert.equal((await inspect(()=>({...matching,isWaterlogged:true}))).ok,false));
test("rejects unloaded cells",async()=>assert.equal((await inspect(()=>undefined)).reason,"unloaded"));
test("rejects empty template",async()=>assert.equal((await inspect(()=>matching,{...template,getBlockPermutation:()=>undefined})).ok,false));
test("lift blocked landing reports error without teleport",()=>{
  const messages=[];assert.equal(liftLanding({isCurrent:()=>true,standing:()=>false,teleport:()=>{throw Error("unexpected teleport");},notify:s=>messages.push(s),label:"Deck"}),"blocked");
  assert.match(messages[0],/blocked/);
});
test("failed teleport reports error; successful teleport reports deck",()=>{
  for(const ok of [false,true]){const messages=[];assert.equal(liftLanding({isCurrent:()=>true,standing:()=>true,teleport:()=>ok,notify:s=>messages.push(s),label:"Deck"}),ok?"arrived":"blocked");assert.equal(messages[0]==="Deck",ok);}
});
test("stale interaction does not teleport or report",()=>assert.equal(liftLanding({isCurrent:()=>false,standing:()=>{throw Error("stale");}}),"cancelled"));
