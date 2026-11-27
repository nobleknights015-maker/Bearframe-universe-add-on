import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync,readdirSync} from "node:fs";
import {inflateSync} from "node:zlib";
const bp=new URL("../behavior_pack/",import.meta.url),rp=new URL("../resource_pack/",import.meta.url);
const read=(base,path)=>JSON.parse(readFileSync(new URL(path,base),"utf8"));
const catalog=JSON.parse(readFileSync(new URL("../docs/loot_gear_catalog.json",import.meta.url),"utf8"));
const atlas=read(rp,"textures/item_texture.json").texture_data;
const lang=readFileSync(new URL("texts/en_US.lang",rp),"utf8");
const signature=Buffer.from([137,80,78,71,13,10,26,10]);
test("twelve original weapon IDs, item components and decodable unique pixel icons",()=>{
 assert.equal(catalog.length,12);assert.equal(new Set(catalog.map(g=>g.id)).size,12);
 const imageSignatures=new Set();
 for(const gear of catalog){
  const item=read(bp,"items/"+gear.id+".json")["minecraft:item"];
  assert.equal(item.description.identifier,"bearframe:"+gear.id);
  assert.equal(item.components["minecraft:damage"],gear.damage);
  assert.equal(item.components["minecraft:max_stack_size"],1);
  assert.equal(item.components["minecraft:hand_equipped"],true);
  assert(gear.damage>=5&&gear.damage<=10);
  assert.equal(item.components["minecraft:durability"]?.max_durability??0,gear.durability);
  assert(gear.tier==="Legendary"?gear.durability===0:gear.durability>0);
  assert(lang.includes("item.bearframe:"+gear.id+".name="));
  const path=atlas[item.components["minecraft:icon"]].textures+".png";
  const image=readFileSync(new URL(path,rp));
  assert.deepEqual(image.subarray(0,8),signature);assert.equal(image.readUInt32BE(16),16);assert.equal(image.readUInt32BE(20),16);
  const idat=[];for(let p=8;p<image.length;){const n=image.readUInt32BE(p),type=image.toString("ascii",p+4,p+8);if(type==="IDAT")idat.push(image.subarray(p+8,p+8+n));p+=n+12;}
  const raw=inflateSync(Buffer.concat(idat));assert.equal(raw.length,16*(1+16*4));
  let opaque=0,transparent=0;for(let y=0;y<16;y++)for(let x=0;x<16;x++){const a=raw[y*65+1+x*4+3];if(a===255)opaque++;else if(a===0)transparent++;}
  assert(opaque>20&&transparent>20);imageSignatures.add(raw.toString("base64"));
 }
 assert.equal(imageSignatures.size,12);
});
test("eight original boss signature drops are guaranteed and all links resolve",()=>{
 const bosses=catalog.filter(g=>g.boss);assert.equal(bosses.length,8);assert.equal(new Set(bosses.map(g=>g.boss)).size,8);
 for(const gear of bosses){
  const def=read(bp,"entities/"+gear.boss+".json")["minecraft:entity"],e=def.components;
  assert(!e["minecraft:boss"]);assert(def.component_groups["bearframe:boss_engaged"]["minecraft:boss"]);assert(e["minecraft:health"].max>=150);
  const path=e["minecraft:loot"].table;assert.equal(path,"loot_tables/entities/boss_"+gear.boss+".json");
  const loot=read(bp,path);assert(loot.pools.some(p=>p.rolls===1&&!p.conditions&&p.entries.length===1&&p.entries[0].name==="bearframe:"+gear.id));
  assert(loot.pools.length>=4);
 }
});
test("all seventeen chest tables keep normal loot and append bounded tiered gear probabilities",()=>{
 let count=0;
 for(const dir of ["chests","structures"])for(const name of readdirSync(new URL("loot_tables/"+dir+"/",bp))){
  if(!name.endsWith(".json"))continue;
  const t=read(bp,"loot_tables/"+dir+"/"+name);assert(t.pools.length>=2);
  const p=t.pools.at(-1);assert.equal(p.rolls,1);assert.equal(p.entries[0].type,"empty");const total=p.entries.reduce((n,e)=>n+e.weight,0);
  assert(p.entries[0].weight/total>=.76);
  const weights=p.entries.slice(1).map(e=>e.weight);
  if(weights.length===2)assert.equal(weights[0],6*weights[1]);
  if(weights.length===3)assert.deepEqual(weights.map(weight=>weight/weights[2]),[60,15,1]);
  for(const e of p.entries.slice(1)){assert(catalog.some(g=>!g.boss&&"bearframe:"+g.id===e.name));assert(e.weight>0);}
  assert((p.entries.find(e=>e.name==="bearframe:foundry_prototype")?.weight??0)/total<=.01);count++;
 }assert.equal(count,17);
});
test("four hostile tables receive low-chance loot without replacing previous drops",()=>{
 for(const name of ["directorate_officer","hollow_breacher","hollow_scout","nullframe_hunter"]){
  const t=read(bp,"loot_tables/entities/"+name+".json");assert(t.pools.length>=2);const p=t.pools.at(-1);assert.equal(p.entries[0].type,"empty");assert(p.entries[0].weight>=86);assert.equal(p.entries.reduce((n,e)=>n+e.weight,0),100);
 }
});
test("all custom item entries across loot tables resolve",()=>{
 const items=new Set(readdirSync(new URL("items/",bp)).map(n=>read(bp,"items/"+n)["minecraft:item"].description.identifier));
 for(const name of readdirSync(new URL("blocks/",bp)))items.add(read(bp,"blocks/"+name)["minecraft:block"].description.identifier);
 for(const dir of ["chests","structures","entities"])for(const name of readdirSync(new URL("loot_tables/"+dir+"/",bp))){
  const t=read(bp,"loot_tables/"+dir+"/"+name);for(const p of t.pools)for(const e of p.entries)if(e.type==="item"&&e.name?.startsWith("bearframe:"))assert(items.has(e.name),name+" references "+e.name);
 }
});
test("world container loot cannot award Farfield or a boss signature weapon",()=>{
 const forbidden=new Set(["bearframe:field_cutter",...catalog.filter(gear=>gear.boss).map(gear=>"bearframe:"+gear.id)]);
 function inspect(path,seen){
  if(seen.has(path))return;
  seen.add(path);
  function walk(node){
   if(!node||typeof node!=="object")return;
   if(node.type==="item")assert(!forbidden.has(node.name),path+" contains "+node.name);
   if(node.type==="loot_table")inspect(node.name,seen);
   for(const value of Object.values(node))walk(value);
  }
  walk(read(bp,path));
 }
 for(const dir of ["chests","structures"])
  for(const name of readdirSync(new URL("loot_tables/"+dir+"/",bp)))
   if(name.endsWith(".json"))inspect("loot_tables/"+dir+"/"+name,new Set());
});
