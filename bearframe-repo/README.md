# Bearframe Universe — Minecraft Bedrock Add-on (v0.4.0)

An original Minecraft Bedrock Edition survival add-on bringing the **Bearframe Universe** (Lore Bible Revision 4.10) into natural Minecraft survival gameplay, optimized for Android Bedrock on 4 GB RAM devices (tested target: Moto G 2025).

## Release 0.4.0 Highlights (Branch `gemini-dev`)

- **19 Distinct Synthetic & Machine Entities + 1 Non-Griefing Energy Bolt Projectile:**
  - **7 Bearframes across all 6 Canonical Departments** (Mira/Farfield, Penney/Commons, Auren/Systems, Sentinel/Watchtower, Atlas Production/Maintenance & Combat Vanguard, Vera/Visual Production), built on articulated player-scale humanoid rigs with immutable glowing chest core displays and dual circular technological side-head display modules (never animal ears).
  - **4 Nullframe Directorate, Hollow & Hunter Units:** `hollow_scout` (rebuilt from the 0.3.0 quadruped into a player-scale humanoid drone), `hollow_breacher`, `directorate_officer` (restricted-thinking AI that issues verbal warnings before escalating), and `nullframe_hunter` (former Watchtower defector with Terminus Blade silhouette).
  - **3 Echo Frames:** `ward_resident`, `echo_drifter` (copper-for-cell barter), and `echo_sentinel` (wary guardian with a nonviolent stabilization path).
  - **5 Dedicated NONHUMANOID Ghost Grid Sci-Fi Machines:** `grid_walker` (6-legged articulated hexapod), `grid_watcher` (hovering tri-thruster drone), `grid_turret` (stationary tripod firing non-griefing `bearframe:grid_bolt`), `grid_hauler` (tracked industrial salvage carrier with crane), and `grid_guardian` (2.6-block heavy legacy sector guardian).
- **128×128 Pixel-Art Entity Atlases & Animation Controllers:** Upgraded from flat 64×32 color swatches to crisp 4×4 32px-tile atlases (matching Infinity Sci-Fi texture density) with idle, walk, head look-at-target, attack, hover, and turret-aim controllers.
- **Expanded Bearframe City (60×8×23 Orbital Station):** All 6 canonical departments now have staffed bays in `bearframe:city_orbit` while preserving 0.3.0 coordinates and save compatibility.
- **Living World Field Gameplay & Survival Tools:** Craftable `bearframe:field_scanner` (canon-safe diagnostics) and `bearframe:repair_wrench` (Sneak-interact field repair), alloy salvage (`bearframe:salvaged_alloy`), `bearframe:legacy_cell`, Atlas iron/copper reclamation trades, Directorate warning/escalation, nonviolent Echo stabilization, and Android-capped ambient spawn rules.
- **10 Overworld Locations + Orbital Hub:** Maintenance Relay, 5 regional sites (`farfield_camp`, `grid_hub`, `echo_ward`, `intrusion_checkpoint`, `foundry_annex`), and 4 ruins (`spillway_bunker`, `shelter_bunker`, `rainline_town`, `saltline_town`) now populated with primary residents and faction escorts.

## Android Installation (No PC or Paid Server Required)

1. Download `Bearframe_Bedrock_0.4.0.mcaddon` on your Android phone.
2. Tap the `.mcaddon` file and open it with **Minecraft** (both `Bearframe | Behavior` and `Bearframe | Resources` import automatically).
3. Create a new Survival world (or copy an existing world):
   - Activate **Bearframe | Behavior** and **Bearframe | Resources**.
   - Optional: stack the external **Infinity Sci-Fi** resource pack **below** `Bearframe | Resources` so Bearframe textures override cleanly.
   - Enable **Content Log File** and **Content Log GUI** in Settings → Creator while testing so any warnings can be captured and fixed.

## Development & Build Commands

```bash
# Regenerate entities, models, textures, items, loot, recipes, spawn rules, and pack icons
python3 tools/make_content.py

# Regenerate all 11 .mcstructure files and worldgen jigsaw JSONs
npm run worldgen

# Run all 20 automated unit & geometry/structure/lore tests
npm test

# Run deep static validation and package .mcaddon + source archive (with .gitbundle)
python3 tools/build.py dist
```

## Third-Party Licensing & Project Boundaries

- **Infinity Sci-Fi** is strictly external and optional; zero licensed textures or files are bundled in this repository.
- **Starbound Frontier** is a separate paused project and is untouched.
- **Validation Honesty:** Release `0.4.0` has passed all 20 automated Node tests and deep Python static validation (JSON, JS syntax, PNG headers/dimensions, UV bounds, bone hierarchies, Android cube/spawn caps, NBT structure traversability). Live in-game verification on Android Bedrock is tracked in `docs/QA_TEST_LOG.md`.
