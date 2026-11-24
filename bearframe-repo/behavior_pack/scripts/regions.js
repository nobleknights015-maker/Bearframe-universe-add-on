import {RUINS} from "./ruins.js";
export const REGION_ANCHOR="bearframe:region_anchor";
export const SURVEY_TYPES=[
  {id:"farfield_camp",name:"Farfield Survey Camp",biome:"plains",spacing:25,salt:773210,
   panel:"minecraft:cartography_table",actor:"bearframe:farfield_surveyor",
   escorts:[
     {type:"bearframe:field_researcher",offset:[-4,0,0]},
     {type:"bearframe:atlas_vanguard",offset:[2,0,0]}
   ]},
  {id:"grid_hub",name:"Overgrown Switchyard",biome:"forest",spacing:24,salt:773213,
   panel:"minecraft:lodestone",actor:"bearframe:grid_walker",cost:["minecraft:redstone",2],
   repair:"Switchyard isolated. The service stores can be opened.",
   loot:[["minecraft:copper_ingot",4],["minecraft:amethyst_shard",2],["bearframe:legacy_cell",1]],
   escorts:[
     {type:"bearframe:grid_protocol_keeper",offset:[-2,1,-3],hover:true},
     {type:"bearframe:grid_turret",offset:[-5,0,0],hostile:true}
   ]},
  {id:"echo_ward",name:"Legacy Support Ward",biome:"taiga",spacing:26,salt:773218,
   panel:"minecraft:smithing_table",actor:"bearframe:ward_resident",cost:["minecraft:iron_ingot",2],
   repair:"Auxiliary lights restored. The resident's core and records are untouched.",
   loot:[["minecraft:iron_ingot",3],["minecraft:gold_ingot",1],["bearframe:salvaged_alloy",2]],
   escorts:[
     {type:"bearframe:echo_sentinel",offset:[0,0,-4]}
   ]},
  {id:"intrusion_checkpoint",name:"Directorate Intrusion Checkpoint",biome:"savanna",spacing:24,salt:773219,
   panel:"minecraft:observer",actor:"bearframe:directorate_guard",cost:["minecraft:copper_ingot",3],
   repair:"Local gate bypassed. The patrol is still active if it survived.",
   loot:[["minecraft:redstone",4],["minecraft:iron_ingot",4],["bearframe:salvaged_alloy",2]],
   escorts:[
     {type:"bearframe:directorate_officer",offset:[-3,0,0]},
     {type:"bearframe:hollow_line",offset:[1,0,4],hostile:true}
   ]},
  {id:"foundry_annex",name:"Ruined Foundry Annex",biome:"desert",spacing:24,salt:773221,
   panel:"minecraft:blast_furnace",actor:"bearframe:grid_hauler",cost:["minecraft:coal",2],
   repair:"Material handler powered. The annex processes parts and stock.",
   loot:[["minecraft:iron_ingot",5],["minecraft:copper_ingot",3],["bearframe:salvaged_alloy",3]],
   escorts:[
     {type:"bearframe:grid_guardian",offset:[0,0,-5]},
     {type:"bearframe:grid_repair_crawler",offset:[-4,0,-3]}
   ]}
];
export const TYPES=[...SURVEY_TYPES,...RUINS];
export const PIN=[1,-2,0], CACHE=[5,0,0], SEAL=[[3,0,0],[3,1,0]], ACTOR=[-1,0,3], SIGNAL=[1,2,2], LANDING=[-2,0,0];
export const ORBIT="bearframe:city_orbit";
export const CITY_SIZE={x:60,y:8,z:23};
export const CITY_ARRIVAL={x:2.5,y:101,z:.5};
export const CITY_EXIT={x:1,y:101,z:2};
export const CITY_ROLES = [
  {type:"bearframe:farfield_surveyor",pos:{x:22.5,y:101,z:-6.5},name:"Farfield Dispatch",
   line:"Chart what you can verify. Mira's rule holds: survey first, designate salvage only when safe. Sneak-interact to check your survey log."},
  {type:"bearframe:city_steward",pos:{x:17.5,y:101,z:7.5},name:"Commons Steward",
   line:"The Commons stays open across every shift. No holidays or weekends here—just neighbors sharing space between rotations."},
  {type:"bearframe:city_engineer",pos:{x:35.5,y:101,z:-6.5},name:"Systems Engineer",
   line:"The station runs on redundant power and heat rejection. Each compartment can isolate a fault before it cascades."},
  {type:"bearframe:city_watch",pos:{x:36.5,y:101,z:7.5},name:"Watchtower Officer",
   line:"Different department, same objective. Use the return desk in the arrival bay when you're heading back down to the surface."},
  {type:"bearframe:atlas_rigger",pos:{x:50.5,y:101,z:-6.5},name:"Atlas Production Rigger",
   line:"Production and maintenance keep the hull standing. Bring salvaged chassis alloy—Sneak-interact to reclaim usable iron and copper."},
  {type:"bearframe:atlas_vanguard",pos:{x:45.5,y:101,z:.5},name:"Atlas Combat Vanguard",
   line:"Thirty-five of us handle structured defense under Atlas. Watchtower tracks threats; we hold the line when they knock."},
  {type:"bearframe:vera_artisan",pos:{x:50.5,y:101,z:6.5},name:"Visual Production Artisan",
   line:"Visual Production keeps displays, signage, and interface standards clean. Vera's rule is simple: higher quality, always."}
];
