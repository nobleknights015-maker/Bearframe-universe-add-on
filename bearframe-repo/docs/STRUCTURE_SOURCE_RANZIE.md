# Owner-selected structure direction: Ranzie's Overgrown Cities

Date: 2026-11-26. Supersedes the earlier choice of Lost Cities / Post Apocaliptic Structures as the primary general city source. Do not spend more time expanding those sources for general settlements.

Selected native Bedrock pack: Ranzie's Overgrown Cities 1.3 by Ranzie.
Project: https://www.curseforge.com/minecraft-bedrock/addons/ranzies-overgrown-cities
File: https://www.curseforge.com/minecraft-bedrock/addons/ranzies-overgrown-cities/files/8758719
Project ID 1473662, file ID 8758719, RandS Overgrown Cities 1.3.mcpack, 11.4 MB, published 2026-08-29. Upstream listing marks All Rights Reserved. Keep upstream dependency separate; store Bearframe-owned compatibility code and reproducible setup instructions here.

Proposed integration boundary (not yet implemented):
- Use the actual native city generation and structures, not lookalike builds. Preserve architecture, street networks, interiors and overgrowth.
- Retain Bearframe-specific bunkers (including flooded variants), quest-critical sites, encounter habitats, Farfield camps, Nullframe facilities, and Astro Station. Disable redundant generic city generation only after mapping every affected quest/route/marker and providing a compatible replacement. Do not delete existing world structures or change pack UUIDs.
- Inspect the actual archive's manifest, namespaces, dependencies, structures, worldgen, scripts and chest pools before making edits. Map original gun-loot integrations to Bearframe scavenging and RPG rewards in a compatibility layer; don't require unrelated firearms mods. Exclude Farfield cutter and boss-only signatures from city chest pools.
- Add lore-appropriate Echo, Ghost Grid, Nullframe and rare expedition inhabitants through bounded, persistent claims; avoid overcrowding or repeated spawns. Verify Field Log and quest routing. Preserve Star Odyssey texture compatibility.
- Test on a fresh world and copied existing save, with multiple seeds, actual city discovery, structure overlap, water boundaries, loot, NPC counts and Android performance. No claim that old chunks regenerate automatically.

Status: source listing verified; downloading the binary into this environment failed. Exact pack contents not inspected. No gameplay, generation, installer or existing structure changes in this commit. Need the original .mcpack before implementing a source-backed compatibility layer. Baseline: 0.11.17 easy-fix candidate. Other boss, weapon, RPG quest and loot priorities remain unchanged.
