import {BlockPermutation, BlockTypes, BlockVolume, SignSide, world} from "@minecraft/server";
import {at} from "./layout.js";
import {
  SPILLWAY_BUILT, SPILLWAY_DATUM, SPILLWAY_FLIGHT, SPILLWAY_MARKER, SPILLWAY_PANEL, SPILLWAY_ROOMS, SPILLWAY_SIZE, SPILLWAY_SIGNS,
} from "./spillway_layout.js";

const stone = ["stone", "granite", "diorite", "andesite", "deepslate", "tuff", "calcite",
  "gravel", "dirt", "coarse_dirt", "rooted_dirt", "grass_block", "podzol", "mud", "clay",
  "sand", "red_sand", "sandstone", "red_sandstone", "moss_block", "dripstone_block"];
const ores = ["coal", "iron", "copper", "gold", "redstone", "lapis", "diamond", "emerald"];
const terrain = new Set([...stone, ...ores.flatMap(ore => [ore + "_ore", "deepslate_" + ore + "_ore"]),
  "lit_redstone_ore", "lit_deepslate_redstone_ore"].map(id => "minecraft:" + id));
const plants = ["short_grass", "tall_grass", "fern", "large_fern", "dandelion", "poppy",
  "blue_orchid", "allium", "azure_bluet", "red_tulip", "orange_tulip", "white_tulip", "pink_tulip",
  "oxeye_daisy", "cornflower", "lily_of_the_valley", "leaf_litter", "snow_layer"];
const foliage = ["oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "azalea", "azalea_leaves_flowered",
  "mangrove", "cherry", "pale_oak"].map(kind=>kind.endsWith("_flowered") ? kind : kind+"_leaves");
const surfaceAllowed = ["minecraft:air", ...[...plants,...foliage].map(id => "minecraft:" + id), SPILLWAY_MARKER];
const surfaceFill = [...surfaceAllowed, ...terrain];
const excavationAllowed = [...terrain, "minecraft:air", "minecraft:water", "minecraft:flowing_water"];

function columnRect([x1,z1,x2,z2], visit) {
  for (let x=x1; x<=x2; x++) for (let z=z1; z<=z2; z++) {
    if (!visit(x,z)) return false;
  }
  return true;
}

function prepareSigns(dim, origin) {
  for (const {pos, text} of SPILLWAY_SIGNS) {
    const sign = dim.getBlock(at(origin,pos))?.getComponent("minecraft:sign");
    if (!sign) continue;
    sign.setText(text);
    sign.setText(text, SignSide.Back);
    sign.setWaxed(true);
  }
}

// The beacon is only an invitation to survey the terrain. Never paste a
// gallery through a ravine, under insufficient cover or into marked builds.
function candidateOrigin(datum, dx, dz) {
  const {dimension:dim,location} = datum;
  const start = {x:location.x+dx,y:location.y,z:location.z+dz};
  if (!dim.isChunkLoaded(start)) return;
  let surface = dim.getTopmostBlock(start);
  while (surface && surfaceAllowed.includes(surface.typeId)) surface = surface.below();
  if (!surface || !terrain.has(surface.typeId) || Math.abs(location.y-surface.y)>12) return;
  return at({...start,y:surface.y+1},SPILLWAY_DATUM.map(n=>-n));
}

