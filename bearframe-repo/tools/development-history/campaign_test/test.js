import assert from "node:assert/strict";
import {picks} from "@minecraft/server-ui";
import {handlers} from "@minecraft/server";
import {campaignDialogue,campaignSignal,installCampaign} from "./campaign.js";
import {read,write} from "./campaign_state.js";
import {MAIN,SIDES} from "./campaign_data.js";
const roles={Mira:14,Auren:11,Atlas:12,Vera:13,Sentinel:15,Penney:16};
const city={id:"bearframe:city_orbit"};
function player(id){
 const data=new Map(),items=new Array(128),notes=[];
 const bag={size:items.length,items,get emptySlotsCount(){return items.filter(Boolean).length===items.length?0:items.length-items.filter(Boolean).length;},
   getItem:i=>items[i],setItem:(i,v)=>items[i]=v};
 return {id,isValid:true,isSneaking:true,dimension:city,location:{x:0,y:0,z:0},notes,bag,
  getDynamicProperty:k=>data.get(k),setDynamicProperty:(k,v)=>data.set(k,v),sendMessage:s=>notes.push(s),getComponent:()=>({container:bag})};
}
const a=player("A"), b=player("B");
const target={isValid:true,dimension:city,location:a.location};
async function click(lead,...choices){
 a.dimension=city;
 picks.push(...choices);
 assert(campaignDialogue(a,target,roles[lead]));
 await new Promise(r=>setImmediate(r));
 assert.equal(picks.length,0);
}
const coords=(x=0)=>({x,y:70,z:4});
const signal=(type,id,x)=>campaignSignal(a,type,id,coords(x));
await click("Mira",0,0);
assert.equal(read(a).chapter,0);
await click("Mira",0,0);
assert.equal(read(a).chapter,0);
signal("read","maintenance_relay");signal("read","grid_hub");
await click("Mira",0,0);
assert.equal(read(a).chapter,1);
signal("read","echo_ward");signal("echo","drifter");
await click("Mira",0,0);
signal("read","intrusion_checkpoint");signal("read","relay_nine");
await click("Sentinel",0,0);
signal("read","flooded_pump_bunker");signal("read","collapsed_transit_bunker");signal("repair","foundry_annex");
await click("Atlas",0,0);
signal("read","sealed_archive_bunker");signal("read","shelter_bunker");
await click("Vera",0,0);
assert.equal(read(a).chapter,5);
signal("read","spillway_bunker");signal("repair","spillway_bunker");
installCampaign([]);
function port(n){
 a.dimension={id:"minecraft:overworld"};
 handlers.block[1]({block:{typeId:"bearframe:dispatch_console",location:a.location,permutation:{getState:()=>n}},isFirstEvent:true,player:a});
}
port(2);port(1);
assert.equal(read(a).calibration,0);
port(2);port(0);port(1);
assert.equal(read(a).facts["calibrated:spillway"],1);
await click("Auren",0,0,1);
assert.equal(read(a).choice,"local");
assert.equal(read(a).chapter,6);
signal("echo","drifter");signal("repair","grid_hub");
await click("Mira",0,0);
assert.equal(read(a).chapter,MAIN.length);
assert.equal(read(b).chapter,-1);

await click("Penney",1,0,0);
await click("Penney",1,0,0);
assert.equal(read(a).side.sleep,2);
const c0=a.bag.items.filter(Boolean).length;
await click("Penney",1,0,0);
assert.equal(a.bag.items.filter(Boolean).length,c0);

await click("Atlas",2,0);
signal("repair","grid_hub",5);signal("repair","grid_hub",5);
assert.equal(read(a).contracts.power.progress,1);
signal("repair","foundry_annex",12);
await click("Atlas",2,0);
assert.equal(read(a).contracts.power.done,1);
assert.equal(a.bag.items.filter(Boolean).length,c0+3);
await click("Atlas",2,0);
assert.equal(read(a).contracts.power.progress,0);

assert.equal(SIDES.length,6);
console.log("Passed: seven chapters, correct briefing gates, resettable calibration, local ending, isolated saves, side reward once, repeat de-duplication and policy bonus.");
const reset=read(a);
reset.chapter=5;
reset.choice=null;
write(a,reset);
const inventory=a.bag.items.slice();
a.bag.items.fill({typeId:"minecraft:dirt",amount:64});
await click("Auren",0,0,0);
assert.equal(read(a).chapter,5);
assert.equal(read(a).choice,null);
for(let i=0;i<inventory.length;i++)a.bag.setItem(i,inventory[i]);
await click("Auren",0,0,0);
assert.equal(read(a).choice,"publish");
assert.equal(read(a).chapter,6);
console.log("Passed: full inventory preserves progress and permits retry; public route policy resolves.");
