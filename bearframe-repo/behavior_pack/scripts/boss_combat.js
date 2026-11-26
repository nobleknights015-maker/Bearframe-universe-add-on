import { Difficulty, EntityDamageCause, GameMode, system, world } from "@minecraft/server";
import { BOSS_MOVES } from "./boss_moves.js";

import { campaignSignal } from "./campaign.js";
import { creditIds } from "./boss_dossiers.js";
import { defeatedClaim } from "./boss_claims.js";
const ENGAGE_RADIUS = 24;
const MAX_HEIGHT_DIFFERENCE = 2.5;
const PARTICLE = "minecraft:endrod";

function offset(from, to) {
  return { x: to.x - from.x, y: to.y - from.y, z: to.z - from.z };
}

function eligible(player) {
  return player.isValid && [GameMode.Survival, GameMode.Adventure].includes(player.getGameMode());
}

function clearPath(dimension, from, to) {
  const direction = offset(from, to);
  const length = Math.hypot(direction.x, direction.y, direction.z);
  if (length < .1) return true;
  return !dimension.getBlockFromRay(from, {
    x: direction.x / length, y: direction.y / length, z: direction.z / length,
  }, { maxDistance: length, includeLiquidBlocks: false, includePassableBlocks: false });
}

function height(point, y) {
  return { x: point.x, y: point.y + y, z: point.z };
}

function findTarget(dimension, origin, players) {
  return players.map(player => {
    const delta = offset(origin, player.location);
    return { player, distance: Math.hypot(delta.x, delta.z), elevation: Math.abs(delta.y) };
  }).filter(target => target.elevation <= MAX_HEIGHT_DIFFERENCE)
    .sort((a, b) => a.distance - b.distance)
    .find(({ player }) => clearPath(dimension, height(origin, .8), height(player.location, .8)));
}

function inside(move, strike, point) {
  const center = move.shape === "mark" ? strike.mark : strike.origin;
  const delta = offset(center, point);
  if (Math.abs(delta.y) > MAX_HEIGHT_DIFFERENCE) return false;
  const distance = Math.hypot(delta.x, delta.z);
  if (move.shape === "mark") return distance <= move.width;
  if (move.shape === "ring") return distance <= move.radius && distance >= (move.inner ?? 0);
  const forward = delta.x * strike.direction.x + delta.z * strike.direction.z;
  if (move.shape === "cone") return distance <= move.radius && forward >= move.dot * distance;
  const cross = delta.x * strike.direction.z - delta.z * strike.direction.x;
  return forward >= 0 && forward <= move.radius && Math.abs(cross) <= move.width;
}

function ringPoints(center, radius, count, start = 0, arc = 2 * Math.PI) {
  return Array.from({ length: count }, (_, index) => {
    const angle = start + index * arc / (arc === 2 * Math.PI ? count : count - 1);
    return { x: center.x + radius * Math.cos(angle), y: center.y, z: center.z + radius * Math.sin(angle) };
  });
}

function warningPoints(move, strike) {
  const { origin, mark, direction } = strike;
  if (move.shape === "mark") return ringPoints(mark, move.width, 10);
  if (move.shape === "ring") {
    return ringPoints(origin, move.radius, 14).concat(move.inner ? ringPoints(origin, move.inner, 8) : []);
  }
  if (move.shape === "cone") {
    const arc = Math.acos(move.dot);
    const start = Math.atan2(direction.z, direction.x) - arc;
    return ringPoints(origin, move.radius, 9, start, arc * 2)
      .concat(ringPoints(origin, move.radius * .55, 5, start, arc * 2));
  }
  return Array.from({ length: 14 }, (_, i) => {
    const length = move.radius * (1 + (i >> 1)) / 7;
    const side = (i % 2 ? -1 : 1) * move.width;
    return { x: origin.x + direction.x * length + direction.z * side, y: origin.y,
      z: origin.z + direction.z * length - direction.x * side };
  });
}

function showWarning(entity, strike) {
  const dimension = entity.dimension;
  const from = height(strike.origin, .8);
  for (const point of warningPoints(strike.move, strike)) {
    const position = height(point, .25);
    if (dimension.isChunkLoaded(position) && clearPath(dimension, from, position)) {
      dimension.spawnParticle(PARTICLE, position);
    }
  }
}

function release(entity, strike, players) {
  const { move, origin, direction, enraged } = strike;
  const dimension = entity.dimension;
  const source = height(origin, .8);
  dimension.playSound("random.anvil_land", origin, { volume: .55, pitch: move.shape === "mark" ? 1.5 : .76 });
  for (const player of players) {
    if (!inside(move, strike, player.location) ||
        !clearPath(dimension, source, height(player.location, .8))) continue;
    const hit = player.applyDamage(move.damage + (enraged ? 2 : 0), {
      cause: EntityDamageCause.entityAttack, damagingEntity: entity,
    });
    if (hit && move.effect) player.addEffect(move.effect[0], move.effect[1], { showParticles: false });
  }
  if (move.drive && clearPath(dimension, source, { x: source.x + direction.x * 2.4, y: source.y,
    z: source.z + direction.z * 2.4 })) {
    entity.applyImpulse({ x: direction.x * move.drive, y: 0, z: direction.z * move.drive });
  }
}

function reset(entity, state, now, cooldown = 24) {
  entity.triggerEvent("bearframe:boss_idle");
  state.strike = undefined;
  state.ready = now + cooldown;
}

