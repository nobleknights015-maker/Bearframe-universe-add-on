import {entityThreat} from "./unit_classification.js";
import {creditedPlayer} from "./combat_credit.js";
import {archiveChart,openCharts,registerChartSite} from "./route_charts.js";
import {fieldProgress} from "./ecology.js";
import {noteActivity} from "./activity_log.js";
import {BlockPermutation,ItemStack,system,world} from "@minecraft/server";
import {ActionFormData} from "@minecraft/server-ui";
import {EVIDENCE,MAIN,SIDES,CONTRACTS} from "./campaign_data.js";
import {read,write,complete,applySignal,calibrate} from "./campaign_state.js";
import {goalCount,eligible,acceptSide,finishSide,standing,lockedReason,inventoryCount,deliveryReady,itemName,rpgState,LEADS} from "./rpg_progress.js";

import {SPECIALIZATIONS,rank,train,specialty,offers,specialtyBonus} from "./rpg_training.js";
import {BOSS_DOSSIERS} from "./boss_dossiers.js";
const CITY="bearframe:city_orbit";
const OVERWORLD="minecraft:overworld";
const ARCHIVE="bearframe:field_archive";
const activeForms=new Set();
const tell=(p,text)=>p.sendMessage("§3[Farfield Dossier]§r "+text);
const MAIN_TALK=[["Why follow the signal?","Mira: A reservation survived. We do not know if anyone still needs it."],["What should I ask the resident?","Mira: Ask what they remember, not what the roster says they should remember."],["What is the Directorate seeking?","Sentinel: An operational key. The checkpoint is recent; the network is not."],["Can I use a repaired terminal?","Atlas: Yes. Confirm the circuit is live. No redundant repair."],["Why separate the channels?","Vera: A useful engineering map does not require a public resident list."],["How do I test the carrier?","Auren: Verify the pump. Beyond the stores, use Return, Intake, Carrier."],["What happens after the policy?","Mira: Tell an Echo what we decided, verify the Switchyard and return. The route isn't ours to command."]];
const editors={
  0:"Mira",11:"Auren",12:"Atlas",13:"Vera",14:"Mira",15:"Sentinel",16:"Penney",
};

export function campaignSignal(player,type,id,place){
  fieldProgress(player,type,id,place);
  if(type==="read"&&place)registerChartSite(id,player.dimension.id,place);
  const state=read(player);
  const fresh=applySignal(state,type,id,place);
  write(player,state);
  if(fresh&&type==="read")noteActivity(player,"Field entry",EVIDENCE[id]?.name??id,place);
  if(fresh&&type==="boss"&&BOSS_DOSSIERS[id]){noteActivity(player,"Campaign","Defeated "+BOSS_DOSSIERS[id].name,place);tell(player,"Encounter logged: "+BOSS_DOSSIERS[id].name+".");}
  if(fresh&&type==="repair")noteActivity(player,"Repair",EVIDENCE[id]?.name??id,place);
  if(type==="echo"&&id==="echo_drifter")noteActivity(player,"Talk","Echo Drifter");
  if(type==="read"&&fresh&&EVIDENCE[id])tell(player,EVIDENCE[id].name+" — "+EVIDENCE[id].text);
  if(type==="echo"&&fresh){
    tell(player,state.choice==="local"?"They agree to maintain the route locally and ask for a copy of the service marks."
      :state.choice==="publish"?"They ask how Farfield will mark routes that their neighbors prefer to leave closed."
      :"I asked someone to keep the light on. I never asked them to send a train.");
  }
}

