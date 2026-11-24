// Temporary build helper for a fresh copy of seed 13221951. Append to main.js.
world.afterEvents.worldLoad.subscribe(()=>system.runTimeout(()=>void(async()=>{
  const dim=world.getDimension("overworld"),mgr=world.tickingAreaManager;
  const from={x:-322,y:40,z:44},to={x:-266,y:144,z:100};
  await mgr.createTickingArea("bf-arrival-world",{dimension:dim,from,to});
  try{
    const candidates=dim.getBlocks(new BlockVolume(from,to),{includeTypes:[REGION_ANCHOR]},true);
    for(const marker of candidates.getBlockLocationIterator()){
      const site=regionAt(dim,at(marker,[0,2,0]));
      if(site?.def.id!=="farfield_camp")continue;
      const spawn=at(site.pos,[-2,0,0],site.r);
      if(!dim.getBlock(spawn)?.isAir||!dim.getBlock({...spawn,y:spawn.y+1})?.isAir)throw Error("Camp spawn blocked");
      for(const p of dim.getBlocks(new BlockVolume(from,to),{includeTypes:[APPROACH_MARKER]},true).getBlockLocationIterator())
        gradeApproach(loaded(dim,p));
      greetRegion(site);
      world.setDefaultSpawnLocation(spawn);
      world.gameRules.spawnRadius=0;
      console.warn("[BF Arrival] READY "+JSON.stringify({spawn,camp:site.pos}));
      return;
    }
    throw Error("No native camp for this seed.");
  } finally {mgr.removeTickingArea("bf-arrival-world");}
})().catch(error=>console.warn("[BF Arrival] FAIL "+error)),80));
