# Bearframe Clean Base 0.1.0

Independent clean source-tree checkpoint, not a continuation of the Last Dispatch campaign. No old project files are inherited in this tree. The previous development branch remains untouched.

Rebuild with Python 3, json5, Node.js and the exact four private/user-supplied input archives listed in INPUTS.json:
`python rebuild_from_inputs.py /path/to/input_archives`

This repository stores the reproducible build recipe, not the redistributable third-party binary assets. The complete extracted source and an independent root-commit Git bundle were delivered separately in the development chat. The verified local bundle commit is ba29c34f5a561d801ca39d7f238204a38b438aeb. The installer SHA256 is 07d4d90ba5d4e824d7450117c06ef1d8c4817a4d0baa843a130f2a2e205ec5e4. ZIP timestamps may vary on reconstruction.

Scope: original Overgrown Cities 1.3 overgrown preset (536 templates, one structure set); Rarity Stats BP v19.4; Chest Loot; nine bosses, 34 other custom NPC/mob definitions, four combat-effect entities and 27 vanilla appearance overrides. Native regular faction spawn rules retained. Bosses and named NPCs can be manually summoned for testing. No old Bearframe quest, station, custom dimension, weapons, custom blocks, additional structure generators or scripted patrols. Original city generation does not suppress Minecraft's native structures.

Compatibility repairs: 12 jigsaw final-state corrections, invalid deepslate identifiers, duplicate city processor and unused invalid template-pool fragment. Original city loot references missing mods; use audited vanilla-only tables. Rarity resource pack not supplied: fallback vanilla icons, simple forms and anvil; removed two unregistered signature item custom components. Chest Loot namespace rrs; omitted unnecessary old player override. Rarity scoreboard/invalid entity guards. Custom boss loot temporarily uses vanilla valuables.

Fresh UUIDs. Static validation passed locally (ZIP, JSON/JSONC, Node syntax, relative imports and custom resource/loot references). Live Bedrock/Android gameplay NOT verified. Test fresh world with only this pair before enabling Star Odyssey; verify Active build 0.1.0, all reskins, boss idle/walk/attacks, /rrs:stats and /rrs:chestloot. Do not add back old systems until baseline passes.
