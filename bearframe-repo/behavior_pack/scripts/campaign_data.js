import {BOSS_QUESTS} from "./boss_dossiers.js";
export const ARCHIVE_SITE_IDS=["relay_nine", "frontier_ruin", "crashed_skiff", "sealed_archive_bunker", "collapsed_transit_bunker", "rootbound_service_bunker", "flooded_pump_bunker", "overgrown_colony", "lost_waystation", "nivalis_lab", "shattered_array"];
const i=(key,count=1)=>[key.includes(":")?key:"minecraft:"+key,count];
const objective=(key,label,count=1)=>({key,label,count});
export const EVIDENCE={
  maintenance_relay:{name:"Maintenance Relay",biome:"Plains",text:"The final log shows a shelter reservation. The return column is blank. Someone kept renewing that reservation after the rest of the relay went quiet."},
  grid_hub:{name:"Overgrown Switchyard",biome:"Forest",text:"The walker reads an itinerary, not a combat order. It has been carrying an empty manifest between the same two switches for years."},
  echo_ward:{name:"Legacy Support Ward",biome:"Taiga",text:"A room inventory survives. The listed names and the names the resident remembers are different. The system accepted one list and refused the other."},
  intrusion_checkpoint:{name:"Directorate Checkpoint",biome:"Savanna",text:"A recent Directorate annotation sits over an older evacuation map. The patrol is looking for a dispatch key. It did not build this network."},
  foundry_annex:{name:"Ruined Foundry Annex",biome:"Desert",text:"The parts ledger lists service chassis and spare housings. The evacuation key was carried through here for repair, not manufactured here."},
  spillway_bunker:{name:"Spillway Facility",biome:"Forest",text:"Pump telemetry links the stay-on circuit to a dispatch carrier. As long as auxiliary power holds, the facility can answer a new route instruction."},
  shelter_bunker:{name:"Signal Shelter",biome:"Taiga",text:"Half the bunk logs ask for help. The other half ask to be left in peace. The old system filed both answers under waiting."},
  rainline_town:{name:"Rainline Works",biome:"Plains",text:"The shop record shows the old fleet was still moving after the streets emptied. A hand-drawn track leads away from the road."},
  saltline_town:{name:"Saltline Depot",biome:"Desert",text:"A cargo seal records an evacuation train. The last car was empty; the computer treated its empty seats as a failed departure."},
  relay_nine:{name:"Relay Nine",biome:"Taiga",text:"Recovered carrier fragment: CONTINUE UNTIL ALL RESERVATIONS CLEAR. It is an instruction for machinery, not consent from a resident."},
  frontier_ruin:{name:"Frontier Ruin",biome:"Forest",text:"A penciled arrow points away from the original muster point. The residents drew an alternate route before the official route failed."},
  crashed_skiff:{name:"Crashed Skiff",biome:"Plains",text:"The flight recorder identifies a civilian rescue crew. They changed course to reach a lower spillway entrance before the crash."},
  sealed_archive_bunker:{name:"Sealed Archive Bunker",biome:"Forest",text:"The archive separates public engineering routes from resident names. The emergency transmitter fused both feeds. A replacement instruction could keep those feeds apart."},
  collapsed_transit_bunker:{name:"Collapsed Transit Bunker",biome:"Hills",text:"The old track ends under the collapse. Reissuing the original route would send both the working machines and anyone following them into the blocked cut."},
  rootbound_service_bunker:{name:"Rootbound Service Bunker",biome:"Taiga",text:"A service notice identifies the compatible endpoint as the Spillway auxiliary pump. The bypass notice gives the bench order: Return, Intake, Carrier."},
  flooded_pump_bunker:{name:"Flooded Pump Bunker",biome:"Swamp",text:"The old route went through the submerged intake. The dry rim still carries a service lead that can be re-used on this circuit family."},
  overgrown_colony:{name:"Overgrown Colony",biome:"Forest",text:"The greenhouse ledger records which plots could feed a return crew. Seeds were left in an accessible cupboard."},
  lost_waystation:{name:"Lost Waystation",biome:"Jungle",text:"The shelter has been swept. Someone has moved the dry bedding under the surviving half of the canopy."},
  nivalis_lab:{name:"Nivalis Lab",biome:"Ice plains",text:"A thermal graph marks the moment the lab stopped getting transport requests. Its sample store stayed powered another winter."},
  shattered_array:{name:"Shattered Array",biome:"Hills",text:"Only a single emitter answers. Low-gain reception could preserve local control without restarting the entire route."},
};
export const MAIN=[
  {title:"I. A Light Left On",speaker:"Mira",intro:"Farfield heard a request to keep a bunk warm. The relay that sent it has been abandoned for longer than our survey charts go back. Read the relay in the plains and trace the same carrier at the Switchyard. Bring back what it says before anyone decides what it means.",goals:[objective("read:maintenance_relay","Read the Maintenance Relay lectern"),objective("read:grid_hub","Read the Overgrown Switchyard terminal")],report:"Auren: Two stations repeated it at the same interval. This is a working route loop. That tells us nothing about who wants to take it.",reward:[i("torch",10),i("compass")]},
  {title:"II. The Names on the Door",speaker:"Mira",intro:"An old roster is not an invitation. Visit the Support Ward. Ask a Ward Resident or Echo Drifter what the signal means to them. Come back with their own words before you open any record beyond that room.",goals:[objective("read:echo_ward","Inspect the Support Ward terminal"),objective("talk:echo","Hear testimony from an Echo")],report:"Mira: They remember being promised a room, not being ordered aboard. That distinction belongs in every version of this report.",reward:[i("iron_ingot",4),i("cooked_beef",4)]},
  {title:"III. The Wrong Recovery",speaker:"Sentinel",intro:"The Directorate has a current field annotation at its checkpoint. Compare it with the legacy carrier at Relay Nine. If someone is seeking a dispatch key, we need to know what that key would actually do.",goals:[objective("read:intrusion_checkpoint","Read the Directorate Checkpoint terminal"),objective("read:relay_nine","Read the Relay Nine field archive")],report:"Sentinel: The checkpoint is an expedition post. The old network is not theirs. They could still activate it if they find an intact route.",reward:[i("iron_ingot",5),i("shield")]},
  {title:"IV. A Route That Goes Nowhere",speaker:"Atlas",intro:"Follow the bypass from a crash recorder or a submerged pump survey. Then check where the rail actually ends. Verify the Foundry Annex has power, so we have somewhere to test a local circuit before changing the dispatch.",goals:[objective("survey:bypass","Read the Crashed Skiff or Flooded Pump Bunker archive"),objective("read:collapsed_transit_bunker","Inspect the collapsed track report"),objective("repair:foundry_annex","Restore or verify the Foundry Annex circuit")],report:"Atlas: The old route ends under rubble. We can send a new instruction, but run it on the Spillway test bench in this order: Return, Intake, Carrier.",reward:[i("copper_ingot",6),i("redstone",6)]},
  {title:"V. What Stays Private",speaker:"Vera",intro:"The archive bunker has the engineering map and the resident ledger on separate channels. Bring back the archive index and compare it with a shelter log or service bunker record. We can isolate either channel, but the people in those rooms need an answer before we transmit.",goals:[objective("read:sealed_archive_bunker","Read the Sealed Archive Bunker registry"),objective("survey:shelter","Read Signal Shelter or Rootbound Service Bunker")],report:"Vera: We can publish only the engineering route, or leave the transmitter local and hand the maintenance work to the residents. The names stay private either way.",reward:[i("bearframe:salvaged_alloy",3),i("gold_ingot",3)]},
  {title:"VI. The Last Dispatch",speaker:"Auren",intro:"The Spillway auxiliary pump is the last reachable endpoint. Take two redstone. Restore it at the auxiliary pump. Beyond the stores, use the three test-bench consoles in Atlas’s order: Return, Intake, Carrier.",goals:[objective("read:spillway_bunker","Reach the Spillway auxiliary pump"),objective("repair:spillway_bunker","Restore or verify the Spillway pump circuit"),objective("calibrated:spillway","Calibrate the three consoles beyond the stores")],report:"Auren: We have a stable carrier. Choose what Farfield puts on it.",choice:true,reward:[i("diamond",1),i("bearframe:legacy_cell",2)]},
  {title:"VII. An Address, Not an Order",speaker:"Mira",intro:"Bring the outcome back to an Echo, and confirm that the Switchyard circuit still answers. Then return to the station. The report is only finished once someone outside Bearframe has heard what we did.",goals:[objective("after:echo","Speak to an Echo after choosing the dispatch policy"),objective("repair:grid_hub","Restore or verify the Switchyard after the dispatch")],report:"Mira: The places on our map belong to the people and machines still using them. We can leave a route open without deciding who has to take it.",reward:[i("bearframe:farfield_insignia"),i("emerald",5)]},
];
export const SIDES=[
  {id:"sleep",title:"Somewhere to Sleep",speaker:"Penney",intro:"Check the old shelter and listen to an Echo. Find out which rooms people still use so the next expedition knows where to knock.",goals:[objective("read:shelter_bunker","Examine Signal Shelter"),objective("talk:echo","Speak with an Echo")],report:"Penney: A shelter can be occupied without looking occupied. I'll put that on the visitor briefing.",reward:[i("bread",6),i("emerald",2)]},
  {id:"grow",title:"The Greenhouse Ledger",speaker:"Penney",intro:"Compare the garden ledger in the Overgrown Colony with the shelter record at the Lost Waystation. I want to know what can actually sustain a crew out there.",goals:[objective("read:overgrown_colony","Read the colony archive"),objective("read:lost_waystation","Read the waystation archive")],report:"Penney: We'll bring seed and dry bedding on the next run. A route is worth more if somebody can rest along it.",reward:[i("melon_seeds",5),i("bone_meal",8),i("emerald",2)]},
  {id:"metal",title:"Hands That Still Work",speaker:"Atlas",intro:"Power both the Foundry Annex and Rainline Works. The maintenance units can use the sites even when no expedition is around.",goals:[objective("repair:foundry_annex","Verify Foundry power"),objective("repair:rainline_town","Verify Rainline workshop power")],report:"Atlas: Good. Both benches can be used again. Here, take some stock for your own.",reward:[i("iron_ingot",7),i("bearframe:salvaged_alloy",2)]},
  {id:"prints",title:"Marks Under the Paint",speaker:"Vera",intro:"The Frontier Ruin was marked by hand. The Nivalis Lab was labeled by machine. Recover both archives so I can preserve the difference.",goals:[objective("read:frontier_ruin","Read the Frontier Ruin record"),objective("read:nivalis_lab","Read the Nivalis Lab record")],report:"Vera: One of these records was written for a reader. The other was written by someone who hoped there would still be a reader.",reward:[i("amethyst_shard",6),i("glow_ink_sac",3)]},
  {id:"watch",title:"A Short Patrol",speaker:"Sentinel",intro:"Verify the Directorate's current checkpoint and clear two hostile Nullframe Directorate units that threaten the field routes.",goals:[objective("read:intrusion_checkpoint","Log the Directorate checkpoint"),objective("kill:directorate","Defeat hostile Nullframe units",2)],report:"Sentinel: Logged. We'll keep the routes watched. Nobody needs a standing occupation out there.",reward:[i("arrow",20),i("iron_ingot",3)]},
  {id:"carrier",title:"Cold Carrier",speaker:"Auren",intro:"Compare the signal at the Shattered Array to Relay Nine. The output should be different if the array is running locally.",goals:[objective("read:shattered_array","Read the Shattered Array"),objective("read:relay_nine","Read Relay Nine")],report:"Auren: The carrier agrees. The array can be useful even if it never rejoins the old network.",reward:[i("redstone",8),i("bearframe:legacy_cell")]},
];
export const CONTRACTS=[
 {id:"charts",title:"Fresh Route Survey",speaker:"Mira",text:"Log three distinct field terminals or archives after accepting. A completed site can be revisited on another commission.",key:"field",count:3,reward:[i("emerald",3),i("torch",8)]},
 {id:"power",title:"Maintenance Circuit",speaker:"Atlas",text:"Verify power at two distinct repaired facilities after accepting. Existing repairs count when you inspect them.",key:"circuit",count:2,reward:[i("iron_ingot",4),i("copper_ingot",4)]},
 {id:"hostiles",title:"Clear the Approach",speaker:"Sentinel",text:"Defeat three hostile Nullframe Directorate units on the surface after accepting. Echo Frames and Ghost Grid units are recorded separately.",key:"defeat",count:3,reward:[i("arrow",16),i("emerald",3)]},
];

