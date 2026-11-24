// Append temporarily to main.js for the seed 13221951 premade release world.
world.afterEvents.worldLoad.subscribe(()=>system.runTimeout(()=>void(async()=>{
 const dim=world.getDimension("overworld"),tm=world.tickingAreaManager;
 const from={x:-722,y:38,z:-257},to={x:-652,y:130,z:-187};
 await tm.createTickingArea("bearframe-ruins-arrival",{dimension:dim,from,to});
 try{
  const locations=dim.getBlocks(new BlockVolume(from,to),{includeTypes:[REGION_ANCHOR]},true);
  const site=[...locations.getBlockLocationIterator()].map(p=>regionAt(dim,at(p,[0,2,0])))
   .find(s=>s?.def.id==="rainline_town");
  if(!site)throw Error("Rainline Works did not generate.");
  const spawn=at(site.pos,[-3,0,0],site.r), feet=dim.getBlock(spawn);
  if(!feet?.isAir||!feet.above()?.isAir||feet.below()?.isAir)throw Error("Rainline spawn is obstructed.");
  for(const p of dim.getBlocks(new BlockVolume(from,to),{includeTypes:[APPROACH_MARKER]},true).getBlockLocationIterator())
    gradeApproach(loaded(dim,p));
  greetRegion(site);
  world.setDefaultSpawnLocation(spawn);
  world.gameRules.spawnRadius=0;
  console.warn("[BF Ruins Arrival] READY "+JSON.stringify({spawn,site:site.pos}));
 }finally{tm.removeTickingArea("bearframe-ruins-arrival");}
})().catch(error=>console.warn("[BF Ruins Arrival] FAIL "+error)),80));
