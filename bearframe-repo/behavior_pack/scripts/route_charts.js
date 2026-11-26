import {chartSiteAvailable} from "./chart_site_checks.js";
import {system,world} from "@minecraft/server";
import {ActionFormData} from "@minecraft/server-ui";
import {SURFACE_SITES,LEGACY_SITES} from "./surface_layout.js";
import {MAIN,SIDES,CONTRACTS,EVIDENCE} from "./campaign_data.js";
import {read as readCampaign} from "./campaign_state.js";
import {goalCount} from "./rpg_progress.js";

import {ALL_LOCAL} from "./local_rpg.js";
import {bossSite,activeHunt} from "./boss_dossiers.js";
import {siteClaimKey,canRetryClaim,HABITAT_DIRECTORY,chooseHabitat} from "./boss_claims.js";
import {ALL_LOCAL as STORY_JOBS} from "./local_rpg.js";
const OVERWORLD="minecraft:overworld";
const DIRECTORY="bearframe:charted_sites:";
const SAVED="bearframe:quest_charts";
const TRACK="bearframe:tracked_chart";
const REQUEST="bearframe:survey_request";
const HUNT_REQUEST="bearframe:hunt_survey_request";
const ROAMING="bearframe:field_requests";
const supportedSurvey=new Set(["spillway_bunker",...[...SURFACE_SITES,...LEGACY_SITES].map(site=>site.id)]);
const GOLD="§6[Field Charts]§r ";
const open=new Set();
const followed=new Map();
const bearings=["N","NE","E","SE","S","SW","W","NW"];
const arrows=["↑","↗","→","↘","↓","↙","←","↖"];
const MAP_ICON="textures/bearframe/field_log_pad";
const biomeHints={
  "Plains":"Scan exposed plains from a rise, then follow the valley edge.",
  "Forest":"Search clearings and dry banks inside forest country.",
  "Taiga":"Search dry breaks in the spruce woods and their lower ridges.",
  "Savanna":"Follow the acacia flats and look for clear ground near a ridge.",
  "Desert":"Search dunes with a broad, dry foot and check the sandstone approaches.",
  "Hills":"Look across lower saddles and broad ridges rather than cliff faces.",
  "Swamp":"Search the dry margins around the swamp pools.",
  "Jungle":"Look in larger jungle clearings and open stretches along its edges.",
  "Ice plains":"Check dry snowfields and the low margins around frozen lakes.",
};
const generic={farfield_camp:{name:"Farfield Survey Camp",biome:"Plains"},coalition_city:{name:"Coalition City",biome:"Plains"},
    frontier_colony:{name:"Frontier Colony",biome:"Plains"},colony_waystation:{name:"Colony Waystation",biome:"Savanna"},
    grid_hub:EVIDENCE.grid_hub};
const station={id:"station",name:"Bearframe Station",dim:"bearframe:city_orbit",p:[2,101,0]};
const sourceOf=id=>EVIDENCE[id]??generic[id];
const point=p=>[Math.floor(p.x),Math.floor(p.y),Math.floor(p.z)];
const loc=a=>({x:a[0],y:a[1],z:a[2]});
const dist=(a,b)=>Math.hypot(a[0]-b[0],a[2]-b[2]);
const load=(owner,k,fallback)=>{
  const val=owner.getDynamicProperty(k);
  return typeof val==="string"?JSON.parse(val):fallback;
};
const save=(owner,k,v)=>owner.setDynamicProperty(k,JSON.stringify(v));
const craftForm=(title,body)=>new ActionFormData().title(title).body(body);

