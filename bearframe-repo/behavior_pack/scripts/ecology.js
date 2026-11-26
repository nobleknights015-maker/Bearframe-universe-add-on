import {archiveChart} from "./route_charts.js";
const HABITATS={
  "sealed_archive_bunker": {
    "pool": [
      "ward_resident",
      "grid_protocol_keeper"
    ],
    "spots": [
      [
        20,
        4,
        23
      ],
      [
        22,
        4,
        15
      ],
      [
        22,
        4,
        30
      ]
    ]
  },
  "flooded_pump_bunker": {
    "pool": [
      "grid_repair_crawler",
      "grid_breach_guard"
    ],
    "spots": [
      [
        21,
        4,
        23
      ],
      [
        23,
        4,
        15
      ],
      [
        28,
        4,
        20
      ]
    ]
  },
  "collapsed_transit_bunker": {
    "pool": [
      "echo_lost",
      "grid_breach_guard"
    ],
    "spots": [
      [
        21,
        4,
        23
      ],
      [
        23,
        4,
        14
      ],
      [
        28,
        4,
        21
      ]
    ]
  },
  "rootbound_service_bunker": {
    "pool": [
      "echo_route_trader",
      "grid_protocol_keeper",
      "echo_lost"
    ],
    "spots": [
      [
        21,
        4,
        23
      ],
      [
        23,
        4,
        15
      ],
      [
        28,
        4,
        20
      ]
    ]
  },
  "overgrown_colony": {
    "pool": [
      "ward_resident",
      "echo_route_trader",
      "echo_lost"
    ],
    "spots": [
      [
        29,
        4,
        30
      ],
      [
        35,
        4,
        26
      ],
      [
        29,
        4,
        20
      ]
    ]
  },
  "collapsed_rail_settlement": {
    "pool": [
      "echo_lost",
      "grid_wayfarer"
    ],
    "spots": [
      [
        30,
        4,
        31
      ],
      [
        32,
        4,
        23
      ],
      [
        37,
        4,
        28
      ]
    ]
  },
  "lost_waystation": {
    "pool": [
      "echo_route_trader",
      "ward_resident"
    ],
    "spots": [
      [
        24,
        4,
        16
      ],
      [
        24,
        4,
        26
      ],
      [
        29,
        4,
        21
      ]
    ]
  },
  "frontier_colony": {
    "pool": [
      "ward_resident",
      "echo_route_trader"
    ],
    "spots": [
      [
        29,
        4,
        30
      ],
      [
        30,
        4,
        21
      ],
      [
        35,
        4,
        26
      ]
    ]
  },
  "coalition_city": {
    "pool": [
      "ward_resident",
      "echo_route_trader",
      "grid_repair_crawler"
    ],
    "spots": [
      [
        32,
        4,
        23
      ],
      [
        32,
        4,
        33
      ],
      [
        37,
        4,
        28
      ]
    ]
  },
  "colony_waystation": {
    "pool": [
      "echo_route_trader",
      "grid_repair_crawler"
    ],
    "spots": [
      [
        22,
        4,
        24
      ],
      [
        24,
        4,
        16
      ],
      [
        29,
        4,
        21
      ]
    ]
  },
  "frontier_ruin": {
    "pool": [
      "echo_lost",
      "echo_route_trader"
    ],
    "spots": [
      [
        24,
        4,
        25
      ],
      [
        28,
        4,
        20
      ],
      [
        18,
        4,
        21
      ]
    ]
  },
  "rainline_town": {
    "pool": [
      "ward_resident",
      "echo_route_trader",
      "grid_repair_crawler"
    ],
    "spots": [
      [
        31,
        14,
        27
      ],
      [
        33,
        14,
        20
      ],
      [
        33,
        14,
        34
      ]
    ]
  },
  "saltline_town": {
    "pool": [
      "echo_route_trader",
      "echo_lost"
    ],
    "spots": [
      [
        31,
        14,
        27
      ],
      [
        33,
        14,
        20
      ],
      [
        33,
        14,
        34
      ]
    ]
  },
  "echo_ward": {
    "pool": [
      "ward_resident",
      "echo_route_trader"
    ],
    "spots": [
      [
        20,
        14,
        18
      ],
      [
        22,
        14,
        11
      ],
      [
        22,
        14,
        25
      ]
    ]
  },
  "grid_hub": {
    "pool": [
      "grid_wayfarer",
      "grid_protocol_keeper"
    ],
    "spots": [
      [
        21,
        14,
        17
      ],
      [
        22,
        14,
        25
      ],
      [
        13,
        14,
        18
      ]
    ]
  },
  "foundry_annex": {
    "pool": [
      "grid_wayfarer",
      "grid_repair_crawler"
    ],
    "spots": [
      [
        21,
        14,
        17
      ],
      [
        22,
        14,
        25
      ],
      [
        22,
        14,
        9
      ]
    ]
  },
  "verdantis_station": {
    "pool": [
      "ward_resident",
      "echo_route_trader"
    ],
    "spots": [
      [
        23,
        4,
        24
      ],
      [
        25,
        4,
        16
      ],
      [
        30,
        4,
        21
      ]
    ]
  },
  "relay_nine": {
    "pool": [
      "grid_wayfarer",
      "grid_protocol_keeper"
    ],
    "spots": [
      [
        20,
        4,
        22
      ],
      [
        22,
        4,
        14
      ],
      [
        27,
        4,
        19
      ]
    ]
  }
};
import {Difficulty,ItemStack,system,world} from "@minecraft/server";
import {ActionFormData} from "@minecraft/server-ui";
import {noteActivity} from "./activity_log.js";
import {applySignal,read as readCampaign,write as writeCampaign} from "./campaign_state.js";
import {LOCAL_JOBS,localStanding,localEligible,localAccept,localSignal,localAdvance,discountedDeals} from "./local_rpg.js";
const OVERWORLD="minecraft:overworld";
const SAVE="bearframe:field_requests";
const stationed=new Set(["echo_drifter","grid_watcher","echo_route_trader","grid_wayfarer","echo_lost","grid_breach_guard","grid_repair_crawler"]);
const dangerous=new Set(["echo_lost","grid_breach_guard"]);
const heavy=new Set(["grid_wayfarer","grid_breach_guard"]);
const activeForms=new Set();