function reward(player,items,commit,payment=[]){
  const bag=player.getComponent("minecraft:inventory")?.container;
  if(!bag)return false;
  const old=Array.from({length:bag.size},(_,i)=>bag.getItem(i)),next=old.slice();
  for(const [id,count] of payment){let remain=count;for(let i=0;i<next.length&&remain>0;i++){const item=next[i];if(item?.typeId!==id)continue;const take=Math.min(item.amount,remain);remain-=take;if(take===item.amount)next[i]=undefined;else{const copy=item.clone();copy.amount-=take;next[i]=copy;}}if(remain){tell(player,"Bring "+count+" "+itemName(id)+".");return false;}}
  const slots=[];for(let i=0;i<next.length;i++)if(!next[i])slots.push(i);
  if(slots.length<items.length){tell(player,"Make room for "+items.length+" reward stacks, then turn this in again.");return false;}
  for(let i=0;i<items.length;i++)next[slots[i]]=new ItemStack(...items[i]);
  const changed=[];try{for(let i=0;i<next.length;i++)if(next[i]!==old[i]){changed.push(i);bag.setItem(i,next[i]);}commit();}catch(error){for(const i of changed)bag.setItem(i,old[i]);throw error;}return true;
}
function goalText(q,state,player){
 const lines=q.goals.map(g=>`${Math.min(g.count,goalCount(q,state,g))}/${g.count}  ${g.label}`);
 const bag=player?.getComponent("minecraft:inventory")?.container;
 for(const [id,n] of q.delivery??[])lines.push((bag?Math.min(n,inventoryCount(bag,id))+"/"+n:n+" ×")+"  Deliver "+itemName(id));return lines.join("\n")||"Return to your contact.";
}
function form(title,body,buttons){
  const f=new ActionFormData().title(title).body(body);
  for(const b of buttons)f.button(b);
  return f;
}
async function show(player,f){
  if(!player.isValid)return;
  const result=await f.show(player);
  if(!result.canceled)return result.selection;
}
function atDesk(player,target){
  if(!player.isValid||!target?.isValid||player.dimension.id!==CITY||target.dimension.id!==CITY)return false;
  const a=player.location,b=target.location;
  return (a.x-b.x)**2+(a.y-b.y)**2+(a.z-b.z)**2<=64;
}
async function mainMenu(player,target,lead){
  const state=read(player);
  if(state.chapter===-1){
    const start=await show(player,form("The Last Dispatch",MAIN[0].intro,[lead==="Mira"?"Accept Farfield's assignment":"Find Mira in Farfield Mapping","Back"]));
    if(start===0&&atDesk(player,target)&&lead==="Mira"&&read(player).chapter===-1){
      const current=read(player);current.chapter=0;
      write(player,current);
      noteActivity(player,"Campaign","Accepted The Last Dispatch");
      tell(player,"Assignment accepted. Ask Mira for the dossier or use a field archive for the current objectives.");
    }
    return;
  }
  const q=MAIN[state.chapter];
  if(!q){
    await show(player,form("The Last Dispatch · Closed",state.choice==="local"
      ?"The carrier is local. Echo residents and maintenance units can keep their own route active. Atlas offers an extra alloy bundle on maintenance contracts."
      :"Farfield is distributing the engineering map without resident names. Mira offers extra survey supplies on chart contracts.",["Return"]));
    return;
  }
  const ready=complete(q,state);
  const here=lead===q.speaker;
  const label=ready&&here?(q.choice?"Select dispatch policy":"Debrief with "+lead):"Back";
  const talk=MAIN_TALK[state.chapter];
  const pick=await show(player,form(q.title,q.intro+"\n\n"+goalText(q,state)+"\n\nDebrief: "+q.speaker,[label,...(here&&talk?[talk[0]]:[]),"Open route charts","Close"]));
  if(!atDesk(player,target))return;
  if(here&&talk&&pick===1){await show(player,form(q.speaker,talk[1],["Close"]));return;}
  if(pick===(here&&talk?2:1)){await openCharts(player);return;}
  if(pick!==0||!ready||!here)return;
  let choice;
  if(q.choice){
    const n=await show(player,form("Dispatch policy",q.report+"\n\nThe engineering map can be shared without the names. A local-only carrier keeps all route control at the site.",["Publish engineering routes","Keep the carrier local","Decide later"]));
    if(n!==0&&n!==1)return;
    choice=n===0?"publish":"local";
  }
  if(!atDesk(player,target))return;
  const now=read(player);
  if(now.chapter!==state.chapter||!complete(q,now))return;
  if(reward(player,q.reward,()=>{
    if(choice){
      now.choice=choice;
      // The final verification is required after the policy is chosen.
      delete now.facts["repair:grid_hub"];
    }
    now.chapter++;
    write(player,now);
  })){
    archiveChart(player,"main",state.chapter,q,now);
    noteActivity(player,"Campaign","Debrief complete: "+q.title);
    tell(player,q.report);
    if(choice)tell(player,choice==="publish"?"Farfield has the engineering route. The names stayed offline.":"Routes remain under local control. The station will send service parts when requested.");
    const next=MAIN[now.chapter];
    tell(player,next?"Next chapter: "+next.title+" · "+next.speaker:"The Last Dispatch complete. The side cases and repeatable contracts remain open.");
  }
}
async function sideMenu(player,target,lead){
  const all=SIDES.filter(q=>q.speaker===lead),now=read(player),rep=standing(now,lead);
  const options=all.filter(q=>now.side[q.id]||eligible(q,now)),locked=all.filter(q=>!options.includes(q));
  const pick=await show(player,form("Assignments · "+lead,rep.tier+" standing · "+rep.points+"\nRecovered evidence counts. New combat orders count only after acceptance.",[...options.map(q=>q.title+(now.side[q.id]===2?" · Closed":now.side[q.id]===1?" · Active":" · Available")),...(locked.length?["Future assignments"]:[]),"Close"]));
  if(!atDesk(player,target))return;
  if(pick===options.length&&locked.length){await show(player,form("Future assignments",locked.map(q=>q.title+" — "+lockedReason(q,now)).join("\n\n"),["Close"]));return;}
  const q=options[pick];if(!q)return;
  const s=read(player),stage=s.side[q.id]??0,ready=complete(q,s)&&deliveryReady(q,player.getComponent("minecraft:inventory")?.container);
  const previous=q.outcomes?.find(o=>o.id===rpgState(s).decisions[q.id]);
  const body=stage===2?q.report+(previous?"\n\n"+previous.report:""):q.intro+"\n\n"+goalText(q,s,player)+(q.delivery?.length?"\n\nSupplies are exchanged only at debrief.":"");
  const action=await show(player,form(q.title,body,[stage===0?"Accept assignment":stage===1&&ready?"Debrief and claim":stage===2?"Close":"Back","Open route charts","Close"]));
  if(!atDesk(player,target))return;if(action===1){await openCharts(player);return;}if(action!==0||stage===2)return;
  if(stage===0){const current=read(player);if(acceptSide(q,current)){write(player,current);noteActivity(player,"Side case","Accepted "+q.title);tell(player,lead+": "+q.title+" is in your Field Log.");}return;}
  if(!ready)return;
  let chosen;if(q.outcomes){const n=await show(player,form(q.title+" · Recommendation","Choose the type of support to prepare. It determines your supply package and recorded recommendation.",[...q.outcomes.map(o=>o.label),"Decide later"]));chosen=q.outcomes[n];if(!chosen)return;}
  if(!atDesk(player,target))return;
  const current=read(player);if(current.side[q.id]!==1||!complete(q,current))return;
  if(reward(player,[...q.reward,...(chosen?.reward??[])],()=>{if(!finishSide(q,current,chosen?.id))throw Error("Assignment changed");write(player,current);},q.delivery??[])){
    archiveChart(player,"side",q.id,q,current);noteActivity(player,"Side case","Closed "+q.title);
    tell(player,lead+": "+q.report+(chosen?" "+chosen.report:""));tell(player,"Department standing: "+standing(current,lead).tier);
  }
}
async function contractMenu(player,target,lead){
  const q=CONTRACTS.find(entry=>entry.speaker===lead);
  if(!q){tell(player,"Mira, Atlas, and Sentinel post field contracts.");return;}
  const state=read(player),prior=state.contracts[q.id];
  const progress=prior?.progress??0;
  const action=await show(player,form(q.title,q.text+"\n\n"+progress+"/"+q.count+" · Completed "+(prior?.done??0),[!prior?.active?"Accept contract":progress>=q.count?"Claim payment":"Back"]));
  if(action!==0||!atDesk(player,target))return;
  const current=read(player),r=current.contracts[q.id];
  if(!prior?.active&&!r?.active){
    current.contracts[q.id]={active:true,progress:0,seen:[],done:r?.done??0};
    write(player,current);
    noteActivity(player,"Contract","Accepted "+q.title);
    tell(player,"Contract accepted: "+q.title);
  }else if(prior?.active&&r?.active&&r.progress>=q.count){
    const bonus=current.chapter>=MAIN.length&&current.choice==="local"&&q.id==="power"?[["bearframe:salvaged_alloy",1]]:
      current.chapter>=MAIN.length&&current.choice==="publish"&&q.id==="charts"?[["minecraft:torch",6]]:[];
    if(reward(player,[...q.reward,...bonus,...specialtyBonus(current,q.id)],()=>{
      current.contracts[q.id]={active:false,progress:0,seen:[],done:r.done+1};
      write(player,current);
    })){
      archiveChart(player,"contract",q.id,q,current,r.seen);
      noteActivity(player,"Contract","Paid for "+q.title);
      tell(player,"Payment received. You can take another commission when ready.");
    }
  }
}
function journalText(state){
  const active=MAIN[state.chapter];
  const stages=active?active.title+"\n"+goalText(active,state):state.chapter<0?"Speak with Mira at Bearframe Station to begin.":"The Last Dispatch is complete.";
  const known=Object.entries(EVIDENCE).map(([id,e])=>{
    const coords=state.sites[id];
    return e.name+" ("+e.biome+")"+(coords?" · "+coords.join(", "):"");
  });
  return stages+"\n\nField directory · Coordinates appear after your first visit\n"+known.join("\n");
}
async function trainingMenu(player,target,lead){
 const state=read(player),sp=SPECIALIZATIONS[lead],r=rank(state,lead),selected=specialty(state);
 if(!sp)return;
 const deals=offers(state,lead);
 const choice=await show(player,form(sp.name+" · Department services","Rank "+r+"/2 · "+(selected?.lead===lead?"Active specialization":"Not selected")+"\nEarn standing through assignments. Rank 1 unlocks supplies; rank 2 unlocks advanced supplies. Selecting this specialty discounts its exchanges.",[r>=1?"Select "+sp.name:"Rank 1 required",...deals.map(d=>d.payment[1]+" "+itemName(d.payment[0])+" → "+d.reward[1]+" "+itemName(d.reward[0])),"Close"]));
 if(!atDesk(player,target))return;
 const fresh=read(player);
 if(choice===0){if(train(fresh,lead)){write(player,fresh);tell(player,"Specialization selected: "+sp.name);}return;}
 const deal=deals[choice-1],current=offers(fresh,lead)[choice-1];
 if(!deal||!current||JSON.stringify(deal)!==JSON.stringify(current))return;
 if(reward(player,[deal.reward],()=>{},[deal.payment]))noteActivity(player,"Trade",sp.name+" supplies");
}
async function openBoard(player,target,lead){
  if(activeForms.has(player.id)||!atDesk(player,target))return;
  activeForms.add(player.id);
  try{
    const pick=await show(player,form("Farfield Dossier",lead+" · Station briefing",["Main campaign","Department assignments","Repeatable field contracts","Field directory and coordinates","Treasure charts","Department standing","Specialization and supplies"]));
    if(!atDesk(player,target))return;
    if(pick===0)await mainMenu(player,target,lead);
    if(pick===1)await sideMenu(player,target,lead);
    if(pick===2)await contractMenu(player,target,lead);
    if(pick===3)await show(player,form("Field directory",journalText(read(player)),["Close"]));
    if(pick===4)await openCharts(player);
    if(pick===6)await trainingMenu(player,target,lead);
    if(pick===5){const s=read(player);await show(player,form("Department standing",LEADS.map(name=>{const r=standing(s,name);return name+" · "+r.tier+" ("+r.points+")";}).join("\n")+"\n\nMain debriefs, assignments and up to two contracts per department count.",["Close"]));}
  }catch(error){console.warn("[Bearframe campaign] "+error);}
  finally{activeForms.delete(player.id);}
}
export function stationReport(player,staff){
  const {facts,choice}=read(player);
  const lines={
    0:facts["read:grid_hub"]?"Farfield Dispatch: The relay and Switchyard records are linked. Check the dossier for the next assignment.":undefined,
    11:facts["repair:spillway_bunker"]?"Auren: Spillway pressure is holding. The workshop test bench is clear to use.":undefined,
    12:facts["repair:foundry_annex"]?"Atlas: The Annex is running. Bring coal to its terminal for another batch of stock. The station rigger can calibrate the Scanner or Wrench with salvaged alloy.":undefined,
    13:facts["read:sealed_archive_bunker"]?"Vera: I can chart the service routes with the ledger sealed. The residents' names stay where they belong.":undefined,
    15:facts["read:intrusion_checkpoint"]?"Sentinel: I logged their patrol route. Assume they still have people near the checkpoint until we hear otherwise.":undefined,
    16:choice==="local"?"Penney: The Commons has a copy of the maintenance schedule. The residents decide who gets the rest.":
      choice==="publish"?"Penney: Travelers can ask for the engineering map here. I kept the room roster out of the public copy.":
      facts["talk:echo"]?"Penney: I reserved a quiet table in the Commons. If any of the ward residents want to visit, they can choose when.":undefined
  };
  if(!lines[staff])return false;
  tell(player,lines[staff]);
  return true;
}

