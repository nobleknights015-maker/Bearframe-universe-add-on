import test from "node:test";
import assert from "node:assert/strict";
import {drySoil,dryClear} from "../behavior_pack/scripts/survey_terrain.js";
const soil=new Set(["minecraft:mud","minecraft:stone"]),clear=new Set(["minecraft:air","minecraft:oak_leaves"]);
test("dry survey accepts only loaded dry approved ground",()=>{
 assert(drySoil({typeId:"minecraft:mud"},soil));
 for(const b of [undefined,{typeId:"minecraft:mud",isWaterlogged:true},{typeId:"minecraft:stone",isLiquid:true},{typeId:"minecraft:water"},{typeId:"minecraft:air"}])assert(!drySoil(b,soil));
});
test("clearance rejects wet foliage, liquids, unapproved blocks and unloaded cells",()=>{
 assert(dryClear({typeId:"minecraft:air"},clear));assert(dryClear({typeId:"minecraft:oak_leaves"},clear));
 for(const b of [undefined,{typeId:"minecraft:oak_leaves",isWaterlogged:true},{typeId:"minecraft:air",isLiquid:true},{typeId:"minecraft:water"},{typeId:"minecraft:stone"}])assert(!dryClear(b,clear));
});
