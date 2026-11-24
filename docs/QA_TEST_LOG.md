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
