import assert from "node:assert/strict";
import {readdirSync,readFileSync} from "node:fs";
import test from "node:test";

const bp = new URL("../behavior_pack/", import.meta.url);
const rp = new URL("../resource_pack/", import.meta.url);
const readJson = (url) => JSON.parse(readFileSync(url, "utf8"));

const BEARFRAMES = [
  "farfield_surveyor", "city_steward", "city_engineer", "city_watch",
  "atlas_rigger", "atlas_vanguard", "vera_artisan", "field_researcher"
];
const NULLFRAMES_AND_HOLLOWS = [
  "hollow_scout", "hollow_breacher", "directorate_officer", "nullframe_hunter", "directorate_guard", "hollow_line"
];
const ECHOES = ["ward_resident", "echo_drifter", "echo_sentinel"];
const GHOST_GRID = [
  "grid_walker", "grid_watcher", "grid_turret", "grid_hauler", "grid_guardian", "grid_repair_crawler", "grid_protocol_keeper"
];
const ALL_LIVING = [...BEARFRAMES, ...NULLFRAMES_AND_HOLLOWS, ...ECHOES, ...GHOST_GRID];

test("all 24 living entities + grid_bolt projectile exist across BP, RP, models, and textures", () => {
  assert.equal(ALL_LIVING.length, 24);
  const bpFiles = new Set(readdirSync(new URL("entities/", bp)));
  const rpFiles = new Set(readdirSync(new URL("entity/", rp)));
  const modelFiles = new Set(readdirSync(new URL("models/entity/", rp)));
  for (const id of [...ALL_LIVING, "grid_bolt"]) {
    assert(bpFiles.has(`${id}.json`), `Missing BP entity ${id}`);
    assert(rpFiles.has(`${id}.entity.json`), `Missing RP client entity ${id}`);
    assert(modelFiles.has(`${id}.geo.json`), `Missing geometry ${id}`);
  }
});

test("all humanoids (Bearframes, Nullframes, Hollows, Hunters, Echoes) use player-scale articulated rigs", () => {
  for (const id of [...BEARFRAMES, ...NULLFRAMES_AND_HOLLOWS, ...ECHOES]) {
    const geo = readJson(new URL(`models/entity/${id}.geo.json`, rp))["minecraft:geometry"][0];
    const bones = new Map(geo.bones.map(b => [b.name, b]));
    for (const req of ["root", "body", "head", "arm0", "arm1", "leg0", "leg1"]) {
      assert(bones.has(req), `${id} missing humanoid bone ${req}`);
    }
    assert.equal(bones.get("body").pivot[1],12);
    assert.equal(bones.get("head").pivot[1],24);
    assert.equal(Math.abs(bones.get("arm0").pivot[0]),5.75);
    assert.equal(Math.abs(bones.get("leg0").pivot[0]),2);
    assert(bones.get("head").cubes.length>=4);
    let minY = Infinity, maxY = -Infinity;
    for (const bone of geo.bones) {
      for (const cube of bone.cubes || []) {
        minY = Math.min(minY, cube.origin[1]);
        maxY = Math.max(maxY, cube.origin[1] + cube.size[1]);
      }
    }
    assert.equal(minY, 0, `${id} feet must rest cleanly at y=0 (got ${minY})`);
    assert(maxY >= 26.5 && maxY <= 36, `${id} humanoid height ${maxY}px out of player-scale range 26.5..36`);
  }
});

test("Bearframes have immutable chest core display + dual side-head tech modules (no animal ears)", () => {
  for (const id of BEARFRAMES) {
    const geo = readJson(new URL(`models/entity/${id}.geo.json`, rp))["minecraft:geometry"][0];
    const body = geo.bones.find(b => b.name === "body");
    const head = geo.bones.find(b => b.name === "head");
    const usesTile = (face, u, v) => face?.uv[0] === u && face.uv[1] === v;
    const hasChestDisplay = body.cubes.some(c => c.origin[2] < -2.3 && usesTile(c.uv.north, 96, 0));
    assert(hasChestDisplay, `${id} missing immutable chest core display cube`);
    const leftSideMod = head.cubes.some(c => c.origin[0] >= 3 && c.origin[1] < 29 && usesTile(c.uv.east, 0, 32));
    const rightSideMod = head.cubes.some(c => c.origin[0] + c.size[0] <= -3 && c.origin[1] < 29 && usesTile(c.uv.west, 0, 32));
    assert(leftSideMod && rightSideMod, `${id} missing dual side-head tech display modules`);
  }
});

