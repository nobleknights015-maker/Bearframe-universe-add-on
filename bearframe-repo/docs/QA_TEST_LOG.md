# Bearframe Bedrock — QA & Testing Log (v0.4.0)

## 1. Automated & Static Validation Results (Completed in Linux Workspace)

Date: 2026-11-24 | Branch: `gemini-dev` | Build: `0.4.0`

| Check | Tool / Command | Result | Details |
|---|---|---|---|
| Asset & Definition Generation | `python3 tools/make_content.py` | **PASSED** | 19 living entities + 1 projectile, 6 items, 4 spawn rules, 2 pack icons |
| Structure & Worldgen NBT Build | `npm run worldgen` | **PASSED** | 11 `.mcstructure` files including expanded `60×8×23` `orbital_city` |
| Automated Test Suite | `npm test` | **PASSED (20/20)** | Layout (3), Regions + Escorts + 7 City Staff (6), Ruins + Escorts + BFS Pathing (4), Entities/Rigs/Lore/Caps (7) |
| Deep Static Validator | `python3 tools/build.py dist` | **PASSED** | Manifests, `@minecraft/server` `2.10.0`, all JSON, `node --check` on all `.js`, 20 geometries (UV bounds, bone parents, `<=60` cubes), 72 animations (bone bindings), 2 controllers, all PNG headers/sizes, localization, zero forbidden assets |
| Package Integrity | `zipfile.testzip()` | **PASSED** | `Bearframe_Bedrock_0.4.0.mcaddon` (160 KB) & `Bearframe_Bedrock_Source_0.4.0.zip` (338 KB) |

## 2. Live Android Bedrock Testing Checklist (**NOT YET TESTED IN BEDROCK**)

Target Device: **Android Bedrock (4 GB RAM, Moto G 2025)** — No PC or paid server required.

Please run through this checklist in Minecraft Bedrock on Android with **Settings → Creator → Content Log File & Content Log GUI** enabled, then report screenshots, observations, or any Content Log lines:

- [ ] **1. Import & Pack Icons:** Tap `Bearframe_Bedrock_0.4.0.mcaddon` -> both `Bearframe | Behavior` and `Bearframe | Resources` import cleanly and display custom Bearframe icons.
- [ ] **2. World Load & Content Log:** Create a Survival world with both packs active (optional: Infinity Sci-Fi stacked below). Record any orange/red Content Log messages on world load.
- [ ] **3. Bearframe Humanoid Models & Proportions:** Use `/summon` or visit `farfield_camp` to inspect `farfield_surveyor`, `atlas_rigger`, `atlas_vanguard`, `city_watch`, `city_steward`, `city_engineer`, `vera_artisan`. Confirm player-scale height, grounded feet, chest core display, dual circular side-head tech modules (no floating parts or stretched UVs), smooth walk + head-look animation.
- [ ] **4. Nullframes, Hollows & Hunters:** Inspect `hollow_scout` (confirm humanoid, no longer a dog!), `hollow_breacher`, `directorate_officer`, `nullframe_hunter`. Hail `directorate_officer` twice to verify verbal warning -> hostile escalation.
- [ ] **5. Echo Frames & Nonviolent Stabilization:** Inspect `ward_resident`, `echo_drifter` (Sneak-interact with 3 copper ingots -> 1 `legacy_cell`), and `echo_sentinel` (Sneak-interact with 1 copper/redstone/legacy cell -> permanently stabilized).
- [ ] **6. Nonhumanoid Ghost Grid Machines:** Inspect `grid_walker` (6-legged tripod gait), `grid_watcher` (smooth hovering + spinning lower scanner), `grid_turret` (aiming + firing non-griefing cyan `grid_bolt` with zero block destruction), `grid_hauler` (treads + crane), `grid_guardian` (2.6-block heavy silhouette).
- [ ] **7. Field Tools & Survival Recipes:** Craft `bearframe:field_scanner` and `bearframe:repair_wrench`. Scan an entity of each faction (verify canon-safe readouts, Ghost Grid remains "unverified"). Sneak-interact with wrench + iron nugget on a damaged Bearframe or Echo to verify healing.
- [ ] **8. Expanded Orbital Bearframe City:** Use a Farfield Surveyor to visit `bearframe:city_orbit`. Walk all 6 department bays (`60×8×23`), talk to all 7 staff including Atlas Rigger (alloy trade), Atlas Vanguard, and Vera Artisan, and return cleanly via the arrival bay lodestone.
- [ ] **9. Overworld Exploration & Android 4 GB RAM Stability:** Explore for 10–15 minutes across plains/forest/taiga/savanna/desert. Verify smooth frame rate, natural ambient spawns are sparse/capped, and existing survival mining/crafting feels intact.
