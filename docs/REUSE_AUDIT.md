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
