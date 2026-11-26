// Optional, original encounter dossiers using the existing 0.10.24 boss roster.
export const BOSS_DOSSIERS={
  "grid_palinode": {
    "id": "grid_palinode",
    "name": "Palinode-6",
    "site": "collapsed_transit_bunker",
    "speaker": "Atlas",
    "chapter": 3,
    "intro": "The transit route is broken, but a heavy legacy walker still patrols it. Approach only after you have checked the collapse. Its ram follows a marked lane; the quake leaves a narrow inner safe zone.",
    "reward": [
      [
        "bearframe:salvaged_alloy",
        5
      ],
      [
        "minecraft:iron_ingot",
        10
      ]
    ]
  },
  "grid_silt_engine": {
    "id": "grid_silt_engine",
    "name": "Silt Engine",
    "site": "flooded_pump_bunker",
    "speaker": "Atlas",
    "chapter": 3,
    "intro": "A submerged industrial engine is discharging through the intake. Watch the long beam warning and the purge around its chassis. The old service record may help locate it.",
    "reward": [
      [
        "bearframe:legacy_cell",
        3
      ],
      [
        "minecraft:redstone",
        16
      ]
    ]
  },
  "grid_gantry_marrow": {
    "id": "grid_gantry_marrow",
    "name": "Gantry Marrow",
    "site": "rootbound_service_bunker",
    "speaker": "Mira",
    "chapter": 4,
    "intro": "Farfield has reports of an ancient load-handling machine moving on a broken service directive. Leave its marked drop point and avoid its forward rake.",
    "reward": [
      [
        "bearframe:salvaged_alloy",
        5
      ],
      [
        "minecraft:copper_ingot",
        12
      ]
    ]
  },
  "grid_cinder_spindle": {
    "id": "grid_cinder_spindle",
    "name": "Cinder Spindle",
    "site": "shattered_array",
    "speaker": "Auren",
    "chapter": 4,
    "intro": "A surviving flywheel assembly still responds to a fragmented carrier. Its induction lance tracks a lane; a flywheel burst threatens the surrounding ring.",
    "reward": [
      [
        "bearframe:legacy_cell",
        3
      ],
      [
        "minecraft:amethyst_shard",
        8
      ]
    ]
  },
  "echo_seam_riven": {
    "id": "echo_seam_riven",
    "name": "Seam-Riven",
    "site": "overgrown_colony",
    "speaker": "Sentinel",
    "chapter": 2,
    "intro": "A hostile, heavily fragmented Echo has been reported at the colony. Avoid the forward cut and step out of its marked rush. Do not mistake other Echo residents for threats.",
    "reward": [
      [
        "minecraft:emerald",
        5
      ],
      [
        "bearframe:salvaged_alloy",
        3
      ]
    ]
  },
  "echo_veil_regent": {
    "id": "echo_veil_regent",
    "name": "Veil Regent",
    "site": "sealed_archive_bunker",
    "speaker": "Vera",
    "chapter": 4,
    "intro": "A fragmented Echo guards the sealed records. Its staff marks a fixed impact point before striking; stay out of its forward sweep. Preserve the archive and leave neutral residents alone.",
    "reward": [
      [
        "minecraft:amethyst_shard",
        10
      ],
      [
        "bearframe:legacy_cell",
        2
      ]
    ]
  },
  "echo_rubble_rook": {
    "id": "echo_rubble_rook",
    "name": "Rubble Rook",
    "site": "frontier_ruin",
    "speaker": "Sentinel",
    "chapter": 1,
    "intro": "Reports describe a hostile Echo moving through broken masonry. Its rush travels straight; its slam threatens the area immediately around it.",
    "reward": [
      [
        "minecraft:iron_ingot",
        12
      ],
      [
        "minecraft:emerald",
        4
      ]
    ]
  },
  "echo_hush_pendulum": {
    "id": "echo_hush_pendulum",
    "name": "Hush Pendulum",
    "site": "lost_waystation",
    "speaker": "Penney",
    "chapter": 2,
    "intro": "A hostile Echo interrupts the old shelter route with an irregular heavy swing. Move away from its marked impact and keep clear of the sweeping arc. The other residents are not part of this assignment.",
    "reward": [
      [
        "minecraft:emerald",
        5
      ],
      [
        "minecraft:cooked_beef",
        12
      ]
    ]
  }
};
export const BOSS_QUESTS=Object.values(BOSS_DOSSIERS).map(b=>({id:"hunt_"+b.id,title:"Expedition · "+b.name,speaker:b.speaker,chapter:b.chapter,requires:[],intro:b.intro+" This is optional. Open the route chart to find the habitat, then investigate an unclaimed site. Other expedition members can receive credit if they actively fight.",goals:[{key:"boss:"+b.id,label:"Defeat "+b.name,count:1}],report:"The encounter report for "+b.name+" is filed. The route remains available for future surveys.",reward:b.reward}));
export function bossSite(id){return BOSS_DOSSIERS[id]?.site;}
export function activeHunt(state,site){return Object.values(BOSS_DOSSIERS).some(b=>b.site===site&&state.side["hunt_"+b.id]===1&&!state.facts["boss:"+b.id]);}
export function creditIds(participants,killer,players,origin,dimension,radius=40){
 const ids=new Set(participants);if(killer)ids.add(killer);
 return players.filter(p=>ids.has(p.id)&&p.valid&&p.dimension===dimension&&Math.hypot(p.location.x-origin.x,p.location.y-origin.y,p.location.z-origin.z)<=radius).map(p=>p.id);
}
