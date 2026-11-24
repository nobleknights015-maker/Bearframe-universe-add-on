# Bearframe Bedrock 0.1.0

A private Minecraft Bedrock survival checkpoint on the planet beneath orbital Bearframe City. Explore the Overworld normally and look for a ruined maintenance relay in plains chunks. The relay and its encounter are gameplay proposals for this add-on.

## Install and play

1. Open `Bearframe_Bedrock_0.1.0.mcaddon` with Minecraft Bedrock 26.50 or newer. This checkpoint was exercised on Dedicated Server 1.26.63.1. Use a fresh world or a backup of an existing world.
2. Under the world's **Behavior Packs**, activate **Bearframe | Behavior** and check that **Bearframe | Resources** is active under **Resource Packs**. No experimental toggles are part of this build.
3. For the Infinity look, install your own Infinity Sci-Fi resource pack separately. Activate it below **Bearframe | Resources**. The add-on also works with the stock textures.
4. Explore new plains chunks. For a quick test, use a normal world with seed `13221951` and go near X `-202`, Z `168`. This is the relay on the tested server version. With commands enabled, use `/locate structure bearframe:maintenance_relay`.

Bring two copper ingots and one redstone dust. The surveyor gives a hint and can trade a torch kit when you sneak-interact. Use the lectern to fit the breaker. Mine the cobblestone debris beside the copper service line and interact with the lectern again to restore lights and unlock the service wing. Use the recovery barrel inside. The schematic is shared across everyone at that site and can be crafted with a torch and iron nugget into two soul lanterns. Treat the scout as hostile and the maintenance walker as neutral.

## Source

Run `npm install`, `npm run worldgen`, and `npm test`. Pillow is needed to regenerate PNG and entity assets with `python3 tools/make_content.py`. Build with `python3 tools/build.py ./dist`. The Bedrock geometry and original PNG atlases can be opened in Blockbench. The source archive contains a Git bundle if built from the checkpoint repository. For a native replay, see `docs/QA_TEST_LOG.md`.

Player survival remains available from world start. There is no orbital travel, no canonical cast recruitment and no playable Echo encounter in this checkpoint. Android rendering, handheld performance, live multiplayer, Realms and console loading need direct testing.
