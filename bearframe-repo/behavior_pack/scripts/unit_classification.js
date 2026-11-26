// Shared classification of the existing vanilla replacements and custom units.
export const FACTION_LABELS={directorate:"Nullframe Directorate",echo:"Echo Frames",grid:"Ghost Grid"};
const rows=[
  [
    "directorate",
    "always",
    "Hollow Crossbow Infantry",
    "minecraft:pillager"
  ],
  [
    "directorate",
    "always",
    "Nullframe Assault Enforcer",
    "minecraft:vindicator"
  ],
  [
    "directorate",
    "always",
    "Nullframe Signal Controller",
    "minecraft:evocation_illager",
    "minecraft:evoker"
  ],
  [
    "directorate",
    "always",
    "Directorate Siege Construct",
    "minecraft:ravager"
  ],
  [
    "directorate",
    "always",
    "Hollow Perimeter Scout",
    "bearframe:hollow_scout"
  ],
  [
    "directorate",
    "always",
    "Hollow Breacher",
    "bearframe:hollow_breacher"
  ],
  [
    "directorate",
    "always",
    "Hollow Line Drone",
    "bearframe:hollow_line"
  ],
  [
    "directorate",
    "always",
    "Nullframe Hunter",
    "bearframe:nullframe_hunter"
  ],
  [
    "directorate",
    "conditional",
    "Directorate Gate Guard",
    "bearframe:directorate_guard"
  ],
  [
    "directorate",
    "conditional",
    "Directorate Officer",
    "bearframe:directorate_officer"
  ],
  [
    "echo",
    "always",
    "Feral Echo · Corrupted Walker",
    "minecraft:zombie"
  ],
  [
    "echo",
    "always",
    "Feral Echo · Desiccated Walker",
    "minecraft:husk"
  ],
  [
    "echo",
    "always",
    "Feral Echo · Flooded Walker",
    "minecraft:drowned"
  ],
  [
    "echo",
    "always",
    "Feral Echo · Corrupted Resident",
    "minecraft:zombie_villager",
    "minecraft:zombie_villager_v2"
  ],
  [
    "echo",
    "always",
    "Feral Echo · Skeletal Marksman",
    "minecraft:skeleton"
  ],
  [
    "echo",
    "always",
    "Feral Echo · Frost Marksman",
    "minecraft:stray"
  ],
  [
    "echo",
    "always",
    "Feral Echo · Overgrown Marksman",
    "minecraft:bogged"
  ],
  [
    "echo",
    "always",
    "Feral Echo · Dune Marksman",
    "minecraft:parched"
  ],
  [
    "echo",
    "always",
    "Feral Echo · Charred Sentinel",
    "minecraft:wither_skeleton"
  ],
  [
    "echo",
    "always",
    "Feral Echo · Chemical Disruptor",
    "minecraft:witch"
  ],
  [
    "echo",
    "always",
    "Feral Echo · Signal Wraith",
    "minecraft:vex"
  ],
  [
    "echo",
    "conditional",
    "Feral Echo · Phase Stalker",
    "minecraft:enderman"
  ],
  [
    "echo",
    "conditional",
    "Echo · Nether Scavenger",
    "minecraft:piglin"
  ],
  [
    "echo",
    "always",
    "Feral Echo · Nether Enforcer",
    "minecraft:piglin_brute"
  ],
  [
    "echo",
    "conditional",
    "Feral Echo · Corrupted Nether Scavenger",
    "minecraft:zombie_pigman",
    "minecraft:zombified_piglin"
  ],
  [
    "echo",
    "always",
    "Feral Echo · Lost Frame",
    "bearframe:echo_lost"
  ],
  [
    "echo",
    "conditional",
    "Echo Chamber Sentinel",
    "bearframe:echo_sentinel"
  ],
  [
    "echo",
    "neutral",
    "Echo Resident",
    "minecraft:villager",
    "minecraft:villager_v2",
    "bearframe:ward_resident"
  ],
  [
    "echo",
    "neutral",
    "Echo Route Trader",
    "minecraft:wandering_trader",
    "bearframe:echo_route_trader"
  ],
  [
    "echo",
    "neutral",
    "Echo Drifter",
    "bearframe:echo_drifter"
  ],
  [
    "echo",
    "neutral",
    "Echo Signal Companion",
    "minecraft:allay"
  ],
  [
    "grid",
    "always",
    "Ghost Grid · Defense Turret",
    "bearframe:grid_turret"
  ],
  [
    "grid",
    "always",
    "Ghost Grid · Breach Guardian",
    "bearframe:grid_breach_guard"
  ],
  [
    "grid",
    "always",
    "Ghost Grid · Deep Defense Colossus",
    "minecraft:warden"
  ],
  [
    "grid",
    "always",
    "Ghost Grid · Rootbound Watcher",
    "minecraft:creaking"
  ],
  [
    "grid",
    "conditional",
    "Ghost Grid · Sector Guardian",
    "bearframe:grid_guardian"
  ],
  [
    "grid",
    "conditional",
    "Ghost Grid · Route Guardian",
    "bearframe:grid_wayfarer"
  ],
  [
    "grid",
    "conditional",
    "Ghost Grid · Hexapod Walker",
    "bearframe:grid_walker"
  ],
  [
    "grid",
    "conditional",
    "Ghost Grid · Recon Drone",
    "bearframe:grid_watcher"
  ],
  [
    "grid",
    "conditional",
    "Ghost Grid · Industrial Hauler",
    "bearframe:grid_hauler"
  ],
  [
    "grid",
    "conditional",
    "Ghost Grid · Protocol Keeper",
    "bearframe:grid_protocol_keeper"
  ],
  [
    "grid",
    "neutral",
    "Ghost Grid · Repair Crawler",
    "bearframe:grid_repair_crawler"
  ],
  [
    "grid",
    "always",
    "Palinode-6",
    "bearframe:grid_palinode"
  ],
  [
    "grid",
    "always",
    "Silt Engine",
    "bearframe:grid_silt_engine"
  ],
  [
    "grid",
    "always",
    "Gantry Marrow",
    "bearframe:grid_gantry_marrow"
  ],
  [
    "grid",
    "always",
    "Cinder Spindle",
    "bearframe:grid_cinder_spindle"
  ],
  [
    "echo",
    "always",
    "Seam-Riven",
    "bearframe:echo_seam_riven"
  ],
  [
    "echo",
    "always",
    "Veil Regent",
    "bearframe:echo_veil_regent"
  ],
  [
    "echo",
    "always",
    "Rubble Rook",
    "bearframe:echo_rubble_rook"
  ],
  [
    "echo",
    "always",
    "Hush Pendulum",
    "bearframe:echo_hush_pendulum"
  ],
  [
    "grid",
    "conditional",
    "Ghost Grid · Settlement Defense Golem",
    "minecraft:iron_golem"
  ]
];
export const UNIT_TYPES=Object.freeze(Object.fromEntries(rows.flatMap(([faction,disposition,variant,...ids])=>ids.map(id=>[id,Object.freeze({faction,disposition,variant,key:ids[0]})]))));
export function classifyUnit(id){if(typeof id!=="string")return undefined;return UNIT_TYPES[id.includes(":")?id:"bearframe:"+id];}
export function isThreat(unit,confirmed=false){return !!unit&&(unit.disposition==="always"||(unit.disposition==="conditional"&&confirmed));}
export function entityThreat(entity){
 const unit=classifyUnit(entity?.typeId);if(!unit)return undefined;
 if(unit.disposition==="always")return unit;
 if(unit.disposition!=="conditional")return undefined;
 try{if(entity.getDynamicProperty("bearframe:stabilized"))return undefined;if(entity.getDynamicProperty("bearframe:escalated")||entity.getDynamicProperty("bearframe:confirmed_aggression"))return unit;}catch{}
 return undefined;
}
export function noteAggression(attacker){const unit=classifyUnit(attacker?.typeId);if(unit?.disposition!=="conditional")return;try{attacker.setDynamicProperty("bearframe:confirmed_aggression",true);}catch{}}
export function unitLabel(unit){return FACTION_LABELS[unit.faction]+" / "+unit.variant;}
