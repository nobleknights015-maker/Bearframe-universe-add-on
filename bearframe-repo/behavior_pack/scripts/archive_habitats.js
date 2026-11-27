// Local positions relative to each archive in the authored structure.
export const ARCHIVE_HABITATS = {
  relay_nine: [["grid_protocol_keeper","grid_repair_crawler"],[[1,0,5],[3,0,-3],[8,0,2]]],
  frontier_ruin: [["echo_route_trader","echo_lost"],[[3,0,8],[7,0,3],[-3,0,4]]],
  crashed_skiff: [["grid_repair_crawler"],[[2,0,10],[0,0,10],[1,0,9]]],
  sealed_archive_bunker: [["ward_resident","grid_protocol_keeper"],[[-4,0,5],[-2,0,-3],[-2,0,12]]],
  collapsed_transit_bunker: [["grid_repair_crawler","echo_lost"],[[1,0,5],[3,0,-4],[8,0,3]]],
  rootbound_service_bunker: [["grid_protocol_keeper","echo_route_trader"],[[-4,0,1],[-2,0,-7],[3,0,-2]]],
  flooded_pump_bunker: [["grid_repair_crawler","grid_breach_guard"],[[1,0,5],[3,0,-3],[8,0,2],[3,0,9]]],
  overgrown_colony: [["ward_resident","echo_route_trader"],[[1,0,6],[7,0,2],[1,0,-4]]],
  lost_waystation: [["echo_route_trader","ward_resident"],[[4,0,-3],[4,0,7],[9,0,2]]],
  nivalis_lab: [["grid_protocol_keeper","grid_repair_crawler"],[[3,0,11],[3,0,10],[3,0,8]]],
  shattered_array: [["grid_repair_crawler","grid_breach_guard"],[[-4,0,11],[-3,0,11],[-5,0,10]]],
};

export function quarterTurns([x,y,z]){
  return [[x,y,z],[-z,y,x],[-x,y,-z],[z,y,-x]];
}
