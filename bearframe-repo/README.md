# Bearframe Bedrock 0.4.1 — Spillway Recovery

A Bearframe Universe survival add-on for Minecraft Bedrock. This recovery release rebuilds the Spillway Waterworks bunker and the Farfield Surveyor. It keeps the existing expedition, repair, salvage, and orbital travel systems.

## Install on Android

1. Download `Bearframe_Bedrock_0.4.1.mcaddon`. It contains both packs.
2. Open the file from **Files → Downloads** and choose **Minecraft**. If the file ends in `.mcaddon.zip`, remove the extra `.zip` before opening it.
3. Open the settings for a new or copied world. Activate **Bearframe | Behavior**, and confirm **Bearframe | Resources** is active under Resource Packs. Use the 0.4.1 version of both.
4. If you use Infinity Sci-Fi, put it below Bearframe Resources. The add-on includes its own models and structure materials.

Windows users can open the same file with Minecraft for Windows. The manifests require Bedrock `1.26.50` and the stable `@minecraft/server` `2.10.0` module. The pack has no experimental API dependency.

## Find the rebuilt bunker

For a repeatable Android test, create a new world with seed **13221951**. Visit the surface around **X 32, Z 32** to load the area. The server-tested entrance is near **X 8, Y 93, Z 32**, facing west. An existing world can generate the revised bunker in new chunks. Previously generated sites keep their original blocks.

With optional cheats, `/locate structure bearframe:spillway_bunker` finds a survey point in new terrain. The entrance can be offset from that point while the script checks the slope. If there is no suitable terrain in range, the point stays unbuilt. It can take a few seconds after both sides of a site load.

Descend the two five-block-wide flights to the concourse. Look for the pump hall, operations room, workshop and caged stores. Bring two redstone dust to repair the power console in Survival and claim the salvage. The Farfield Surveyor is stationed in operations.

## Development and verification

From `bearframe-repo/`:

```sh
npm install
python3 tools/make_content.py
npm run worldgen
npm test
python3 tools/build.py dist
```

The recovery probe in `tests/server_spillway_probe.js` exercises real Bedrock terrain generation and Script API behavior in a disposable world. See [the recovery notes](docs/SPILLWAY_RECOVERY.md) for the audit, tested scenarios and remaining Android visual checks.
