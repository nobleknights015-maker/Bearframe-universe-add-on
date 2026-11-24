// Append temporarily to main.js in a disposable world with seed 13221951.
import {ensureCity,interactRegion,travelCity,travelSurface} from "./expedition.js";
import {reportSurvey} from "./survey_log.js";
import {SURVEY_TYPES,CACHE,CITY_ARRIVAL,CITY_EXIT,CITY_ROLES,SEAL,ORBIT as CITY_DIM} from "./regions.js";

world.afterEvents.worldLoad.subscribe(()=>system.runTimeout(()=>void (async()=>{
 const dim=world.getDimension("overworld"),areas=world.tickingAreaManager;
 const check=(value,why)=>{if(!value)throw Error(why);};
 const locations=[["farfield_camp",-294,72],["grid_hub",582,-312],["echo_ward",38,-648],["intrusion_checkpoint",8,422],["foundry_annex",-186,1224]];
 await ensureCity();
 const city=world.getDimension(CITY_DIM);
 await areas.createTickingArea("bf-city-qa",{dimension:city,from:{x:0,y:99,z:-11},to:{x:43,y:107,z:11}});
 try{
   check(city.getBlock(CITY_ARRIVAL).isAir,"City arrival bay clear");
   check(city.getBlock(CITY_EXIT).typeId==="minecraft:lodestone","City return desk");
   for(const [index,role] of CITY_ROLES.entries()){
     check(city.getEntities({type:role.type,location:role.pos,maxDistance:4})
       .filter(e=>e.getDynamicProperty("bearframe:city_role")===index).length===1,"City staff "+role.name);
   }
   console.warn("[BF 0.2 QA] PASS orbital city, four staffed sectors, named arrival and return");
 }finally{areas.removeTickingArea("bf-city-qa");}
 for(const [id,x,z] of locations){
   const from={x:x-28,y:40,z:z-28},to={x:x+28,y:144,z:z+28};
   await areas.createTickingArea("bf-surface-qa",{dimension:dim,from,to});
   try{
     const markers=dim.getBlocks(new BlockVolume(from,to),{includeTypes:[REGION_ANCHOR]},true);
     const sites=[...markers.getBlockLocationIterator()].map(p=>regionAt(dim,at(p,[0,2,0]))).filter(s=>s?.def.id===id);
     check(sites.length===1,`expected one natural site at ${x},${z}, got ${sites.length}`);
     const site=sites[0],{pos,def,r}=site;
     const count=[...dim.getBlocks(new BlockVolume(from,to),{includeTypes:[APPROACH_MARKER]},true).getBlockLocationIterator()]
        .map(p=>gradeApproach(loaded(dim,p))).filter(Boolean).length;
     greetRegion(site);greetRegion(site);
     check(dim.getEntities({type:def.actor,location:pos,maxDistance:10}).length===1,def.id+" crew");
     const fixture=dim.spawnEntity("minecraft:armor_stand",{x:pos.x-1.5,y:pos.y,z:pos.z+.5});
     const box=dim.getBlock(at(pos,[-2,0,2],r));
     box.setType("minecraft:barrel");
     const bag=box.getComponent("minecraft:inventory").container;
     const proxy={id:fixture.id,get isValid(){return fixture.isValid;},
       get location(){return fixture.location;},get dimension(){return fixture.dimension;},
       getDynamicProperty:k=>fixture.getDynamicProperty(k),
       setDynamicProperty:(k,v)=>fixture.setDynamicProperty(k,v),
       tryTeleport:(p,opts)=>fixture.tryTeleport(p,opts),
       getComponent:()=>({container:bag}),sendMessage:()=>{}};
     if(def.cost){
       const [currency,n]=def.cost;
       bag.setItem(0,new ItemStack(currency,n+1));
       interactRegion(proxy,site,"minecraft:barrel",spend);
       check(bag.emptySlotsCount===26,"locked store");
       interactRegion(proxy,site,def.panel,spend);
       check(bag.getItem(0).amount===1,"paid once");
       check(SEAL.every(p=>dim.getBlock(at(pos,p,r)).isAir),"opened site seal");
       check(dim.getBlock(at(pos,CACHE,r)).typeId==="minecraft:barrel","physical locker");
       interactRegion(proxy,site,"minecraft:barrel",spend);
       interactRegion(proxy,site,"minecraft:barrel",spend);
       for(const [i,[type,qty]] of def.loot.entries()){
         check(bag.getItem(i+1)?.typeId===type&&bag.getItem(i+1)?.amount===qty,"unique award");
       }
       check(bag.emptySlotsCount===26-def.loot.length,"no duplicated awards");
     }else{
       for(const id of ["maintenance_relay",...SURVEY_TYPES.map(d=>d.id)])recordSurvey(proxy,id);
       await travelCity(proxy,site);
       check(proxy.dimension.id===CITY_DIM,"fixture traveled from camp to city");
       reportSurvey(proxy);
       reportSurvey(proxy);
       check(bag.getItem(0)?.typeId==="bearframe:farfield_insignia"&&bag.emptySlotsCount===26,"unique survey award");
       await travelSurface(proxy);
       check(proxy.dimension.id===dim.id,"fixture returned to camp");
       console.warn("[BF 0.2 QA] PASS round trip from actual generated camp");
     }
     fixture.remove();
     console.warn("[BF 0.2 QA] PASS "+def.id+" rotation "+r+" graded approaches "+count);
   }finally{areas.removeTickingArea("bf-surface-qa");}
   await new Promise(resolve=>system.runTimeout(resolve,8));
 }
})().catch(error=>console.warn("[BF 0.2 QA] FAIL "+error+"\n"+error.stack)),87));
