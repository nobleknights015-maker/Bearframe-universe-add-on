import {ItemStack} from "@minecraft/server";
import {SURVEY_TYPES} from "./regions.js";

const LOG="bearframe:survey_log";
const AWARDED="bearframe:survey_awarded";
const FIELD_ROUTES=["maintenance_relay",...SURVEY_TYPES.map(r=>r.id)];
const TITLES=["Maintenance Relay",...SURVEY_TYPES.map(r=>r.name)];
const INSIGNIA="bearframe:farfield_insignia";

export function recordSurvey(player,id){
  const index=FIELD_ROUTES.indexOf(id);
  if(index<0)return;
  const mask=1<<index;
  const log=Number(player.getDynamicProperty(LOG)??0);
  if(log&mask)return;
  player.setDynamicProperty(LOG,log|mask);
  player.sendMessage("§3[Farfield Log]§r Survey recorded for "+TITLES[index]+".");
}

export function reportSurvey(player){
  const log=Number(player.getDynamicProperty(LOG)??0);
  const missing=TITLES.filter((_,i)=>!(log&(1<<i)));
  if(missing.length){
    player.sendMessage(`§3[Farfield Dispatch]§r ${TITLES.length-missing.length} of ${TITLES.length} sites surveyed. Still unlogged: ${missing.join(", ")}.`);
    return;
  }
  if(player.getDynamicProperty(AWARDED)){
    player.sendMessage("§3[Farfield Dispatch]§r Your complete surface survey is already on record.");
    return;
  }
  const bag=player.getComponent("minecraft:inventory")?.container;
  if(!bag)return;
  let slot=0;
  while(slot<bag.size && bag.getItem(slot))slot++;
  if(slot>=bag.size){player.sendMessage("§3[Farfield Dispatch]§r Make room for your survey insignia.");return;}
  bag.setItem(slot,new ItemStack(INSIGNIA));
  try{player.setDynamicProperty(AWARDED,true);}catch(error){bag.setItem(slot,undefined);throw error;}
  player.sendMessage("§3[Farfield Dispatch]§r Surface survey complete. Farfield issued your insignia.");
}
