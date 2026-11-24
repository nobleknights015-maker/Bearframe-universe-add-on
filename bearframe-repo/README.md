# Bearframe Bedrock 0.4.3 — Frontier Recovery

A Bearframe Universe survival add-on for Minecraft Bedrock. This release reviews both Frontier site exports and rebuilds the useful concepts in the maintained Bearframe project. It restores dry siting for eight existing surface locations, rebuilds the Directorate checkpoint, and adds or updates seven original synthetic roles. Version 0.4.3 fits all 17 humanoid NPCs to player proportions while preserving faction-specific 3D armor, equipment and displays. Ghost Grid keeps its machine geometry.

## Install on Android

1. Download `Bearframe_Bedrock_0.4.3.mcaddon`. It contains both packs.
2. Open it from **Files → Downloads** with **Minecraft**. If Android adds `.zip` after `.mcaddon`, remove the extra extension.
3. Activate **Bearframe | Behavior** in a fresh world or a copy of your world. Check that **Bearframe | Resources** is activated and both list 0.4.3. Disable the separately imported Forgotten Frontier and Synthetic Frontier packs in the test world so their old content does not also generate.
4. If you use Infinity Sci-Fi, place it below Bearframe Resources. The add-on supplies its own models, textures, and structure materials.

The same archive can be opened with Minecraft for Windows. The manifests declare Bedrock `1.26.50` and stable `@minecraft/server` `2.10.0`. There is no experimental API dependency.

## Find a test site

Use a new world with seed **13221951**. The terrain checks run automatically when you approach the native survey point.

- **Directorate checkpoint:** Visit the surface near **X -240, Z 2368** first. The tested checkpoint centered near **X -252, Y 70, Z 2404**. You can bring three copper ingots to the console to bypass the gate. Nearby guards warn or escalate and the salvage can be claimed once.
- **Spillway Waterworks:** Visit near **X 32, Z 32** first, then approach the entrance near **X 8, Y 93, Z 32** from the west. Its enclosed pump basin is intentionally flooded. The primary route is dry.

With optional cheats, `/locate structure bearframe:intrusion_checkpoint` finds a survey point. The building can move up to 36 blocks per horizontal axis to reach dry, stable ground. Unsafe candidates are skipped. The new placement logic affects unexplored chunks. Previously generated flooded sites remain as saved.

## Development and verification

From `bearframe-repo/`:

```sh
npm install
python3 tools/make_content.py
npm run worldgen
npm test
python3 tools/build.py dist
```

See [Frontier recovery notes](docs/FRONTIER_RECOVERY.md) for the attachment audit, role map, and verification.
