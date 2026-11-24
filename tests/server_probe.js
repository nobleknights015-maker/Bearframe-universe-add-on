// Append to the disposable server copy of main.js.
world.afterEvents.worldLoad.subscribe(()=>system.runTimeout(()=>void (async()=>{
 const dim=world.getDimension("overworld"), manager=world.tickingAreaManager;
 const from={x:-225,y:45,z:144},to={x:-179,y:145,z:194};
 await manager.createTickingArea("bearframe-relay-qa",{dimension:dim,from,to});
 try {
  const check=(yes,message)=>{if(!yes)throw Error(message);};
  const list=dim.getBlocks(new BlockVolume(from,to),{includeTypes:[ANCHOR]},true);
  const markers=[...list.getBlockLocationIterator()];
  check(markers.length===1,"natural anchor count "+markers.length);
  const site=resolveSite(dim,at(markers[0],[0,2,0]));
  check(site,"resolve native rotated relay");
  const {terminal,rotation}=site;
  console.warn("[BF QA] NATURAL terminal "+JSON.stringify(terminal)+" rotation "+rotation+" phase "+phase(site));
  if(world.getDynamicProperty("bearframe:test:done")){
    check(phase(site)===3,"saved relay phase");
    check(GATE.every(p=>loaded(dim,at(terminal,p,rotation))?.isAir),"saved gate");
    check(POWER_LIGHTS.every(p=>loaded(dim,at(terminal,p,rotation))?.typeId==="minecraft:sea_lantern"),"saved lights");
    console.warn("[BF QA] PASS saved relay, open gate and restored power survived restart");
    return;
  }
  const roads=dim.getBlocks(new BlockVolume(from,to),{includeTypes:[APPROACH_MARKER]},true);
  const count=[...roads.getBlockLocationIterator()].map(p=>gradeApproach(loaded(dim,p))).filter(Boolean).length;
  check(count>=1,"no walkable graded approach on test seed");
  console.warn("[BF QA] PASS supported graded approaches "+count);
  const under=loaded(dim,at(terminal,[0,-3,0]));
  check(under&&!under.isAir&&!under.isLiquid,"buried foundation");
  check(phase(site)===0,"fresh marker state");
  check(GATE.every(p=>loaded(dim,at(terminal,p,rotation))?.typeId==="minecraft:iron_bars"),"gate starts closed");
  activateSite(site); activateSite(site);
  const actors=dim.getEntities({location:terminal,maxDistance:10});
  for(const id of Object.values(ACTOR_TYPES))check(actors.filter(e=>e.typeId===id).length===1,"resident count "+id);
  const crate=loaded(dim,at(terminal,RECOVERY,rotation));
  check(findLinked(crate)?.rotation===rotation,"rotated crate binding");
  const fixtures=[at(terminal,[-4,0,2],rotation),at(terminal,[-3,0,2],rotation)];
  const inventories=fixtures.map(pos=>{
    const block=loaded(dim,pos);block.setType("minecraft:barrel");
    check(!findLinked(block),"ordinary barrel incorrectly bound");
    return block.getComponent("minecraft:inventory").container;
  });
  const simulation=bag=>({getComponent:()=>({container:bag}),sendMessage:()=>{},playSound:()=>{}});
  const [a,b]=inventories.map(simulation);
  inventories[0].setItem(0,new ItemStack("minecraft:copper_ingot",3));
  inventories[1].setItem(0,new ItemStack("minecraft:redstone",2));
  useRelay(a,site,CRATE); check(phase(site)===0,"sealed locker");
  useRelay(a,site,PANEL); check(phase(site)===1&&inventories[0].getItem(0)?.amount===1,"copper debit");
  useRelay(b,site,PANEL); check(phase(site)===1&&inventories[1].getItem(0)?.amount===2,"blocked repair");
  loaded(dim,at(terminal,BULKHEAD,rotation)).setType("minecraft:air");
  useRelay(b,site,PANEL); check(phase(site)===2&&inventories[1].getItem(0)?.amount===1,"redstone debit");
  check(GATE.every(p=>loaded(dim,at(terminal,p,rotation))?.isAir),"opened both gate cells");
  check(POWER_LIGHTS.every(p=>loaded(dim,at(terminal,p,rotation))?.typeId==="minecraft:sea_lantern"),"visible change");
  useRelay(a,site,CRATE); useRelay(b,site,CRATE);
  check(phase(site)===3&&inventories[0].getItem(1)?.typeId===PART&&!inventories[1].getItem(1),"single shared schematic");
  world.setDynamicProperty("bearframe:test:done",true);
  console.warn("[BF QA] PASS native structure, three unique residents, preserved normal barrel, two inventories, physical repair, locked storage and unique schematic");
 } finally {manager.removeTickingArea("bearframe-relay-qa");}
})().catch(e=>console.warn("[BF QA] FAIL "+e+"\n"+e.stack)),85));
