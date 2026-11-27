import test from "node:test";
import assert from "node:assert/strict";
import {creditedPlayer} from "../behavior_pack/scripts/combat_credit.js";
import {readFileSync} from "node:fs";
const p={typeId:"minecraft:player",isValid:true,id:"p"};
const projectile=owner=>({getComponent:id=>id==="minecraft:projectile"?{owner}:undefined});
test("direct player damage and projectile owner both receive quest attribution",()=>{assert.equal(creditedPlayer({damagingEntity:p}),p);assert.equal(creditedPlayer({damagingProjectile:projectile(p)}),p);assert.equal(creditedPlayer({damagingEntity:{typeId:"minecraft:arrow",isValid:true},damagingProjectile:projectile(p)}),p);});
test("invalid entities, nonplayers and despawned projectiles cannot earn quest credit",()=>{assert.equal(creditedPlayer(undefined),undefined);assert.equal(creditedPlayer({damagingEntity:{...p,isValid:false}}),undefined);assert.equal(creditedPlayer({damagingProjectile:projectile({typeId:"minecraft:skeleton",isValid:true})}),undefined);assert.equal(creditedPlayer({damagingProjectile:{getComponent(){throw Error("unloaded");}}}),undefined);});
test("source manifests are synchronized without changing pack identity",()=>{const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url),"utf8"));const b=read("../behavior_pack/manifest.json"),r=read("../resource_pack/manifest.json");assert.deepEqual(b.header.version,[0,11,14]);assert.deepEqual(r.header.version,b.header.version);assert.equal(b.header.uuid,"ee5e4ba0-f2dc-594a-bcaf-248e7f41559f");assert.equal(r.header.uuid,"57aabde7-cd63-5995-b00d-a69f983ba905");for(const m of [b,r])for(const mod of m.modules)assert.deepEqual(mod.version,b.header.version);assert(b.dependencies.some(d=>d.uuid===r.header.uuid&&JSON.stringify(d.version)===JSON.stringify(r.header.version)));});
