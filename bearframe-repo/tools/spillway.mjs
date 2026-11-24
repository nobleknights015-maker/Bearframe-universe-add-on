import {SPILLWAY_DATUM, SPILLWAY_FLIGHT, SPILLWAY_MARKER, SPILLWAY_PANEL, SPILLWAY_ROOMS, SPILLWAY_SIGNS} from "../behavior_pack/scripts/spillway_layout.js";
import {REGION_ANCHOR, PIN} from "../behavior_pack/scripts/regions.js";

const mc = id => "minecraft:" + id;
const air = mc("air");
const frame = mc("polished_deepslate");
const footing = mc("deepslate_bricks");
const deck = mc("polished_andesite");
const skin = mc("smooth_stone");
const teal = mc("oxidized_cut_copper");
const amber = mc("yellow_terracotta");
const blue = mc("cyan_terracotta");
const lamp = "bearframe:spillway_lamp";
const grate = "bearframe:spillway_grate";
const casing = "bearframe:spillway_casing";
const bulkhead = mc("chiseled_deepslate");
const stair = {weirdo_direction: 1, upside_down_bit: false};

export function stampSpillwayBeacon({put}) {
  // Native worldgen leaves a single datum. The surveyed surface shell and
  // underground rooms are placed together only if the terrain can support them.
  put(0, 0, 0, SPILLWAY_MARKER, {"bearframe:excavated": false});
}

