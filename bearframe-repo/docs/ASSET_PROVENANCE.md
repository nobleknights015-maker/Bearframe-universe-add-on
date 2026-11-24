# Bearframe Bedrock — Asset Provenance & Licensing (v0.4.0)

## 100% Original / Project-Owned Assets

Every file inside `behavior_pack/` and `resource_pack/` is 100% original and deterministically generated from project source code:

- **Entity Textures (20 × 128×128 PNGs), Item Icons (6 × 32×32 PNGs), Block Texture (1 × 32×32 PNG), Pack Icons (2 × 128×128 PNGs):** Generated directly by `tools/make_content.py` using a zero-dependency pure-Python RGBA PNG encoder.
- **Entity Geometries (20 `.geo.json`), Animations (72 clips across 20 `.animation.json`), Animation Controllers (2 `.json`), Render Controllers, Client Entities, Behavior Entities, Items, Recipes, Loot Tables, Spawn Rules:** Generated directly by `tools/make_content.py`.
- **Structures (11 `.mcstructure`) & Worldgen Jigsaw Definitions:** Generated directly by `tools/worldgen.mjs` and `tools/ruin_layouts.mjs`.
- **Scripting API Logic (`@minecraft/server` 2.10.0):** Original JavaScript modules in `behavior_pack/scripts/`.

## Strict Third-Party & Separate Project Boundaries

- **Infinity Sci-Fi Resource Pack:** Strictly external and optional. Users who own Infinity Sci-Fi may stack it **below** `Bearframe | Resources` in Bedrock. Zero licensed textures, models, sounds, or manifests from Infinity Sci-Fi are included or redistributed here.
- **Starbound Frontier:** Separate paused add-on project; zero files from Starbound Frontier were modified or redistributed. Only general NBT serialization conventions documented in v0.3.0 remain in `tools/worldgen.mjs`.
- **Automated Enforcement:** `tools/build.py` fails the build if any filename under `behavior_pack/` or `resource_pack/` contains `starbound` or `infinity`.
