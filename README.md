# Bearframe Bedrock 0.2.0 · Farfield Survey

Explore the planet beneath orbital Bearframe City in ordinary Minecraft Survival. Six biome-linked surface sites have their own stories, interiors and jobs. A Farfield camp connects to the orbital city as a separate destination. The encounters and locations are gameplay interpretations.

## Install

- **New, ready-to-explore world**: Open `Bearframe_Farfield_Arrival_0.2.0.mcworld`. It starts near the camp with both packs included.
- **Your own world**: Open `Bearframe_Bedrock_0.2.0.mcaddon`, then activate **Bearframe | Behavior** and **Bearframe | Resources**. New sites appear in newly generated chunks. Back up existing saves before updating. Use Bedrock 26.50 or newer.
- **Optional Infinity look**: Install your own Infinity Sci-Fi pack separately and place it below **Bearframe | Resources**. Both downloads work with stock resources.

## Explore

| Site | Biome | Activity |
|---|---|---|
| Farfield Survey Camp | Plains | Use the cartography table to log the camp. Sneak-interact on it for the ride to Bearframe City. |
| Maintenance Relay | Plains | Fit the breaker with 2 copper ingots, mine its cobblestone debris and reconnect with 1 redstone dust. |
| Overgrown Switchyard | Forest | Isolate the switches with 2 redstone dust to open service stores. |
| Legacy Support Ward | Taiga | Talk to the ward resident. Bring 2 iron ingots to restore auxiliary fixtures, then retrieve ordinary supplies. |
| Directorate Checkpoint | Savanna | Beware the perimeter scout. Use 3 copper ingots to bypass the service seal. |
| Ruined Foundry Annex | Desert | Bring 2 coal to run the material handler and access reclaimed stock. |
| Bearframe City | Orbit | Visit Farfield Dispatch, Commons, Systems and Watchtower. Use the lodestone at the arrival bay to return. |

Use each surface site's interaction terminal to fill your personal survey log. Sneak-interact with **Farfield Dispatch** aboard the city to see progress and claim your insignia after all six sites. Site stores are communal and yield their supplies once per structure.

### Quick route on the included seed

Seed `13221951` on the tested server version. Approximate X, Z locations are camp `-294, 72`, relay `-202, 168`, switchyard `582, -312`, ward `38, -648`, checkpoint `8, 422`, and annex `-186, 1224`. With commands enabled, `/locate structure bearframe:farfield_camp` and the other native IDs in `docs/STRUCTURE_BIBLE.md` will find sites on alternate seeds.

## Source

Run `npm install`, `npm run worldgen` and `npm test`. Regenerate original PNG and entity assets with Pillow and `python3 tools/make_content.py`. Build with `python3 tools/build.py ./dist`; pass `--world PATH` for a packaged starter save. The source archive includes the models, tests, canon ledger, original textures and a Git bundle when built from the source checkout.