export function stampSpillway({put, fill}, def, index) {
  const [datum, surface, center] = SPILLWAY_DATUM;
  const [px, py, pz] = SPILLWAY_PANEL;

  // Grade-level wayside headhouse. Leave the west access open and use a
  // buttressed, stepped canopy with a narrow exhaust stack over the shaft.
  fill(0, surface + 1, 12, 10, surface + 2, 24, air);
  fill(0, surface, 12, 10, surface, 24, frame);
  fill(0, surface, 15, 3, surface, 21, deck);
  fill(0, surface, 17, 3, surface, 19, blue);
  for (const x of [1, 7, 10]) {
    for (const z of [13, 23]) {
      fill(x, surface + 1, z, x, surface + 2, z, footing);
      put(x, surface + 2, z, casing);
    }
  }
  fill(1, 23, 13, 10, 23, 23, teal);
  fill(2, 23, 15, 9, 23, 21, frame);
  fill(1, 24, 14, 4, 24, 22, teal);
  fill(1, 23, 15, 3, 23, 21, air);
  fill(1, 25, 16, 4, 25, 20, frame);
  fill(7, 24, 18, 9, 24, 20, casing);
  fill(7, 25, 18, 9, 25, 20, teal);
  put(8, 26, 19, casing);
  put(8, 27, 19, mc("lightning_rod"));
  for (const z of [13, 23]) {
    put(0, 21, z, footing);
    put(0, 22, z, mc("deepslate_brick_stairs"), {weirdo_direction: 0, upside_down_bit: false});
    put(1, 22, z, lamp);
  }
  fill(1, 21, 14, 10, 21, 14, bulkhead);
  fill(1, 21, 22, 10, 21, 22, bulkhead);
  for (const x of [2, 6, 9]) {
    put(x, 22, 14, lamp);
    put(x, 22, 22, lamp);
  }
  fill(10, 21, 15, 10, 22, 21, bulkhead);
  put(10, 22, 18, lamp);
  put(datum, surface, center, SPILLWAY_MARKER, {"bearframe:excavated": true});

  // Two flights, a flat rest landing and flush wall lighting. Stairs run from
  // west (high) to east (low). Only the ground-level hatch is cut at the datum.
  for (const {x, y, stair: sloped} of SPILLWAY_FLIGHT) {
    fill(x, y - 1, 15, x, y, 21, footing);
    fill(x, y + 1, 15, x, y + 4, 21, frame);
    fill(x, y + 1, 16, x, Math.min(y + 4, 22), 20, air);
    fill(x, y, 16, x, y, 20, deck);
    if (sloped) for (let z = 16; z <= 20; z++) put(x, y, z, mc("stone_brick_stairs"), stair);
    for (const z of [15, 21]) {
      put(x, y + 1, z, teal);
      if (x % 3 === 1) put(x, y + 2, z, lamp);
    }
    if (y + 5 < surface) fill(x, y + 5, 15, x, y + 5, 21, footing);
  }

  for (const {rect: [x1, z1, x2, z2], roof} of SPILLWAY_ROOMS) {
    fill(x1, 4, z1, x2, 4, z2, footing);
    fill(x1, 5, z1, x2, roof, z2, skin);
    fill(x1 + 1, 5, z1 + 1, x2 - 1, roof - 1, z2 - 1, air);
    fill(x1 + 1, 4, z1 + 1, x2 - 1, 4, z2 - 1, deck);
    fill(x1, roof, z1, x2, roof, z2, frame);
    for (const x of [x1 + 2, x2 - 2]) for (const z of [z1 + 2, z2 - 2]) put(x, roof, z, lamp);
    for (let x = x1; x <= x2; x++) for (const z of [z1, z2]) {
      put(x, 5, z, footing);
      if (x % 4 === 0) {
        put(x, 6, z, casing);
        put(x, 7, z, casing);
      }
    }
  }

  // Four-block-high access portals, kept clear of room dressings.
  fill(22, 5, 16, 22, 8, 20, air);
  fill(28, 5, 16, 28, 8, 20, air);
  fill(31, 5, 13, 35, 8, 13, air);
  fill(31, 5, 23, 35, 8, 23, air);
  fill(43, 5, 23, 47, 8, 23, air);
  fill(39, 5, 28, 39, 8, 31, air);

  // Continuous wayfinding and framed portals. Palette and ceiling heights
  // shift between public circulation, machinery and service rooms.
  fill(22, 4, 17, 41, 4, 19, deck);
  fill(23, 4, 16, 41, 4, 16, blue);
  fill(23, 4, 20, 40, 4, 20, teal);
  fill(32, 4, 10, 34, 4, 13, amber);
  fill(32, 4, 21, 34, 4, 26, blue);
  fill(44, 4, 21, 46, 4, 25, teal);
  for (const [x, z] of [[22,15],[22,21],[28,15],[28,21],[30,13],[36,13],[30,23],[36,23],[42,23],[48,23]]) {
    fill(x, 5, z, x, 8, z, frame);
    put(x, 7, z, lamp);
  }
  for (const [x1, x2, z] of [[30,36,13],[30,36,23],[42,48,23]]) fill(x1, 9, z, x2, 9, z, frame);
  for (const x of [30, 36, 42, 47]) fill(x, 10, 14, x, 10, 22, frame);
  for (const x of [30, 34, 38, 42, 46]) {
    put(x, 11, 18, lamp);
    for(const z of [13,23])put(x,10,z,teal);
  }
  fill(29, 8, 15, 32, 8, 15, mc("tinted_glass"));
  put(29, 8, 16, lamp);
  put(32, 8, 16, lamp);

  // Pump gallery: enclosed recessed wet bed with two banks of old machinery,
  // visible from a protected rim. The working route remains level and dry.
  fill(36, 3, 5, 45, 3, 10, footing);
  fill(37, 4, 6, 44, 4, 9, mc("water"));
  fill(36, 4, 5, 45, 4, 5, grate);
  fill(36, 4, 10, 45, 4, 10, grate);
  fill(36, 5, 5, 45, 5, 5, mc("iron_bars"));
  fill(36, 5, 10, 45, 5, 10, mc("iron_bars"));
  fill(36, 5, 6, 36, 5, 9, mc("iron_bars"));
  fill(45, 5, 6, 45, 5, 9, mc("iron_bars"));
  for (const x of [36, 40, 44]) {
    fill(x, 5, 3, x, 9, 3, casing);
    put(x, 7, 4, lamp);
    fill(x, 10, 3, x, 10, 10, teal);
  }
  fill(30, 4, 4, 33, 4, 9, grate);
  put(30, 5, 4, mc("moss_block"));
  put(31, 5, 4, mc("moss_carpet"));
  put(30, 6, 3, mc("mossy_stone_bricks"));
  put(46, 5, 11, mc("moss_block"));

  // Operations: relief map and abandoned consoles face the manifold.
  fill(30, 5, 31, 37, 5, 31, casing);
  fill(32, 6, 31, 35, 6, 31, mc("light_blue_stained_glass"));
  put(31, 6, 31, lamp);
  put(36, 6, 31, lamp);
  fill(31, 6, 34, 37, 8, 34, bulkhead);
  fill(32, 7, 34, 36, 7, 34, teal);
  put(34, 7, 34, lamp);
  put(30, 5, 26, mc("cartography_table"));
  put(36, 5, 26, mc("lectern"));
  fill(37, 5, 24, 38, 5, 26, grate);

  // Maintenance shop: parts bench, stock racks and a hoist footway.
  fill(41, 5, 26, 41, 5, 29, casing);
  put(41, 6, 27, mc("grindstone"));
  put(41, 6, 29, lamp);
  fill(42, 5, 33, 47, 5, 33, grate);
  for (const x of [42, 44, 46, 47]) put(x, 6, 33, mc("barrel"));
  fill(46, 9, 25, 46, 9, 33, teal);
  put(46, 8, 30, mc("chain"));
  put(46, 7, 30, lamp);

  // A separate grated stock cage keeps the gate from bottlenecking public
  // corridors. Standard offsets retain old salvage, actor and repair logic.
  fill(43, 5, 14, 48, 7, 20, frame);
  fill(44, 5, 15, 47, 7, 19, air);
  fill(44, 6, 20, 47, 7, 20, mc("iron_bars"));
  fill(43, 5, 18, 43, 6, 18, air);
  fill(43, 4, 18, 47, 4, 18, amber);
  for (const x of [44, 47]) put(x, 7, 17, lamp);
  fill(36, 5, 15, 38, 5, 15, casing);
  put(36, 6, 15, lamp);
  put(38, 6, 15, mc("tinted_glass"));

  const local = ([x,y,z],name,states) => put(px+x, py+y, pz+z, name, states);
  for (const p of def.layout.seal) local(p, mc("iron_bars"));
  local(def.layout.cache, mc("barrel"));
  local(def.layout.signal, mc("coal_block"));
  local(def.layout.actor, air);
  local([0,-2,0], REGION_ANCHOR, {"bearframe:region": index, "bearframe:status": 0});
  local(PIN, mc("lodestone"));
  local([0,0,0], def.panel);
  for (const {pos, rotation} of SPILLWAY_SIGNS) put(...pos, mc("spruce_standing_sign"), {ground_sign_direction: rotation});
}
