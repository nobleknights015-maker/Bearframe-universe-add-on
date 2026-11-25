import {fieldInteraction} from "./ecology.js";
import {campaignSignal} from "./campaign.js";
import {ItemStack,system,world} from "@minecraft/server";
import {ORBIT} from "./regions.js";

const directorateCadres = new Set(["bearframe:directorate_officer","bearframe:directorate_guard"]);

const SCAN_DB={
  "bearframe:field_researcher":{
    tag:"Bearframe · Farfield Instrument Research",
    note:"Sentient Farfield specialist. Records environmental readings and clears samples for transport."
  },
  "bearframe:directorate_guard":{
    tag:"Directorate · Gate Guard",
    note:"A thinking perimeter guard bound by checkpoint directives. Will challenge strangers before escalating."
  },
  "bearframe:hollow_line":{
    tag:"Directorate · Hollow Line Drone",
    note:"Standardized infantry chassis. The broad forearm housing identifies its coordinated line role."
  },
  "bearframe:grid_repair_crawler":{
    tag:"Unverified Legacy Machine · Repair Crawler",
    note:"Low underdeck chassis with two probe arms. Avoids fighting and checks for corroded contacts."
  },
  "bearframe:grid_protocol_keeper":{
    tag:"Unverified Legacy Machine · Protocol Keeper",
    note:"A walking legacy custodian that polls obsolete site permissions. It has no recognized faction signature."
  },
  "bearframe:farfield_surveyor":{
    tag:"Bearframe · Exploration (Farfield)",
    note:"Individually sentient Bearframe assigned to Mira's independent Exploration Dept. Chest & side-head displays nominal."
  },
  "bearframe:city_steward":{
    tag:"Bearframe · Community & Culture",
    note:"Sentient Community staff under Penney. Supports shared spaces and resident welfare across continuous station shifts."
  },
  "bearframe:city_engineer":{
    tag:"Bearframe · Systems & Engineering",
    note:"Sentient systems specialist under Auren. Monitors station power, thermal loops, and diagnostic stability."
  },
  "bearframe:city_watch":{
    tag:"Bearframe · Watchtower",
    note:"Independent security & law enforcement officer under Sentinel. Motto: Different department. Same objective."
  },
  "bearframe:atlas_rigger":{
    tag:"Bearframe · Atlas Production/Maintenance",
    note:"Heavy-build sentient Frame in Atlas's department. Reinforced chassis configured for industrial lifting and salvage reclamation."
  },
  "bearframe:atlas_vanguard":{
    tag:"Bearframe · Atlas Combat Division",
    note:"Dedicated defense Frame from Atlas's 35-unit combat division. Coordinates with Watchtower without merging command."
  },
  "bearframe:vera_artisan":{
    tag:"Bearframe · Visual Production",
    note:"Sentient visual specialist under Vera. Maintains display legibility, architectural clarity, and visual standards."
  },
  "bearframe:hollow_scout":{
    tag:"Nullframe Directorate · Hollow Drone",
    note:"Mass-produced limited-AI reconnaissance drone from a Directorate Hollow Foundry. Standardized behavioral directives; no free sentience."
  },
  "bearframe:hollow_breacher":{
    tag:"Nullframe Directorate · Hollow Breacher",
    note:"Heavy standardized assault Hollow drone. High armor plating and kinetic gauntlets; slow approach with heavy melee impact."
  },
  "bearframe:directorate_officer":{
    tag:"Nullframe Directorate · Thinking AI Cadre",
    note:"Advanced restricted-AI Directorate specialist. Capable of reasoning and verbal warnings, but bound by Directorate command constraints."
  },
  "bearframe:nullframe_hunter":{
    tag:"Nullframe Hunters · Watchtower Defector Lineage",
    note:"High-threat pursuit specialist descended from former Watchtower personnel. Independent tactical judgment—not a Hollow drone."
  },
  "bearframe:ward_resident":{
    tag:"Echo Frame · Residual / Repeat Presentation",
    note:"Ancient non-Bearframe synthetic person with disrupted memory continuity. Treat with care and consent—do not overwrite core records."
  },
  "bearframe:echo_drifter":{
    tag:"Echo Frame · Drift / Fragment Presentation",
    note:"Ancient patched legacy synthetic wanderer. Disjointed autobiographical index; generally peaceful unless threatened."
  },
  "bearframe:echo_sentinel":{
    tag:"Echo Frame · Split / Corrupt Presentation",
    note:"Archaic security-chassis Echo with unstable power bus. Nonviolent stabilization possible with Copper, Redstone, or a Legacy Cell."
  },
  "bearframe:grid_walker":{
    tag:"Unverified Legacy Machine · Hexapod Maintenance",
    note:"Articulated six-legged autonomous repair robot of pre-Bearframe industrial stratum. Origin unresolved in Bearframe archives."
  },
  "bearframe:grid_watcher":{
    tag:"Unverified Legacy Machine · Hovering Recon Drone",
    note:"Autonomous anti-grav survey probe obeying obsolete perimeter routines. Observational unless provoked."
  },
  "bearframe:grid_turret":{
    tag:"Unverified Legacy Machine · Automated Defense Turret",
    note:"Stationary tripod rail emitter enforcing outdated zone access protocols. Use cover between charging volleys."
  },
  "bearframe:grid_hauler":{
    tag:"Unverified Legacy Machine · Tracked Salvage Hauler",
    note:"Heavy tracked industrial utility carrier still hauling scrap across abandoned yards. Passive unless struck."
  },
  "bearframe:grid_guardian":{
    tag:"Unverified Legacy Machine · Heavy Sector Guardian",
    note:"Massive autonomous industrial protector. Dormant while undisturbed; extreme melee threat if provoked."
  }
};

