# Bearframe Bedrock — Feature Status Ledger (v0.4.0)

Status taxonomy (honest reporting — never conflated):
- **PROPOSED**: Planned for a future development round.
- **IMPLEMENTED**: Authored in code/assets.
- **STATICALLY VALIDATED**: Verified by automated Node unit tests (`npm test`), JS syntax check (`node --check`), NBT structure checks, and `tools/build.py` deep validator.
- **TESTED IN BEDROCK**: Verified live inside Minecraft Bedrock on Android with content logs reviewed.

| Feature / System | Status | Notes |
|---|---|---|
| 0.3.0 Relay Circuit & 10 Overworld Sites Compatibility | STATICALLY VALIDATED | All 0.3.0 `bearframe:` IDs, indices `0..8`, and relay phases preserved unchanged |
| 19 Living Entities + 1 Projectile (`grid_bolt`) | STATICALLY VALIDATED | 7 Bearframes, 4 Nullframe/Hollow/Hunter, 3 Echoes, 5 Nonhumanoid Ghost Grid + bolt |
| `hollow_scout` Humanoid Rebuild | STATICALLY VALIDATED | Rebuilt from broken 0.3.0 quadruped into player-scale humanoid drone |
| Player-Scale Humanoid Proportions & Bearframe Displays | STATICALLY VALIDATED | Grounded feet (`y=0`), immutable chest core display + dual side-head tech modules |
| Nonhumanoid Ghost Grid Sci-Fi Rigs | STATICALLY VALIDATED | Hexapod, hover drone, tripod turret, tracked hauler, 2.6-block heavy guardian |
| 128×128 Pixel-Art Atlases & Pack Icons | STATICALLY VALIDATED | Generated via pure-Python RGBA encoder; PNG headers & dimensions verified |
| Animation Controllers (`locomotion`, `turret`) & Look-at-Target | STATICALLY VALIDATED | 72 animations + 2 controllers; all animated bones verified against `.geo.json` |
| Expanded Orbital Bearframe City (`60×8×23`, all 6 departments) | STATICALLY VALIDATED | All 7 staff positions & arrival/return points verified in `orbital_city.mcstructure` |
| Living World Script (`living_world.js`) | STATICALLY VALIDATED | Field Scanner diagnostics, Repair Wrench, Echo stabilization, Directorate escalation, trades |
| 6 Custom Items & 4 Survival Recipes | STATICALLY VALIDATED | Zero sentience-chip / Prime-duplication recipes; survival-balanced |
| Android-Capped Natural Spawn Rules (4 entities) | STATICALLY VALIDATED | `echo_drifter`, `hollow_scout`, `nullframe_hunter`, `grid_watcher` (`density_limit <= 3`) |
| Android 4 GB RAM Performance & Rendering Test | NOT YET TESTED IN BEDROCK | Ready for user install via `Bearframe_Bedrock_0.4.0.mcaddon` |
| Content Log Zero-Error Verification in Live Bedrock | NOT YET TESTED IN BEDROCK | Awaiting Android Bedrock content log report |
| Multi-stage Ruins / Deep Subterranean Sleeper Site Hints | PROPOSED | Scheduled for Round 2 after 0.4.0 in-game baseline verification |
| Custom Ambient Sound Events & Particle Polish | PROPOSED | Scheduled for Round 2 (lightweight Android-safe budget) |
| Additional Faction Patrols & Modular Outpost Variants | PROPOSED | Scheduled for Round 2 |
