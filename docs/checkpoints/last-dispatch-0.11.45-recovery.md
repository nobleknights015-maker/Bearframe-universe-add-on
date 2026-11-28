# Last Dispatch — 0.11.45 local recovery checkpoint (2026-11-27)

Previous verified branch HEAD: f4c4241394c812b254670f0f41dc095c2da747ea (0.11.25).

The latest complete local installer is Bearframe_The_Last_Dispatch_0.11.45_Held_Arsenal.mcaddon (SHA256 9f5e14cbdaaaf3ae1b56cead6969048d0b5be554ff434557f8d9f4394c0229ee). The 0.11.44 Mechanical Arsenal rollback (SHA256 d861f69c88b0a1980e8a872f2e52a57386a3ff7cc9b1462f7ef9f2d0517919cf) contains approved inventory icons. Both actual files were inspected and ZIP integrity passed. Full private recovery archive Last_Dispatch_0.11.45_Recovery.zip includes complete checkpoints, uploaded inputs, available rebuild scripts, previews and SHA256SUMS.txt. It was verified locally; the binaries and later source changes are NOT uploaded by this note. Do not mistake this note for a synchronized build.

## Locked
- Four Echo bosses at 0.11.35: Seam-Riven, Veil Regent, Hush Pendulum, Rubble Rook; approved native attacks and special VFX.
- Five Ghost Grid bosses at 0.11.40: Palinode-6, Gantry Marrow, Cinder Spindle, Vestige-Arc 11, Oracle-Delta3. Corrected halos, weighted locomotion, unique specials, outdoor encounters. Silt Engine removed; legacy weapon definition retained.
- All 724 structure files and Echo/Grid entity/model/animation files match 0.11.40 byte-for-byte in 0.11.45. 38 loot tables (not 39 after Silt removal).
- Preserve existing station, integrated cities, bunkers, quest progression, original UUIDs and paired manifests.
- Preserve approved 32x32 inventory icons from 0.11.44 and corrected six katanas from 0.11.42. No random chest gear; only salvaged_alloy and legacy_cell custom materials. Preserve all stats, recipes and intended boss drops.

## Next task
User rejected 0.11.45 thin held models. Actual Nongko source archive nongko's_Fantasy_Weapons_v1.20A.zip (SHA256 103f787fa5a77914ce69f81a1b79f3e6b5dedfe2e10f264e1be32e11e907bf7f) contains Java element-based models, face UVs, rotation origins and display transforms (uchigatana has 17 elements). Not Bedrock skeleton rigs. Port real geometry and UV atlases, adapt rotation and hand transforms, retexture sci-fi, scale compactly. Start with one actual model, render and review before batch. Do not use image generation or concept posters as game assets. No conversion has been completed. Keep rejected appearance isolated to held geometry, textures and attachables; preserve inventory icons. Silt is legacy only.

Live Bedrock/Android testing remains pending; offline previews and static tests do not establish in-game compatibility. Full source synchronization for 0.11.26–45 remains pending. Use the private recovery archive and detailed Work handoff, not old main.