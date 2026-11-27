import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync,readdirSync} from "node:fs";
import nbt from "prismarine-nbt";
const bp=new URL("../behavior_pack/",import.meta.url);
const catalog=JSON.parse(readFileSync(new URL("../docs/loot_gear_catalog.json",import.meta.url),"utf8"));
const forbidden=new Set(["bearframe:field_cutter",...catalog.filter(g=>g.boss).map(g=>"bearframe:"+g.id)]);
function files(dir){
 return readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(new URL(e.name+"/",dir)):[new URL(e.name,dir)]);
}
export function inspectContainerData(node,path,checkTable){
 if(typeof node==="string"){assert(!forbidden.has(node),path+" contains restricted item "+node);return;}
 if(!node||typeof node!=="object")return;
 for(const [key,value] of Object.entries(node)){
  if(key.toLowerCase()==="loottable"&&typeof value==="string"&&value)checkTable(value,path);
  inspectContainerData(value,path+"."+key,checkTable);
 }
}
function inspectTable(name,source,seen=new Set()){
 const path=name.replace(/^behavior_pack\//,"");
 assert(/^loot_tables\/[a-zA-Z0-9_./-]+\.json$/.test(path)&&!path.includes(".."),source+" has unsupported loot reference "+name);
 if(seen.has(path))return;
 seen.add(path);
 const data=JSON.parse(readFileSync(new URL(path,bp),"utf8"));
 function walk(node){
  if(!node||typeof node!=="object")return;
  if(node.type==="item")assert(!forbidden.has(node.name),source+" links to "+node.name);
  if(node.type==="loot_table")inspectTable(node.name,source,seen);
  for(const child of Object.values(node))walk(child);
 }
 walk(data);
}
test("structure container records cannot bypass restricted loot rules",()=>{
 let count=0;
 for(const path of files(new URL("structures/",bp)).filter(p=>p.pathname.endsWith(".mcstructure"))){
  const data=nbt.simplify(nbt.parseUncompressed(readFileSync(path),"little"));
  const palette=data.structure.palette.default;
  inspectContainerData(palette.block_position_data??{},path.pathname,inspectTable);
  count++;
 }
 assert(count>=100,"expected at least the original structure inventory");
});
test("embedded stack and nested container loot references are inspected",()=>{
 assert.throws(()=>inspectContainerData({Items:[{Name:"bearframe:field_cutter"}]},"fixture",()=>{}),/restricted item/);
 assert.throws(()=>inspectContainerData({Items:[{tag:{Items:[{Name:"bearframe:veil_anchor"}]}}]},"fixture",()=>{}),/restricted item/);
 const references=[];
 inspectContainerData({LootTable:"loot_tables/chests/bearframe_archive.json"},"fixture",(name)=>references.push(name));
 assert.deepEqual(references,["loot_tables/chests/bearframe_archive.json"]);
});
