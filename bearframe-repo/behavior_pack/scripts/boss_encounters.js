import { Difficulty, GameMode, world, system } from "@minecraft/server";
import { BOSS_HABITATS, encounterRoll } from "./boss_habitats.js";

import { read } from "./campaign_state.js";
import { activeHunt } from "./boss_dossiers.js";
import { siteClaimKey, canRetryClaim } from "./boss_claims.js";
const SITE_BOSS = "bearframe_site_boss";
const ARENA_FLOORS = new Set([
  "bearframe:frontier_deck", "bearframe:frontier_dust",
  "minecraft:chiseled_stone_bricks", "minecraft:polished_andesite", "minecraft:mossy_stone_bricks",
  "minecraft:mud_bricks", "minecraft:light_gray_concrete", "minecraft:polished_deepslate",
  "minecraft:stone_bricks", "minecraft:cobbled_deepslate",
]);

function clearArena(dimension, position) {
  for (let x = -1; x <= 1; x++) {
    for (let z = -1; z <= 1; z++) {
      const feet = { x: position.x + x, y: position.y, z: position.z + z };
      if (!dimension.isChunkLoaded(feet)) return false;
      const block = dimension.getBlock(feet);
      const floor = block?.below();
      if (!floor || !ARENA_FLOORS.has(floor.typeId) ||
          !block.isAir || !block.above()?.isAir || !block.above(2)?.isAir) return false;
    }
  }
  return true;
}

export function discoverBoss(siteId, marker, player) {
  const habitat = BOSS_HABITATS[siteId];
  if (!habitat || world.getDifficulty() === Difficulty.Peaceful ||
      ![GameMode.Survival, GameMode.Adventure].includes(player.getGameMode())) return;
  const { dimension, location } = marker;
  const hunt=activeHunt(read(player),siteId);
  if (dimension.id !== "minecraft:overworld" || (!hunt && !encounterRoll(siteId, location))) return;
  const siteKey=siteClaimKey(siteId,location);
  const claim=world.getDynamicProperty(siteKey);
  if(claim&&!canRetryClaim(claim,hunt,system.currentTick))return;
  // Native jigsaw pieces can be quarter-turned. Keep attempts on authored flooring.
  const candidates = habitat.offsets.flatMap(([x, y, z]) =>
    [[x,y,z],[-z,y,x],[-x,y,-z],[z,y,-x]]);
  for (const [x, y, z] of candidates) {
    const feet = { x: location.x + x, y: location.y + y, z: location.z + z };
    const center = { x: feet.x + .5, y: feet.y, z: feet.z + .5 };
    const distance = Math.hypot(center.x - player.location.x, center.z - player.location.z);
    if (distance < 10 || distance > 28 || Math.abs(center.y - player.location.y) > 5) continue;
    if (dimension.getPlayers({ location: center, maxDistance: 9 }).length ||
        dimension.getEntities({ location: center, maxDistance: 48, tags: [SITE_BOSS] }).length ||
        !clearArena(dimension, feet)) continue;
    const boss = dimension.spawnEntity("bearframe:" + habitat.boss, center);
    try {
      boss.addTag(SITE_BOSS);
      boss.setDynamicProperty("bearframe:boss_claim",siteKey);
      world.setDynamicProperty(siteKey,"active");
    } catch (error) {
      if (boss.isValid) boss.remove();
      throw error;
    }
    return;
  }
}
