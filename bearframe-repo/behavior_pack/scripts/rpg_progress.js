import {MAIN,SIDES,CONTRACTS} from "./campaign_data.js";
export const LEADS=["Mira","Atlas","Vera","Sentinel","Penney","Auren"];
export function rpgState(s){const p=s.rpg??{};s.rpg={...p,kills:Math.max(0,Number(p.kills??s.facts?.["kill:directorate"]??0)||0),accepted:p.accepted??{},decisions:p.decisions??{}};return s.rpg;}
export function goalCount(q,s,g){if(q?.chapter!==undefined&&g.key==="kill:directorate"){const p=rpgState(s),start=p.accepted[q.id];return start===undefined?0:Math.max(0,p.kills-start);}return s.facts[g.key]??0;}
export function eligible(q,s){return (q.chapter===undefined||s.chapter>=q.chapter)&&(q.requires??[]).every(id=>s.side[id]===2);}
export function acceptSide(q,s){if((s.side[q.id]??0)!==0||!eligible(q,s))return false;s.side[q.id]=1;if(q.chapter!==undefined){const p=rpgState(s);p.accepted[q.id]=p.kills;}return true;}
export function finishSide(q,s,decision){if(s.side[q.id]!==1||!q.goals.every(g=>goalCount(q,s,g)>=g.count))return false;if(q.outcomes&&!q.outcomes.some(o=>o.id===decision))return false;s.side[q.id]=2;if(decision)rpgState(s).decisions[q.id]=decision;return true;}
export function standing(s,lead){const points=MAIN.slice(0,Math.max(0,s.chapter)).filter(q=>q.speaker===lead).length+SIDES.filter(q=>q.speaker===lead&&s.side[q.id]===2).length+CONTRACTS.filter(q=>q.speaker===lead).reduce((n,q)=>n+Math.min(2,s.contracts[q.id]?.done??0),0);return {points,tier:points>=6?"Trusted":points>=3?"Established":points>=1?"Recognized":"Unproven"};}
export function lockedReason(q,s){const needed=(q.requires??[]).filter(id=>s.side[id]!==2).map(id=>SIDES.find(t=>t.id===id)?.title??id);if(q.chapter!==undefined&&s.chapter<q.chapter)needed.push(q.chapter===MAIN.length?"Complete The Last Dispatch":"Reach chapter "+(q.chapter+1));return needed.join(" · ");}
export function inventoryCount(bag,id){let n=0;if(!bag)return n;for(let i=0;i<bag.size;i++){const item=bag.getItem(i);if(item?.typeId===id)n+=item.amount;}return n;}
export function deliveryReady(q,bag){return (q.delivery??[]).every(([id,n])=>inventoryCount(bag,id)>=n);}
export const itemName=id=>id.split(":").at(-1).replaceAll("_"," ");
