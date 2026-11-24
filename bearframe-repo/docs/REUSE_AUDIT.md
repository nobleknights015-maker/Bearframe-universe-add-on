# Reuse audit

Baseline is the paused local Starbound Frontier release source archive 1.3.4. SHA-256 is `6076c8516b50125e15b18656d38bc84217878899220bbfcc8c7edb3b5989ac75`. Frontier was used as a read-only reference.

| Candidate | Decision | Bearframe result |
|---|---|---|
| Native `.mcstructure` writer, random spread shape and grounded template concept | Adapt | Original relay geometry exported with the compatible writer format; garden, gate, branch and coordinates authored here. |
| Terrain approach grader | Adapt | Borrowed the original Frontier grading routine, constrained it to adding support in open space or shallow water, and use Bearframe-specific markers. |
| Rotated buried device lookup and stable vanilla hardware | Adapt | One `bearframe:relay_anchor` per site with a rotation pin and durable step state. |
| Starter campaign, offworld travel, vehicles, scanning and faction contracts | Rebuild or defer | Scope begins with one Overworld site. No Frontier identifiers, dialogue, destination list or story assets were copied. |
| Inventory debit and single shared reward patterns | Adapt | Feature-local synchronous consumption and rollback. |
| Star Odyssey and Infinity resources | Exclude | Independently installed visual packs. Only Infinity is a compatibility target for this checkpoint. |

## Worldbuilding research applied

The November 23 Starbound Frontier worldbuilding study and implementation notes informed this pass. Each biome receives a distinct material palette and former function. Street networks lead to interiors instead of ending at isolated facades. Clues use damaged infrastructure, accent lighting and short records. Test a true approach and repair on generated terrain, including fluid interference and headroom, before claiming a structure is playable. This project samples Infinity's native texture scale as a separate visual dependency, with no redistribution of Star Odyssey or Infinity.

## Spillway 0.4.1

The four project-owned industrial tiles are copied from the original 1.3.4 Starbound Frontier resource pack, under `textures/sf/blocks/`. Bearframe stores copies under `textures/bearframe/spillway/` and registers them in its own atlas. No Frontier script, pack identity or worldgen seed is required.

| Tile | Role | SHA-256 |
|---|---|---|
| `bulkhead.png` | Machinery casing | `e128552058a9a05279f7093e83b0b7c628992099e69af15c76008f154bd59b2d` |
| `grate.png` | Dry service grates | `6246e9a42446bd78d321bdad3bbe4a689214ee781eec7d2509a1bc8a5e648d3e` |
| `luminaire.png` | Flush service lights | `223d1117e0abcb49f559e7b8a894b95255d88723dd8db5973b9051dd926c66e2` |
| `power_conduit.png` | Survey datum | `e960ce92a032612ddfee7a77f08257032315fc991ae0bb9185e39e7c7d7d6ba4` |
