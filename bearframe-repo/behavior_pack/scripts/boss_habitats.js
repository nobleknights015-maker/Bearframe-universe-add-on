// Offsets are relative to the field archive block in each authored template.
export const BOSS_HABITATS = {
  collapsed_transit_bunker: { boss: "grid_palinode", offsets: [[4,0,9],[-3,0,9],[3,0,9]] },
  flooded_pump_bunker: { boss: "grid_silt_engine", offsets: [[3,0,9],[2,0,9],[0,0,9]] },
  rootbound_service_bunker: { boss: "grid_gantry_marrow", offsets: [[0,0,-9],[0,0,-8],[-4,0,5]] },
  shattered_array: { boss: "grid_cinder_spindle", offsets: [[-4,0,11],[-3,0,11],[-5,0,10]] },
  overgrown_colony: { boss: "echo_seam_riven", offsets: [[22,0,19],[-19,0,19],[-18,0,20]] },
  sealed_archive_bunker: { boss: "echo_veil_regent", offsets: [[-9,0,8],[-7,0,9],[-8,0,8]] },
  frontier_ruin: { boss: "echo_rubble_rook", offsets: [[12,0,4],[3,0,12],[11,0,4]] },
  lost_waystation: { boss: "echo_hush_pendulum", offsets: [[-8,0,15],[-7,0,15],[-6,0,5]] },
};

export function encounterRoll(siteId, position) {
  let hash = 2166136261;
  for (const char of [siteId, position.x, position.y, position.z].join(":")) {
    hash = Math.imul(hash ^ char.charCodeAt(0), 16777619);
  }
  return (hash >>> 0) % 3 === 0;
}
