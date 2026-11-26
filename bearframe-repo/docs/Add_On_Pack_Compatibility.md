# Building a pack around Bearframe: The Last Dispatch

## One import

Import `Bearframe_The_Last_Dispatch_0.10.5.mcaddon` and enable its behavior
and resource packs. Bearframe's vanilla mob makeovers and original sci-fi structure
materials are included and active by default. Existing Bearframe pack and content IDs
carry forward when updating.

## Dependencies and namespaces

| Dependency | UUID | Version |
|---|---|---|
| Core behavior | `ee5e4ba0-f2dc-594a-bcaf-248e7f41559f` | `[0, 10, 5]` |
| Core resources | `57aabde7-cd63-5995-b00d-a69f983ba905` | `[0, 10, 5]` |

For example, an extension that relies on Bearframe gameplay can declare this
entry in its manifest dependencies:

```json
{"uuid":"ee5e4ba0-f2dc-594a-bcaf-248e7f41559f","version":[0,10,5]}
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
