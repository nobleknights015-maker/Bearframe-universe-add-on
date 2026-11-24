# 0.2.0 world and travel checks

Bedrock Dedicated Server 1.26.63.1 generated and located all six surface types in the regular Overworld. The first checkpoint attempt exposed a waterlogged seal in the river at X 8, Z 422. The expansion checkpoint now uses the surface projection and drains waterlogged bars during a successful bypass. The clean retest opened that seal and collected the stores once.

- The final live probe covered five new native sites and their unique residents, four separate repair and reward sequences, the generated camp, the orbital city and a same-berth round trip. One camp and switchyard approach and four approaches at the ward and annex graded on the test seed. The checkpoint test cleared the interior, but no approach graded there. Terrain and construction clearance govern which approaches can be built.
- Seven resource models/identifiers and their texture and animation references were validated. Nine offline tests checked foundations, device stamping, entry floors, biome filters and the supported city arrival.
- The same probe issued one insignia after six survey records, and a repeat report left the inventory unchanged.
- Transport uses a real in-server entity as a player stand-in; repair and claim use real in-game inventories. No graphical Bedrock client or live two-player session was available. Handheld rendering, user steering and touch inputs, client performance, Realms and console remain unverified.

The runtime probe is `tests/server_world_probe.js`. Run only on disposable seed 13221951. It places fixture blocks, repairs sites, and consumes their shared rewards.

# QA test log

Bedrock Dedicated Server 1.26.63.1, stable server module 2.10.0. Loaded the distinct Bearframe packs and used the attached Infinity v1.0.9 resource pack separately in the test world. Native jigsaw structure placement used the regular Overworld seed 13221951, terminal X -202, Y 68, Z 168, rotation 180°. Three offline tests verified the template, phase hardware, doors, interior routes and separated recovery room.

## Observed on the server

- Vanilla locate found the native relay. Its runtime marker, standing spaces and foundation resolved at the rotated in-world coordinates.
- A first runtime repair exposed an invalid Bedrock copper block ID. The rerun used the registered `minecraft:waxed_cut_copper`.
- The initial generated terrain exposed a drop between the deck and surrounding terrain. The amended entrance grader constructed one supported approach on the test seed without removing any solid terrain blocks. The other exits depend on local terrain.
- Native spawning produced one surveyor, one legacy walker and one Hollow scout. A second activation pass produced no duplicates.
- Two real in-game barrel inventories represented two players in the scripted probe. The copper debit, obstruction guard, redstone debit, functional lights, closed/then open gate, sole schematic and ordinary barrel isolation all passed.
- Restart restored phase 3, the opened gate and the lit circuit. The scripted probe lives in `tests/server_probe.js`. Append it to the loaded `scripts/main.js` only in a disposable test world with the indicated seed. The probe consumes resources and changes its fixture world.

## Still unverified

No graphical Bedrock client was available for model visibility, animation appearance or texture layering. No live two-player clients joined. Attack behavior against a live player, handheld import and frame rate, Realms and console loading still need a direct playtest. The test seed exercises one rotated generation, and it does not certify every plains placement.

## Technical references

- [Microsoft Bedrock world generation](https://learn.microsoft.com/en-us/minecraft/creator/documents/world-generation?view=minecraft-bedrock-stable)
- [Microsoft Bedrock native structure sets](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/worldgenreference/examples/jigsawstructuresets?view=minecraft-bedrock-stable)
- [Microsoft Bedrock Script API events](https://learn.microsoft.com/en-us/minecraft/creator/documents/scripting/events?view=minecraft-bedrock-stable)
