import test from "node:test";
import assert from "node:assert/strict";
import {withTemporaryArea} from "../behavior_pack/scripts/temporary_area.js";
function fixture(){
 const loaded=new Set(),removed=[];let resolve,timeout,cleared=0;
 const areas={createTickingArea:name=>new Promise(r=>{resolve=()=>{loaded.add(name);r();};}),hasTickingArea:name=>loaded.has(name),removeTickingArea:name=>{loaded.delete(name);removed.push(name);}};
 return {loaded,removed,resolve:()=>resolve(),timeout:()=>timeout(),cleared:()=>cleared,args:{areas,dimension:{},from:{},to:{},name:"test-1",scheduleTimeout:fn=>{timeout=fn;return 1;},cancelTimeout:()=>cleared++}};
}
test("late chunk ticket is removed after timeout, without invoking travel",async()=>{
 const f=fixture();let ran=false;
 const p=withTemporaryArea({...f.args,task:()=>{ran=true;}});
 f.timeout();await assert.rejects(p,/timed out/);
 f.loaded.add("test-2");f.resolve();await Promise.resolve();await Promise.resolve();
 assert.deepEqual([...f.loaded],["test-2"]);assert.deepEqual(f.removed,["test-1"]);assert.equal(ran,false);assert.equal(f.cleared(),1);
});
test("successful and failed tasks release their tickets",async()=>{
 for(const fail of [false,true]){
  const f=fixture();const p=withTemporaryArea({...f.args,task:()=>{assert(f.loaded.has("test-1"));if(fail)throw Error("task failed");return 42;}});
  f.resolve();if(fail)await assert.rejects(p,/task failed/);else assert.equal(await p,42);
  assert.equal(f.loaded.size,0);assert.deepEqual(f.removed,["test-1"]);assert.equal(f.cleared(),1);
 }
});
