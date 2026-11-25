# Bearframe Bedrock 0.8.3

A Minecraft Bedrock survival add-on set in the Bearframe universe.

The behavior and resource packs in this directory are the editable source for
version 0.8.3. They include the expanded ruins, bunkers and orbital station,
faction models and vanilla mob replacements, campaign and repeatable quests,
loot, Field Log, and archived Treasure Charts.

## Build and install

Run `python3 tools/package_current.py` from this directory with Node.js
available for script validation. The generated import file is
`dist/Bearframe_Bedrock_0.8.3_Star_Odyssey.mcaddon`.

Import the add-on and your original Star Odyssey resource pack into Minecraft.
Enable the Bearframe behavior and resource packs and the Star Odyssey resource
pack in the world. Bearframe's structures and Treasure Charts resolve texture
paths from Star Odyssey, including `textures/items/map_filled` for charts.
The original Star Odyssey pack is a separate dependency.

## Development history

The [campaign guide](docs/Bearframe_0.7.0_Campaign_Guide.md) and
[structure research notes](docs/Bearframe_0.5.0_Structure_Research_and_QA.md)
record earlier implementation and design decisions.
`tools/development-history/` preserves the iteration scripts and campaign
test sources from the 0.4.4 to 0.8.3 work. These historical scripts may expect
earlier archives, local reference assets or test stubs. Use
`tools/package_current.py` to build from the current packs.