export function registerChartSite(id,dim,pos,status="ready"){
  if(!sourceOf(id)||dim!==OVERWORLD)return;
  const p=point(pos), key=DIRECTORY+id;
  const list=load(world,key,[]);
  const near=list.findIndex(e=>dist(p,e.p)<(status==="ready"?40:18));
  if(near>=0){
    const old=list[near];
    if(status==="beacon")return;
    if(old.status==="ready"){
      const dimension=world.getDimension?.(dim);
      if(!dimension?.isChunkLoaded||chartSiteAvailable(dimension,id,loc(old.p)))return;
    }
    list.splice(near,1);
  }
  list.unshift({p,status});
  save(world,key,list.slice(0,12));
}
export function removeChartBeacon(id,dim,pos){
  if(!sourceOf(id)||dim!==OVERWORLD)return;
  const p=point(pos),key=DIRECTORY+id,list=load(world,key,[]);
  const current=list.filter(e=>e.status!=="beacon"||dist(p,e.p)>2);
  if(current.length!==list.length)save(world,key,current);
}
export function hasSurveySiteNearby(id,position,radius,dimension){
  return load(world,DIRECTORY+id,[]).some(entry=>entry.status==="ready"&&
    dist(entry.p,point(position))<=radius&&chartSiteAvailable(dimension,id,loc(entry.p)));
}

const available=(player,id,p)=>player.dimension.id!==OVERWORLD||!player.dimension.isChunkLoaded||
  !p||chartSiteAvailable(player.dimension,id,loc(p));

function solution(id,player,state,visitedOnly=false){
  const e=sourceOf(id);
  if(!e)return;
  const saved=state.sites[id];
  const list=load(world,DIRECTORY+id,[]);
  const visit=id==="spillway_bunker"&&saved?
    list.find(v=>v.status==="ready"&&dist(v.p,saved)<=46)?.p??saved:saved;
  if(visit&&(visitedOnly||available(player,id,visit)))
    return {id,name:e.name,biome:e.biome,dim:OVERWORLD,p:visit,status:"visited"};
  if(visitedOnly)return;
  const origin=player.dimension.id===OVERWORLD?point(player.location):[0,0,0];
  const candidates=list.filter(v=>v.status!=="ready"||available(player,id,v.p));
  const ready=candidates.filter(v=>v.status==="ready");
  const entries=ready.length?ready:candidates;
  const found=entries.sort((a,b)=>dist(a.p,origin)-dist(b.p,origin))[0];
  return {id,name:e.name,biome:e.biome,dim:OVERWORLD,p:found?.p??null,status:found?.status??"unconfirmed"};
}
// Keep hunt routing distinct from ordinary discovery/visited coordinates.
function huntSolution(id,player,state){
  const e=sourceOf(id);if(!e)return;
  const origin=player.dimension.id===OVERWORLD?point(player.location):[0,0,0];
  const entries=load(world,HABITAT_DIRECTORY+id,[]);
  const found=chooseHabitat(entries,origin,p=>world.getDynamicProperty(siteClaimKey(id,loc(p))),p=>available(player,id,p),system.currentTick);
  return {id,name:e.name,biome:e.biome,dim:OVERWORLD,p:found??null,status:found?"ready":"unconfirmed",encounter:true};
}
function requestedSolution(id,player,state){
  return player.getDynamicProperty(HUNT_REQUEST)===id&&activeHunt(state,id)?huntSolution(id,player,state):solution(id,player,state);
}
export function offerRelayLead(player){
  if(player.dimension.id!==OVERWORLD||player.getDynamicProperty(TRACK)||
    player.getDynamicProperty("bearframe:relay_lead_received"))return;
  const state=readCampaign(player);
  if(state.chapter>0||state.facts["read:maintenance_relay"])return;
  const dest=solution("maintenance_relay",player,state);
  if(dest.status!=="ready"||dist(dest.p,point(player.location))>100)return;
  save(player,TRACK,dest);
  player.setDynamicProperty("bearframe:relay_lead_received",true);
  player.sendMessage("§b[Farfield]§r We have a real signal. Follow the bearing to the Maintenance Relay and read the lectern. I'll file the coordinates in your Field Log.");
}