test("hollow_scout was rebuilt from quadruped into player-scale humanoid drone", () => {
  const geo = readJson(new URL("models/entity/hollow_scout.geo.json", rp))["minecraft:geometry"][0];
  const boneNames = new Set(geo.bones.map(b => b.name));
  assert(boneNames.has("arm0") && boneNames.has("arm1") && boneNames.has("head"));
  assert(!boneNames.has("leg2") && !boneNames.has("leg3"), "hollow_scout must no longer use old quadruped rig");
});

test("Ghost Grid machines use dedicated NONHUMANOID sci-fi rigs", () => {
  const walkerBones = new Set(readJson(new URL("models/entity/grid_walker.geo.json", rp))["minecraft:geometry"][0].bones.map(b => b.name));
  for (let i = 0; i < 6; i++) assert(walkerBones.has(`leg${i}`), `grid_walker missing hexapod leg${i}`);

  const watcherBones = new Set(readJson(new URL("models/entity/grid_watcher.geo.json", rp))["minecraft:geometry"][0].bones.map(b => b.name));
  assert(watcherBones.has("scanner") && watcherBones.has("thruster0") && watcherBones.has("thruster1") && watcherBones.has("thruster2"));
  assert(!watcherBones.has("leg0"), "grid_watcher should hover without legs");

  const turretBones = new Set(readJson(new URL("models/entity/grid_turret.geo.json", rp))["minecraft:geometry"][0].bones.map(b => b.name));
  assert(turretBones.has("body") && turretBones.has("head") && turretBones.has("barrels"));
  assert(!turretBones.has("leg0"), "grid_turret should be stationary tripod");

  const haulerBones = new Set(readJson(new URL("models/entity/grid_hauler.geo.json", rp))["minecraft:geometry"][0].bones.map(b => b.name));
  assert(haulerBones.has("tread0") && haulerBones.has("tread1") && haulerBones.has("crane"));
  assert(!haulerBones.has("leg0"), "grid_hauler should run on industrial treads");

  const guardianGeo = readJson(new URL("models/entity/grid_guardian.geo.json", rp))["minecraft:geometry"][0];
  const guardianMaxY = Math.max(...guardianGeo.bones.flatMap(b => (b.cubes || []).map(c => c.origin[1] + c.size[1])));
  assert(guardianMaxY >= 40, `grid_guardian should be a massive heavy mech (>=40px tall, got ${guardianMaxY})`);
});

test("Android 4 GB RAM spawn caps and non-griefing projectile constraints hold", () => {
  const bolt = readJson(new URL("entities/grid_bolt.json", bp))["minecraft:entity"];
  const proj = bolt.components["minecraft:projectile"];
  assert(proj, "grid_bolt missing projectile component");
  assert(!proj.on_hit.definition_event, "grid_bolt should not trigger block destruction");

  const spawnFiles = readdirSync(new URL("spawn_rules/", bp));
  assert.equal(spawnFiles.length, 4);
  for (const f of spawnFiles) {
    const sr = readJson(new URL(`spawn_rules/${f}`, bp))["minecraft:spawn_rules"];
    const cap = sr.conditions[0]["minecraft:density_limit"];
    assert(cap && cap.surface <= 3, `${f} exceeds Android surface density cap of 3`);
  }
});

test("all 4 survival recipes and 6 custom items are properly registered without sentience-chip lore violations", () => {
  const items = readdirSync(new URL("items/", bp));
  assert.equal(items.length, 6);
  const recipes = readdirSync(new URL("recipes/", bp));
  assert.equal(recipes.length, 4);
  for (const f of items) {
    assert(!f.includes("sentience") && !f.includes("prime_core"), `Lore violation item: ${f}`);
  }
});

test("the seven Frontier roles use distinct authored rigs and matching resources",()=>{
  const lineup=["field_researcher","directorate_guard","hollow_line","nullframe_hunter","echo_drifter",
    "grid_repair_crawler","grid_protocol_keeper"];
  const signatures=new Set();
  for(const id of lineup){
    const client=readJson(new URL(`entity/${id}.entity.json`,rp))["minecraft:client_entity"].description;
    const geo=readJson(new URL(`models/entity/${id}.geo.json`,rp))["minecraft:geometry"][0];
    assert.equal(client.identifier,"bearframe:"+id);
    assert.equal(client.geometry.default,geo.description.identifier);
    assert.equal(client.textures.default,"textures/bearframe/"+id);
    assert(client.spawn_egg);
    const shape=geo.bones.map(b=>[b.name,b.pivot,b.cubes.map(c=>[c.origin,c.size,c.rotation])]);
    signatures.add(JSON.stringify(shape));
    if(id==="grid_repair_crawler")assert.equal(geo.bones.filter(b=>/^leg\d$/.test(b.name)).length,6);
    if(id==="grid_protocol_keeper")assert(geo.bones.some(b=>b.name==="scanner")&&!geo.bones.some(b=>b.name==="leg0"));
  }
  assert.equal(signatures.size,lineup.length);
});
