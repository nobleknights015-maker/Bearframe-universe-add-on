# Bearframe: The Last Dispatch 0.10.1

A Minecraft Bedrock survival add-on set in the Bearframe universe.

The behavior and resource packs in this directory are the editable source for
version 0.10.1. They include the expanded ruins, bunkers and orbital station,
faction models, campaign and repeatable quests,
loot, Field Log, and archived Treasure Charts. Craft a Field Log Pad at a crafting table and use it from your hand to open the same records as the placed Field Log Terminal. The craftable Teleport Tablet takes you from solid ground in the Overworld to Bearframe Station and back to your recorded surface berth. The Farfield Survey Camp cartography table also provides station transit when used while sneaking.

## Build and install

Run `python3 tools/package_current.py` from this directory with Node.js
available for script validation. The generated import file is
`dist/Bearframe_The_Last_Dispatch_0.10.1.mcaddon`.

Import the single add-on and enable its behavior and resource packs. In the
Bearframe resource pack settings, select **Compatibility** for mixed add-on
worlds. The same import also includes selectable Bearframe mob visuals and
Star Odyssey material options.

See [the pack-building guide](docs/Add_On_Pack_Compatibility.md) for the
settings, dependency IDs, and integration guidance.

## Development history

The [campaign guide](docs/Bearframe_0.7.0_Campaign_Guide.md) and
[structure research notes](docs/Bearframe_0.5.0_Structure_Research_and_QA.md)
record earlier implementation and design decisions.
`tools/development-history/` preserves the iteration scripts and campaign
test sources from the 0.4.4 to 0.9.2 work. These historical scripts may expect
earlier archives, local reference assets or test stubs. Use
`tools/package_current.py` to build from the current packs.
