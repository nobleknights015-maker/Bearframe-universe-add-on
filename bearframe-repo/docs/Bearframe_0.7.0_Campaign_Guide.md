# Bearframe Bedrock 0.7.0
## The Last Dispatch

An abandoned relay still asks someone to keep a bunk warm. Farfield sends you to learn who made the request. The trail leads through an old evacuation network, Echo testimony, a Directorate recovery expedition, and a route that no longer reaches its destination. The finale asks what the station should do with a signal that still works.

### Start the campaign

1. Find **Farfield Survey Camp** in the Overworld. Sneak-interact with its cartography table to board for Bearframe Station.
2. Enter the **Farfield Annex**, find **Mira**, and sneak-interact with her. Open **Main campaign**, then accept the assignment.
3. At any department lead, sneak-interact for the dossier. Use the main tab to see the chapter, objectives, and debrief contact. The field directory gives each site's biome and records exact coordinates after you inspect it. Regular interaction still gives the lead's ordinary dialogue.
4. On the surface, interact with existing named terminals or the new **Farfield Record Readers**. Sneak-interact with a record reader to show the current main objectives in chat. If an objective says *repair or verify*, interact with the terminal after the circuit is live. Network repairs are shared by everyone in the world. Individual players get credit when they inspect the working terminal.
5. Return to the indicated lead for each debrief. Leave room for the reward stacks. The station return desk uses your recorded surface berth.

This campaign fits the existing survival world. You can gather tools, build, trade, open the existing randomized chests, and advance side cases while following the main story. The directory gives guidance for undiscovered sites. It does not know an undiscovered structure's coordinates. The larger sites keep their existing natural-generation rules, so how far you travel will vary by seed.

### What is playable

| Content | Scope |
|---|---|
| Main campaign | Seven chapters, field evidence, Echo testimony, two repair checks after the opening investigation, a physical test-bench puzzle in the Spillway service wing, a dispatch decision, and a final return to the field |
| Side cases | Six authored cases with their own briefings, goals, debriefs, and rewards |
| Repeatables | Mira commissions surveys, Atlas commissions circuit checks, and Sentinel posts anti-Directorate field patrols. Contracts count activity after acceptance. A site can count only once per active survey or maintenance contract. |
| Loot | Chapter and case rewards, repeatable payments, and the existing 61 random ruin chests |
| Choice | The dispatch decision changes the epilogue response and gives a small bonus to either survey or maintenance contracts after the campaign |
| Multiplayer | Evidence, chapter, choice, journal coordinates, active contracts, and payout status are stored per player. Structure repairs are shared and can be verified by each player. |

The expansion and return desk are inherited from the previous pack. For an existing test world, explore **newly generated sites** for the record readers added in this release. Already built Spillway service wings can get the test bench when you verify the pump, provided the wing and mounting blocks are present and clear. A substantially older Spillway without the service wing needs a newly generated facility.

### Modpack comparison

- **Prominence II: Hasturian Era.** Downloaded the author's Modrinth release archive and inspected its FTB Quests configuration. It contained 30 quest chapter files and 15 separate reward tables. Early onboarding, the main story, the later Hasturian chapter, and collection tracks use separate task and reward definitions. Bearframe uses a short onboarding route, a single readable main thread, and side and repeatable systems that can run independently. [Project](https://www.curseforge.com/minecraft/modpacks/prominence-2-hasturian-era) · [Modrinth release page](https://modrinth.com/modpack/prominence-2-fabric)
- **Blightfall.** Downloaded the Technic server archive and verified that it ships authored region files and a separate Hardcore Questing Mode database. Its map and mission locations are part of the premise. Bearframe similarly uses its distinctive places as evidence, while placing them through the existing procedural Overworld rather than shipping a fixed world. [Technic project](https://www.technicpack.net/modpack/blightfall)
- **Material Energy^5: Entity.** Reviewed the release and map-based progression reference. Its useful comparison here was concentrating a test inside an authored space. The Spillway service wing houses an ordered three-console check that follows the existing pump repair. [Project](https://www.curseforge.com/minecraft/modpacks/material-energy-5-entity)
- **DawnCraft: Echoes of Legends.** Reviewed the project description for its dedicated quest and reputation systems. Bearframe keeps threats tied to its own lore and exposes patrols as repeatable work. Completing hostile contracts does not require attacking Echo residents or Ghost Grid units. [Project](https://www.curseforge.com/minecraft/modpacks/dawn-craft)

The Java archives were inspected as design references. Their maps, assets, scripts, characters, and quest text are absent from the Bedrock add-on.

### Verification

The package passed JSON and JavaScript parsing. All 11 new archive readers were placed in reachable cells, with the original loot container data verified unchanged. The packaged JavaScript passed a mocked end-to-end progression through all seven chapters, including an early turn-in rejection, calibration reset, a policy choice, closing the dossier, a side-case reward claimed once, separate player saves, repeatable contract de-duplication, and the policy-specific payment bonus. Live Bedrock tests remain open for form display, world generation, travel, chest loot, repair events, and the full journey on Android.
