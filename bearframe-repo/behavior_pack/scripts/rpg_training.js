import {standing,rpgState} from "./rpg_progress.js";
export const SPECIALIZATIONS={
 Mira:{name:"Explorer",base:["minecraft:paper",4],output:["minecraft:torch",12],advanced:["minecraft:compass",1],advancedOutput:["minecraft:torch",24]},
 Atlas:{name:"Engineer",base:["minecraft:copper_ingot",4],output:["minecraft:redstone",6],advanced:["minecraft:iron_ingot",4],advancedOutput:["bearframe:salvaged_alloy",2]},
 Sentinel:{name:"Security",base:["minecraft:iron_ingot",3],output:["minecraft:arrow",12],advanced:["minecraft:iron_ingot",5],advancedOutput:["minecraft:arrow",28]},
 Vera:{name:"Research",base:["minecraft:paper",6],output:["minecraft:glow_ink_sac",2],advanced:["minecraft:amethyst_shard",4],advancedOutput:["minecraft:glow_ink_sac",5]},
 Penney:{name:"Support",base:["minecraft:wheat",6],output:["minecraft:bread",4],advanced:["minecraft:emerald",2],advancedOutput:["minecraft:cooked_beef",8]},
 Auren:{name:"Coordinator",base:["minecraft:paper",5],output:["minecraft:compass",1],advanced:["minecraft:emerald",3],advancedOutput:["bearframe:legacy_cell",2]}
};
export function rank(s,lead){const n=standing(s,lead).points;return n>=5?2:n>=2?1:0;}
export function train(s,lead){if(!SPECIALIZATIONS[lead]||rank(s,lead)<1)return false;rpgState(s).specialization=lead;return true;}
export function specialty(s){const lead=rpgState(s).specialization;return SPECIALIZATIONS[lead]?{lead,name:SPECIALIZATIONS[lead].name,rank:rank(s,lead)}:null;}
export function offers(s,lead){const spec=SPECIALIZATIONS[lead],r=rank(s,lead);if(!spec||r<1)return [];const selected=specialty(s)?.lead===lead;const reduce=pair=>[pair[0],Math.max(1,pair[1]-(selected?1:0))];const o=[{payment:reduce(spec.base),reward:spec.output}];if(r>=2)o.push({payment:reduce(spec.advanced),reward:spec.advancedOutput});return o;}
export function specialtyBonus(s,contract){const sp=specialty(s);if(!sp||sp.rank<1)return [];if(sp.lead==="Mira"&&contract==="charts")return [["minecraft:paper",sp.rank*3]];if(sp.lead==="Atlas"&&contract==="power")return [["minecraft:copper_ingot",sp.rank*2]];if(sp.lead==="Sentinel"&&contract==="hostiles")return [["minecraft:arrow",sp.rank*6]];return [];}
