import {DECK,SIZE} from "./layout.js";
import {SURVEY_TYPES} from "./regions.js";
import {RUINS,TOWN_SIZE} from "./ruins.js";

export const SURFACE_DATUM="bearframe:surface_survey";
export const SURFACE_DONE="bearframe:sited";
export const SURFACE_SITES=[
  {id:"maintenance_relay",biome:"plains",spacing:22,salt:681147,size:SIZE,deck:DECK},
  ...SURVEY_TYPES.map(site=>({...site,size:SIZE,deck:DECK})),
  ...RUINS.slice(2).map(site=>({...site,size:TOWN_SIZE,deck:DECK})),
];
