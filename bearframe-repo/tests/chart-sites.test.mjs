import assert from "node:assert/strict";
import test from "node:test";
import {loadStructure,terminalLookup} from "./structure-fixture.mjs";
import {chartSiteAvailable} from "../behavior_pack/scripts/chart_site_checks.js";
import {SURFACE_SITES,LEGACY_SITES} from "../behavior_pack/scripts/surface_layout.js";
import {ARCHIVE_SITE_IDS} from "../behavior_pack/scripts/campaign_data.js";
import {SPILLWAY_DATUM,SPILLWAY_MARKER,SPILLWAY_BUILT} from "../behavior_pack/scripts/spillway_layout.js";

const asPoint=([x,y,z])=>({x,y,z});
function adapter(template){
 return {
  isChunkLoaded:()=>true,
  getBlock({x,y,z}){
   const voxel=template.cell(x,y,z);
   if(!voxel)return;
   return {typeId:voxel.name,isAir:voxel.name==="minecraft:air",
    permutation:{getState:key=>voxel.states[key]}};
  }
 };
}
test("chart recheck recognizes current archive structures and their reader coordinates",()=>{
 for(const id of ARCHIVE_SITE_IDS){
  const site=[...SURFACE_SITES,...LEGACY_SITES].find(s=>s.id===id);
  const template=loadStructure(id+"_site"),dim=adapter(template);
  const waypoint={x:site.size.x>>1,y:site.deck+1,z:site.size.z>>1};
  assert(chartSiteAvailable(dim,id,waypoint),id+" chart waypoint");
  assert(chartSiteAvailable(dim,id,asPoint(template.find("bearframe:field_archive")[0])),id+" visited reader");
 }
});
test("loaded missing relay is stale, unloaded relay is undetermined",()=>{
 const template=loadStructure("maintenance_relay_field");
 const {position}=terminalLookup(template,"bearframe:relay_anchor");
 const dim=adapter(template),point=asPoint(position);
 assert(chartSiteAvailable(dim,"maintenance_relay",point));
 const getBlock=dim.getBlock;
 dim.getBlock=p=>p.x===point.x&&p.y===point.y&&p.z===point.z?{typeId:"minecraft:air"}:getBlock(p);
 assert(!chartSiteAvailable(dim,"maintenance_relay",point));
 dim.isChunkLoaded=p=>p.x!==point.x;
 assert(chartSiteAvailable(dim,"maintenance_relay",point));
});
test("built Spillway remains available only with a clear authored entry",()=>{
 const dim=adapter(loadStructure("spillway_facility"));
 const getBlock=dim.getBlock;
 const marker=asPoint(SPILLWAY_DATUM);
 const entry={...marker,x:marker.x+2};
 const reference=p=>p.x===marker.x&&p.y===marker.y&&p.z===marker.z?
   {typeId:SPILLWAY_MARKER,permutation:{getState:key=>key===SPILLWAY_BUILT}}:getBlock(p);
 dim.getBlock=reference;
 assert(chartSiteAvailable(dim,"spillway_bunker",marker));
 dim.getBlock=p=>p.x===entry.x&&p.y===entry.y&&p.z===entry.z?{typeId:"minecraft:stone",isAir:false}:reference(p);
 assert(!chartSiteAvailable(dim,"spillway_bunker",marker));
});
