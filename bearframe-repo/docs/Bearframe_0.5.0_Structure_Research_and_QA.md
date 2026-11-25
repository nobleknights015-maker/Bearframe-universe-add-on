# Bearframe Bedrock 0.5.0 structure research and verification

## Sources and design decisions

**The approach should establish a destination.** Trail Ruins expose a tower and use a road to connect buried buildings. The reusable idea is to give a site one feature players can recognize before they see its individual rooms. In Bearframe, the approach lanes lead to Relay Nine’s antenna, Coalition City’s communications monument, the Syndicate Forge gantry, and the stepped ice shell at Nivalis Lab. Frontier Ruin instead uses broken posts and surviving lines of masonry to suggest a former route. [Minecraft’s Trail Ruins field guide](https://www.minecraft.net/en-us/article/trail-ruins)

**Useful spaces make the floor plan legible.** Trial Chambers use distinct rooms and place encounters and rewards within a navigable complex. Bastion types use distinct architecture to support recognizable activities. On this pass, the colony uses dwellings, a workshop and a greenhouse. The waystation splits sheltered supply handling from its rooms. The forge puts the equipment in covered bays and the overhead hoist in a loading yard. The wreck concentrates salvage around its open hull. Existing Bearframe repair sequences keep their linked locations and paths. [Minecraft’s Trial Chamber field guide](https://www.minecraft.net/en-us/article/trial-chamber) · [Minecraft’s Bastion Remnant field guide](https://www.minecraft.net/en-us/article/bastion-remnant)

**Climate and purpose both affect the architecture.** Atlas Warehouse’s Starbound study calls for functional material families, concentrated accents, and distinct regional silhouettes. Its glacial pressure-shell, industrial heat-management, raised forest, and buried machinery proposals informed the four Wilds adaptations. Nivalis uses calcite and ice, Cinder uses sandstone around basalt and exhausts, Verdantis uses roots and a living canopy, and the Shattered Array uses deepslate, a broken emitter ring, and amethyst. The four builds are regional discoveries in the Bearframe Overworld. The warehouse’s planet-scale systems remain design references. [Atlas Warehouse’s Starbound Frontier worldbuilding study](https://github.com/nobleknights015-maker/Atlas-Warehouse/blob/HEAD/warehouse/studies/starbound-frontier-bedrock-worldbuilding-research-2026-11-23.md)

**Placement and the actual build need separate templates.** Bedrock structure sets place eligible starts, pools reference the templates, and jigsaw settings control generation and terrain projection. This release extends Bearframe’s existing datum-and-survey approach. One-block jigsaw candidates route to full templates through the script. The script checks loaded chunks, grade, waterlogging, dry approach space, and obstructing blocks before placement. The larger sites therefore depend on finding a suitable footprint near a candidate. Each new discovery has its own spacing, salt and biome filter. [Microsoft’s introduction to jigsaw structures](https://learn.microsoft.com/en-us/minecraft/creator/documents/structures/introductiontojigsawstructures) · [Microsoft’s structure set reference](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/worldgenreference/examples/jigsawstructuresets) · [Microsoft’s template pool reference](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/worldgenreference/examples/jigsawtemplatepools)

## Implementation

### Existing Bearframe structures

| Site | Rework |
|---|---|
| Farfield Survey Camp | Quartz wall panels, copper roof edges and survey beacons around the original expedition layout |
| Overgrown Switchyard | Dark support ribs, oxidized casing, mossy walls and rooted growth on the storehouse |
| Legacy Support Ward | Pale layered walls, blue markers, framed openings and capped roof sections |
| Directorate Checkpoint | Blackstone framing, narrow tinted windows and red control accents |
| Ruined Foundry Annex | Cut sandstone against dark structural members, copper cap and contrasting vent stacks |
| Maintenance Relay | Deepslate wall sections, roof divisions and cyan service markings |
| Rainline Works | Banded workshop walls and copper roof details along the original wash channel |
| Saltline Depot | Sandstone freight buildings, contrasting loading edges and amber markings |
| Signal Shelter | Ribbed service walls and downlights around the descending access and flooded rooms |
| Orbital City | Quartz and dark frames around the transit spine, new roof trusses and overhead lamps |
| Spillway Facility | Banded service walls and pump-gallery lighting around the mapped machinery and repair route |

This portion reworks the architecture and material treatment around the shipped floor plans. It preserves gameplay coordinates so the existing actors, terminals, caches and repairs still refer to the same places.

### Starbound concepts reauthored for Bearframe

| Source concept | Bearframe ID | Readable plan |
|---|---|---|
| Colony | frontier_colony | Homes, a workshop, greenhouse and shared crossroads |
| Colony Waystation | colony_waystation | Covered freight shelter, supply barrels and two support rooms |
| Coalition City | coalition_city | Civic square, four accessible wings and antenna landmark |
| Crashed Skiff | crashed_skiff | Tapered hull, fins, damaged access side and salvage compartment |
| Relay Nine | relay_nine | Paired service rooms and a freestanding communications rig |
| Ruin | frontier_ruin | Remnant walls, weathered bridge and excavated center |
| Syndicate Forge | syndicate_forge | Furnaces, smithing, overhead hoist and loading yard |
| Cinder Wilds | cinder_works | Basalt outcrops, heat exhausts and separate work bays |
| Nivalis Wilds | nivalis_lab | Twin insulated pods and ice observation deck |
| Verdantis Wilds | verdantis_station | Rooted compound, canopy shelters and research walkway |
| Shattered Moon Wilds | shattered_array | Broken sensor ring, reinforced storage and exposed dust bed |

The new templates were built in the Bearframe namespace with vanilla blocks and Bearframe salvage references. They use original block layouts. Natural placement uses dry Overworld terrain and appropriate biome filters, including plains, savanna, taiga, forest, desert, mesa, ice plains, jungle and hills.

## Verification and limits

- Validated the ZIP and parsed every shipped JSON and little-endian NBT structure. Checked template dimensions, block-layer lengths and palette indices.
- Checked both blocks of headroom and a solid footing from all four entrance lanes to the new sites’ interactive props. The 11 new layouts passed that static test.
- Checked original scripted and functional block coordinates in the 11 Bearframe sites, including terminal and marker positions, gates, barrels, cables, stairs and water. The original entity/resource assets were retained.
- The preview uses the packaged structure block data, with simplified display colors. Signal Shelter, Spillway Facility and Orbital City are shown in cutaway.
- Live Bedrock testing remains open. Seed-by-seed appearance and rarity, actual collision, current-version loot container behavior, existing-world upgrades and Android performance are unverified. Natural jigsaw candidates are intended for newly generated terrain. Established builds already placed in a world have no retroactive rebuild path.
