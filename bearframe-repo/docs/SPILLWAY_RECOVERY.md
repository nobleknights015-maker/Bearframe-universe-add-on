# Spillway recovery audit

The recovery started at GitHub `5d34079`, which includes Gemini's `08a12d2` expansion. The Android screenshots showed two separate defects. The Spillway's old jigsaw template used `beard_box` around a single tall rectangular shell. The surface projection could put the shell across a ravine. Ceiling lamps also occupied the stair walking volume. The Farfield Surveyor had a large rectangular face panel with square optics and prominent brass bands.

## Facility

Spillway 04 was a gravity-fed waterworks addition to a legacy industrial site. The intake lost pressure and the crew isolated the bypass before evacuating. The dry concourse links a stepped surface service pavilion, a tall pump hall with a retained pool, an operations room with a shift record, a maintenance workshop and a separately gated stock cage. Floor colors identify the public route, pump corridor and workshop. Recessed lights, support frames, floor grates, pipe runs, a map bench and isolated equipment establish each room's former use. Farfield is surveying the ruin in the add-on's optional discovery. It has no bearing on the novel's timeline.

The native structure set keeps the prior spacing and salt. Its small survey datum can generate in forest or plains. The repairable facility appears only after loaded terrain passes a bounded siting survey. It can move up to 24 blocks per horizontal axis from the datum. Only a shallow graded cap and the stairs displace surface terrain. The main rooms require natural cover and foundation layers. The check rejects construction materials, block inventories, tree trunks, open ravine floors and exposed roofs. Bedrock does not expose a universal player-placed flag for ordinary terrain such as natural stone or dirt, so test in new chunks. Failed sites keep the original terrain and a small datum. A generated site from an earlier pack version remains as saved.

## Farfield

Revision 4.10 and the approved visual handoff govern the individual chassis, chest core/display, technological side-head displays, independent Farfield role under Mira and nonhumanoid Ghost Grid machinery. This pass preserves the Surveyor's identifier, trade, dialogue and locomotion channels. The new-player-scale chassis uses ceramic plate sections, dark joint gaps, an inset optical band, a Farfield badge and asymmetric field equipment. The two display modules are low-profile technical hardware. The previously implemented Grid walker, watcher, turret, hauler and guardian meshes remain distinct. The new bunker assigns the existing walker and hovering watcher to different parts of the pump area.

## Verification

- **Automated checks:** 21 tests cover the shipped layouts, mechanical links, model bounds, display surfaces and asset references. The pack builder also validates JSON, JavaScript, PNG dimensions, UV bounds, entity references and manifests.
- **Bedrock Dedicated Server 1.26.63.1:** Native survey datum in seed 13221951 built at template origin `(6, 72, 14)`. Both the natural site and a controlled fixture passed the in-engine route and headroom checks, signs and water containment. The controlled fixture rejects an occupied block inventory and missing floor support. The probe verifies the power charge, gate, one-time salvage, both Ghost Grid machines, one Farfield Surveyor and persistent state after a restart.
- **Android client check pending:** Import, hand-walk the route and check the approach, sign readability, Farfield rendering and animations on the handset. Repeat with Infinity Sci-Fi active below Bearframe Resources if you use it. The server probe queries terrain and entity state, so it does not evaluate client lighting, touch controls or framerate.