function update(entity, state, now) {
  if (!state.strike && now < state.ready) return;
  const origin = entity.location;
  const dimension = entity.dimension;
  state.origin=origin;state.dimension=dimension.id;state.claim=entity.getDynamicProperty("bearframe:boss_claim");
  const players = dimension.getPlayers({ location: origin, maxDistance: ENGAGE_RADIUS }).filter(eligible);
  if (world.getDifficulty() === Difficulty.Peaceful || !players.length) {
    if (state.strike) reset(entity, state, now, 60);
    else state.ready=now+40;
    return;
  }
  if (state.strike) {
    const strike = state.strike;
    const elapsed = now - strike.started;
    if (!strike.released && elapsed >= strike.move.windup && elapsed < strike.move.end) {
      // Resolve once, even when an update skips the exact windup tick.
      strike.released = true;
      release(entity, strike, players);
    }
    if (elapsed < strike.move.windup && elapsed % 8 === 2) showWarning(entity, strike);
    if (elapsed >= strike.move.end) reset(entity, state, now, strike.enraged ? 15 : 28);
    return;
  }
  state.ready = now + 4;
  const target = findTarget(dimension, origin, players);
  if (!target) return;
  const moves = BOSS_MOVES[entity.typeId];
  const index = [state.next, 1 - state.next].find(i => {
    const move = moves[i];
    return target.distance <= move.radius && target.distance >= (move.minRange ?? 0);
  });
  if (index === undefined) return;
  const move = moves[index];
  const mark = target.player.location;
  const delta = offset(origin, mark);
  const yaw = target.distance < .05 ? entity.getRotation().y : Math.atan2(-delta.x, delta.z) * 180 / Math.PI;
  const radians = yaw * Math.PI / 180;
  const direction = { x: -Math.sin(radians), z: Math.cos(radians) };
  const health = entity.getComponent("minecraft:health");
  const enraged = health.currentValue <= health.effectiveMax * .4;
  entity.setRotation({ x: 0, y: yaw });
  entity.clearVelocity();
  entity.triggerEvent("bearframe:boss_attack" + index);
  dimension.playSound("note.pling", origin, { volume: .65, pitch: enraged ? 1.55 : .93 });
  state.strike = { started: now, origin, mark, direction, move, enraged };
  state.next = 1 - index;
}

export function installBossCombat() {
  const active = new Map();
  const participants = new Map();
  const register = entity => {
    if (!entity.isValid || !BOSS_MOVES[entity.typeId] || active.has(entity.id)) return;
    const state = { entity, next: 0, origin:entity.location, dimension:entity.dimension.id, claim:entity.getDynamicProperty("bearframe:boss_claim") };
    reset(entity, state, system.currentTick, 32);
    active.set(entity.id, state);
  };
  world.afterEvents.entitySpawn.subscribe(({ entity }) => register(entity));
  world.afterEvents.entityLoad.subscribe(({ entity }) => register(entity));
  world.afterEvents.entityHurt.subscribe(({hurtEntity,damageSource})=>{
    if(!BOSS_MOVES[hurtEntity.typeId])return;
    const p=damageSource.damagingEntity;
    if(p?.typeId!=="minecraft:player"||!eligible(p))return;
    const state=active.get(hurtEntity.id);
    if(state){state.origin=hurtEntity.location;state.dimension=hurtEntity.dimension.id;state.claim=hurtEntity.getDynamicProperty("bearframe:boss_claim")??state.claim;}
    const record=participants.get(hurtEntity.id)??new Map();
    record.set(p.id,system.currentTick);
    participants.set(hurtEntity.id,record);
  });
  world.afterEvents.entityDie.subscribe(({deadEntity,damageSource})=>{
    if(!BOSS_MOVES[deadEntity.typeId])return;
    const now=system.currentTick;
    const record=participants.get(deadEntity.id)??new Map();
    const snapshot=active.get(deadEntity.id);
    active.delete(deadEntity.id);participants.delete(deadEntity.id);
    try{
      let origin=snapshot?.origin,dim=snapshot?.dimension,key=snapshot?.claim;
      try{origin=deadEntity.location;dim=deadEntity.dimension.id;key=deadEntity.getDynamicProperty("bearframe:boss_claim")??key;}catch{}
      if(!origin||!dim)return;
      if(typeof key==="string"&&key.startsWith("bearframe:boss_site:"))world.setDynamicProperty(key,defeatedClaim(now));
      if(dim!=="minecraft:overworld"||world.getDifficulty()===Difficulty.Peaceful)return;
      const candidates=world.getAllPlayers().filter(eligible);
      const killer=damageSource.damagingEntity;
      const recent=[...record].filter(([,tick])=>now-tick<=2400).map(([id])=>id);
      const ids=new Set(creditIds(recent,killer?.typeId==="minecraft:player"&&eligible(killer)?killer.id:null,candidates.map(p=>({id:p.id,valid:p.isValid,dimension:p.dimension.id,location:p.location})),origin,dim));
      for(const player of candidates)if(ids.has(player.id)){
        try{campaignSignal(player,"boss",deadEntity.typeId.split(":")[1],origin);}catch(error){console.warn("[Bearframe boss credit] "+error);}
      }
    }catch(error){console.warn("[Bearframe boss death] "+error);}
  });
  system.runInterval(() => {
    const now = system.currentTick;
    for (const [id, state] of active) {
      if (!state.entity.isValid) {
        active.delete(id);
        participants.delete(id);
        continue;
      }
      try {
        update(state.entity, state, now);
      } catch (error) {
        console.warn("[Bearframe bosses] " + error);
        if (state.entity.isValid) {
          state.strike=undefined;state.ready=now+60;
          try{reset(state.entity,state,now,60);}catch(resetError){console.warn("[Bearframe boss reset] "+resetError);}
        }
      }
    }
  }, 1);
}
