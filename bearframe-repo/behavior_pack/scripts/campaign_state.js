import {goalCount,rpgState} from "./rpg_progress.js";
export const STATE_KEY="bearframe:campaign_v1";
export const initial=()=>({chapter:-1,facts:{},sites:{},side:{},contracts:{},choice:null});
export function read(player){
  const raw=player.getDynamicProperty(STATE_KEY);
  const state=typeof raw==="string"?{...initial(),...JSON.parse(raw)}:initial();rpgState(state);return state;
}
export const write=(player,state)=>player.setDynamicProperty(STATE_KEY,JSON.stringify(state));
export function complete(q,state){
  return q.goals.every(g=>goalCount(q,state,g)>=g.count);
}
export function applySignal(state,type,id,place){
  const facts=state.facts;
  const mark=k=>{
    const had=Boolean(facts[k]);
    facts[k]=1;
    return !had;
  };
  let fresh=false;
  if(type==="read"||type==="repair"){
    fresh=mark(type+":"+id);
    if(place)state.sites[id]=[place.x,place.y,place.z];
    if(type==="read"&&["crashed_skiff","flooded_pump_bunker"].includes(id))mark("survey:bypass");
    if(type==="read"&&["shelter_bunker","rootbound_service_bunker"].includes(id))mark("survey:shelter");
  }else if(type==="echo"){
    fresh=mark("talk:echo");
    if(state.choice)fresh=mark("after:echo")||fresh;
  }else if(type==="boss"){
    fresh=mark("boss:"+id);
    if(place&&(fresh||!state.sites["boss:"+id]))state.sites["boss:"+id]=[Math.floor(place.x),Math.floor(place.y),Math.floor(place.z)];
  }else if(type==="kill"){
    rpgState(state).kills++;
    facts["kill:directorate"]=Math.min(99,(facts["kill:directorate"]??0)+1);
    fresh=true;
  }
  const contract=type==="read"?"charts":type==="repair"?"power":type==="kill"?"hostiles":undefined;
  const record=state.contracts[contract];
  if(record?.active&&record.progress<(contract==="power"?2:3)){
    if(contract==="hostiles"){
      record.progress++;
      fresh=true;
    }else{
      const key=place?[id,place.x,place.y,place.z].join(":"):id;
      if(!record.seen.includes(key)){
        record.seen.push(key);
        record.progress++;
        fresh=true;
      }
    }
  }
  return fresh;
}

export function calibrate(state,port){
  if(state.chapter!==5||!state.facts["repair:spillway_bunker"])return "offline";
  if(state.facts["calibrated:spillway"])return "complete";
  const step=state.calibration??0;
  if(port!==[2,0,1][step]){
    state.calibration=0;
    return "reset";
  }
  state.calibration=step+1;
  if(state.calibration===3){
    state.facts["calibrated:spillway"]=1;
    return "complete";
  }
  return "accepted";
}