const DIALOGUES={
  "bearframe:field_researcher":[
    "I run the instruments while the surveyor maps the route. The next sampling site is still unverified.",
    "The intake residue is older than the casing. I recorded both so we don't mistake a later repair for the original build."
  ],
  "bearframe:grid_repair_crawler":[
    "Twin probes sweep the floor seam. The unit backs away, checks its reading, and continues."
  ],
  "bearframe:grid_protocol_keeper":[
    "The mast rotates. A legacy status display prompts for an obsolete clearance token, then returns to standby."
  ],
  "bearframe:atlas_rigger":[
    "Atlas's crews reclaim everything worth keeping. Sneak-interact with 2 Salvaged Chassis Alloy to refine iron and copper.",
    "Heavy chassis isn't for show—someone has to lift conduit girders when the cranes stall.",
    "Remember: Foundry builds the hardware, but only the Founder prepares a new sentience chip."
  ],
  "bearframe:atlas_vanguard":[
    "Perimeter looks steady. Keep your distance from Hollow patrols unless you're geared up.",
    "We answer to Atlas, Watchtower answers to Sentinel—same city to protect either way."
  ],
  "bearframe:vera_artisan":[
    "Clean silhouettes, legible lighting, zero sloppy seams. Vera doesn't approve unfinished work.",
    "Every Bearframe keeps their department color and fixed core display—everything else is personal craft."
  ],
  "bearframe:city_watch":[
    "Watchtower tracks anomalies across the orbit and surface. Different department, same objective.",
    "If you spot Hunters out there, don't treat them like ordinary Hollows. They still know our old playbooks."
  ],
  "bearframe:echo_drifter":[
    "Conduit seven... no, that corridor collapsed. Wait—you're new. Sneak-interact with 2 copper ingots if you want to trade for a legacy cell.",
    "Parts keep changing. Left knee isn't mine anymore. Still remember how to check a fuse box, though.",
    "Don't wake the big machines if you don't have to. They only know their old schedules."
  ],
  "bearframe:grid_walker":[
    "The six-legged maintenance unit taps a corroded pipe joint, emits a cyan pulse, and resumes its obsolete circuit.",
    "Diagnostic markings predate Bearframe records. Its chassis is weathered, with moss anchored cleanly to the upper plates."
  ],
  "bearframe:grid_watcher":[
    "The hovering probe tilts its cyan optical lens toward you, logs an unrecognized signature, and holds altitude.",
    "Soft thruster hum. It appears to be running an old perimeter census rather than an attack script."
  ],
  "bearframe:grid_hauler":[
    "The tracked industrial hauler pauses its crane arm as you pass. Its cargo rack holds oxidized conduits from an unknown era.",
    "Heavy treads rumble on standby. No modern Bearframe or Directorate markings are visible."
  ],
  "bearframe:grid_guardian":[
    "The towering legacy machine tracks your movement with a low hydraulic hum, holding defensive standby while unprovoked.",
    "Ancient armor plates and cyan reactor vents—its directives outlived whoever built this yard."
  ]
};

