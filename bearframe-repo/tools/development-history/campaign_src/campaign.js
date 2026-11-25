import {BlockPermutation,ItemStack,system,world} from "@minecraft/server";
import {ActionFormData} from "@minecraft/server-ui";
import {EVIDENCE,MAIN,SIDES,CONTRACTS} from "./campaign_data.js";
import {read,write,complete,applySignal,calibrate} from "./campaign_state.js";

const CITY="bearframe:city_orbit";
const OVERWORLD="minecraft:overworld";
const ARCHIVE="bearframe:field_archive";
const activeForms=new Set();
const tell=(p,text)=>p.sendMessage("§3[Farfield Dossier]§r "+text);
const editors={
  0:"Mira",11:"Auren",12:"Atlas",13:"Vera",14:"Mira",15:"Sentinel",16:"Penney",
};

export function campaignSignal(player,type,id,place){
  const state=read(player);
  const fresh=applySignal(state,type,id,place);
  write(player,state);
  if(type==="read"&&fresh&&EVIDENCE[id])tell(player,EVIDENCE[id].name+" — "+EVIDENCE[id].text);
  if(type==="echo"&&fresh){
    tell(player,state.choice==="local"?"They agree to maintain the route locally and ask for a copy of the service marks."
      :state.choice==="publish"?"They ask how Farfield will mark routes that their neighbors prefer to leave closed."
      :"I asked someone to keep the light on. I never asked them to send a train.");
  }
}

function reward(player,items,commit){
  const bag=player.getComponent("minecraft:inventory")?.container;
  if(!bag||bag.emptySlotsCount<items.length){
    tell(player,"Make room for "+items.length+" reward stacks, then turn this in again.");
    return false;
  }
  const slots=[];
  for(let i=0;i<bag.size&&slots.length<items.length;i++)if(!bag.getItem(i))slots.push(i);
  let written=0;
  try{
    for(const [id,count] of items){
      bag.setItem(slots[written],new ItemStack(id,count));
      written++;
    }
    commit();
  }catch(error){
    for(let i=0;i<written;i++)bag.setItem(slots[i],undefined);
    throw error;
  }
  return true;
}
function goalText(q,state){
  return q.goals.map(g=>`${Math.min(g.count,state.facts[g.key]??0)}/${g.count}  ${g.label}`).join("\n");
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
      state.chapter=0;
      write(player,state);
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
  const pick=await show(player,form(q.title,q.intro+"\n\n"+goalText(q,state)+"\n\nDebrief: "+q.speaker,[label]));
  if(pick!==0||!ready||!here||!atDesk(player,target))return;
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
    tell(player,q.report);
    if(choice)tell(player,choice==="publish"?"Farfield has the engineering route. The names stayed offline.":"Routes remain under local control. The station will send service parts when requested.");
    const next=MAIN[now.chapter];
    tell(player,next?"Next chapter: "+next.title+" · "+next.speaker:"The Last Dispatch complete. The side cases and repeatable contracts remain open.");
  }
}
async function sideMenu(player,target,lead){
  const options=SIDES.filter(q=>q.speaker===lead);
  if(!options.length){tell(player,"This lead has no open side cases.");return;}
  const now=read(player);
  const pick=await show(player,form("Side cases · "+lead,"Cases can run alongside the campaign.",options.map(q=>q.title+(now.side[q.id]===2?" ✓":""))));
  const q=options[pick];
  if(!q||!atDesk(player,target))return;
  const state=read(player),stage=state.side[q.id]??0,ready=complete(q,state);
  const action=await show(player,form(q.title,q.intro+"\n\n"+goalText(q,state),[stage===0?"Accept case":stage===1&&ready?"Turn in case":stage===2?"Case closed":"Back"]));
  if(action!==0||!atDesk(player,target))return;
  const current=read(player);
  if((current.side[q.id]??0)!==stage)return;
  if(stage===0){current.side[q.id]=1;write(player,current);tell(player,"Case accepted: "+q.title);}
  if(stage===1&&complete(q,current)&&reward(player,q.reward,()=>{current.side[q.id]=2;write(player,current);})){
    tell(player,q.report);
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
    tell(player,"Contract accepted: "+q.title);
  }else if(prior?.active&&r?.active&&r.progress>=q.count){
    const bonus=current.chapter>=MAIN.length&&current.choice==="local"&&q.id==="power"?[["bearframe:salvaged_alloy",1]]:
      current.chapter>=MAIN.length&&current.choice==="publish"&&q.id==="charts"?[["minecraft:torch",6]]:[];
    if(reward(player,[...q.reward,...bonus],()=>{
      current.contracts[q.id]={active:false,progress:0,seen:[],done:r.done+1};
      write(player,current);
    }))tell(player,"Payment received. You can take another commission when ready.");
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
async function openBoard(player,target,lead){
  if(activeForms.has(player.id)||!atDesk(player,target))return;
  activeForms.add(player.id);
  try{
    const pick=await show(player,form("Farfield Dossier",lead+" · Station briefing",["Main campaign","Side cases","Repeatable field contracts","Field directory and coordinates"]));
    if(!atDesk(player,target))return;
    if(pick===0)await mainMenu(player,target,lead);
    if(pick===1)await sideMenu(player,target,lead);
    if(pick===2)await contractMenu(player,target,lead);
    if(pick===3)await show(player,form("Field directory",journalText(read(player)),["Close"]));
  }catch(error){console.warn("[Bearframe campaign] "+error);}
  finally{activeForms.delete(player.id);}
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
    if(deadEntity.dimension.id!==OVERWORLD||!/^bearframe:(hollow_|nullframe_hunter)/.test(deadEntity.typeId))return;
    const killer=damageSource.damagingEntity;
    if(killer?.typeId==="minecraft:player")campaignSignal(killer,"kill",deadEntity.typeId);
  });
}
