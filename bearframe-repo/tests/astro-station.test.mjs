import test from "node:test";
import assert from "node:assert/strict";
import {ASTRO} from "../behavior_pack/scripts/astro_layout.js";
import {CITY_ROLES} from "../behavior_pack/scripts/regions.js";
import {loadStructure} from "./structure-fixture.mjs";

test("Astro decks connect all staff, department lift and return desk",()=>{
  const parts=ASTRO.parts.map(p=>({...p,template:loadStructure(p.id)}));
  assert.equal(parts.length,44);
  const filled=(x,y,z)=>parts.some(({origin:o,template})=>{
    const cell=template.cell(x-o.x,y-o.y,z-o.z);
    return cell&&cell.name!=="minecraft:air";
  });
  const cell=p=>[Math.floor(p.x),Math.floor(p.z)];
  const occupants=ASTRO.staff.filter(person=>!person.name);
  assert.deepEqual(occupants.map(p=>p.role).sort((a,b)=>a-b),CITY_ROLES.map((_,i)=>i));
  assert.equal(new Set(occupants.map(p=>p.section)).size,6);
  const visitors=ASTRO.staff.filter(person=>person.name);
  assert.equal(new Set(visitors.map(p=>p.role)).size,5);
  assert(visitors.every(p=>p.section==="Main Commons"));
  for(const start of [ASTRO.arrival,ASTRO.lifts[0].target]){
    const y=start.y, queue=[cell(start)], seen=new Set(queue.map(p=>p.join(",")));
    for(const [x,z] of queue){
      for(const [a,b] of [[x-1,z],[x+1,z],[x,z-1],[x,z+1]]){
        const k=[a,b].join(",");
        if(seen.has(k)||filled(a,y,b)||filled(a,y+1,b)||!filled(a,y-1,b))continue;
        seen.add(k);queue.push([a,b]);
      }
    }
    for(const person of ASTRO.staff.filter(person=>person.pos.y===y))
      assert(seen.has(cell(person.pos).join(",")),CITY_ROLES[person.role].name);
    for(const fixture of [ASTRO.exit,...ASTRO.lifts.map(l=>l.pos)].filter(p=>p.y===y)){
      assert(filled(fixture.x,y,fixture.z));
      assert(queue.some(([x,z])=>Math.abs(x-fixture.x)+Math.abs(z-fixture.z)===1));
    }
  }
});