const pick=(arr,seed)=>arr[Math.abs(seed)%arr.length];
const distSq=(a,b)=>(a.x-b.x)**2+(a.y-b.y)**2+(a.z-b.z)**2;
const say=(player,prefix,text)=>player.sendMessage(`${prefix}§r ${text}`);

function heldItem(player){
  const inv=player.getComponent("minecraft:inventory")?.container;
  return inv?.getItem(player.selectedSlotIndex);
}

export function escalateNearbyDirectorate(dim,origin,radius=14){
  const officers=dim.getEntities({location:origin,maxDistance:radius}).filter(entity=>directorateCadres.has(entity.typeId));
  for(const officer of officers){
    if(officer.getDynamicProperty("bearframe:escalated"))continue;
    officer.setDynamicProperty("bearframe:escalated",true);
    try{officer.triggerEvent("bearframe:escalate");}catch{}
  }
}

export function installLivingWorld({validPlayer,spend,attempt}){
  // 1. Farfield Diagnostic Scanner item use
  world.afterEvents.itemUse.subscribe(event=>{
    const {source:player,itemStack}=event;
    if(!itemStack||itemStack.typeId!=="bearframe:field_scanner")return;
    attempt(()=>{
      if(!validPlayer(player))return;
      const dim=player.dimension;
      const nearby=dim.getEntities({location:player.location,maxDistance:18})
        .filter(e=>e.typeId.startsWith("bearframe:") && e.typeId!=="bearframe:grid_bolt")
        .sort((a,b)=>distSq(player.location,a.location)-distSq(player.location,b.location));
      if(!nearby.length){
        return say(player,"§b[Farfield Scanner]","No synthetic signatures or autonomous machines within 18 blocks.");
      }
      const target=nearby[0];
      const entry=SCAN_DB[target.typeId]??{tag:target.typeId,note:"Unclassified Bearframe-universe entity."};
      const hp=target.getComponent("minecraft:health");
      const hpText=hp?`Integrity ${Math.round(hp.currentValue)}/${Math.round(hp.effectiveMax)}`:"Integrity unreadable";
      const calm=target.getDynamicProperty("bearframe:stabilized")?" · Stabilized":"";
      const esc=target.getDynamicProperty("bearframe:escalated")?" · Hostile Alert":"";
      say(player,"§b[Farfield Scanner]",`${entry.tag} (${hpText}${calm}${esc}) — ${entry.note}`);
      try{player.playSound("note.pling",{pitch:1.4,volume:0.35});}catch{}
    });
  });

  // 2. Rich Entity Interactions (Trades, Echo Stabilization, Wrench Repair, Directorate Warnings)
  world.beforeEvents.playerInteractWithEntity.subscribe(event=>{
    const {player,target}=event;
    if(!target?.typeId?.startsWith("bearframe:"))return;
    if(fieldInteraction(player,target))return;
    const isCityStaff=typeof target.getDynamicProperty("bearframe:city_role")==="number";
    const held=heldItem(player);
    const holdingWrench=held?.typeId==="bearframe:repair_wrench";

    // Handle Atlas Maintenance Wrench field repair on damaged friendly/stabilized units
    if(holdingWrench && player.isSneaking && (
      target.typeId.startsWith("bearframe:atlas_") ||
      target.typeId.startsWith("bearframe:city_") ||
      target.typeId==="bearframe:farfield_surveyor" ||
      target.typeId==="bearframe:field_researcher" ||
      target.typeId==="bearframe:vera_artisan" ||
      target.typeId==="bearframe:echo_drifter" ||
      (target.typeId==="bearframe:echo_sentinel" && target.getDynamicProperty("bearframe:stabilized"))
    )){
      event.cancel=true;
      system.run(()=>attempt(()=>{
        if(!validPlayer(player)||!target.isValid||distSq(player.location,target.location)>36)return;
        const hp=target.getComponent("minecraft:health");
        if(!hp||hp.currentValue>=hp.effectiveMax){
          return say(player,"§6[Atlas Wrench]","Chassis integrity is already nominal.");
        }
        const paid=spend(player,"minecraft:iron_nugget",1,()=>{
          hp.setCurrentValue(Math.min(hp.effectiveMax,hp.currentValue+8));
        });
        if(!paid)return say(player,"§6[Atlas Wrench]","Carry 1 iron nugget to patch chassis damage.");
        try{target.dimension.spawnParticle("minecraft:villager_happy",{x:target.location.x,y:target.location.y+1.4,z:target.location.z});}catch{}
        say(player,"§6[Atlas Wrench]",`Field patch complete (${Math.round(hp.currentValue)}/${Math.round(hp.effectiveMax)} HP).`);
      }));
      return;
    }

    // Echo Chamber Sentinel: nonviolent stabilization path
    if(target.typeId==="bearframe:echo_sentinel"){
      event.cancel=true;
      system.run(()=>attempt(()=>{
        if(!validPlayer(player)||!target.isValid||distSq(player.location,target.location)>49)return;
        if(target.getDynamicProperty("bearframe:stabilized")){
          return say(player,"§d[Echo Sentinel]","Power bus steady... thank you. My shift log is still missing pages, but the corridor is safe.");
        }
        if(!player.isSneaking){
          return say(player,"§d[Echo Sentinel]","[SIGNAL FRAGMENTED] Halt—access badge expired... my power rail is arcing. Sneak-interact with 1 Copper Ingot, Redstone, or Legacy Cell to stabilize me.");
        }
        const bag=player.getComponent("minecraft:inventory")?.container;
        if(!bag||bag.emptySlotsCount===0)return say(player,"§d[Echo Sentinel]","Free one slot before stabilizing the bus.");
        const stabilize=()=> {
          target.setDynamicProperty("bearframe:stabilized",true);
          try{target.triggerEvent("bearframe:stabilize");}catch{}
          bag.addItem(new ItemStack("bearframe:salvaged_alloy",1));
        };
        const ok=spend(player,"bearframe:legacy_cell",1,stabilize)
          || spend(player,"minecraft:copper_ingot",1,stabilize)
          || spend(player,"minecraft:redstone",1,stabilize);
        if(!ok)return say(player,"§d[Echo Sentinel]","Bring 1 Copper Ingot, 1 Redstone Dust, or 1 Legacy Power Cell to steady my relay.");
        try{
          target.dimension.spawnParticle("minecraft:villager_happy",{x:target.location.x,y:target.location.y+1.6,z:target.location.z});
          player.playSound("random.levelup",{volume:0.35});
        }catch{}
        say(player,"§d[Echo Sentinel]","Voltage steadied. The alarm loop stopped... Take this spare alloy plate. I'll keep quiet watch here.");
      }));
      return;
    }

    // Directorate Officer: verbal restricted-AI hail & escalation warning
    if(directorateCadres.has(target.typeId)){
      const prefix=target.typeId==="bearframe:directorate_guard"?"§c[Directorate Gate Guard]":"§c[Directorate Officer]";
      event.cancel=true;
      system.run(()=>attempt(()=>{
        if(!validPlayer(player)||!target.isValid||distSq(player.location,target.location)>49)return;
        if(target.getDynamicProperty("bearframe:escalated")){
          return say(player,prefix,"Negotiation window closed. Directive enforcement active.");
        }
        const warnings=Number(target.getDynamicProperty("bearframe:warnings")??0)+1;
        target.setDynamicProperty("bearframe:warnings",warnings);
        if(warnings===1){
          return say(player,prefix,"Unregistered entity. This perimeter is under Nullframe Directorate control. Vacate immediately.");
        }
        target.setDynamicProperty("bearframe:escalated",true);
        try{target.triggerEvent("bearframe:escalate");}catch{}
        say(player,prefix,"Non-compliance logged. Authorizing containment force.");
      }));
      return;
    }

    // Atlas Rigger (both surface camps & Bearframe City): salvage reclamation trade
    if(target.typeId==="bearframe:atlas_rigger"){
      event.cancel=true;
      system.run(()=>attempt(()=>{
        if(!validPlayer(player)||!target.isValid||distSq(player.location,target.location)>49)return;
        if(!player.isSneaking){
          const line=pick(DIALOGUES["bearframe:atlas_rigger"],Math.floor(system.currentTick/40));
          return say(player,"§6[Atlas Rigger]",line);
        }
        const bag=player.getComponent("minecraft:inventory")?.container;
        if(!bag||bag.emptySlotsCount<2)return say(player,"§6[Atlas Rigger]","Free 2 inventory slots for reclaimed iron and copper.");
        const traded=spend(player,"bearframe:salvaged_alloy",2,()=>{
          bag.addItem(new ItemStack("minecraft:iron_ingot",2));
          bag.addItem(new ItemStack("minecraft:copper_ingot",3));
        });
        if(!traded)return say(player,"§6[Atlas Rigger]","Bring 2 Salvaged Chassis Alloy to reclaim 2 Iron and 3 Copper.");
        try{player.playSound("random.anvil_use",{volume:0.25,pitch:1.3});}catch{}
        say(player,"§6[Atlas Rigger]","Clean melt. Two iron, three copper—waste nothing.");
      }));
      return;
    }

    // Echo Drifter: peaceful salvage exchange & continuity dialogue
    if(target.typeId==="bearframe:echo_drifter"){
      event.cancel=true;
      system.run(()=>attempt(()=>{
        if(!validPlayer(player)||!target.isValid||distSq(player.location,target.location)>49)return;
        if(!player.isSneaking){
          if(player.dimension.id==="minecraft:overworld")campaignSignal(player,"echo","echo_drifter");
          return say(player,"§d[Echo Drifter]",pick(DIALOGUES["bearframe:echo_drifter"],Math.floor(system.currentTick/50)));
        }
        const bag=player.getComponent("minecraft:inventory")?.container;
        if(!bag||bag.emptySlotsCount===0)return say(player,"§d[Echo Drifter]","Need one open slot for the legacy cell.");
        const traded=spend(player,"minecraft:copper_ingot",2,()=>{
          bag.addItem(new ItemStack("bearframe:legacy_cell",1));
        });
        if(!traded)return say(player,"§d[Echo Drifter]","Two copper ingots for a charged legacy cell—fair swap.");
        say(player,"§d[Echo Drifter]","Good wire, clean copper. Keep that cell dry.");
      }));
      return;
    }

    // Remaining non-city Bearframes & Ghost Grid machines (inspect / dialogue)
    if(!isCityStaff && DIALOGUES[target.typeId]){
      if(target.typeId==="bearframe:grid_walker" && target.dimension.id!==ORBIT){
        // Let main.js or this handle walker cleanly; handle here and cancel duplicate
      }
      event.cancel=true;
      system.run(()=>attempt(()=>{
        if(!validPlayer(player)||!target.isValid||distSq(player.location,target.location)>49)return;
        const prefix=target.typeId.startsWith("bearframe:grid_")?"§3[Legacy Telemetry]":
          target.typeId==="bearframe:city_watch"?"§c[Watchtower]":
          target.typeId==="bearframe:field_researcher"?"§b[Farfield Research]":
          target.typeId==="bearframe:vera_artisan"?"§d[Visual Production]":"§6[Atlas Division]";
        say(player,prefix,pick(DIALOGUES[target.typeId],Math.floor(system.currentTick/60)));
      }));
    }
  });

  // 3. Lightweight Android-safe Ambient Living-World Pulse (every 100 ticks = 5 sec)
  system.runInterval(()=>{
    for(const player of world.getAllPlayers())attempt(()=>{
      if(!validPlayer(player)||player.dimension.id===ORBIT)return;
      const dim=player.dimension;
      const machines=dim.getEntities({location:player.location,maxDistance:22})
        .filter(e=>e.typeId==="bearframe:grid_walker"||e.typeId==="bearframe:grid_hauler"||e.typeId==="bearframe:directorate_officer")
        .slice(0,6);
      for(const mob of machines){
        if(mob.typeId==="bearframe:grid_walker"||mob.typeId==="bearframe:grid_hauler"){
          try{
            dim.spawnParticle("minecraft:endrod",{x:mob.location.x,y:mob.location.y+0.85,z:mob.location.z});
          }catch{}
        }else if(mob.typeId==="bearframe:directorate_officer" && !mob.getDynamicProperty("bearframe:escalated")){
          if(distSq(player.location,mob.location)<=81 && !mob.getDynamicProperty("bearframe:hailed_"+player.id)){
            mob.setDynamicProperty("bearframe:hailed_"+player.id,true);
            say(player,"§c[Directorate Officer]","Hold position. Unregistered frame approaching Directorate checkpoint—do not tamper with hardware.");
          }
        }
      }
    });
  },100);
}
