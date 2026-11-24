import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import test from "node:test";
import nbt from "prismarine-nbt";
import {ACTORS,BREAKER,DECK,DIRECTION,GATE,RECOVERY,SIZE,at} from "../behavior_pack/scripts/layout.js";
const root=new URL("../behavior_pack/",import.meta.url);
const origin={x:10,y:DECK+1,z:8};
const template=nbt.simplify(nbt.parseUncompressed(readFileSync(new URL("structures/bearframe/maintenance_relay.mcstructure",root)),"little"));
const data=template.structure.block_indices[0], palette=template.structure.palette.default.block_palette;
function cell(x,y,z){return palette[data[(x*SIZE.y+y)*SIZE.z+z]]?.name;}
function named(p){const loc=at(origin,p);return cell(loc.x,loc.y,loc.z);}
test("all printed deck positions have continuous foundation",()=>{
  assert.deepEqual(template.size,[SIZE.x,SIZE.y,SIZE.z]);
  for(let x=0;x<SIZE.x;x++)for(let z=0;z<SIZE.z;z++){
    assert.notEqual(cell(x,DECK,z),"minecraft:air");
    for(let y=0;y<DECK;y++)assert(cell(x,y,z),`missing structure at ${x}/${y}/${z}`);
  }
});
test("mechanics resolve authored terminal, marker, breaker, gate, locker, and three standing slots",()=>{
  assert.equal(named([0,0,0]),"minecraft:lectern");
  assert.equal(named([0,-2,0]),"bearframe:relay_anchor");
  assert.equal(named(DIRECTION),"minecraft:lodestone");
  assert.equal(named(BREAKER),"minecraft:cut_copper");
  assert(GATE.every(p=>named(p)==="minecraft:iron_bars"));
  assert.equal(named(RECOVERY),"minecraft:barrel");
  for(const [x,y,z] of Object.values(ACTORS)){
    assert.equal(named([x,y,z]),"minecraft:air");
    assert.equal(named([x,y+1,z]),"minecraft:air");
  }
});
test("both exits and the west path reach the terminal; east locker stays behind the locked partition",()=>{
  const good=(x,z,open)=>{
    const state=(y)=>open&&x===14&&z===8?"minecraft:air":cell(x,y,z);
    return state(DECK+1)==="minecraft:air"&&state(DECK+2)==="minecraft:air";
  };
  function visited(open){
    const queue=[[0,8]],seen=new Set();
    while(queue.length){
      const [x,z]=queue.pop(), key=`${x},${z}`;
      if(x<0||x>=SIZE.x||z<0||z>=SIZE.z||seen.has(key)||!good(x,z,open))continue;
      seen.add(key);
      queue.push([x+1,z],[x-1,z],[x,z+1],[x,z-1]);
    }
    return seen;
  }
  const before=visited(false);
  assert(before.has("11,8"));
  assert(before.has("5,0")&&before.has("5,16"));
  assert(!before.has("16,8"));
  assert(visited(true).has("16,8"));
});
