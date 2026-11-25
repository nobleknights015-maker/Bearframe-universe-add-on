import {DECK,SIZE} from "./layout.js";
import {SURVEY_TYPES} from "./regions.js";
import {RUINS,TOWN_SIZE} from "./ruins.js";

export const SURFACE_DATUM="bearframe:surface_survey";
export const EXTENDED_SURFACE_DATUM="bearframe:surface_survey_extended";
export const SURFACE_DONE="bearframe:sited";
export const SURFACE_SITES=[
  {id:"maintenance_relay",biome:"plains",spacing:22,salt:681147,size:SIZE,deck:DECK},
  ...SURVEY_TYPES.map(site=>({...site,size:SIZE,deck:DECK})),
  ...RUINS.slice(2).map(site=>({...site,size:TOWN_SIZE,deck:DECK})),

  {id:"frontier_colony",biome:"plains",size:{x:29,y:16,z:25},deck:3},
  {id:"colony_waystation",biome:"savanna",size:{x:23,y:16,z:21},deck:3},
  {id:"coalition_city",biome:"plains",size:{x:33,y:16,z:29},deck:3},
  {id:"crashed_skiff",biome:"plains",size:{x:25,y:16,z:21},deck:3},
  {id:"relay_nine",biome:"taiga",size:{x:23,y:16,z:21},deck:3},
  {id:"frontier_ruin",biome:"forest",size:{x:25,y:16,z:23},deck:3},
  {id:"syndicate_forge",biome:"desert",size:{x:29,y:16,z:25},deck:3},
  {id:"cinder_works",biome:"mesa",size:{x:27,y:16,z:23},deck:3},
  {id:"nivalis_lab",biome:"ice_plains",size:{x:25,y:16,z:23},deck:3},
  {id:"verdantis_station",biome:"jungle",size:{x:27,y:16,z:23},deck:3},
  {id:"shattered_array",biome:"hills",size:{x:27,y:16,z:25},deck:3},
];

export const LEGACY_DATUM="bearframe:legacy_survey";
export const LEGACY_SITES=[
  {
    "id": "sealed_archive_bunker",
    "size": {
      "x": 25,
      "y": 14,
      "z": 21
    },
    "deck": 3
  },
  {
    "id": "flooded_pump_bunker",
    "size": {
      "x": 25,
      "y": 14,
      "z": 21
    },
    "deck": 3
  },
  {
    "id": "collapsed_transit_bunker",
    "size": {
      "x": 25,
      "y": 14,
      "z": 21
    },
    "deck": 3
  },
  {
    "id": "rootbound_service_bunker",
    "size": {
      "x": 25,
      "y": 14,
      "z": 21
    },
    "deck": 3
  },
  {
    "id": "overgrown_colony",
    "size": {
      "x": 29,
      "y": 16,
      "z": 25
    },
    "deck": 3
  },
  {
    "id": "collapsed_rail_settlement",
    "size": {
      "x": 33,
      "y": 16,
      "z": 29
    },
    "deck": 3
  },
  {
    "id": "lost_waystation",
    "size": {
      "x": 23,
      "y": 16,
      "z": 21
    },
    "deck": 3
  }
];

const expandedSizes={
  "rainline_town": {
    "x": 67,
    "y": 21,
    "z": 55
  },
  "saltline_town": {
    "x": 67,
    "y": 21,
    "z": 55
  },
  "frontier_colony": {
    "x": 61,
    "y": 16,
    "z": 53
  },
  "coalition_city": {
    "x": 65,
    "y": 16,
    "z": 57
  },
  "overgrown_colony": {
    "x": 61,
    "y": 16,
    "z": 53
  },
  "collapsed_rail_settlement": {
    "x": 65,
    "y": 16,
    "z": 57
  },
  "colony_waystation": {
    "x": 49,
    "y": 16,
    "z": 43
  },
  "lost_waystation": {
    "x": 49,
    "y": 16,
    "z": 43
  },
  "farfield_camp": {
    "x": 45,
    "y": 20,
    "z": 37
  },
  "grid_hub": {
    "x": 45,
    "y": 20,
    "z": 37
  },
  "echo_ward": {
    "x": 45,
    "y": 20,
    "z": 37
  },
  "intrusion_checkpoint": {
    "x": 43,
    "y": 20,
    "z": 37
  },
  "foundry_annex": {
    "x": 45,
    "y": 20,
    "z": 37
  },
  "maintenance_relay": {
    "x": 41,
    "y": 20,
    "z": 35
  },
  "crashed_skiff": {
    "x": 47,
    "y": 16,
    "z": 39
  },
  "relay_nine": {
    "x": 45,
    "y": 16,
    "z": 39
  },
  "frontier_ruin": {
    "x": 49,
    "y": 16,
    "z": 43
  },
  "syndicate_forge": {
    "x": 53,
    "y": 16,
    "z": 45
  },
  "cinder_works": {
    "x": 51,
    "y": 16,
    "z": 43
  },
  "nivalis_lab": {
    "x": 49,
    "y": 16,
    "z": 43
  },
  "verdantis_station": {
    "x": 51,
    "y": 16,
    "z": 43
  },
  "shattered_array": {
    "x": 51,
    "y": 16,
    "z": 45
  },
  "sealed_archive_bunker": {
    "x": 45,
    "y": 14,
    "z": 41
  },
  "flooded_pump_bunker": {
    "x": 47,
    "y": 14,
    "z": 41
  },
  "collapsed_transit_bunker": {
    "x": 47,
    "y": 14,
    "z": 41
  },
  "rootbound_service_bunker": {
    "x": 47,
    "y": 14,
    "z": 41
  }
};
for (const site of [...SURFACE_SITES,...LEGACY_SITES]) {
  if (expandedSizes[site.id]) { site.size=expandedSizes[site.id]; site.expanded=true; }
}
