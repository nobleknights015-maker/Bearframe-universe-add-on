# Bearframe Bedrock — Asset Provenance & Licensing (v0.4.1)

## 100% Original / Project-Owned Assets

Bearframe-owned artwork and code are generated from the source in this repository. Four additional industrial tiles come from the separate project-owned Starbound Frontier pack.

- **Entity Textures (20 × 128×128 PNGs), Item Icons (6 × 32×32 PNGs), Block Texture (1 × 32×32 PNG), Pack Icons (2 × 128×128 PNGs):** Generated directly by `tools/make_content.py` using a zero-dependency pure-Python RGBA PNG encoder.
- **Entity Geometries (20 `.geo.json`), Animations (72 clips across 20 `.animation.json`), Animation Controllers (2 `.json`), Render Controllers, Client Entities, Behavior Entities, Items, Recipes, Loot Tables, Spawn Rules:** Generated directly by `tools/make_content.py`.
- **Structures (12 `.mcstructure`) & Worldgen Jigsaw Definitions:** Generated directly by `tools/worldgen.mjs` and `tools/ruin_layouts.mjs` and `tools/spillway.mjs`.
- **Scripting API Logic (`@minecraft/server` 2.10.0):** Original JavaScript modules in `behavior_pack/scripts/`.

## Strict Third-Party & Separate Project Boundaries

- **Infinity Sci-Fi Resource Pack:** Strictly external and optional. Users who own Infinity Sci-Fi may stack it **below** `Bearframe | Resources` in Bedrock. Zero licensed textures, models, sounds, or manifests from Infinity Sci-Fi are included or redistributed here.
- **Starbound Frontier:** The original add-on is untouched. The four tiles reused in Spillway are listed with checksum and source in the [reuse audit](REUSE_AUDIT.md).
- **Automated Enforcement:** `tools/build.py` fails the build if any filename under `behavior_pack/` or `resource_pack/` contains `starbound` or `infinity`.