export function relayDebrief(player){
  const state=read(player);
  if(state.chapter>0||!state.facts["read:maintenance_relay"])return false;
  if(state.facts["repair:maintenance_relay"]){
    tell(player,"Mira: You got the relay transmitting again. That reservation was still open. Check the Switchyard for the other end of the signal. The field charts have the survey notes.");
  }else{
    tell(player,"Mira: A shelter reservation with no one checked in. Keep a copy of that log. The Switchyard may tell us where the signal was going.");
  }
  return true;
}
export function campaignDialogue(player,target,staff){
  const lead=editors[staff];
  if(!lead||!player.isSneaking)return false;
  if(staff===0&&read(player).chapter<0){
    tell(player,"Mira starts The Last Dispatch in the Farfield Annex. Sneak-interact with her to open the dossier.");
  }else{
    openBoard(player,target,lead);
  }
  return true;
}
// Provide the same bench in a service wing that was already constructed
// before this update. Only install onto the authored floor when all cells
// are empty or already contain their correct console.
export function ensureDispatchBench(site,at){
  const cells=[17,21,25].map(dx=>at(site.pos,[dx,0,-3],site.r));
  if(cells.some(pos=>!site.dim.isChunkLoaded(pos)))return;
  const blocks=cells.map(pos=>site.dim.getBlock(pos));
  const console="bearframe:dispatch_console";
  if(blocks.some((b,i)=>!b||(!b.isAir&&(b.typeId!==console||b.permutation.getState("bearframe:port")!==i))||
      !b.below()||b.below().isAir||b.below().isLiquid))return;
  for(const [i,b] of blocks.entries()){
    if(b.isAir)b.setPermutation(BlockPermutation.resolve(console,{"bearframe:port":i}));
  }
}

