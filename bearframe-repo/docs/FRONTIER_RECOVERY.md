# Frontier recovery 0.4.2

## Baseline and imports

The starting GitHub commit was `251ed1a`. The Android shoreline screenshot matched the Directorate checkpoint layout. An earlier Bedrock log for seed 13221951 showed its old console at `(8,61,422)` and water in both open gate blocks. Version 0.4.1 had already replaced Spillway placement, but the checkpoint still used the older native platform.

The Forgotten Frontier upload has its own pack UUIDs and an independent namespace. It ships towns, bunkers, faction sites and a separate station. Its manifest also contains a larger design prompt. The Synthetic Frontier upload is another independently named pack with seven generated roles. Its behavior includes borrowed vanilla routines such as village pathing and spider-style climbing. These are treated as references for the requested location and role mix. No files from either export are redistributable dependencies or included in the new release.

## Placed world generation

The maintenance relay, five regional sites and both existing towns now start as one native survey block. The script waits for loaded chunks and looks for dry support beneath the entire footprint, dry clearance in the construction envelope, and a three-wide walk-in approach. It rejects existing block inventories, non-terrain blocks, water, and unsupported edges. The templates contain two buried footing layers. The runtime can use up to two blocks of shallow backfill over natural support, with a bounded search for a different center. No high retaining wall is poured across a ravine or the sea. Existing worlds retain generated blocks. The default site search is deliberately conservative, and a native survey point can be skipped.

The rebuilt Directorate checkpoint has a tiered gatehouse, an inspection lane, a separate maintenance bay, the existing salvage cage and a three-copper repair sequence. It can generate in plains or savanna. Existing Spillway siting still governs that bunker. Signal Shelter retains its earlier template and its designed flooded section. Bearframe City still uses the dedicated orbital transit sequence.

## Roles

| Role from the export | Implemented appearance and habitat |
|---|---|
| Bearframe Researcher | Farfield Researcher, player-scale pale armor, individual survey apron, assay cassette, chest and side-head displays. Survey camp. |
| Nullframe Guard | Directorate Gate Guard, uniform silver plate, narrow red optics and a watchful hail. Checkpoint. |
| Hollow Line Drone | Broad, mass-produced actuator armor and integrated forearm equipment. Checkpoint. |
| Hunter Tracker | Low-reflectivity Watchtower-defector profile, sensor fins and split trailing armor. Saltline patrol. |
| Echo Drift | Patched Echo Drifter, disrupted optics, uneven armor and a makeshift knee brace. Shelters and abandoned settlements. |
| Ghost Grid Repair Crawler | Low six-legged service chassis with paired probes and an alternating gait. Foundry annex. |
| Ghost Grid Protocol Keeper | Tri-thruster legacy machine with a separate scanning mast. Switchyard. |

Models and textures are original Bearframe assets. Roles use authored spawn positions, existing expedition crew persistence and bounded ambient populations. The Ghost Grid inspections frame them as discoveries whose origin is unresolved. There is no new canonical timeline event.

## QA

- **Static validation:** 31 tests and the pack validator cover placement templates, manifests, mob registrations, geometry, UVs, animation bone bindings, and pack contents.
- **Bedrock Dedicated Server 1.26.63.1:** Reproduced the old shoreline seed, confirmed the old submerged checkpoint did not build, and located a naturally generated dry checkpoint at the new candidate. A controlled fixture exercised rejection of floodwater, an unsupported edge and an existing inventory. It also verified gate spending, dry passage, all seven registrations, repeated greeting without duplicate crew, and one-time salvage. Save/reload was checked in a subsequent server session.
- **Client check pending:** Use Android to verify the on-device import, real rendering, animation, and touch traversal. The model preview is an offline render using the shipped JSON and textures.
