# Building a pack around Bearframe: The Last Dispatch

## One import

Import `Bearframe_The_Last_Dispatch_0.10.1.mcaddon` and activate its behavior
and resource packs. Choose a mode in the Bearframe resource pack settings.

| Mode | What it changes |
|---|---|
| Compatibility | Uses bundled Bearframe textures and leaves vanilla mobs available for other appearance packs. Select this for mixed worlds. |
| Bearframe mob visuals | Gives selected vanilla mobs Bearframe appearances. |
| Star Odyssey materials | Uses the original Star Odyssey pack's materials on Bearframe structures. |
| Star Odyssey materials + Bearframe mobs | Enables both appearance options. |

Keep the original Star Odyssey resource pack active below Bearframe when using
either Star Odyssey mode. The Compatibility and Bearframe mob visuals modes use
bundled materials. If you installed the separate 0.10.0 Mob Visuals or Bridge
pack, deactivate them in the world so the selected 0.10.1 mode controls the look.
The behavior and resource pack UUIDs and the `bearframe:` content IDs carry
forward for existing worlds.

## Dependencies and namespaces

| Dependency | UUID | Version |
|---|---|---|
| Core behavior | `ee5e4ba0-f2dc-594a-bcaf-248e7f41559f` | `[0, 10, 1]` |
| Core resources | `57aabde7-cd63-5995-b00d-a69f983ba905` | `[0, 10, 1]` |

For example, an extension that relies on Bearframe gameplay can declare this
entry in its manifest dependencies:

```json
{"uuid":"ee5e4ba0-f2dc-594a-bcaf-248e7f41559f","version":[0,10,1]}
```

Give your pack its own UUIDs and use your own namespace for entities, items,
structures, feature rules, textures, and dynamic properties. Content you can
refer to by ID includes `bearframe:city_orbit`, `bearframe:field_log_pad`,
`bearframe:teleport_tablet`, and `bearframe:grid_repair_crawler`. Campaign
state, station build flags, and survey markers are internal implementation
details. The station is managed by Bearframe transit and construction scripts.

The main conflict surfaces are packs that replace the same vanilla client
entities, modify the same campaign or station locations, or heavily alter
terrain around structure candidates. Test each pack combination in a fresh
world and in a copy of an upgraded world. Check discovery, the Field Log,
station travel, and the other packs' main interactions before publishing.