function sitesFor(goal){
  const [action,id]=goal.key.split(":");
  if(action==="read"||action==="repair"||action==="calibrated")return [id==="spillway"?"spillway_bunker":id];
  if(goal.key==="survey:bypass")return ["crashed_skiff","flooded_pump_bunker"];
  if(goal.key==="survey:shelter")return ["rootbound_service_bunker","shelter_bunker"];
  if(action==="talk"||action==="after")return ["echo_ward","shelter_bunker"];
  if(action==="boss")return bossSite(id)?[bossSite(id)]:[];
  if(action==="kill")return ["intrusion_checkpoint"];
  return [];
}
export function missingCampaignSite(player){
  const state=readCampaign(player);
  const requested=player.getDynamicProperty(REQUEST);
  if(typeof requested==="string"){
    const status=requestedSolution(requested,player,state)?.status;
    if(status==="unconfirmed"||status==="beacon")return requested;
  }
  const chapter=MAIN[state.chapter];
  const pending=chapter?.goals.filter(goal=>(state.facts[goal.key]??0)<goal.count);
  if(!pending?.length)return;
  for(const goal of pending){
    const sites=sitesFor(goal);
    if(sites.some(id=>{
      const status=solution(id,player,state)?.status;
      return status==="ready"||status==="visited";
    }))continue;
    const supported=sites.find(id=>supportedSurvey.has(id));
    if(supported)return supported;
  }
}

