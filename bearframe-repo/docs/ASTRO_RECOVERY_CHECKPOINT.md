# Astro station recovery — development checkpoint
Base: release/last-dispatch-0.11.15 at d8f676b791909bbf4dae9c7e6d9ceb37866e726d.
The original release and its installer are unchanged. This is a development branch, not a published 0.11.16 package.

Changes:
- On an occupied section whose completion marker is missing, compare each authored structure cell's block type, permutation states and waterlogging to the loaded world, yielding every 512 scanned cells. Omitted sparse cells are ignored and are not rewritten. If the section matches, restore only the completion marker. If it does not match, preserve all existing blocks and report the failing section and coordinate. This does not auto-repair partially placed sections or validate block-entity contents; it deliberately avoids overwriting them.
- Lift interactions give a clear error when the landing is blocked or the teleport fails; chunk-loading errors are also reported. Serialize per-player transit to prevent overlapping lift tickets.
- Correct stale npm metadata to the current 0.11.15 baseline.
- Add isolated regression tests. Nine targeted mock scenarios passed when executing the committed helper in a JS isolate; full Node suite and real Bedrock testing have not been run here.

Client/server acceptance: on a disposable copy of the world, interrupt placement after the structure is placed but before its marker is set, then use the tablet twice. Check no containers or players' builds were overwritten. Repeat with mismatched authored cells, unloaded cells, a blocked lift, cleared lift, failed teleport, and concurrent users. Confirm Bedrock runtime returns matching permutations on actual sparse station sections; mutable block states can produce conservative rejection and must not be force-reset. Test Android client with Star Odyssey, station walk-through, re-entry, surface return, and timing.

Remaining work: Mowzie's Mobs full rig/animation/attack integration for all eight Ghost Grid and Echo Frame bosses, not just timing approximations; recover exact source inputs and mapping, preserve custom visuals and rewards. Exact Rex RPG Quest and RPG Loot mechanics, structure integration, first/third-person grip verification, shoreline/update-block reproduction, and mobile/live multiplayer QA still open. Do not repeat completed Astro conversion or assume earlier server fixtures prove client quality.
