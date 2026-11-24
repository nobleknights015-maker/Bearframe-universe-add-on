# Bearframe Bedrock — Structure Bible (v0.4.0)

All 11 `.mcstructure` templates are generated deterministically by `tools/worldgen.mjs` and `tools/ruin_layouts.mjs`, serialized as little-endian Bedrock NBT, and mathematically verified by `tests/layout.test.mjs`, `tests/regions.test.mjs`, and `tests/ruins.test.mjs`.

## 1. Orbital Hub — Bearframe City (`orbital_city.mcstructure`)

- **Dimension:** `bearframe:city_orbit` (void orbital station around the salvage planet).
- **Dimensions:** Expanded in `0.4.0` from `44×8×23` to **`60×8×23`** (`CITY_SIZE`) while keeping `x=0..43` identical so existing arrival (`CITY_ARRIVAL`), return desk (`CITY_EXIT`), and 0.3.0 staff stay compatible.
- **All 6 Canonical Departments Staffed:**
  1. **Mira — Farfield Dispatch** (`x=11..26, z=2..8`, cyan bay): `farfield_surveyor`
  2. **Penney — Community & Culture Commons** (`x=11..26, z=14..20`, pink bay with greenery): `city_steward`
  3. **Auren — Systems Engineering** (`x=28..41, z=2..8`, blue bay): `city_engineer`
  4. **Sentinel — Watchtower Security** (`x=28..41, z=14..20`, red bay): `city_watch`
  5. **Atlas — Production, Maintenance & Combat** (`x=43..58, z=2..8`, orange bay + concourse): `atlas_rigger` (bay) and `atlas_vanguard` (concourse at `x=45.5, z=0.5`)
  6. **Vera — Visual Production Studio** (`x=43..58, z=14..20`, purple bay): `vera_artisan`

## 2. Overworld Survey & Regional Sites (6 Structures)

| Structure ID | Biome | Primary Actor | v0.4.0 Escorts | Gameplay |
|---|---|---|---|---|
| `maintenance_relay` | `plains` | `farfield_surveyor` | `grid_walker`, `hollow_scout` | 3-phase power circuit repair -> `relay_schematic` |
| `farfield_camp` | `plains` | `farfield_surveyor` | `atlas_rigger`, `atlas_vanguard` | Survey dispatch, orbital transfer, alloy reclamation |
| `grid_hub` | `forest` | `grid_walker` | `grid_watcher` (hover), `grid_turret` | Switchyard isolation -> copper, amethyst, `legacy_cell` |
| `echo_ward` | `taiga` | `ward_resident` | `echo_sentinel` (stabilizable) | Auxiliary lighting -> iron, gold, `salvaged_alloy` |
| `intrusion_checkpoint` | `savanna` | `hollow_scout` | `directorate_officer`, `hollow_breacher` | Bypass gate (triggers Directorate escalation!) -> redstone, iron, `salvaged_alloy` |
| `foundry_annex` | `desert` | `grid_hauler` | `grid_guardian` (dormant heavy) | Material handler power -> iron, copper, `salvaged_alloy` |

## 3. Overworld Ruins (4 Larger Structures)

| Structure ID | Size | Biome | Primary Actor | v0.4.0 Escorts |
|---|---|---|---|---|
| `spillway_bunker` | `36×25×23` | `forest` | `grid_walker` | `grid_watcher` (hover) |
| `shelter_bunker` | `36×25×23` | `taiga` | `ward_resident` | `echo_drifter` |
| `rainline_town` | `37×21×31` | `plains` | `grid_hauler` | `echo_drifter` |
| `saltline_town` | `37×21×31` | `desert` | `directorate_officer` | `hollow_scout`, `hollow_breacher` |

Every primary spawn, landing pad, and escort offset is verified in automated tests to have clear 2-block vertical air headroom and solid floor support (for non-hover units).