function surveySite(datum, origin) {
  const dim = datum.dimension;
  const point = (x,y,z) => at(origin,[x,y,z]);
  if (origin.y+2 < dim.heightRange.min || origin.y+SPILLWAY_SIZE.y >= dim.heightRange.max) return false;
  for (let x=(origin.x-1)>>4; x<=((origin.x+SPILLWAY_SIZE.x-1)>>4); x++) {
    for (let z=origin.z>>4; z<=((origin.z+SPILLWAY_SIZE.z-1)>>4); z++) {
      if (!dim.isChunkLoaded({x:x*16,y:origin.y,z:z*16})) return false;
    }
  }

  const surface = SPILLWAY_DATUM[1], top = SPILLWAY_SIZE.y-1;
  const natural = (x,y,z) => terrain.has(dim.getBlock(point(x,y,z))?.typeId);
  const foundations = [];
  if (!columnRect([0,12,10,24],(x,z) => {
    for(let y=surface-1;y>=surface-4;y--){
      if(natural(x,y,z))return true;
      const block=dim.getBlock(point(x,y,z));
      if(!surfaceAllowed.includes(block?.typeId))return false;
      if(block.typeId===SPILLWAY_MARKER)continue;
      foundations.push(block);
    }
    return false;
  })) return false;
  const approach = [];
  if (!columnRect([-1,17,-1,19],(x,z) => {
    const ground = [surface+1,surface,surface-1,surface-2].find(y=>natural(x,y,z));
    if(ground===undefined || ![1,2].every(h =>
      surfaceAllowed.includes(dim.getBlock(point(x,ground+h,z))?.typeId)))return false;
    if(ground===surface-2)approach.push(point(x,ground+1,z));
    return true;
  })) return false;

  for (const {rect,roof} of SPILLWAY_ROOMS) {
    if (!columnRect(rect,(x,z) => natural(x,2,z) && natural(x,3,z) &&
      natural(x,roof+1,z) && natural(x,roof+2,z))) return false;
  }
  for (const {x,y} of SPILLWAY_FLIGHT) {
    if (!columnRect([x,15,x,21],(u,z) => natural(u,y-2,z) &&
      (y+5>=surface-1 || natural(u,y+6,z)))) return false;
  }

  const clean = (from,to,allowed) => dim.getBlocks(
    new BlockVolume(at(origin,from),at(origin,to)),{excludeTypes:allowed.filter(id=>BlockTypes.get(id))},false
  ).getCapacity() === 0;
  if (!clean([0,surface,12],[10,surface+2,24],surfaceFill) ||
      !clean([0,surface+3,12],[10,top,24],surfaceAllowed) ||
      !clean([11,surface,15],[21,surface+1,21],surfaceFill)) return false;
  if (!clean([22,3,2],[49,13,34],excavationAllowed) ||
      !clean([4,3,15],[21,surface-1,21],excavationAllowed)) return false;
  if (dim.getPlayers({location:point(2,surface,18),maxDistance:65}).some(player => {
    const {x,y,z}=player.location;
    return x>=origin.x && x<origin.x+50 && z>=origin.z+2 && z<origin.z+35 &&
      y>=origin.y+2 && (y<=origin.y+13 || x<origin.x+22 && y<=origin.y+top && z>=origin.z+12 && z<origin.z+25);
  })) return false;
  return {foundations,approach};
}

const candidates = [[0,0],[-11,0],[11,0],[0,-11],[0,11],[-12,-12],[-12,12],[12,-12],[12,12],
  [-24,0],[24,0],[0,-24],[0,24],[-24,-24],[-24,24],[24,-24],[24,24]];

export function buildSpillway(datum, search=true) {
  if (datum.permutation.getState(SPILLWAY_BUILT)) return false;
  const dim=datum.dimension;
  const beacon=datum.location;
  const nominal = at(beacon,SPILLWAY_DATUM.map(n=>-n));
  for (const [dx,dz] of search ? candidates : [[0,0]]) {
    const base=search ? candidateOrigin(datum,dx,dz) : nominal;
    if (!base) continue;
    for(const grade of search ? [0,-1,1] : [0]){
      const origin=at(base,[0,grade,0]);
      const site=surveySite(datum,origin);
      if(!site) continue;
      world.structureManager.place("bearframe:spillway_facility",dim,origin,{includeEntities:false});
      // The native beacon may sit several blocks back in the shoulder while the
      // lit panel on the completed site marks the actual approach.
      if (datum.typeId===SPILLWAY_MARKER) datum.setPermutation(datum.permutation.withState(SPILLWAY_BUILT,true));
      for(const block of site.foundations)block.setType("minecraft:deepslate_bricks");
      const stair=BlockPermutation.resolve("minecraft:stone_brick_stairs",{weirdo_direction:0,upside_down_bit:false});
      for(const pos of site.approach)dim.getBlock(pos).setPermutation(stair);
      prepareSigns(dim,origin);
      return origin;
    }
  }
  return false;
}

export function isRecoverySpillway(site) {
  if (site.def.id !== "spillway_bunker" || site.r !== 0) return false;
  const delta = SPILLWAY_DATUM.map((value,i) => value-SPILLWAY_PANEL[i]);
  const loc = at(site.pos,delta);
  return site.dim.isChunkLoaded(loc) && site.dim.getBlock(loc)?.typeId === SPILLWAY_MARKER;
}
