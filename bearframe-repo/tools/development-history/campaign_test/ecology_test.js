import assert from "node:assert/strict";
import {world,Difficulty} from "@minecraft/server";
import {picks} from "@minecraft/server-ui";
import {fieldProgress,installEcology,populateRuin,retainResident} from "./ecology.js";

const scope=new Map();
const dim={id:"minecraft:overworld"};
const cargo=new Array(20);
const bag={size:cargo.length,getItem:i=>cargo[i],setItem:(i,value)=>cargo[i]=value};
const p={id:"traveler",dimension:dim,location:{x:3,y:70,z:3},isValid:true,isSneaking:false,selectedSlotIndex:0,
 getComponent:()=>({container:bag}),getDynamicProperty:k=>scope.get(k),setDynamicProperty:(k,v)=>scope.set(k,v),sendMessage:()=>{}};
const trader={typeId:"bearframe:echo_route_trader",isValid:true,dimension:dim,location:p.location};
installEcology();
async function menu(...choices){
 picks.push(...choices);
 world.beforeEvents.playerInteractWithEntity.fire({player:p,target:trader});
 await new Promise(r=>setImmediate(r));
 assert.equal(picks.length,0);
}
await menu(1,0);
fieldProgress(p,"read","relay_nine",{x:1,y:70,z:4});
fieldProgress(p,"read","relay_nine",{x:1,y:70,z:4});
assert.equal(JSON.parse(scope.get("bearframe:field_requests")).echo_route_trader.progress,1);
assert.equal(JSON.parse(scope.get("bearframe:campaign_v1")).facts["talk:echo"],1);
fieldProgress(p,"read","frontier_ruin",{x:9,y:70,z:4});
await menu(1,0);
assert.equal(cargo.filter(Boolean).length,2);
assert.equal(JSON.parse(scope.get("bearframe:field_requests")).echo_route_trader.done,1);
await menu(1,0);
assert.equal(JSON.parse(scope.get("bearframe:field_requests")).echo_route_trader.progress,0);
const settlers=[];
const floor={isAir:false,isLiquid:false};
const air={isAir:true,above:()=>air,below:()=>floor};
const mock={isChunkLoaded:()=>true,getBlock:()=>air,spawnEntity:(id)=>({typeId:id,triggerEvent:event=>settlers.push([id,event]),setDynamicProperty(){}})};
world.getDifficulty=()=>Difficulty.Normal;
for(let idx=0;idx<20;idx++)populateRuin(mock,"collapsed_transit_bunker",{x:idx*47,y:66,z:50});
assert(settlers.some(([id])=>id==="bearframe:echo_lost"));
assert(settlers.some(([id])=>id==="bearframe:grid_breach_guard"));
const n=settlers.length;
world.getDifficulty=()=>Difficulty.Peaceful;
for(let idx=0;idx<20;idx++)populateRuin(mock,"collapsed_transit_bunker",{x:idx*47,y:66,z:50});
assert.equal(settlers.length,n);
console.log("Passed resident role retention, variable hostile spawn choice, Peaceful suppression, Echo testimony, distinct-site counting and repeatable local payout.");