// Preserve all legacy IDs and main chapter indices.
export const RPG_SIDES=[
  {
    "id": "mira_bearings",
    "title": "The Unmarked Bearing",
    "speaker": "Mira",
    "chapter": 0,
    "requires": [],
    "intro": "The old route is not the only way through. Compare the handwritten detour with Rainline's surviving records.",
    "goals": [
      {
        "key": "read:frontier_ruin",
        "label": "Read the hand-marked detour",
        "count": 1
      },
      {
        "key": "read:rainline_town",
        "label": "Read the workshop record",
        "count": 1
      }
    ],
    "delivery": [],
    "report": "A useful bearing is one someone can actually follow.",
    "reward": [
      [
        "minecraft:paper",
        8
      ],
      [
        "minecraft:compass",
        1
      ]
    ]
  },
  {
    "id": "mira_manifest",
    "title": "An Empty Seat",
    "speaker": "Mira",
    "chapter": 1,
    "requires": [
      "mira_bearings"
    ],
    "intro": "The old system treated empty seats as failed departures. Compare the cargo seal with the civilian rescue recorder.",
    "goals": [
      {
        "key": "read:saltline_town",
        "label": "Read the cargo seal",
        "count": 1
      },
      {
        "key": "read:crashed_skiff",
        "label": "Inspect the rescue recorder",
        "count": 1
      }
    ],
    "delivery": [],
    "report": "A missing passenger is not automatically a missing person.",
    "reward": [
      [
        "minecraft:bread",
        6
      ],
      [
        "minecraft:iron_ingot",
        3
      ]
    ]
  },
  {
    "id": "mira_detour",
    "title": "A Survey Worth Returning From",
    "speaker": "Mira",
    "chapter": 3,
    "requires": [
      "mira_manifest"
    ],
    "intro": "Check the collapsed railway and submerged bypass. Bring paper for a field copy.",
    "goals": [
      {
        "key": "read:collapsed_transit_bunker",
        "label": "Verify the blocked rail",
        "count": 1
      },
      {
        "key": "read:flooded_pump_bunker",
        "label": "Read the intake bypass",
        "count": 1
      }
    ],
    "delivery": [
      [
        "minecraft:paper",
        6
      ]
    ],
    "report": "A practical detour, not a line through a mountain.",
    "reward": [
      [
        "minecraft:emerald",
        3
      ],
      [
        "minecraft:torch",
        12
      ]
    ]
  },
  {
    "id": "mira_routes",
    "title": "The Route We Leave Behind",
    "speaker": "Mira",
    "chapter": 6,
    "requires": [
      "mira_detour"
    ],
    "intro": "Compare the shelter and alternate carrier. Choose the expedition's next supply package.",
    "goals": [
      {
        "key": "read:shelter_bunker",
        "label": "Read the shelter record",
        "count": 1
      },
      {
        "key": "read:shattered_array",
        "label": "Inspect the local carrier",
        "count": 1
      }
    ],
    "delivery": [],
    "report": "The survey is filed. The recorded sites remain available.",
    "reward": [
      [
        "minecraft:emerald",
        4
      ]
    ],
    "outcomes": [
      {
        "id": "shelter",
        "label": "Prioritize shelter supplies",
        "report": "The rest points come first.",
        "reward": [
          [
            "minecraft:bread",
            12
          ],
          [
            "minecraft:torch",
            8
          ]
        ]
      },
      {
        "id": "survey",
        "label": "Prioritize survey equipment",
        "report": "We will document the entrances.",
        "reward": [
          [
            "minecraft:paper",
            16
          ],
          [
            "minecraft:compass",
            1
          ]
        ]
      }
    ]
  },
  {
    "id": "atlas_stock",
    "title": "Stock for the Bench",
    "speaker": "Atlas",
    "chapter": 0,
    "requires": [],
    "intro": "A wrench is useless with an empty parts bin. Bring copper and redstone to the expedition workshop.",
    "goals": [],
    "delivery": [
      [
        "minecraft:copper_ingot",
        6
      ],
      [
        "minecraft:redstone",
        4
      ]
    ],
    "report": "Sorted, labeled, usable.",
    "reward": [
      [
        "minecraft:iron_ingot",
        4
      ],
      [
        "minecraft:torch",
        8
      ]
    ]
  },
  {
    "id": "atlas_relay",
    "title": "A Circuit That Holds",
    "speaker": "Atlas",
    "chapter": 1,
    "requires": [
      "atlas_stock"
    ],
    "intro": "Verify the relay and Switchyard. I need working endpoints, not a picture of a panel.",
    "goals": [
      {
        "key": "repair:maintenance_relay",
        "label": "Verify relay power",
        "count": 1
      },
      {
        "key": "repair:grid_hub",
        "label": "Verify Switchyard power",
        "count": 1
      }
    ],
    "delivery": [],
    "report": "Both ends answer. Good.",
    "reward": [
      [
        "minecraft:redstone",
        8
      ],
      [
        "bearframe:salvaged_alloy",
        1
      ]
    ]
  },
  {
    "id": "atlas_workshops",
    "title": "Borrowed Workbenches",
    "speaker": "Atlas",
    "chapter": 3,
    "requires": [
      "atlas_relay"
    ],
    "intro": "Verify both workshops. Deliver replacement iron brackets without stripping your own base.",
    "goals": [
      {
        "key": "repair:foundry_annex",
        "label": "Verify Annex power",
        "count": 1
      },
      {
        "key": "repair:rainline_town",
        "label": "Verify Rainline power",
        "count": 1
      }
    ],
    "delivery": [
      [
        "minecraft:iron_ingot",
        4
      ]
    ],
    "report": "Those benches belong to the crews using them.",
    "reward": [
      [
        "bearframe:salvaged_alloy",
        3
      ],
      [
        "minecraft:copper_ingot",
        6
      ]
    ]
  },
  {
    "id": "atlas_spares",
    "title": "A Repair That Lasts",
    "speaker": "Atlas",
    "chapter": 5,
    "requires": [
      "atlas_workshops"
    ],
    "intro": "Compare the rootbound instructions and auxiliary pump. Choose the next spare-parts package.",
    "goals": [
      {
        "key": "read:rootbound_service_bunker",
        "label": "Recover service instructions",
        "count": 1
      },
      {
        "key": "repair:spillway_bunker",
        "label": "Verify the auxiliary pump",
        "count": 1
      }
    ],
    "delivery": [],
    "report": "Keep the circuit accessible.",
    "reward": [
      [
        "bearframe:legacy_cell",
        1
      ]
    ],
    "outcomes": [
      {
        "id": "electrical",
        "label": "Electrical spares",
        "report": "Copper and redstone, ready to go.",
        "reward": [
          [
            "minecraft:redstone",
            12
          ],
          [
            "minecraft:copper_ingot",
            8
          ]
        ]
      },
      {
        "id": "structural",
        "label": "Mechanical spares",
        "report": "Brackets and housings. Built to last.",
        "reward": [
          [
            "minecraft:iron_ingot",
            8
          ],
          [
            "bearframe:salvaged_alloy",
            2
          ]
        ]
      }
    ]
  },
  {
    "id": "vera_marks",
    "title": "Signs of a Reader",
    "speaker": "Vera",
    "chapter": 0,
    "requires": [],
    "intro": "Compare the informal markings at the Frontier Ruin with the relay's formal log.",
    "goals": [
      {
        "key": "read:frontier_ruin",
        "label": "Read informal markings",
        "count": 1
      },
      {
        "key": "read:maintenance_relay",
        "label": "Read the relay log",
        "count": 1
      }
    ],
    "delivery": [],
    "report": "One was written for a machine; one for a reader who might never arrive.",
    "reward": [
      [
        "minecraft:paper",
        8
      ],
      [
        "minecraft:glow_ink_sac",
        2
      ]
    ]
  },
  {
    "id": "vera_records",
    "title": "A Record Without a Name",
    "speaker": "Vera",
    "chapter": 2,
    "requires": [
      "vera_marks"
    ],
    "intro": "Inspect Relay Nine and the ward roster. A registry is not a complete account of its residents.",
    "goals": [
      {
        "key": "read:relay_nine",
        "label": "Read carrier fragment",
        "count": 1
      },
      {
        "key": "read:echo_ward",
        "label": "Read ward record",
        "count": 1
      }
    ],
    "delivery": [],
    "report": "Preserve the record without treating its errors as facts.",
    "reward": [
      [
        "minecraft:amethyst_shard",
        4
      ],
      [
        "minecraft:paper",
        6
      ]
    ]
  },
  {
    "id": "vera_index",
    "title": "The Sealed Index",
    "speaker": "Vera",
    "chapter": 4,
    "requires": [
      "vera_records"
    ],
    "intro": "Compare the archive and Nivalis thermal record. Bring clean paper for an engineering-only index.",
    "goals": [
      {
        "key": "read:sealed_archive_bunker",
        "label": "Inspect sealed registry",
        "count": 1
      },
      {
        "key": "read:nivalis_lab",
        "label": "Recover thermal record",
        "count": 1
      }
    ],
    "delivery": [
      [
        "minecraft:paper",
        8
      ]
    ],
    "report": "No resident names were copied into the route sheet.",
    "reward": [
      [
        "minecraft:emerald",
        3
      ],
      [
        "minecraft:glow_ink_sac",
        3
      ]
    ]
  },
  {
    "id": "vera_archive",
    "title": "What a Map Cannot Say",
    "speaker": "Vera",
    "chapter": 6,
    "requires": [
      "vera_index"
    ],
    "intro": "Compare the greenhouse ledger and the Array's machine report. Choose how to present the engineering-only archive.",
    "goals": [
      {
        "key": "read:overgrown_colony",
        "label": "Read greenhouse ledger",
        "count": 1
      },
      {
        "key": "read:shattered_array",
        "label": "Inspect emitter status",
        "count": 1
      }
    ],
    "delivery": [],
    "report": "Both accounts are preserved.",
    "reward": [
      [
        "minecraft:amethyst_shard",
        6
      ]
    ],
    "outcomes": [
      {
        "id": "field",
        "label": "Field-readable notes",
        "report": "Clear marks, nothing unnecessary.",
        "reward": [
          [
            "minecraft:paper",
            16
          ],
          [
            "minecraft:glow_ink_sac",
            4
          ]
        ]
      },
      {
        "id": "technical",
        "label": "Technical index",
        "report": "Measurements and annotations kept separate.",
        "reward": [
          [
            "minecraft:redstone",
            10
          ],
          [
            "minecraft:amethyst_shard",
            4
          ]
        ]
      }
    ]
  },
  {
    "id": "sentinel_trace",
    "title": "Signs of a Patrol",
    "speaker": "Sentinel",
    "chapter": 1,
    "requires": [],
    "intro": "Read the checkpoint. Clear two hostile units threatening the surface routes. Neutral Echoes and maintenance machines are not targets.",
    "goals": [
      {
        "key": "read:intrusion_checkpoint",
        "label": "Inspect current checkpoint",
        "count": 1
      },
      {
        "key": "kill:directorate",
        "label": "Defeat hostile Nullframe Directorate units after accepting",
        "count": 2
      }
    ],
    "delivery": [],
    "report": "Keep the distinction between threats and residents.",
    "reward": [
      [
        "minecraft:arrow",
        16
      ],
      [
        "minecraft:iron_ingot",
        3
      ]
    ]
  },
  {
    "id": "sentinel_detour",
    "title": "A Safe Approach",
    "speaker": "Sentinel",
    "chapter": 2,
    "requires": [
      "sentinel_trace"
    ],
    "intro": "Compare Relay Nine and the rescue recorder. Clear three more hostile Directorate units.",
    "goals": [
      {
        "key": "read:relay_nine",
        "label": "Inspect Relay Nine",
        "count": 1
      },
      {
        "key": "read:crashed_skiff",
        "label": "Inspect rescue route",
        "count": 1
      },
      {
        "key": "kill:directorate",
        "label": "Defeat hostile Nullframe Directorate units after accepting",
        "count": 3
      }
    ],
    "delivery": [],
    "report": "A cleared route is not permanent security.",
    "reward": [
      [
        "minecraft:arrow",
        24
      ],
      [
        "minecraft:cooked_beef",
        6
      ]
    ]
  },
  {
    "id": "sentinel_supply",
    "title": "Field Watch Resupply",
    "speaker": "Sentinel",
    "chapter": 3,
    "requires": [
      "sentinel_detour"
    ],
    "intro": "Bring iron and torches for routine patrol equipment. Confirm the checkpoint record.",
    "goals": [
      {
        "key": "read:intrusion_checkpoint",
        "label": "Confirm checkpoint record",
        "count": 1
      }
    ],
    "delivery": [
      [
        "minecraft:iron_ingot",
        5
      ],
      [
        "minecraft:torch",
        8
      ]
    ],
    "report": "Small patrols. Short reports. No occupation.",
    "reward": [
      [
        "minecraft:emerald",
        4
      ],
      [
        "minecraft:arrow",
        16
      ]
    ]
  },
  {
    "id": "sentinel_watch",
    "title": "A Watch Without an Occupation",
    "speaker": "Sentinel",
    "chapter": 6,
    "requires": [
      "sentinel_supply"
    ],
    "intro": "Inspect the blocked route and local signal. Clear four hostile units. Recommend a patrol support package.",
    "goals": [
      {
        "key": "read:collapsed_transit_bunker",
        "label": "Inspect blocked route",
        "count": 1
      },
      {
        "key": "read:shattered_array",
        "label": "Inspect local signal",
        "count": 1
      },
      {
        "key": "kill:directorate",
        "label": "Defeat hostile Nullframe Directorate units after accepting",
        "count": 4
      }
    ],
    "delivery": [],
    "report": "Watchtower will monitor the route, not claim settlements.",
    "reward": [
      [
        "minecraft:emerald",
        5
      ]
    ],
    "outcomes": [
      {
        "id": "observation",
        "label": "Observation supplies",
        "report": "Contact before escalation.",
        "reward": [
          [
            "minecraft:torch",
            24
          ],
          [
            "minecraft:paper",
            8
          ]
        ]
      },
      {
        "id": "defense",
        "label": "Defensive supplies",
        "report": "Equip patrols for confirmed hostiles.",
        "reward": [
          [
            "minecraft:arrow",
            32
          ],
          [
            "minecraft:iron_ingot",
            6
          ]
        ]
      }
    ]
  },
  {
    "id": "penney_lamps",
    "title": "A Lamp in the Window",
    "speaker": "Penney",
    "chapter": 0,
    "requires": [],
    "intro": "A shelter needs light and food before another expedition arrives. Bring bread and torches to the Commons.",
    "goals": [],
    "delivery": [
      [
        "minecraft:bread",
        6
      ],
      [
        "minecraft:torch",
        8
      ]
    ],
    "report": "We can ask before we offer.",
    "reward": [
      [
        "minecraft:emerald",
        2
      ],
      [
        "minecraft:cooked_beef",
        4
      ]
    ]
  },
  {
    "id": "penney_rooms",
    "title": "Rooms Still in Use",
    "speaker": "Penney",
    "chapter": 1,
    "requires": [
      "penney_lamps"
    ],
    "intro": "Listen to an Echo and inspect the ward. The room inventory isn't permission to enter.",
    "goals": [
      {
        "key": "talk:echo",
        "label": "Listen to an Echo resident",
        "count": 1
      },
      {
        "key": "read:echo_ward",
        "label": "Inspect ward record",
        "count": 1
      }
    ],
    "delivery": [],
    "report": "I'll mark the briefing as a request to ask, not an instruction to search.",
    "reward": [
      [
        "minecraft:bread",
        8
      ],
      [
        "minecraft:emerald",
        2
      ]
    ]
  },
  {
    "id": "penney_garden",
    "title": "Enough for Tomorrow",
    "speaker": "Penney",
    "chapter": 3,
    "requires": [
      "penney_rooms"
    ],
    "intro": "Inspect the colony and waystation records. Bring wheat and seeds for anyone who wants a garden.",
    "goals": [
      {
        "key": "read:overgrown_colony",
        "label": "Read greenhouse ledger",
        "count": 1
      },
      {
        "key": "read:lost_waystation",
        "label": "Read shelter record",
        "count": 1
      }
    ],
    "delivery": [
      [
        "minecraft:wheat",
        8
      ],
      [
        "minecraft:wheat_seeds",
        8
      ]
    ],
    "report": "A little food and a way to grow more.",
    "reward": [
      [
        "minecraft:bone_meal",
        12
      ],
      [
        "minecraft:carrot",
        6
      ],
      [
        "minecraft:emerald",
        2
      ]
    ]
  },
  {
    "id": "penney_welcome",
    "title": "A Place to Stop",
    "speaker": "Penney",
    "chapter": 6,
    "requires": [
      "penney_garden"
    ],
    "intro": "Read the shelter and Saltline logs. Help choose the next care package. Nobody is required to travel.",
    "goals": [
      {
        "key": "read:shelter_bunker",
        "label": "Read shelter log",
        "count": 1
      },
      {
        "key": "read:saltline_town",
        "label": "Read empty-car record",
        "count": 1
      }
    ],
    "delivery": [],
    "report": "A standing offer of help, not a list of people to collect.",
    "reward": [
      [
        "minecraft:emerald",
        4
      ]
    ],
    "outcomes": [
      {
        "id": "food",
        "label": "Food for residents",
        "report": "For those who choose to stay.",
        "reward": [
          [
            "minecraft:bread",
            16
          ],
          [
            "minecraft:carrot",
            8
          ]
        ]
      },
      {
        "id": "travel",
        "label": "Traveler supplies",
        "report": "For those who leave on their own terms.",
        "reward": [
          [
            "minecraft:cooked_beef",
            10
          ],
          [
            "minecraft:torch",
            16
          ]
        ]
      }
    ]
  },
  {
    "id": "auren_paper",
    "title": "Before the Signal",
    "speaker": "Auren",
    "chapter": 0,
    "requires": [],
    "intro": "Bring paper for a briefing packet and compare both signal endpoints.",
    "goals": [
      {
        "key": "read:maintenance_relay",
        "label": "Read first relay",
        "count": 1
      },
      {
        "key": "read:grid_hub",
        "label": "Read route loop",
        "count": 1
      }
    ],
    "delivery": [
      [
        "minecraft:paper",
        4
      ]
    ],
    "report": "A signal is evidence, not an order.",
    "reward": [
      [
        "minecraft:emerald",
        2
      ],
      [
        "minecraft:redstone",
        4
      ]
    ]
  },
  {
    "id": "auren_conflict",
    "title": "Two Accounts of One Route",
    "speaker": "Auren",
    "chapter": 2,
    "requires": [
      "auren_paper"
    ],
    "intro": "Compare the ward record and Directorate annotation without assuming either is the original authority.",
    "goals": [
      {
        "key": "read:echo_ward",
        "label": "Review ward record",
        "count": 1
      },
      {
        "key": "read:intrusion_checkpoint",
        "label": "Review current annotation",
        "count": 1
      }
    ],
    "delivery": [],
    "report": "The old network predates the current conflict.",
    "reward": [
      [
        "minecraft:iron_ingot",
        4
      ],
      [
        "minecraft:paper",
        8
      ]
    ]
  },
  {
    "id": "auren_endpoints",
    "title": "An Endpoint, Not a Promise",
    "speaker": "Auren",
    "chapter": 4,
    "requires": [
      "auren_conflict"
    ],
    "intro": "Inspect compatible service instructions and the local carrier. Verify the Foundry test circuit.",
    "goals": [
      {
        "key": "read:rootbound_service_bunker",
        "label": "Read service instructions",
        "count": 1
      },
      {
        "key": "read:shattered_array",
        "label": "Inspect local carrier",
        "count": 1
      },
      {
        "key": "repair:foundry_annex",
        "label": "Verify Foundry power",
        "count": 1
      }
    ],
    "delivery": [],
    "report": "We have alternatives to restarting the whole network.",
    "reward": [
      [
        "minecraft:redstone",
        8
      ],
      [
        "bearframe:legacy_cell",
        1
      ]
    ]
  },
  {
    "id": "auren_followup",
    "title": "After the Dispatch",
    "speaker": "Auren",
    "chapter": 7,
    "requires": [
      "auren_endpoints"
    ],
    "intro": "Verify the Switchyard and speak to an Echo after the dispatch. Recommend the station's next support package.",
    "goals": [
      {
        "key": "after:echo",
        "label": "Speak to an Echo after the dispatch",
        "count": 1
      },
      {
        "key": "repair:grid_hub",
        "label": "Verify Switchyard circuit",
        "count": 1
      }
    ],
    "delivery": [],
    "report": "The people affected still decide what they need.",
    "reward": [
      [
        "minecraft:emerald",
        5
      ]
    ],
    "outcomes": [
      {
        "id": "maintenance",
        "label": "Maintenance assistance",
        "report": "Keep local infrastructure repairable.",
        "reward": [
          [
            "bearframe:salvaged_alloy",
            3
          ],
          [
            "minecraft:redstone",
            8
          ]
        ]
      },
      {
        "id": "expedition",
        "label": "Expedition assistance",
        "report": "Keep routes documented and supplies available.",
        "reward": [
          [
            "minecraft:torch",
            16
          ],
          [
            "minecraft:paper",
            12
          ]
        ]
      }
    ]
  }
];
SIDES.push(...RPG_SIDES);

SIDES.push(...BOSS_QUESTS);