export function retainResident(entity){
  if(stationed.has(entity.typeId.split(":")[1]))entity.triggerEvent("bearframe:settle");
}
function hash(id,x,y,z){
  let n=2166136261;
  for(const c of [id,x,y,z].join(":")) n=Math.imul(n^c.charCodeAt(0),16777619);
  return n>>>0;
}
function openFeet(dim,p,name){
  if(!dim.isChunkLoaded(p))return false;
  const b=dim.getBlock(p);
  if(!b?.isAir||!b.above()?.isAir||!b.below()||b.below().isAir||b.below().isLiquid)return false;
  if(!heavy.has(name))return true;
  for(const [x,z] of [[0,0],[1,0],[-1,0],[0,1],[0,-1]]){
    const p0={x:p.x+x,y:p.y,z:p.z+z};
    if(!dim.isChunkLoaded(p0))return false;
    const b0=dim.getBlock(p0);
    if(!b0?.isAir||!b0.above()?.isAir||!b0.above(2)?.isAir||!b0.below()||b0.below().isAir||b0.below().isLiquid)return false;
  }
  return true;
}
function spawnResident(dim,p,name,site){
  if(dangerous.has(name)&&world.getDifficulty()===Difficulty.Peaceful)return false;
  if(!openFeet(dim,p,name))return false;
  const entity=dim.spawnEntity("bearframe:"+name,{x:p.x+.5,y:p.y,z:p.z+.5});
  retainResident(entity);
  entity.setDynamicProperty("bearframe:region_role",site);
  return true;
}
export function populateRuin(dim,key,base){
  const plan=HABITATS[key];
  if(!plan)return;
  const n=hash(key,base.x,base.y,base.z);
  const count=n%5===0?0:n%4===0?2:1;
  for(let i=0;i<Math.min(count,plan.spots.length);i++){
    const name=plan.pool[(n+i)%plan.pool.length];
    const [x,y,z]=plan.spots[(n+i)%plan.spots.length];
    try{spawnResident(dim,{x:base.x+x,y:base.y+y,z:base.z+z},name,key);}
    catch(error){console.warn("[Bearframe habitat] "+error);}
  }
}
export function populateBuriedSite(site,at){
  const {def,dim,pos,r}=site;
  if(!def.bunker)return;
  const key="bearframe:buried_population:"+[def.id,pos.x,pos.y,pos.z].join(":");
  if(world.getDynamicProperty(key))return;
  const n=hash(def.id,pos.x,pos.y,pos.z);
  const pool=def.id==="spillway_bunker"?["grid_protocol_keeper","grid_repair_crawler","grid_breach_guard"]:
    ["ward_resident","echo_route_trader","echo_lost"];
  if(n%6===0){world.setDynamicProperty(key,true);return;}
  const intent=pool[n%pool.length];
  const name=dangerous.has(intent)&&world.getDifficulty()===Difficulty.Peaceful?pool[0]:intent;
  const offsets=def.id==="spillway_bunker"?[[17,0,0],[14,0,0],[-2,0,-8],[4,0,7]]:[[14,0,0],[11,0,2],[-3,0,4],[-4,0,-3]];
  let loaded=false;
  for(const offset of offsets){
    const p=at(pos,offset,r);
    if(!dim.isChunkLoaded(p))continue;
    loaded=true;
    try{
      if(spawnResident(dim,p,name,def.id)){world.setDynamicProperty(key,true);return;}
    }catch(error){console.warn("[Bearframe bunker population] "+error);return;}
  }
  // Allow a later visit to retry an unloaded wing. A fully loaded but
  // obstructed site can be left vacant without repeatedly sampling it.
  if(loaded&&offsets.every(offset=>dim.isChunkLoaded(at(pos,offset,r))))world.setDynamicProperty(key,true);
}

