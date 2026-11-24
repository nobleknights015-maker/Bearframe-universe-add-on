import {BlockTypes,BlockVolume,world} from "@minecraft/server";
import {at} from "./layout.js";
import {SURFACE_DATUM,SURFACE_DONE,SURFACE_SITES} from "./surface_layout.js";

const mineral=["grass_block","dirt","coarse_dirt","rooted_dirt","podzol","stone","andesite","diorite","granite",
  "tuff","gravel","sand","red_sand","sandstone","red_sandstone","clay","terracotta",
  ...["white","orange","yellow","red","brown","light_gray"].map(c=>c+"_terracotta")];
const cuttable=["short_grass","tall_grass","fern","large_fern","leaf_litter","snow_layer","deadbush","dead_bush","dandelion","poppy",
  "blue_orchid","allium","azure_bluet","red_tulip","orange_tulip","white_tulip","pink_tulip","oxeye_daisy","cornflower","lily_of_the_valley",
  ...["oak","acacia","birch","spruce","jungle","dark_oak","cherry","pale_oak"].map(n=>n+"_leaves")];
const soil=new Set(mineral.map(s=>"minecraft:"+s));
const clear=new Set(["minecraft:air",...cuttable.map(s=>"minecraft:"+s)]);
const findOffsets=[0,12,-12,24,-24,36,-36];
const order=findOffsets.flatMap(x=>findOffsets.map(z=>[x,z])).sort((a,b)=>Math.abs(a[0])+Math.abs(a[1])-Math.abs(b[0])-Math.abs(b[1]));

function rect(x1,z1,x2,z2,visit){
  for(let x=x1;x<=x2;x++)for(let z=z1;z<=z2;z++)if(!visit(x,z))return false;
  return true;
}
function grade(dim,p){
  let block=dim.getTopmostBlock(p);
  for(let i=0;block&&i<20;i++){
    if(soil.has(block.typeId))return block.y;
    if(!clear.has(block.typeId)&&block.typeId!==SURFACE_DATUM)return;
    block=block.below();
  }
}
function survey(dim,base,site,beacon){
  const {x:width,y:height,z:depth}=site.size;
  const floor=site.deck;
  const p=(x,y,z)=>at(base,[x,y,z]);
  const block=(x,y,z)=>dim.getBlock(p(x,y,z));
  for(let x=(base.x-2)>>4;x<=((base.x+width+1)>>4);x++)
    for(let z=(base.z-2)>>4;z<=((base.z+depth+1)>>4);z++)
      if(!dim.isChunkLoaded({x:x*16,y:base.y+floor,z:z*16}))return;

  const isBeacon=b=>b?.typeId===SURFACE_DATUM&&b.x===beacon.x&&b.y===beacon.y&&b.z===beacon.z;
  const foundations=[];
  // The entire platform needs dry ground no more than two blocks below it.
  if(!rect(0,0,width-1,depth-1,(x,z)=>{
    for(let y=floor-1;y>=floor-3;y--){
      const b=block(x,y,z);
      if(soil.has(b?.typeId))return true;
      if(isBeacon(b))continue;
      if(!clear.has(b?.typeId)||b.isWaterlogged)return false;
      foundations.push({pos:p(x,y,z),type:b.typeId});
    }
    return false;
  }))return;
  // At least one complete, three-block-wide approach must touch dry ground
  // one step from the curb and have clear feet and head space.
  const midX=(width-1)>>1, midZ=(depth-1)>>1;
  const corridors=[
    [-2,midZ-1,-1,midZ+1],[width,midZ-1,width+1,midZ+1],
    [midX-1,-2,midX+1,-1],[midX-1,depth,midX+1,depth+1],
  ];
  if(!corridors.some(r=>rect(...r,(x,z)=>{
    for(const y of [floor,floor-1]){
      const b=block(x,y,z);
      if(soil.has(b?.typeId)&&[1,2].every(h=>{
        const above=block(x,y+h,z);
        return above&&!above.isWaterlogged&&clear.has(above.typeId);
      }))return true;
    }
    return false;
  })))return;

  const valid=[...soil,...clear,SURFACE_DATUM].filter(id=>BlockTypes.get(id));
  const occupied=dim.getBlocks(new BlockVolume(p(0,floor-2,0),p(width-1,height-1,depth-1)),{excludeTypes:valid},false);
  if(occupied.getCapacity())return;
  // Reject waterlogged foliage and other survey sites in the grade envelope.
  if(!rect(0,0,width-1,depth-1,(x,z)=>{
    for(let y=floor-2;y<=height-1;y++){
      const b=block(x,y,z);
      if(b?.isWaterlogged||(b?.typeId===SURFACE_DATUM&&!isBeacon(b)))return false;
    }
    return true;
  }))return;
  if(dim.getPlayers({location:p(midX,floor,midZ),maxDistance:45}).some(player=>{
    const {x,y,z}=player.location;
    return x>=base.x&&x<base.x+width&&z>=base.z&&z<base.z+depth&&y>=base.y+floor-3&&y<base.y+height;
  }))return;
  return foundations;
}

export function buildSurfaceSite(marker, search=true){
  if(marker.permutation.getState(SURFACE_DONE))return;
  const site=SURFACE_SITES[marker.permutation.getState("bearframe:site")];
  if(!site)return;
  const {dimension:dim,location:loc}=marker;
  for(const [dx,dz] of search?order:[[0,0]]){
    const center={x:loc.x+dx,y:loc.y,z:loc.z+dz};
    if(!dim.isChunkLoaded(center))continue;
    const actual=search?grade(dim,center):loc.y;
    if(actual===undefined||Math.abs(actual-loc.y)>14)continue;
    for(const lift of search?[0,1,-1]:[0]){
      const base=at({...center,y:actual+lift},[-(site.size.x>>1),-site.deck,-(site.size.z>>1)]);
      const foundations=survey(dim,base,site,loc);
      if(!foundations)continue;
      world.structureManager.place("bearframe:"+site.id+"_site",dim,base,{includeEntities:false});
      for(const {pos,type} of foundations){
        const block=dim.getBlock(pos);
        const slab=dim.getBlock({...pos,y:base.y+site.deck});
        if(slab&&!soil.has(slab.typeId)&&!clear.has(slab.typeId)&&block?.typeId===type)
          block.setType("minecraft:stone");
      }
      if(marker.typeId===SURFACE_DATUM)marker.setPermutation(marker.permutation.withState(SURFACE_DONE,true));
      return base;
    }
  }
}
