import { BlockPermutation, BlockVolume } from "@minecraft/server";
export const APPROACH_MARKER="bearframe:approach_anchor";
const APPROACH_BACK="minecraft:polished_deepslate";

const SIDES=[[1,0],[-1,0],[0,1],[0,-1]];
const SOIL=new Set(["minecraft:grass_block","minecraft:dirt","minecraft:coarse_dirt","minecraft:rooted_dirt",
  "minecraft:stone","minecraft:granite","minecraft:andesite","minecraft:diorite","minecraft:gravel",
  "minecraft:sand","minecraft:sandstone","minecraft:red_sand","minecraft:red_sandstone","minecraft:terracotta",
  "minecraft:tuff","minecraft:moss_block","minecraft:podzol","minecraft:mud","minecraft:snow"]);
const PLANT=/^minecraft:.*(?:_leaves|_grass|_flower|_sapling|_vine|_fern|_tulip|snow_layer|fern|deadbush|vine)$/;
const water=block=>block?.typeId==="minecraft:water" || block?.typeId==="minecraft:flowing_water";

function naturalGrade(dim,x,z){
  if(!dim.isChunkLoaded({x,y:64,z})) return;
  let block=dim.getTopmostBlock({x,z});
  while(block && PLANT.test(block.typeId))block=block.below();
  if(block && !block.isLiquid && SOIL.has(block.typeId))return block.y;
}

// Only new templates carry an apron marker. Work is limited to a short strip of
// loaded, ordinary terrain outside the stamped building.
export function gradeApproach(marker){
  if(marker.typeId!==APPROACH_MARKER) return;
  if(marker.permutation.getState("bearframe:graded")) return true;
  const dim=marker.dimension, {x,y,z}=marker.location, floor=y+2;
  const back=SIDES.find(([u,v])=>dim.getBlock({x:x+u,y,z:z+v})?.typeId===APPROACH_BACK);
  if(!back) return false;
  const dx=-back[0],dz=-back[1];
  const position=(n,lane,h)=>({x:x+n*dx+lane*dz,y:h,z:z+n*dz-lane*dx});
  const stepGrade=(n,end,last)=>Math.round(floor+(last-floor)*n/end);
  let route;
  for(let end=3;end<=18 && !route;end++){
    const p=position(end,0,floor), distant=position(end+1,0,floor);
    const last=naturalGrade(dim,p.x,p.z), outside=naturalGrade(dim,distant.x,distant.z);
    if(last===undefined || outside===undefined || water(dim.getBlock({...p,y:last+1})) ||
      water(dim.getBlock({...distant,y:outside+1})) || Math.abs(last-floor)>end ||
      Math.abs(last-outside)>1)continue;
    const slices=[];
    for(let n=1;n<=end;n++){
      const grade=stepGrade(n,end,last);
      for(const lane of [-1,0,1]){
        const p=position(n,lane,grade), ground=naturalGrade(dim,p.x,p.z);
        if(ground===undefined || ground>grade || grade-ground>14){slices.push(null);continue;}
        let safe=true;
        for(let h=ground+1;h<=grade+2;h++){
          const b=dim.getBlock({...p,y:h});
          if(h<=grade && water(b))continue;
          if(!b?.isAir){safe=false;break;}
        }
        slices.push(safe?{p,ground,n}:null);
      }
    }
    if(slices.every(Boolean))route={slices,end,last};
  }
  if(!route)return false;
  for(const {p} of route.slices){
    const nearby=dim.getPlayers({location:{x:p.x+.5,y:p.y+1,z:p.z+.5},maxDistance:2});
    if(nearby.some(player=>Math.floor(player.location.x)===p.x&&Math.floor(player.location.z)===p.z &&
      Math.abs(player.location.y-p.y)<=2)) return false;
  }
  for(const {p,ground,n} of route.slices){
    if(ground<p.y){
      dim.fillBlocks(new BlockVolume({...p,y:ground+1},p),"minecraft:stone");
      dim.getBlock(p).setType("minecraft:stone_bricks");
    }
    const ahead=stepGrade(n+1,route.end,route.last), behind=stepGrade(n-1,route.end,route.last);
    const west=ahead>p.y?dx:behind>p.y?-dx:0;
    const south=ahead>p.y?dz:behind>p.y?-dz:0;
    if(n<route.end && (west||south)){
      const face=west===1?0:west===-1?1:south===1?2:3;
      dim.getBlock({...p,y:p.y+1}).setPermutation(BlockPermutation.resolve("minecraft:stone_brick_stairs",
        {weirdo_direction:face,upside_down_bit:false}));
    }
  }
  marker.setPermutation(marker.permutation.withState("bearframe:graded",true));
  return true;
}
