// Append to a disposable copy of behavior_pack/scripts/main.js. Start a fresh
// Bedrock Dedicated Server Overworld with seed 13221951, then restart to check persistence.
import {SURFACE_SITES} from "./surface_layout.js";
import {BlockPermutation} from "@minecraft/server";
import {greetRegion as greetSite,interactRegion} from "./expedition.js";
world.afterEvents.worldLoad.subscribe(()=>system.runTimeout(()=>void(async()=>{
 const dim=world.getDimension("overworld"), mgr=world.tickingAreaManager;
 const check=(yes,message)=>{if(!yes)throw Error(message);};
 const index=SURFACE_SITES.findIndex(site=>site.id==="intrusion_checkpoint");
 const {deck}=SURFACE_SITES[index];
 let nativeBuilt=0;
 for(const [cx,cz] of [[8,422],[-240,2368]]){
  await mgr.createTickingArea("terrain042-native",{dimension:dim,from:{x:cx-57,y:44,z:cz-52},to:{x:cx+58,y:155,z:cz+53}});
  try{
   const top=dim.getTopmostBlock({x:cx,z:cz});
   console.warn("[FRONTIER QA] Area "+cx+","+cz+" top "+top?.typeId+" Y "+top?.y);
   const markers=dim.getBlocks(new BlockVolume({x:cx-18,y:-55,z:cz-18},{x:cx+18,y:300,z:cz+18}),{includeTypes:[SURFACE_DATUM]},true);
   for(const p of markers.getBlockLocationIterator()){
    const marker=dim.getBlock(p);
    if(marker.permutation.getState("bearframe:site")!==index)continue;
    const base=buildSurfaceSite(marker);
    if(base){inspect(base,true);nativeBuilt++;}
    else if(marker.typeId===SURFACE_DATUM&&marker.permutation.getState("bearframe:sited"))nativeBuilt++;
    console.warn("[FRONTIER QA] Native checkpoint datum "+JSON.stringify(p)+", site "+JSON.stringify(base??null));
   }
   if(cx===8){
    const old=dim.getBlock({x:8,y:61,z:422});
    check(old.typeId!=="minecraft:observer","old submerged checkpoint footprint still built");
    console.warn("[FRONTIER QA] PASS old submerged checkpoint skipped");
   }
  }finally{mgr.removeTickingArea("terrain042-native");}
 }
 if(!nativeBuilt)throw Error("native dry checkpoint did not build");

 const origin={x:1500,y:70,z:1500};
 const start=at(origin,[-2,deck-4,-2]), end=at(origin,[22,deck+8,18]);
 await mgr.createTickingArea("terrain042-fixture",{dimension:dim,from:start,to:end});
 try{
  if(!world.getDynamicProperty("surface_042_fixture")){
   dim.fillBlocks(new BlockVolume(start,end),"minecraft:air");
   dim.fillBlocks(new BlockVolume(start,at(origin,[22,deck-1,18])),"minecraft:stone");
   const pos=at(origin,[10,deck,8]);
   const marker=dim.getBlock(pos);
   marker.setPermutation(BlockPermutation.resolve(SURFACE_DATUM,{"bearframe:site":index,"bearframe:sited":false}));
   const coast=dim.getBlock(at(origin,[0,deck,0]));
   coast.setType("minecraft:water");
   check(!buildSurfaceSite(marker,false)&&coast.isLiquid,"flooded footprint accepted or overwritten");
   coast.setType("minecraft:air");
   const drop=dim.getBlock(at(origin,[0,deck-1,0]));
   for(let i=0;i<3;i++)dim.getBlock({...drop.location,y:drop.y-i}).setType("minecraft:air");
   check(!buildSurfaceSite(marker,false),"unsupported edge accepted");
   for(let i=0;i<3;i++)dim.getBlock({...drop.location,y:drop.y-i}).setType("minecraft:stone");
   const barrel=dim.getBlock(at(origin,[3,deck,3]));
   barrel.setType("minecraft:barrel");
   check(!buildSurfaceSite(marker,false)&&barrel.typeId==="minecraft:barrel","existing construction overwritten");
   barrel.setType("minecraft:air");
   check(Boolean(buildSurfaceSite(marker,false)),"valid dry terrain rejected");
   inspect(origin,false);
   const here=regionAt(dim,at(origin,[10,deck+1,8]));
   greetSite(here);greetSite(here);
   for(const type of ["directorate_guard","directorate_officer","hollow_line"]){
    check(dim.getEntities({type:"bearframe:"+type,location:here.pos,maxDistance:12}).length===1,type+" did not spawn once");
   }
   const holder=dim.getBlock(at(origin,[10,deck+1,0]));
   holder.setType("minecraft:barrel");
   const bag=holder.getComponent("minecraft:inventory").container;
   const proxy={getComponent:()=>({container:bag}),sendMessage:()=>{}};
   bag.setItem(0,new ItemStack("minecraft:copper_ingot",4));
   interactRegion(proxy,here,here.def.panel,spend);
   check(bag.getItem(0)?.amount===1&&here.anchor.permutation.getState("bearframe:status")===1,"gate repair spending");
   check(dim.getBlock(at(here.pos,[3,0,0])).isAir&&dim.getBlock(at(here.pos,[3,1,0])).isAir,"gate stayed closed or flooded");
   interactRegion(proxy,here,"minecraft:barrel",spend);
   interactRegion(proxy,here,"minecraft:barrel",spend);
   check(bag.emptySlotsCount===26-here.def.loot.length,"duplicate or missing salvage");
   for(const [i,type] of ["field_researcher","echo_drifter","nullframe_hunter","grid_repair_crawler","grid_protocol_keeper"].entries()){
    const npc=dim.spawnEntity("bearframe:"+type,at(origin,[2+i*3,deck+15,8]));
    check(npc.getComponent("minecraft:health")?.effectiveMax>0,type+" was not registered");
    npc.remove();
   }
   world.setDynamicProperty("surface_042_fixture",true);
   console.warn("[FRONTIER QA] PASS water, unsupported edge, existing inventory, repaired gate, one-time loot and all seven roles");
  }else{
   const here=regionAt(dim,at(origin,[10,deck+1,8]));
   check(here?.anchor.permutation.getState("bearframe:status")===2,"salvage state lost");
   check(dim.getEntities({type:"bearframe:directorate_guard",location:here.pos,maxDistance:30}).length===1,"guard persistence");
   console.warn("[FRONTIER QA] PASS reload after gate repair and salvage");
  }
 }finally{mgr.removeTickingArea("terrain042-fixture");}

 function inspect(base,native){
  const get=(x,y,z)=>dim.getBlock(at(base,[x,y,z]));
  check(regionAt(dim,at(base,[10,deck+1,8]))?.def.id==="intrusion_checkpoint","missing built checkpoint anchor");
  for(let x=0;x<=12;x++)for(let z=7;z<=9;z++){
   check(!get(x,deck,z).isAir&&!get(x,deck,z).isLiquid,"unsupported inspection lane");
   if(x!==10||z!==8)for(let y=deck+1;y<deck+3;y++)check(get(x,y,z).isAir,"obstructed inspection lane");
  }
  for(let x=0;x<=20;x++)for(let z=0;z<=16;z++)for(let y=deck-2;y<=deck+5;y++){
   const b=get(x,y,z);
   check(!b.isLiquid&&!b.isWaterlogged,"water in the built checkpoint");
  }
  console.warn("[FRONTIER QA] PASS "+(native?"native":"fixture")+" dry three-wide inspection lane");
 }
 console.warn("[FRONTIER QA] COMPLETE");
})().catch(error=>console.warn("[FRONTIER QA] FAIL "+error+"\n"+error.stack)),60));
