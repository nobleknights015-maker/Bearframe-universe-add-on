// Append to the disposable test copy of main.js. Use Overworld seed 13221951.
import {BUNKER_TERMINAL,TOWN_TERMINAL} from "./ruins.js";
import {interactRegion,matchRegionDevice} from "./expedition.js";

world.afterEvents.worldLoad.subscribe(()=>system.runTimeout(()=>void(async()=>{
 const dim=world.getDimension("overworld"), mgr=world.tickingAreaManager;
 const fixtures=[["shelter_bunker",242,-693,true],
  ["rainline_town",-687,-222,false],["saltline_town",1727,526,false]];
 const check=(yes,message)=>{if(!yes)throw Error(message);};
 for(const [id,x,z,bunker] of fixtures){
  const from={x:x-35,y:31,z:z-35},to={x:x+35,y:160,z:z+35};
  await mgr.createTickingArea("bearframe-ruins-qa",{dimension:dim,from,to});
  try{
   const markers=dim.getBlocks(new BlockVolume(from,to),{includeTypes:[REGION_ANCHOR]},true);
   const sites=[...markers.getBlockLocationIterator()].map(p=>regionAt(dim,at(p,[0,2,0]))).filter(s=>s?.def.id===id);
   check(sites.length===1,id+" generated marker count "+sites.length);
   const site=sites[0],{pos,r,def}=site;
   prepareBunker(site);
   await new Promise(resolve=>system.runTimeout(resolve,12));
   const center=bunker?BUNKER_TERMINAL:TOWN_TERMINAL;
   const structure=(x,y,z)=>at(pos,[x-center[0],y-center[1],z-center[2]],r);
   const queue=[bunker?[0,21,11]:[0,14,15]],seen=new Set(),walk=new Set();
   for(let i=0;i<queue.length;i++){
    const [x,y,z]=queue[i],key=[x,y,z].join(",");
    if(seen.has(key))continue;
    seen.add(key);
    if(x<0||x>=(bunker?36:37)||z<0||z>=(bunker?23:31)||y<3||y>24)continue;
    const feet=dim.getBlock(structure(x,y,z));
    const floor=feet?.below();
    const water=b=>b?.typeId==="minecraft:water"||b?.typeId==="minecraft:flowing_water";
    const passable=b=>b?.isAir||def.flooded&&water(b);
    if(!passable(feet)||!passable(feet.above())||!floor||
       (floor.isAir||floor.isLiquid)&&!(def.flooded&&water(feet)))continue;
    walk.add(key);
    for(const [dx,dz] of [[1,0],[-1,0],[0,1],[0,-1]])for(const dy of [0,-1,1])queue.push([x+dx,y+dy,z+dz]);
   }
   check([[1,0],[-1,0],[0,1],[0,-1]].some(([x,z])=>
     walk.has([center[0]+x,center[1],center[2]+z].join(","))),id+" surface entrance to terminal obstructed");
   if(def.flooded){
    check(dim.getBlock(structure(23,8,17)).typeId==="minecraft:water","flooded cistern");
    check(dim.getBlock(structure(4,22,11)).isAir&&dim.getBlock(structure(20,10,11)).isAir,"air pockets at both ends");
   }
   if(bunker){
    const grade=dim.getTopmostBlock(structure(24,20,17));
    check(grade.y>=pos.y+5,id+" lower wing lacks terrain cover");
   }
   const budget=dim.getBlock(at(pos,[-2,0,-2],r));
   budget.setType("minecraft:barrel");
   const bag=budget.getComponent("minecraft:inventory").container;
   const proxy={getComponent:()=>({container:bag}),sendMessage:()=>{}};
   const [currency,count]=def.cost;
   bag.setItem(0,new ItemStack(currency,count+1));
   const cache=dim.getBlock(at(pos,def.layout.cache,r));
   check(matchRegionDevice(cache)?.def.id===id,"unique rotated locker");
   interactRegion(proxy,site,"minecraft:barrel",spend);
   check(bag.emptySlotsCount===26,"closed locker issued items");
   interactRegion(proxy,site,def.panel,spend);
   check(bag.getItem(0)?.amount===1,id+" terminal repair charge");
   check(def.layout.seal.every(p=>dim.getBlock(at(pos,p,r)).isAir),id+" gate failed");
   interactRegion(proxy,site,"minecraft:barrel",spend);
   interactRegion(proxy,site,"minecraft:barrel",spend);
   check(bag.emptySlotsCount===26-def.loot.length,id+" duplicate or missing stores");
   greetRegion(site);greetRegion(site);
   check(dim.getEntities({type:def.actor,location:pos,maxDistance:9}).length===1,id+" resident");
   const ramps=dim.getBlocks(new BlockVolume(from,to),{includeTypes:[APPROACH_MARKER]},true);
   const graded=[...ramps.getBlockLocationIterator()].filter(p=>dist(p,pos)<22**2)
       .map(p=>gradeApproach(loaded(dim,p))).filter(Boolean).length;
   console.warn("[BF 0.3 QA] PASS "+id+" at "+JSON.stringify(pos)+" rotation "+r+" graded "+graded);
  }finally{mgr.removeTickingArea("bearframe-ruins-qa");}
  await new Promise(resolve=>system.runTimeout(resolve,7));
 }
})().catch(error=>console.warn("[BF 0.3 QA] FAIL "+error+"\n"+error.stack)),85));
