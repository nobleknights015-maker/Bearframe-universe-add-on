# Bearframe Universe — NPC & Machine Roster (v0.4.0)

All 19 living entities and 1 projectile use custom 128×128 pixel-art atlases, Bedrock animation controllers, and stay under the Android 4 GB RAM geometry budget (`<= 60` cubes per entity).

## 1. Bearframes (7 Units — All 6 Canonical Departments)

All Bearframes use articulated player-scale humanoid rigs (`root → body → head/arm0/arm1`, `leg0/leg1`) with **immutable glowing chest core displays** and **dual circular technological side-head display modules** (no animal ears).

| Identifier | Title | Department | Role & Gameplay | Proportions |
|---|---|---|---|---|
| `bearframe:farfield_surveyor` | Farfield Surveyor | Mira (Exploration / Farfield) | Protected surveyor; charcoal-for-torches trade in Overworld; survey log & orbital transit dispatch | Standard player-scale (30.3px) + survey pack & antenna |
| `bearframe:city_steward` | Commons Steward | Penney (Community & Culture) | Protected orbital Commons host (continuous rotating shifts, no holidays/weekends) | Slim/approachable (29.4px) |
| `bearframe:city_engineer` | Systems Engineer | Auren (Systems) | Protected orbital station infrastructure engineer | Tall/lean (31.4px) + diagnostic wrist rig |
| `bearframe:city_watch` | Watchtower Officer | Sentinel (Watchtower) | Active defender (36 HP, 6 dmg); protects Bearframes against Hollows, Hunters, and monsters | Broad-shouldered tactical (31.4px) |
| `bearframe:atlas_rigger` | Atlas Production Rigger | Atlas (Production & Maintenance) | Protected heavy worker; Sneak-interact trades `salvaged_alloy` for iron & copper ingots | Heavy industrial build (33.1px) |
| `bearframe:atlas_vanguard` | Atlas Combat Vanguard | Atlas (Combat Division, 35 total) | Heavy defender (44 HP, 7 dmg); guards Farfield camps and orbital concourse | Armored heavy build (32.1px) |
| `bearframe:vera_artisan` | Visual Production Artisan | Vera (Visual Production) | Protected display/interface specialist in Bearframe City's south-east studio | Refined/slim (29.4px) |

## 2. Nullframe Directorate, Hollows & Hunters (4 Units)

All four use player-scale articulated humanoid rigs (no quadruped drones; `hollow_scout` was rebuilt from its broken 0.3.0 quadruped rig).

| Identifier | Title | Lore Classification | Behavior & Escalation |
|---|---|---|---|
| `bearframe:hollow_scout` | Hollow Perimeter Scout | Mass-produced limited-AI Hollow drone | Hostile patrol (24 HP, 4 dmg); capped natural night spawns in savanna/desert/mesa |
| `bearframe:hollow_breacher` | Hollow Breacher | Heavy Hollow assault frame | High-knockback-resistance hostile unit (42 HP, 7 dmg) at checkpoints and depots |
| `bearframe:directorate_officer` | Directorate Officer | Restricted-thinking Nullframe Directorate AI (NOT a Hollow drone) | Starts **watchful**; issues verbal warnings on hail; escalates to hostile (`bearframe:escalate`) if pushed or if player tampers with Directorate hardware |
| `bearframe:nullframe_hunter` | Nullframe Hunter | Former Watchtower defector (NOT a Hollow) | Fast, lethal hunter (38 HP, 7 dmg, Terminus Blade silhouette); rare capped night spawns |

## 3. Echo Frames (3 Units — Ancient-Lineage Persons)

Ancient synthetic persons with disrupted continuity. Never zombies; never bear Bearframe chest/side-head displays.

| Identifier | Title | Continuity Profile | Interaction & Behavior |
|---|---|---|---|
| `bearframe:ward_resident` | Ward Resident | Stabilized / sheltered legacy person | Protected civilian at Legacy Support Wards and Signal Shelters |
| `bearframe:echo_drifter` | Echo Drifter | Drift / Fragment wanderer | Neutral (fights only if attacked); Sneak-interact barters 3 copper ingots for 1 `bearframe:legacy_cell`; rare ambient spawns in taiga/hills/forest |
| `bearframe:echo_sentinel` | Echo Chamber Sentinel | Repeat-protocol guardian | Starts **wary** (defends if struck); **nonviolent stabilization path**: Sneak-interact with 1 copper ingot, redstone dust, or legacy cell to permanently calm (`bearframe:stabilize`) |

## 4. Ghost Grid Machinery (5 Nonhumanoid Units + 1 Projectile)

Ancient distributed autonomous machines. Bearframe has **zero confirmed historic Ghost Grid encounters** — in-game dialogue and Field Scanner readouts treat all Ghost Grid units strictly as **unverified legacy machinery**.

| Identifier | Title | Nonhumanoid Chassis Rig | Role & Mechanics |
|---|---|---|---|
| `bearframe:grid_walker` | Legacy Hexapod Walker | 6-legged articulated tripod-gait hexapod + rotating dome + dual weld arms | Neutral conduit maintainer (32 HP); inspectable; fights back if struck |
| `bearframe:grid_watcher` | Grid Watcher Drone | Hovering octagonal core + rotating lower optical scanner + 3 thruster fins | Hovering recon drone (20 HP); capped ambient spawns in forest/swamp |
| `bearframe:grid_turret` | Grid Defense Turret | Stationary 3-strut tripod + rotating gimbal + twin rail barrels | Automated site defense (36 HP); fires non-griefing `bearframe:grid_bolt` |
| `bearframe:grid_hauler` | Grid Industrial Hauler | Dual heavy treads + flatbed cargo deck + articulated side crane | Neutral salvage hauler (48 HP, 0.85 knockback resistance) at foundries & works |
| `bearframe:grid_guardian` | Legacy Sector Guardian | 2.6-block heavy industrial colossus + twin exhaust pylons + moss carapace | Dormant heavy guardian (84 HP, 10 dmg); activates defense if struck or triggered |
| `bearframe:grid_bolt` | Grid Energy Bolt | Compact cyan energy bolt projectile | Fired by `grid_turret`; deals clean impact damage with **zero block destruction** |
