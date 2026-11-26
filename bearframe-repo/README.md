# Bearframe: The Last Dispatch 0.10.14

A Minecraft Bedrock survival add-on set in the Bearframe universe.

The behavior and resource packs in this directory are the editable source for
version 0.10.14. They include the expanded ruins, bunkers and orbital station,
faction models, campaign and repeatable quests,
loot, Field Log, and archived Treasure Charts. Craft a Field Log Pad at a crafting table and use it from your hand to open the same records as the placed Field Log Terminal. The craftable Teleport Tablet takes you from solid ground in the Overworld to Bearframe Station and back to your recorded surface berth. The Farfield Survey Camp cartography table also provides station transit when used while sneaking.

## Build and install

Run `python3 tools/package_current.py` from this directory with Node.js
available for script validation. The generated import file is
`dist/Bearframe_The_Last_Dispatch_0.10.14.mcaddon`.

Import the generated add-on and activate its behavior and resource packs.
Bearframe's mob makeovers and original sci-fi materials are included.

See [the pack-building guide](docs/Add_On_Pack_Compatibility.md) for the
settings, dependency IDs, and integration guidance.

## Boss encounters

All four bosses have Creative spawn eggs and can be summoned with cheats.
Use a clear arena at least 32 blocks across and switch to Survival or
Adventure to engage. The bosses are opt-in encounters.

| Faction | Boss | Summon ID | Attacks |
| --- | --- | --- | --- |
| Ghost Grid | Palinode-6 | `bearframe:grid_palinode` | Piston Ram, Tripod Quake |
| Ghost Grid | Silt Engine | `bearframe:grid_silt_engine` | Discharge Beam, Purge Valve |
| Echo Frame | Seam-Riven | `bearframe:echo_seam_riven` | Seam Cut, Frame Skip |
| Echo Frame | Veil Regent | `bearframe:echo_veil_regent` | Anchor Sigil, Broken Court |

Particle markers preview the strike area. Below 40% health, bosses recover
faster between moves and hit harder. Run `python3 tools/build_bosses.py` with
Pillow installed to regenerate their rigs, textures and animation bindings.

## Regenerate station and terrain templates

Install the Node development dependency with `npm install`. Run
`node tools/import_gateway.mjs` to rebuild the Gateway II orbital hull and
its furnished central cabin from the saved block data. The upstream build is
credited in [Gateway II credits](behavior_pack/GATEWAY_II_CREDITS.txt).
Run `node tools/build_settlements.mjs` to rebuild the Lost Cities districts
and bunker annexes from their source templates.

Gateway II builds on first station arrival in a fresh world or a save that
has not yet built an orbital station.

## Development history

The [campaign guide](docs/Bearframe_0.7.0_Campaign_Guide.md) and
[structure research notes](docs/Bearframe_0.5.0_Structure_Research_and_QA.md)
record earlier implementation and design decisions.
`tools/development-history/` preserves the iteration scripts and campaign
test sources from the 0.4.4 to 0.9.2 work. These historical scripts may expect
earlier archives, local reference assets or test stubs. Use
`tools/package_current.py` to build from the current packs.
