import {registerChartSite,removeChartBeacon} from "./route_charts.js";
import {BlockPermutation, BlockTypes, BlockVolume, SignSide, world} from "@minecraft/server";
import {at} from "./layout.js";
import {PIN,REGION_ANCHOR,TYPES} from "./regions.js";
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

function prepareSigns(dim, origin, rotation=0) {
  for (const {pos, text} of SPILLWAY_SIGNS) {
    const sign = dim.getBlock(at(origin,pos,rotation))?.getComponent("minecraft:sign");
    if (!sign) continue;
    sign.setText(text);
    sign.setText(text, SignSide.Back);
    sign.setWaxed(true);
  }
}

// The beacon is only an invitation to survey the terrain. Never paste a
// gallery through a ravine, under insufficient cover or into marked builds.
function candidateOrigin(dim, location, dx, dz) {
  const start = {x:location.x+dx,y:location.y,z:location.z+dz};
  if (!dim.isChunkLoaded(start)) return;
  let surface = dim.getTopmostBlock(start);
  while (surface && surfaceAllowed.includes(surface.typeId)) surface = surface.below();
  if (!surface || !terrain.has(surface.typeId) || Math.abs(location.y-surface.y)>12) return;
  return at({...start,y:surface.y+1},SPILLWAY_DATUM.map(n=>-n));
}

function surveySite(dim, origin) {
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
  if (!clean([48,4,13],[67,11,23],excavationAllowed)) return false;
  if (!clean([22,3,2],[49,13,34],excavationAllowed) ||
      !clean([4,3,15],[21,surface-1,21],excavationAllowed)) return false;
  if (dim.getPlayers({location:point(2,surface,18),maxDistance:95}).some(player => {
    const {x,y,z}=player.location;
    return x>=origin.x && x<origin.x+SPILLWAY_SIZE.x && z>=origin.z+2 && z<origin.z+35 &&
      y>=origin.y+2 && (y<=origin.y+13 || x<origin.x+22 && y<=origin.y+top && z>=origin.z+12 && z<origin.z+25);
  })) return false;
  return {foundations,approach};
}

const candidates = [[0,0],[-11,0],[11,0],[0,-11],[0,11],[-12,-12],[-12,12],[12,-12],[12,12],
  [-24,0],[24,0],[0,-24],[0,24],[-24,-24],[-24,24],[24,-24],[24,24]];

export function buildSpillway(datum, search=true) {
  if (datum.permutation.getState(SPILLWAY_BUILT)) return false;
  return placeSpillway(datum.dimension,datum.location,search,datum);
}

export function surveySpillway(dim,location){
  return placeSpillway(dim,location,true);
}

function placeSpillway(dim,beacon,search,datum) {
  const nominal = at(beacon,SPILLWAY_DATUM.map(n=>-n));
  for (const [dx,dz] of search&&datum ? candidates : [[0,0]]) {
    const base=search ? candidateOrigin(dim,beacon,dx,dz) : nominal;
    if (!base) continue;
    for(const grade of search ? [0,-1,1] : [0]){
      const origin=at(base,[0,grade,0]);
      const site=surveySite(dim,origin);
      if(!site) continue;
      world.structureManager.place("bearframe:spillway_facility",dim,origin,{includeEntities:false});
      if(datum)removeChartBeacon("spillway_bunker",dim.id,datum.location);
      registerChartSite("spillway_bunker",dim.id,at(origin,SPILLWAY_DATUM));
      // The native beacon may sit several blocks back in the shoulder while the
      // lit panel on the completed site marks the actual approach.
      const placed=dim.getBlock(at(origin,SPILLWAY_DATUM));
      placed.setPermutation(placed.permutation.withState(SPILLWAY_BUILT,true));
      if(datum?.typeId===SPILLWAY_MARKER)datum.setPermutation(datum.permutation.withState(SPILLWAY_BUILT,true));
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
  if (site.def.id !== "spillway_bunker") return false;
  const delta = SPILLWAY_DATUM.map((value,i) => value-SPILLWAY_PANEL[i]);
  const loc = at(site.pos,delta,site.r);
  return site.dim.isChunkLoaded(loc) && site.dim.getBlock(loc)?.typeId === SPILLWAY_MARKER;
}


export function prepareGeneratedSpillway(marker,regionAt){
  const {dimension:dim,location:beacon}=marker;
  const delta=SPILLWAY_PANEL.map((value,i)=>value-SPILLWAY_DATUM[i]);
  const candidates=[0,1,2,3].map(r=>({r,pos:at(beacon,delta,r)}));
  const region=TYPES.findIndex(def=>def.id==="spillway_bunker");
  const loaded=pos=>dim.isChunkLoaded(pos)?dim.getBlock(pos):undefined;
  if(marker.permutation.getState(SPILLWAY_BUILT)&&candidates.every(({pos})=>dim.isChunkLoaded(pos))){
    const panels=candidates.filter(({pos})=>loaded(pos)?.typeId===TYPES[region].panel);
    if(panels.length===1){
      const {r,pos}=panels[0];
      const anchor=loaded(at(pos,[0,-2,0]));
      const pin=loaded(at(pos,PIN,r));
      const existingAnchor=anchor?.typeId===REGION_ANCHOR&&anchor.permutation.getState("bearframe:region")===region;
      // Restore only missing fixture blocks at a unique pump linked to this datum.
      if((anchor?.isAir||existingAnchor)&&(pin?.isAir||pin?.typeId==="minecraft:lodestone")){
        if(anchor.isAir)anchor.setPermutation(BlockPermutation.resolve(REGION_ANCHOR,{"bearframe:region":region,"bearframe:status":0}));
        if(pin.isAir)pin.setType("minecraft:lodestone");
      }
    }
  }
  for(const {r,pos} of candidates){
    const site=regionAt(dim,pos);
    if(site?.def.id!=="spillway_bunker"||site.r!==r)continue;
    if(!marker.permutation.getState(SPILLWAY_BUILT)){
      const origin=at(beacon,SPILLWAY_DATUM.map(value=>-value),r);
      prepareSigns(dim,origin,r);
      marker.setPermutation(marker.permutation.withState(SPILLWAY_BUILT,true));
    }
    registerChartSite(site.def.id,dim.id,beacon);
    return;
  }
}