export function installCampaign(archiveIds){
  world.beforeEvents.playerInteractWithBlock.subscribe(event=>{
    if(event.block.typeId!==ARCHIVE||!event.isFirstEvent)return;
    event.cancel=true;
    const {player,block}=event;
    const location=block.location,id=archiveIds[block.permutation.getState("bearframe:record")];
    if(!id)return;
    system.run(()=>{
      if(!player.isValid||player.dimension.id!==OVERWORLD)return;
      const pos=player.location;
      if((pos.x-location.x)**2+(pos.y-location.y)**2+(pos.z-location.z)**2>49)return;
      const had=read(player).facts["read:"+id];
      campaignSignal(player,"read",id,location);
      if(had)tell(player,EVIDENCE[id].text);
      if(player.isSneaking)tell(player,journalText(read(player)).split("\n\n")[0]);
    });
  });
  world.beforeEvents.playerInteractWithBlock.subscribe(event=>{
    if(event.block.typeId!=="bearframe:dispatch_console"||!event.isFirstEvent)return;
    event.cancel=true;
    const {player,block}=event;
    const port=block.permutation.getState("bearframe:port"), location=block.location;
    system.run(()=>{
      if(!player.isValid||player.dimension.id!==OVERWORLD)return;
      const pos=player.location;
      if((pos.x-location.x)**2+(pos.y-location.y)**2+(pos.z-location.z)**2>49)return;
      const state=read(player),result=calibrate(state,port);
      write(player,state);
      const label=["Intake","Carrier","Return"][port];
      const message={
        offline:"Awaiting Auren's dispatch assignment and a verified auxiliary pump.",
        reset:"Signal out of order. The test bench has reset. Atlas's sequence starts at Return.",
        accepted:"Port accepted. "+state.calibration+"/3 verified.",
        complete:"Carrier calibrated. Return to Auren to choose the dispatch policy.",
      };
      tell(player,label+" — "+message[result]);
    });
  });
  world.afterEvents.entityDie.subscribe(({deadEntity,damageSource})=>{
    if(deadEntity.dimension.id!==OVERWORLD||!entityThreat(deadEntity))return;
    const killer=creditedPlayer(damageSource);
    if(killer?.typeId==="minecraft:player")campaignSignal(killer,"kill",deadEntity.typeId);
  });
}
