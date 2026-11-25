// Each layout binds the cache, circuit and resident to a rotated terminal.
const bunkerLayout={cache:[9,0,0],seal:[[6,0,0],[6,1,0]],signal:[1,2,2],actor:[-3,0,-3]};
const townLayout={cache:[5,0,0],seal:[[3,0,0],[3,1,0]],signal:[1,2,2],actor:[-5,0,2]};
export const RUINS=[
  {id:"spillway_bunker",name:"Spillway Bunker",biome:"forest",spacing:28,salt:861102,
   panel:"minecraft:blast_furnace",actor:"bearframe:grid_walker",layout:bunkerLayout,bunker:true,
   cost:["minecraft:redstone",2],loot:[["minecraft:iron_ingot",5],["minecraft:copper_ingot",4],["minecraft:bucket",1],["bearframe:legacy_cell",1]],
   repair:"Auxiliary pump power returned. The stores beyond the flood gate are open.",
   note:"The pumps once moved water uphill to a street-level reservoir. The last shift noted a drop in line pressure.",
   escorts:[
     {type:"bearframe:grid_watcher",offset:[-2,1,0],hover:true}
   ]},
  {id:"shelter_bunker",name:"Signal Shelter",biome:"taiga",spacing:28,salt:861103,
   panel:"minecraft:lectern",actor:"bearframe:ward_resident",layout:bunkerLayout,bunker:true,flooded:true,
   cost:["minecraft:copper_ingot",3],loot:[["minecraft:redstone",5],["minecraft:iron_ingot",3],["minecraft:torch",8],["bearframe:salvaged_alloy",2]],
   repair:"The relay isolated the battery bus. The service locker is open.",
   note:"The lower cistern and parts of the approach flooded when the drain failed. The last transmission log repeats a standby signal.",
   escorts:[
     {type:"bearframe:echo_drifter",offset:[-2,0,0]}
   ]},
  {id:"rainline_town",name:"Rainline Works",biome:"plains",spacing:31,salt:861107,
   panel:"minecraft:stonecutter",actor:"bearframe:grid_hauler",layout:townLayout,
   cost:["minecraft:iron_ingot",2],loot:[["minecraft:copper_ingot",6],["minecraft:iron_ingot",3],["bearframe:salvaged_alloy",2]],
   repair:"Workshop power is back. Check the municipal stockroom.",
   note:"A wash channel connects the repair shop to the square. Residents patched the road around the overflowing drain.",
   escorts:[
     {type:"bearframe:echo_drifter",offset:[-4,0,-3]}
   ]},
  {id:"saltline_town",name:"Saltline Depot",biome:"desert",spacing:30,salt:861109,
   panel:"minecraft:cartography_table",actor:"bearframe:ward_resident",layout:townLayout,
   cost:["minecraft:coal",2],loot:[["minecraft:gold_ingot",3],["minecraft:redstone",4],["minecraft:torch",6],["bearframe:salvaged_alloy",2]],
   repair:"The dispatch station is powered. Its loading store is open.",
   note:"The road markings lead from the old sleeping quarters to the freight gantry. Sand buried the outer lanes first.",
   escorts:[
     {type:"bearframe:echo_drifter",offset:[-4,0,-3]},
     {type:"bearframe:grid_repair_crawler",offset:[-2,0,4]}
   ]}
];
export const BUNKER_SIZE={x:36,y:25,z:23};
export const BUNKER_ENTRY=[3,20,11];
export const BUNKER_TERMINAL=[22,9,11];
export const TOWN_SIZE={x:37,y:21,z:31};
export const TOWN_DECK=13;
export const TOWN_TERMINAL=[18,14,15];
