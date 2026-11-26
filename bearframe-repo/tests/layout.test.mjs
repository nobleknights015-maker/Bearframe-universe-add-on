import assert from "node:assert/strict";
import test from "node:test";
import {ACTORS,BREAKER,BULKHEAD,DIRECTION,GATE,POWER_LIGHTS,RECOVERY} from "../behavior_pack/scripts/layout.js";
import {SURFACE_SITES} from "../behavior_pack/scripts/surface_layout.js";
import {loadStructure,terminalLookup,walkableCells} from "./structure-fixture.mjs";

const site=SURFACE_SITES.find(s=>s.id==="maintenance_relay");
const template=loadStructure(site.id+"_site");
const {position,at}=terminalLookup(template,"bearframe:relay_anchor");
const absolute=([x,y,z])=>[position[0]+x,position[1]+y,position[2]+z];

test("relay template fits its surveyed footprint and preserves deep terrain",()=>{
  assert.deepEqual(template.size,[site.size.x,site.size.y,site.size.z]);
  for(let x=0;x<site.size.x;x++)for(let z=0;z<site.size.z;z++)
    for(let y=0;y<site.deck-2;y++)assert.equal(template.cell(x,y,z),undefined);
});

test("relay hardware and actor slots match the runtime layout",()=>{
  assert.equal(at([0,0,0])?.name,"minecraft:lectern");
  assert.equal(at(DIRECTION)?.name,"minecraft:lodestone");
  assert.equal(at(BREAKER)?.name,"minecraft:cut_copper");
  assert.equal(at(BULKHEAD)?.name,"minecraft:cobblestone");
  for(const p of POWER_LIGHTS)assert.equal(at(p)?.name,"minecraft:coal_block");
  for(const p of GATE)assert.equal(at(p)?.name,"minecraft:iron_bars");
  assert.equal(at(RECOVERY)?.name,"minecraft:barrel");
  for(const [x,y,z] of Object.values(ACTORS)){
    assert.equal(at([x,y,z])?.name,"minecraft:air");
    assert.equal(at([x,y+1,z])?.name,"minecraft:air");
    assert(at([x,y-1,z])?.name && at([x,y-1,z]).name!=="minecraft:air");
  }
});

test("relay approach reaches the terminal and repairing the gate grants locker access",()=>{
  const starts=template.find("bearframe:approach_anchor").map(([x,y,z])=>[x,y+3,z]);
  assert(starts.length>0);
  const before=walkableCells(template,starts);
  const terminal=absolute([-1,0,0]).join(",");
  const locker=absolute([6,0,0]).join(",");
  assert(before.has(terminal),"Lectern unreachable");
  assert(!before.has(locker),"Locker accessible before repair");
  assert(walkableCells(template,starts,GATE.map(absolute)).has(locker),"Locker unreachable after repair");
});

test("compact discovery relay has a reachable terminal and working circuit",()=>{
  const compact=loadStructure("maintenance_relay_field");
  const {position,at}=terminalLookup(compact,"bearframe:relay_anchor");
  assert.deepEqual(compact.size,[21,19,17]);
  assert.equal(at([0,0,0])?.name,"minecraft:lectern");
  assert.equal(at(BREAKER)?.name,"minecraft:cut_copper");
  assert.equal(at(BULKHEAD)?.name,"minecraft:cobblestone");
  for(const p of POWER_LIGHTS)assert.equal(at(p)?.name,"minecraft:coal_block");
  assert.equal(at(RECOVERY)?.name,"minecraft:barrel");
  for(const p of GATE)assert.equal(at(p)?.name,"minecraft:iron_bars");
  const [x,y,z]=position;
  const starts=compact.find("bearframe:approach_anchor").map(([x,y,z])=>[x,y+3,z]);
  assert(walkableCells(compact,starts).has([x-1,y,z].join(",")));
});