const catalogs={
  echo_route_trader:{
    name:"Echo Route Trader",intro:"I keep supplies moving between the sites that still have someone to answer the door.",
    quest:"Notes for the Next Traveler",task:"Inspect two distinct ruin archives or terminals after taking this route.",event:"read",count:2,pay:[["minecraft:emerald",2],["minecraft:torch",8]],
    deals:[["minecraft:copper_ingot",3,"minecraft:bread",4],["minecraft:emerald",2,"minecraft:compass",1],["minecraft:paper",5,"minecraft:torch",8]],
  },
  ward_resident:{
    name:"Echo Resident",intro:"The rooms with a lamp are the ones we still use. Leave the other doors as you found them.",
    quest:"Neighbors' Signal",task:"Read an Echo Ward, a Signal Shelter, an Overgrown Colony, or a Lost Waystation record after accepting.",event:"read",include:["echo_ward","shelter_bunker","overgrown_colony","lost_waystation"],count:1,pay:[["minecraft:bread",4],["minecraft:emerald",2]],once:true,
    deals:[["minecraft:wheat",4,"minecraft:bread",2],["minecraft:coal",2,"minecraft:torch",8]],
  },
  grid_protocol_keeper:{
    name:"Grid Protocol Keeper",intro:"Local infrastructure is available. Record active circuits to update service routing.",
    quest:"Service Loop",task:"Inspect two distinct functioning terminals after accepting. Existing repairs count.",event:"repair",count:2,pay:[["minecraft:redstone",5],["bearframe:salvaged_alloy",1]],
    deals:[["minecraft:redstone",4,"minecraft:copper_ingot",3]],
  },
  grid_wayfarer:{
    name:"Legacy Route Guardian",intro:"Route clearance unconfirmed. My current directive permits passage and cooperative maintenance.",
    quest:"Clear Where You Can",task:"Defeat two Lost Echoes or hostile Grid Breach Guardians after accepting.",event:"hazard",count:2,pay:[["minecraft:iron_ingot",4],["bearframe:legacy_cell",1]],
    deals:[["bearframe:salvaged_alloy",2,"minecraft:iron_ingot",3]],
  },
  grid_guardian:{
    name:"Legacy Sector Guardian",intro:"Local defense idle. Non-hostile visitors may request a service assignment.",
    quest:"Clear Where You Can",task:"Defeat two Lost Echoes or hostile Grid Breach Guardians after accepting.",event:"hazard",count:2,pay:[["minecraft:iron_ingot",4],["bearframe:legacy_cell",1]],
    deals:[["bearframe:salvaged_alloy",2,"minecraft:iron_ingot",3]],
  },
  grid_repair_crawler:{
    name:"Grid Repair Crawler",intro:"Two working service stations requested. Substitute stock accepted.",
    quest:"Crawler Service Run",task:"Verify power at one repaired site after accepting.",event:"repair",count:1,pay:[["minecraft:copper_ingot",4],["minecraft:iron_nugget",6]],
    deals:[["minecraft:iron_nugget",4,"minecraft:rail",6]],
  },
};
const pretty=id=>id.split(":").at(-1).replaceAll("_"," ");
const say=(p,text)=>p.sendMessage("§6[Local Routes]§r "+text);
function read(player){
  const s=player.getDynamicProperty(SAVE);
  return typeof s==="string"?JSON.parse(s):{};
}
const write=(player,state)=>player.setDynamicProperty(SAVE,JSON.stringify(state));
function keyFor(type){return type==="grid_guardian"?"grid_wayfarer":type;}
export function fieldProgress(player,event,id,place){
  const state=read(player);
  let touched=false;
  for(const [key,r] of Object.entries(state)){
    const job=catalogs[key];
    if(!job||!r.active||r.progress>=job.count||job.event!==event)continue;
    if(job.include&&!job.include.includes(id))continue;
    const item=place?[id,place.x,place.y,place.z].join(":"):id;
    if(event!=="hazard"&&r.seen.includes(item))continue;
    if(event!=="hazard")r.seen.push(item);
    r.progress++;
    touched=true;
    say(player,job.quest+" · "+r.progress+"/"+job.count);
  }
  const extra=localSignal(state,event,id,place);
  for(const text of extra)say(player,text);
  if(touched||extra.length)write(player,state);
}

