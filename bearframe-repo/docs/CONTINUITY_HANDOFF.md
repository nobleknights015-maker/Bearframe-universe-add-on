# Bearframe Bedrock — Continuity Handoff (v0.4.0)

## Repository & Branch State

- **Repository:** `https://github.com/nobleknights015-maker/Bearframe-universe-add-on`
- **Preserved Baseline:** `main` branch remains untouched at `6f4fbb8` (tagged `baseline-work-0.3.0`).
- **Active Development Branch:** `gemini-dev` (v0.4.0 release).
- **Distribution Method:** Because no GitHub push credentials are stored in the AI Studio sandbox, `Bearframe_Bedrock_Source_0.4.0.zip` bundles `Bearframe_Bedrock.gitbundle` containing all branches/tags (`main`, `baseline-work-0.3.0`, `gemini-dev`) so the user can import/push directly into GitHub when ready.

## What Changed in Round 1 (`0.3.0` -> `0.4.0`)

1. **Zero-Dependency Pixel-Art Pipeline (`tools/make_content.py`):** Replaced Pillow dependency with pure-Python RGBA PNG encoding, upgrading entity textures from 64×32 flat swatches to 128×128 4×4 pixel-art atlases + 128×128 pack icons.
2. **Full Faction Roster (19 Living Entities + 1 Projectile):**
   - Expanded Bearframes from 4 to 7 covering all 6 canonical departments (`atlas_rigger`, `atlas_vanguard`, `vera_artisan` added).
   - Rebuilt `hollow_scout` from quadruped to player-scale humanoid; added `hollow_breacher`, `directorate_officer` (warning/escalation), and `nullframe_hunter`.
   - Expanded Echo Frames from 1 to 3 (`ward_resident`, `echo_drifter`, `echo_sentinel` with nonviolent stabilization).
   - Expanded Ghost Grid from 1 to 5 strictly nonhumanoid sci-fi rigs (`grid_walker` hexapod, `grid_watcher` hover drone, `grid_turret` + non-griefing `grid_bolt`, `grid_hauler` tracked crane, `grid_guardian` heavy colossus).
3. **Animation Controllers & Head Tracking:** Added `controller.animation.bearframe.locomotion` and `controller.animation.bearframe.turret` with `look` head tracking, idle breathing, walk/tripod/hover cycles, and attack animations.
4. **Living World Scripting (`behavior_pack/scripts/living_world.js`):** Added `field_scanner`, `repair_wrench`, Echo nonviolent stabilization, Directorate warning/escalation, Atlas alloy reclamation, Echo copper-for-cell barter, and lightweight ambient behavior loop.
5. **Expanded Bearframe City & Populated Overworld Sites:** Expanded `orbital_city.mcstructure` to `60×8×23` (preserving `x=0..43`), staffed all 6 canonical departments, and populated escorts across all 9 Overworld regional/ruin structures.
6. **Deep Static Validation & Automated Tests:** Expanded `tools/build.py` and `tests/` to 20 passing tests verifying structures, escorts, entity rigs, UV bounds, bone bindings, lore rules, and Android 4 GB RAM budgets.

## Next Priorities (Round 2 — After Android Bedrock Feedback)

1. Fix any rendering, UV orientation, animation, hitbox, or Content Log issues reported from the user's Android Moto G 2025 playtest.
2. Add lightweight custom sound definitions and subtle ambient particles for Ghost Grid machines and Bearframe terminals (within 4 GB RAM budget).
3. Expand Overworld storytelling with additional multi-room ruin variants, readable environmental logs, and subtle archaeological hints toward buried ancient sites (strictly respecting Lore Bible Rev 4.10 epistemic boundaries).
4. Polish combat balance, faction skirmish behavior (Watchtower/Vanguard vs Hollows/Hunters), and multiplayer sync edge cases.
