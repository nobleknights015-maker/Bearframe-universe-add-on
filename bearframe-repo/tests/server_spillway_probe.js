// Append to a disposable copy of behavior_pack/scripts/main.js. Use Bedrock
// Dedicated Server and a new Overworld with seed 13221951. Restart to test saves.
import {SPILLWAY_DATUM,SPILLWAY_PANEL,SPILLWAY_SIGNS,SPILLWAY_SIZE,SPILLWAY_FLIGHT} from "./spillway_layout.js";
import {interactRegion,matchRegionDevice} from "./expedition.js";
world.afterEvents.worldLoad.subscribe(()=>system.runTimeout(()=>void(async()=>{
  const dim=world.getDimension("overworld"), mgr=world.tickingAreaManager;
  const check=(yes,message)=>{if(!yes)throw Error(message);};
  const origin={x:1500,y:64,z:1500};
  const end=at(origin,[50,SPILLWAY_SIZE.y-1,36]);
  await mgr.createTickingArea("spillway-fixture",{dimension:dim,from:origin,to:end});
  try{
    if(!world.getDynamicProperty("spillway_test")) {
      for(const [lo,hi] of [[0,9],[10,19]])dim.fillBlocks(new BlockVolume(at(origin,[-1,lo,0]),at(origin,[50,hi,36])),"minecraft:stone");
      dim.fillBlocks(new BlockVolume(at(origin,[-1,20,0]),end),"minecraft:air");
      const marker=dim.getBlock(at(origin,SPILLWAY_DATUM));
      marker.setType(SPILLWAY_MARKER);
      const obstacle=dim.getBlock(at(origin,[35,7,16]));
      obstacle.setType("minecraft:barrel");
      check(!buildSpillway(marker,false)&&obstacle.typeId==="minecraft:barrel","protected barrel overwritten");
      obstacle.setType("minecraft:stone");
      const cave=dim.getBlock(at(origin,[35,3,16]));
      cave.setType("minecraft:air");
      check(!buildSpillway(marker,false),"unsupported floor accepted");
      cave.setType("minecraft:stone");
      check(buildSpillway(marker,false),"sound test terrain rejected");
      check(!buildSpillway(marker,false),"duplicate build");
      runChecks(origin);
      const site=regionAt(dim,at(origin,SPILLWAY_PANEL));
      const box=dim.getBlock(at(origin,[35,5,16]));
      box.setType("minecraft:barrel");
      const bag=box.getComponent("minecraft:inventory").container;
      const proxy={getComponent:()=>({container:bag}),sendMessage:()=>{}};
      bag.setItem(0,new ItemStack("minecraft:redstone",3));
      const cache=dim.getBlock(at(site.pos,site.def.layout.cache));
      check(matchRegionDevice(cache)?.def.id==="spillway_bunker","linked locker");
      interactRegion(proxy,site,"minecraft:barrel",spend);
      check(bag.emptySlotsCount===26,"unpowered locker");
      interactRegion(proxy,site,site.def.panel,spend);
      check(bag.getItem(0)?.amount===1,"repair cost");
      check(site.def.layout.seal.every(p=>dim.getBlock(at(site.pos,p)).isAir),"repair gate");
      interactRegion(proxy,site,"minecraft:barrel",spend);
      interactRegion(proxy,site,"minecraft:barrel",spend);
      check(bag.emptySlotsCount===26-site.def.loot.length,"salvage once");
      greetRegion(site);greetRegion(site);
      check(dim.getEntities({type:"bearframe:grid_walker",location:site.pos,maxDistance:20}).length===1,"primary machine once");
      check(dim.getEntities({type:"bearframe:grid_watcher",location:site.pos,maxDistance:20}).length===1,"watcher once");
      const [npc]=dim.getEntities({type:"bearframe:farfield_surveyor",location:site.pos,maxDistance:25});
      check(npc.getComponent("minecraft:health").effectiveMax===28,"surveyor registration");
      world.setDynamicProperty("spillway_test",true);
      console.warn("[SPILLWAY QA] PASS integrity, two machines, Farfield entity, repair + salvage once");
    } else {
      const site=regionAt(dim,at(origin,SPILLWAY_PANEL));
      runChecks(origin);
      check(site?.anchor.permutation.getState("bearframe:status")===2,"salvage state reload");
      check(dim.getBlock(at(origin,SPILLWAY_DATUM)).permutation.getState("bearframe:excavated"),"construction flag reload");
      const npc=dim.getEntities({type:"bearframe:farfield_surveyor",location:site.pos,maxDistance:30});
      check(npc.length===1,"Farfield entity reload");
      console.warn("[SPILLWAY QA] PASS reload: construction, salvage and persistent Farfield");
    }
  }finally{mgr.removeTickingArea("spillway-fixture");}
  let nativeBuilt=false;
  const found=new Set();
  for(const [ax,az] of [[43,15]]){
    const from={x:ax-45,y:43,z:az-45}, to={x:ax+60,y:145,z:az+45};
    await mgr.createTickingArea("spillway-qa",{dimension:dim,from,to});
    try{
      const test=new BlockVolume({x:ax-45,y:43,z:az-40},{x:ax+12,y:145,z:az+40});
      for(const p of dim.getBlocks(test,{includeTypes:[SPILLWAY_MARKER]},true).getBlockLocationIterator()){
        const id=JSON.stringify(p);
        if(found.has(id))continue;
        found.add(id);
        const b=dim.getBlock(p);
        const result=buildSpillway(b);
        console.warn("[SPILLWAY QA] Native beacon "+id+" facility origin="+JSON.stringify(result));
        if(result){runChecks(result);nativeBuilt=true;}
        else if(b.permutation.getState("bearframe:excavated"))nativeBuilt=true;
      }
    }finally{mgr.removeTickingArea("spillway-qa");}
  }
  check(nativeBuilt,"native terrain fixture did not produce a facility");
  console.warn("[SPILLWAY QA] Completed native search: "+found.size);
  function runChecks(origin){
    const get=(x,y,z)=>dim.getBlock(at(origin,[x,y,z]));
    const site=regionAt(dim,at(origin,SPILLWAY_PANEL));
    check(site?.def.id==="spillway_bunker"&&site.r===0,"terminal rotation");
    for(const {x,y,stair} of SPILLWAY_FLIGHT)for(let z=16;z<=20;z++){
      const block=get(x,y,z);
      check(block.typeId===(stair?"minecraft:stone_brick_stairs":"minecraft:polished_andesite"),"stair block "+JSON.stringify(block.location));
      if(stair)check(block.permutation.getState("weirdo_direction")===1,"stair rotation");
      for(let h=1;h<=(x<=5?3:4);h++)check(block.above(h)?.isAir,"stair clearance "+x+","+y+","+z+","+h);
    }
    check(get(40,4,7).typeId==="minecraft:water"&&get(35,5,8).isAir,"contained water, dry rim");
    for(const {pos,text} of SPILLWAY_SIGNS)check(dim.getBlock(at(origin,pos)).getComponent("minecraft:sign")?.getText()===text,"sign "+text);
    const reached=new Set(), todo=[[1,21,18]];
    for(let i=0;i<todo.length;i++){
      const [x,y,z]=todo[i], id=[x,y,z].join(",");
      if(reached.has(id)||x<0||x>49||z<2||z>34||y<5||y>22)continue;
      const b=get(x,y,z);
      if(!b?.isAir||!b.above()?.isAir||b.below()?.isAir||b.below()?.isLiquid)continue;
      reached.add(id);
      for(const [dx,dz] of [[1,0],[-1,0],[0,1],[0,-1]])for(const dy of [0,1,-1])todo.push([x+dx,y+dy,z+dz]);
    }
    for(const room of [[24,5,18],[36,5,18],[34,5,5],[34,5,25],[45,5,28]])check(reached.has(room.join(",")),"room unreachable "+room);
    console.warn("[SPILLWAY QA] PASS path from grade to all five spaces, 5-wide flights, wet bed, signs");
  }
})().catch(error=>console.warn("[SPILLWAY QA] FAIL "+error+"\n"+error.stack)),60));