function exchange(player,payment,reward,commit){
  const container=player.getComponent("minecraft:inventory")?.container;
  if(!container)return false;
  const vacant=[];
  const changes=[];
  let remain=payment?.[1]??0;
  for(let i=0;i<container.size;i++){
    const item=container.getItem(i);
    if(!item){vacant.push(i);continue;}
    if(remain>0&&item.typeId===payment[0]){
      const take=Math.min(remain,item.amount);
      changes.push([i,item,item.amount-take]);
      if(take===item.amount)vacant.push(i);
      remain-=take;
    }
  }
  if(remain>0){say(player,"Bring "+payment[1]+" "+pretty(payment[0])+".");return false;}
  if(vacant.length<reward.length){say(player,"Make room for the supplies.");return false;}
  let given=0;
  try{
    for(const [i,old,left] of changes){
      if(!left)container.setItem(i,undefined);
      else{const next=old.clone();next.amount=left;container.setItem(i,next);}
    }
    for(const [item,n] of reward){container.setItem(vacant[given],new ItemStack(item,n));given++;}
    if(commit)commit();
  }catch(error){
    while(given>0)container.setItem(vacant[--given],undefined);
    for(const [i,old] of changes)container.setItem(i,old);
    throw error;
  }
  return true;
}
export function fieldInteraction(player,target){
  if(!target?.isValid||player.dimension.id!==OVERWORLD||target.dimension.id!==OVERWORLD)return false;
  const type=target.typeId.split(":")[1];
  if(!catalogs[type])return false;
  const bag=player.getComponent("minecraft:inventory")?.container;
  const held=bag?.getItem(player.selectedSlotIndex);
  if(held?.typeId==="bearframe:field_scanner"||held?.typeId==="bearframe:repair_wrench")return false;
  return type==="echo_route_trader"||type==="grid_wayfarer"||player.isSneaking;
}
function nearby(player,target){
  if(!player.isValid||!target.isValid||player.dimension.id!==OVERWORLD||target.dimension.id!==OVERWORLD)return false;
  const a=player.location,b=target.location;
  return (a.x-b.x)**2+(a.y-b.y)**2+(a.z-b.z)**2<81;
}
async function dialog(player,title,body,options){
  const f=new ActionFormData().title(title).body(body);
  for(const option of options)f.button(option);
  const result=await f.show(player);
  return result.canceled?undefined:result.selection;
}
async function localStory(player,target,key,entry){
 const state=read(player),jobs=LOCAL_JOBS[key]??[];
 const options=jobs.filter(q=>localEligible(q,state)||state[q.id]?.done);
 const n=await dialog(player,entry.name+" · Local stories","These requests come from the people and machines who still use the routes.",[...options.map(q=>q.title+(state[q.id]?.done?" · Closed":state[q.id]?.active?" · Active":"")),"Close"]);
 if(!nearby(player,target))return;
 const q=options[n];if(!q)return;
 const r=read(player)[q.id],step=q.steps[r?.step??0];
 if(r?.done){await dialog(player,q.title,"Your help is recorded. The route is still yours to visit.",["Close"]);return;}
 const ready=r?.active&&(step.delivery||r.progress>=step.count);
 const pick=await dialog(player,q.title,q.intro+"\n\n"+(r?.active?"Stage "+(r.step+1)+"/"+q.steps.length+" · "+step.label+(step.delivery?"":" · "+r.progress+"/"+step.count):"Stages: "+q.steps.length),[!r?.active?"Accept request":ready?"Report / deliver":"Close","Leave"]);
 if(pick!==0||!nearby(player,target))return;
 const fresh=read(player);
 if(!r?.active){if(localAccept(q,fresh)){write(player,fresh);noteActivity(player,"Side case","Accepted "+q.title);}return;}
 const cur=fresh[q.id];if(!cur?.active||cur.step!==r.step)return;
 const current=q.steps[cur.step];if(!current.delivery&&cur.progress<current.count)return;
 const final=cur.step===q.steps.length-1;
 if(exchange(player,current.delivery,final?q.pay:[],()=>{if(!localAdvance(q,fresh))throw Error("Local stage changed");write(player,fresh);})){
  if(final){archiveChart(player,"local",q.id,{title:q.title},fresh,cur.seen);noteActivity(player,"Side case","Closed "+q.title);say(player,"Request complete. "+localStanding(fresh,key).tier+" standing.");}
  else say(player,q.title+" · Next: "+q.steps[cur.step].label);
 }
}
async function interact(player,target){
  if(activeForms.has(player.id)||!nearby(player,target))return;
  activeForms.add(player.id);
  try{
    const type=target.typeId.split(":")[1], key=keyFor(type), entry=catalogs[type];
    noteActivity(player,"Talk",entry.name,target.location);
    if(type==="echo_route_trader"||type==="ward_resident"){
      const state=readCampaign(player);
      if(applySignal(state,"echo",type)){
        writeCampaign(player,state);
        say(player,"They remember staying behind when the last signal went out.");
      }
    }
    const trust=localStanding(read(player),key),policy=readCampaign(player).choice;
    const response=trust.points>=3?" I remember your help. We can spare a little more now.":trust.points>=1?" Good to see you again.":"";
    const action=await dialog(player,entry.name,entry.intro+response+"\n\n"+trust.tier+" standing",["Trade supplies","Local request","Local stories","Ask about the dispatch","Leave"]);
    if(!nearby(player,target))return;
    if(action===0){
      const deals=discountedDeals(entry.deals,trust,policy,key);
      if(trust.points>=3)deals.push(["minecraft:emerald",2,"minecraft:torch",12]);
      const i=await dialog(player,entry.name,"Exchange · "+trust.tier,deals.map(([a,n,b,m])=>n+" "+pretty(a)+" → "+m+" "+pretty(b)));
      if(!nearby(player,target)||!deals[i])return;
      const [a,n,b,m]=deals[i];
      if(exchange(player,[a,n],[[b,m]]))noteActivity(player,"Trade",entry.name+" offered "+m+" "+pretty(b));
    }else if(action===2){await localStory(player,target,key,entry);
    }else if(action===3){await dialog(player,entry.name,policy==="local"?"The carrier stays local. We decide when to use it.":policy==="publish"?"The engineering routes are available. Our names stayed offline.":"The old request is still repeating. It does not speak for everyone.",["Close"]);
    }else if(action===1){
      const r=read(player)[key];
      const label=r?.active?(r.progress>=entry.count?"Claim reward":"Back"):entry.once&&r?.done?"Completed":"Accept request";
      const decision=await dialog(player,entry.quest,entry.task+"\n\n"+(r?.progress??0)+"/"+entry.count,[label,"Leave"]);
      if(decision!==0||!nearby(player,target))return;
      const state=read(player),cur=state[key];
      if(!r?.active&&!cur?.active&&!(entry.once&&cur?.done)){
        state[key]={active:true,progress:0,seen:[],done:cur?.done??0};
        write(player,state);
        noteActivity(player,"Side case","Accepted "+entry.quest);
      }else if(r?.active&&cur?.active&&cur.progress>=entry.count){
        if(exchange(player,null,entry.pay,()=>{
          state[key]={active:false,progress:0,seen:[],done:cur.done+1};
          write(player,state);
        })){
          archiveChart(player,"local",key,{title:entry.quest},state,cur.seen);
          noteActivity(player,"Side case","Closed "+entry.quest);
        }
      }
    }
  }catch(error){console.warn("[Bearframe local routes] "+error);}
  finally{activeForms.delete(player.id);}
}
export function installEcology(){
  world.beforeEvents.playerInteractWithEntity.subscribe(event=>{
    const {player,target}=event;
    if(!fieldInteraction(player,target))return;
    event.cancel=true;
    system.run(()=>interact(player,target));
  });
  world.afterEvents.entityDie.subscribe(({deadEntity,damageSource})=>{
    if(deadEntity.dimension.id!==OVERWORLD||!dangerous.has(deadEntity.typeId.split(":")[1]))return;
    const p=damageSource.damagingEntity;
    if(p?.typeId==="minecraft:player")fieldProgress(p,"hazard",deadEntity.typeId);
  });
}