function staticTargets(id){
  if(id==="charts")return ["frontier_ruin","grid_hub","farfield_camp","maintenance_relay","echo_ward"];
  if(id==="power")return ["grid_hub","foundry_annex","rainline_town","spillway_bunker"];
  return ["intrusion_checkpoint"];
}
function goalMaps(q,player,state,finished=false){
  const rows=[];
  for(const g of q.goals){
    for(const id of sitesFor(g)){
      let dest=solution(id,player,state,finished);
      if(g.key.startsWith("boss:")){
        const actual=state.sites[g.key];
        if(actual)dest={id,name:sourceOf(id).name,biome:sourceOf(id).biome,dim:OVERWORLD,p:actual,status:"visited",encounter:true};
        else if(!finished)dest=huntSolution(id,player,state);
      }
      if(dest&&!rows.some(x=>x.id===id))rows.push({...dest,
        objective:g.label,done:goalCount(q,state,g)>=g.count});
    }
  }
  return rows;
}
function visitedFromSeen(values,player,state){
  const seen=[];
  for(const entry of values??[]){
    const [id,...parts]=entry.split(":");
    const coords=parts.map(Number);
    const route=solution(id,player,state,true);
    if(coords.length===3&&coords.every(Number.isFinite)&&sourceOf(id))
      seen.push({id,name:sourceOf(id).name,dim:OVERWORLD,p:coords,status:"visited",done:true});
    else if(route)seen.push(route);
  }
  return seen;
}
function isPermanentChart(x){return x.key.startsWith("main:")||x.key.startsWith("side:")||STORY_JOBS.some(q=>x.key.startsWith("local:"+q.id+":"));}
function fitArchive(fixed,runs){
 const result=[...fixed,...runs];
 // Conservative UTF-8 budget: up to four bytes per Unicode code point.
 const bytes=s=>Array.from(JSON.stringify(s)).reduce((n,c)=>n+(c.codePointAt(0)<=127?1:c.codePointAt(0)<=2047?2:c.codePointAt(0)<=65535?3:4),0);
 while(bytes(result)>30000&&result.length>fixed.length)result.pop();
 // Quest records can be reconstructed from persistent progress; preserve newest permanent entries first.
 while(bytes(result)>30000&&result.length)result.pop();
 return result;
}
export function archiveChart(player,kind,id,quest,state,seen){
  const chartState=kind==="local"?readCampaign(player):state;
  const maps=kind==="main"||kind==="side"?goalMaps(quest,player,chartState,true):visitedFromSeen(seen,player,chartState);
  const all=load(player,SAVED,[]);
  const run=kind==="contract"?state.contracts[id]?.done:kind==="local"?state[id]?.done:null;
  const key=kind+":"+id+(run!=null?":"+run:"");
  if(all.some(x=>x.key===key))return;
  all.unshift({key,title:quest.title,maps});
  const fixed=all.filter(isPermanentChart);
  const runs=all.filter(x=>!isPermanentChart(x)).slice(0,36);
  save(player,SAVED,fitArchive(fixed,runs));
}
function completedLists(player,state){
  const saved=load(player,SAVED,[]);
  const restore=[];
  for(let i=0;i<Math.min(state.chapter,MAIN.length);i++){
    if(!saved.some(r=>r.key==="main:"+i))
      restore.push({key:"main:"+i,title:MAIN[i].title,maps:goalMaps(MAIN[i],player,state,true)});
  }
  for(const q of SIDES)if(state.side[q.id]===2&&!saved.some(r=>r.key==="side:"+q.id))
    restore.push({key:"side:"+q.id,title:q.title,maps:goalMaps(q,player,state,true)});
  for(const q of CONTRACTS)if(state.contracts[q.id]?.done&&!saved.some(r=>r.key.startsWith("contract:"+q.id+":")))
    restore.push({key:"contract:"+q.id+":legacy",title:q.title+" · earlier runs",maps:[]});
  const local=load(player,ROAMING,{});
  for(const q of STORY_JOBS)if(local[q.id]?.done&&!saved.some(r=>r.key.startsWith("local:"+q.id+":")))restore.push({key:"local:"+q.id+":restored",title:q.title,maps:visitedFromSeen(local[q.id].seen,player,state)});
  return [...saved,...restore.reverse()];
}
function activeLists(player,state){
  const rows=[];
  const q=MAIN[state.chapter];
  if(q)rows.push({title:q.title,maps:[...goalMaps(q,player,state),{...station,objective:"Debrief with "+q.speaker}]});
  else if(state.chapter<0)rows.push({title:"Start The Last Dispatch",maps:[solution("farfield_camp",player,state),station]});
  for(const side of SIDES)if(state.side[side.id]===1)rows.push({title:side.title,maps:[...goalMaps(side,player,state),{...station,objective:"Debrief with "+side.speaker}]});
  for(const c of CONTRACTS)if(state.contracts[c.id]?.active)rows.push({title:c.title,
    maps:[...visitedFromSeen(state.contracts[c.id]?.seen,player,state),...staticTargets(c.id).map(id=>solution(id,player,state)).filter(Boolean)]});
  const local=load(player,ROAMING,{});
  const localTypes={
    echo_route_trader:["Notes for the Next Traveler",staticTargets("charts")],
    ward_resident:["Neighbors' Signal",["echo_ward","shelter_bunker","overgrown_colony","lost_waystation"]],
    grid_protocol_keeper:["Service Loop",staticTargets("power")],
    grid_wayfarer:["Clear Where You Can",["collapsed_transit_bunker","flooded_pump_bunker"]],
    grid_repair_crawler:["Crawler Service Run",staticTargets("power")],
  };
  for(const q of ALL_LOCAL)localTypes[q.id]=[q.title,q.sites];
  for(const [id,value] of Object.entries(local)){
    if(!value.active||!localTypes[id])continue;
    const [title,sites]=localTypes[id];
    rows.push({title,maps:sites.map(id=>solution(id,player,state)).filter(Boolean)});
  }
  return rows;
}
export function bearing(from,to){
  if(from[0]===to[0]&&from[2]===to[2])return 0;
  const dx=to[0]-from[0],dz=to[2]-from[2];
  const n=Math.round(Math.atan2(dx,-dz)*4/Math.PI);
  return (n+8)%8;
}
function direction(player,dest){
  if(!dest.p||player.dimension.id!==dest.dim)return null;
  const p=point(player.location);
  const d=Math.round(dist(p,dest.p));
  const b=bearing(p,dest.p);
  const dy=dest.p[1]-p[1];
  return {d,b,dy};
}
function status(dest){
  return {ready:"Confirmed site",beacon:"Survey beacon · site placement still pending",visited:"Your recorded visit",unconfirmed:"Search area only"}[dest.status]??"Station docking route";
}
function body(player,dest){
  const dir=direction(player,dest);
  const guide=!dest.p?"Biome to search: "+dest.biome+"\n"+(biomeHints[dest.biome]??"Explore and check this chart again when Farfield detects a site."):
    "X "+dest.p[0]+"   Y "+dest.p[1]+"   Z "+dest.p[2]+"\n"+(dir?
      arrows[dir.b]+" "+bearings[dir.b]+" · "+dir.d+" blocks · "+(dir.dy>4?"Above you":dir.dy< -4?"Below you":"Near your level"):
      "This waypoint is in "+(dest.dim===OVERWORLD?"the Overworld":"Bearframe Station")+".");
  return status(dest)+"\n"+(dest.objective?dest.objective+"\n":"")+"\n"+guide;
}
async function show(f,player){
  if(!player.isValid)return;
  const r=await f.show(player);
  return r.canceled?undefined:r.selection;
}
async function waypoint(player,dest){
  const f=craftForm(dest.name,body(player,dest));
  const needsSurvey=dest.status==="beacon"||!dest.p||(!dest.encounter&&!available(player,dest.id,dest.p));
  const requestable=needsSurvey&&supportedSurvey.has(dest.id);
  if(dest.p)f.button("Track this X",MAP_ICON);
  if(requestable)f.button("Request a Farfield survey",MAP_ICON);
  f.button("Back");
  const result=await show(f,player);
  if(!player.isValid)return;
  if(requestable&&result===(dest.p?1:0)){
    player.setDynamicProperty(REQUEST,dest.id);
    player.setDynamicProperty(HUNT_REQUEST,dest.encounter?dest.id:undefined);
    player.setDynamicProperty(TRACK,undefined);followed.delete(player.id);
    player.sendMessage(GOLD+"Survey requested for "+dest.name+". "+(biomeHints[dest.biome]??"Look for broad, dry ground.")+" Farfield will report the entrance once you get close enough to verify it.");
  }else if(dest.p&&result===0){
    save(player,TRACK,dest);
    followed.set(player.id,{dest,near:false});
    player.sendMessage(GOLD+"Tracking "+dest.name+". Your bearing appears while you travel.");
  }
}
async function group(player,section){
  const state=readCampaign(player);
  let options;
  if(section===0)options=activeLists(player,state);
  if(section===1)options=completedLists(player,state);
  if(section===2)options=[{title:"Visited and reported sites",maps:[...Object.keys({...EVIDENCE,...generic}).map(id=>solution(id,player,state)).filter(x=>x?.p),station]}];
  if(!options?.length){player.sendMessage(GOLD+"No charts filed in this section yet.");return;}
  const chooser=craftForm(["Active quest charts","Completed quest charts","Field coordinates"][section],
    section===1?"Saved routes can be tracked again.":"X marks a recorded site or a reported survey beacon.");
  for(const x of options)chooser.button(x.title);
  const chosen=options[await show(chooser,player)];
  if(!chosen)return;
  const places=craftForm(chosen.title,chosen.maps.length?"Pick a site to open its chart.":"This job has no recorded location.");
  for(const m of chosen.maps)places.button(m.name+"\n"+status(m),MAP_ICON);
  places.button("Close");
  const dest=chosen.maps[await show(places,player)];
  if(dest)await waypoint(player,dest);
}
export async function openCharts(player){
  if(open.has(player.id))return;
  open.add(player.id);
  try{
    const f=craftForm("Field Log · Treasure Charts","Plan a route, track an X, or reopen a route after the quest is done.");
    f.button("Active quest charts",MAP_ICON);
    f.button("Completed quest charts",MAP_ICON);
    f.button("Field coordinates",MAP_ICON);
    f.button("Clear tracking");
    const result=await show(f,player);
    if(result===3){
      player.setDynamicProperty(TRACK,undefined);
      player.setDynamicProperty(REQUEST,undefined);
      player.setDynamicProperty(HUNT_REQUEST,undefined);
      followed.delete(player.id);
      player.onScreenDisplay.setActionBar("");
    }else if(result!==undefined)await group(player,result);
  }catch(error){console.warn("[Bearframe charts] "+error);}
  finally{open.delete(player.id);}
}
export function installRouteCharts(){
  world.afterEvents.playerLeave.subscribe(({playerId})=>{followed.delete(playerId);open.delete(playerId);});
  system.runInterval(()=>{
    for(const p of world.getAllPlayers()){
      const request=p.getDynamicProperty(REQUEST);
      if(typeof request==="string"){
        const ready=requestedSolution(request,p,readCampaign(p));
        if(ready?.status==="ready"||ready?.status==="visited"){
          const current=load(p,TRACK,null);
          const canTrack=!current||current.id===request;
          if(canTrack){
            followed.set(p.id,{dest:ready,near:false});
            save(p,TRACK,ready);
          }
          p.setDynamicProperty(REQUEST,undefined);
          p.setDynamicProperty(HUNT_REQUEST,undefined);
          p.sendMessage(GOLD+"Entrance confirmed for "+ready.name+(canTrack?". Tracking your requested route.":". Open your Field Log to switch routes."));
        }
      }
      let tracked=followed.get(p.id);
      if(!tracked){
        const dest=load(p,TRACK,null);
        if(!dest)continue;
        tracked={dest,near:false};
        followed.set(p.id,tracked);
      }
      let dest=tracked.dest;
      if(dest.encounter&&dest.status!=="visited"&&activeHunt(readCampaign(p),dest.id)){
        const next=huntSolution(dest.id,p,readCampaign(p));
        const claim=dest.p?world.getDynamicProperty(siteClaimKey(dest.id,loc(dest.p))):undefined;
        if(!dest.p||!available(p,dest.id,dest.p)||claim!=="active"&&!canRetryClaim(claim,true,system.currentTick)){
          if(next?.p){dest=next;tracked.dest=dest;tracked.near=false;save(p,TRACK,dest);}
          else {p.setDynamicProperty(REQUEST,dest.id);p.setDynamicProperty(HUNT_REQUEST,dest.id);p.setDynamicProperty(TRACK,undefined);followed.delete(p.id);p.onScreenDisplay.setActionBar("");p.sendMessage(GOLD+"Encounter cleared or unavailable. Farfield is surveying another habitat.");continue;}
        }
      }
      if(dest.dim===OVERWORLD&&!dest.encounter&&(dest.status==="beacon"||!available(p,dest.id,dest.p))){
        const hadBeacon=dest.status==="beacon";

        const candidate=solution(dest.id,p,readCampaign(p));
        if(candidate?.p&&(candidate.status!=="beacon"||!hadBeacon)){
          dest=candidate;tracked.dest=dest;tracked.near=false;
          save(p,TRACK,dest);
        }else if(!hadBeacon){
          p.setDynamicProperty(TRACK,undefined);
          followed.delete(p.id);
          p.onScreenDisplay.setActionBar("");
          p.sendMessage(GOLD+"The reported "+dest.name+" entrance could not be verified. Open the Field Log to survey again.");
          continue;
        }
      }
      if(dest.encounter&&dest.status!=="visited"&&!activeHunt(readCampaign(p),dest.id)){
        p.setDynamicProperty(TRACK,undefined);followed.delete(p.id);p.onScreenDisplay.setActionBar("");continue;
      }
      const d=direction(p,dest);
      if(!d){
        p.onScreenDisplay.setActionBar("§6× §r"+dest.name+" · "+(dest.dim===OVERWORLD?"Overworld":"Bearframe Station"));
        continue;
      }
      if(d.d<=8&&Math.abs(d.dy)<=5){
        p.onScreenDisplay.setActionBar("§6× §r"+dest.name+" · "+(dest.status==="beacon"?"Survey beacon area":"At the marked location"));
        if(!tracked.near){tracked.near=true;p.sendMessage(GOLD+"Reached "+dest.name+".");}
      }else{
        tracked.near=false;
        p.onScreenDisplay.setActionBar("§6× §r"+dest.name+" "+arrows[d.b]+" "+bearings[d.b]+" "+d.d+"m"+(Math.abs(d.dy)>5?(d.dy>0?" ↑ ":" ↓ ")+Math.abs(d.dy)+"m":""));
      }
    }
  },40);
}
