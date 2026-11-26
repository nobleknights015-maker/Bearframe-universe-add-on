import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import nbt from "prismarine-nbt";

export function loadStructure(id){
  const path=new URL(`../behavior_pack/structures/bearframe/${id}.mcstructure`,import.meta.url);
  const n=nbt.simplify(nbt.parseUncompressed(readFileSync(path),"little"));
  const [width,height,depth]=n.size;
  const palette=n.structure.palette.default.block_palette;
  const indices=n.structure.block_indices[0];
  function cell(x,y,z){
    if(x<0||x>=width||y<0||y>=height||z<0||z>=depth)return;
    return palette[indices[(x*height+y)*depth+z]];
  }
  function find(name){
    return indices.flatMap((index,i)=>palette[index]?.name===name?
      [[Math.floor(i/(height*depth)),Math.floor(i/depth)%height,i%depth]]:[]);
  }
  return {size:n.size,cell,find};
}

export function terminalLookup(template,anchor,region){
  const markers=template.find(anchor).filter(p=>region===undefined||
    template.cell(...p).states["bearframe:region"]===region);
  assert.equal(markers.length,1,`Expected one terminal anchor for region ${region}`);
  const [x,y,z]=markers[0];
  return {position:[x,y+2,z],at:([dx,dy,dz])=>template.cell(x+dx,y+2+dy,z+dz)};
}

export function walkableCells(template,starts,cleared=[]){
  const open=new Set(cleared.map(p=>p.join(",")));
  const name=(x,y,z)=>open.has([x,y,z].join(","))?"minecraft:air":template.cell(x,y,z)?.name;
  const seen=new Set(),queue=[...starts];
  while(queue.length){
    const [x,y,z]=queue.pop(),key=[x,y,z].join(",");
    const floor=name(x,y-1,z);
    if(seen.has(key)||name(x,y,z)!=="minecraft:air"||name(x,y+1,z)!=="minecraft:air"||
      !floor||floor==="minecraft:air"||floor==="minecraft:water")continue;
    seen.add(key);
    for(const [dx,dz] of [[1,0],[-1,0],[0,1],[0,-1]])
      for(const dy of [0,1,-1])queue.push([x+dx,y+dy,z+dz]);
  }
  return seen;
}
