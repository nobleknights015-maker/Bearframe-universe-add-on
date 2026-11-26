import {writeFileSync} from "node:fs";
import nbt from "prismarine-nbt";
import {CITY_ARRIVAL,CITY_EXIT,CITY_ROLES,CITY_SIZE} from "../behavior_pack/scripts/regions.js";
import {CITY_ORIGIN,DOCK_ROLES,STATION_WINGS} from "../behavior_pack/scripts/station_layout.js";

const modules=[{id:"orbital_city",origin:CITY_ORIGIN,size:Object.values(CITY_SIZE),roleIds:DOCK_ROLES},...STATION_WINGS];
const plans={
 orbital_city:[["dispatch","systems","fabrication"],["lounge","security","gallery"]],
 orbit_commons:[["galley","greenhouse","quarters"],["library","medbay","gallery"]],
 orbit_farfield:[["dispatch","laboratory"],["library","sample_store"]],
 orbit_operations:[["fabrication","engineering"],["cargo","security"]],
};
const furnishings={
 dispatch:["cartography_table","bookshelf","lectern","light_blue_stained_glass"],
 systems:["redstone_lamp","smooth_quartz","observer","cyan_stained_glass"],
 fabrication:["smithing_table","blast_furnace","anvil","iron_block"],
 lounge:["bookshelf","smooth_quartz_stairs","flower_pot","cyan_wool"],
 security:["iron_block","observer","barrel","red_stained_glass"],
 gallery:["chiseled_quartz_block","amethyst_block","smooth_quartz","purple_stained_glass"],
 galley:["smoker","cauldron","smooth_quartz","white_terracotta"],
 greenhouse:["flowering_azalea","moss_block","azalea","green_stained_glass"],
 quarters:["bookshelf","cyan_wool","white_wool","barrel"],
 library:["bookshelf","bookshelf","lectern","flower_pot"],
 medbay:["smooth_quartz","white_wool","brewing_stand","light_blue_stained_glass"],
 laboratory:["brewing_stand","cauldron","tinted_glass","amethyst_block"],
 sample_store:["barrel","moss_block","tinted_glass","raw_copper_block"],
 engineering:["copper_block","lightning_rod","observer","redstone_lamp"],
 cargo:["barrel","iron_block","hay_block","raw_iron_block"],
};
const roomDetails={
 dispatch:["map","map","server"],
 systems:["server","server","server"],
 fabrication:["bench","bench","cargo"],
 lounge:["seating","seating","planter"],
 security:["server","cargo","desk"],
 gallery:["exhibit","exhibit","exhibit"],
 galley:["stove","seating","seating"],
 greenhouse:["planter","planter","planter"],
 quarters:["bunk","bunk","bunk"],
 library:["shelves","desk","shelves"],
 medbay:["bunk","medical","bunk"],
 laboratory:["medical","experiment","experiment"],
 sample_store:["experiment","cargo","experiment"],
 engineering:["server","reactor","reactor"],
 cargo:["cargo","cargo","cargo"],
};
const corridor="smooth_quartz", hull="polished_blackstone", trim="polished_deepslate", window="tinted_glass";

for(const {id,origin,size:[w,h,d],roleIds} of modules){
 const cells=new Map();
 const put=(x,y,z,block)=>cells.set((x*h+y)*d+z,"minecraft:"+block);
 const fill=(x0,x1,y0,y1,z0,z1,block)=>{
  for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++)put(x,y,z,block);
 };
 const core=id==="orbital_city", middle=d>>1;
 fill(0,w-1,0,1,0,d-1,hull);
 fill(1,w-2,1,1,1,d-2,corridor);
 fill(0,w-1,2,h-2,0,d-1,hull);
 fill(1,w-2,2,h-2,1,d-2,"air");
 fill(0,w-1,h-1,h-1,0,d-1,hull);
 fill(2,w-3,h-1,h-1,2,d-3,trim);
 fill(1,w-2,1,1,middle-1,middle+1,"cyan_terracotta");
 // Recessed observation strips and ribbed pressure hull.
 for(const z of [0,d-1]){
  for(let x=2;x<w-2;x++){
   if(x%8<6)fill(x,x,3,4,z,z,window);
   else put(x,1,z,"iron_block");
  }
 }
 for(let x=4;x<w-3;x+=6){
  for(const z of [middle-2,middle+2]){
   put(x,h-2,z,trim);
   put(x,h-3,z,"sea_lantern");
  }
 }
 const groups=plans[id], first=core?9:4;
 for(let side=0;side<2;side++){
  const z0=side?middle+4:2,z1=side?d-3:middle-4;
  for(const [i,role] of groups[side].entries()){
   const span=(w-first-2)/groups[side].length;
   const x0=first+Math.floor(i*span),x1=first+Math.floor((i+1)*span)-1;
   const face=side?z0:z1, back=side?z1:z0;
   const tone=["cyan_terracotta","light_gray_terracotta","blue_terracotta"][i];
   fill(x0,x1,1,1,z0,z1,"polished_andesite");
   fill(x0+1,x1-1,1,1,z0+1,z1-1,tone);
   fill(x0+1,x1-1,2,2,back,back,"smooth_quartz");
   const furniture=furnishings[role];
   for(let x=x0+2;x<x1;x+=3){
    put(x,3,back,furniture[(x-x0)%furniture.length]);
    if((x-x0)%2===0)put(x,2,back+(side?-2:2),furniture[(x-x0+1)%furniture.length]);
   }
   const inward=side?1:-1;
   const front=face+inward, inner=face+inward*2;
   const features=roomDetails[role];
   for(const [index,kind] of features.entries()){
    const x=x0+2+Math.floor(index*(x1-x0-4)/2);
    if(kind==="bunk"){
     put(x,2,front,"white_wool");
     put(x,2,inner,"light_blue_wool");
     put(x,2,inner+inward,"light_blue_wool");
     put(x+1,2,inner,"barrel");
    }else if(kind==="seating"){
     put(x,2,front,"smooth_quartz_stairs");
     put(x+1,2,front,"smooth_quartz_stairs");
     put(x,2,inner+inward,"polished_andesite");
    }else if(kind==="planter"){
     put(x,2,inner,"moss_block");
     put(x,3,inner,"flowering_azalea");
     put(x,2,inner+inward,"moss_block");
     put(x,3,inner+inward,"azalea");
    }else if(kind==="server"||kind==="reactor"){
     fill(x,x,2,4,inner,inner,kind==="server"?"observer":"waxed_copper_block");
     put(x,3,inner,kind==="server"?"sea_lantern":"redstone_lamp");
    }else if(kind==="experiment"||kind==="exhibit"||kind==="medical"){
     put(x,2,inner,"smooth_quartz");
     put(x,3,inner,kind==="medical"?"brewing_stand":kind==="experiment"?"amethyst_block":"chiseled_quartz_block");
     put(x+1,2,inner,"tinted_glass");
     put(x+1,3,inner,"tinted_glass");
    }else{
     const unit={map:"cartography_table",bench:"smithing_table",cargo:"barrel",
      desk:"lectern",stove:"smoker",shelves:"bookshelf"}[kind];
     put(x,2,inner,unit);
     if(kind==="shelves"||kind==="cargo")put(x,3,inner,unit);
    }
   }
   put(x0,2,face,trim);
   put(x0,3,face,trim);
   put(x0,4,face,"sea_lantern");
  }
 }
 // Open every join on both sides of the docking spine.
 for(const wing of STATION_WINGS){
  for(const [gx,gy,gz] of wing.link){
   const localX=gx-origin.x, y=gy-origin.y, localZ=gz-origin.z;
   for(const [dx,dz] of [[0,0],[0,1],[0,-1],[1,0],[-1,0]]){
    const x=localX+dx,z=localZ+dz;
    if(x>=0&&x<w&&z>=0&&z<d&&y>=2&&y<=5)put(x,y,z,"air");
   }
  }
 }
 if(core){
  fill(1,7,1,1,1,d-2,"polished_andesite");
  for(const z of [3,d-4]){
   fill(3,6,2,2,z,z,"smooth_quartz");
   put(7,2,z,"barrel");
  }
  put(CITY_EXIT.x-origin.x,CITY_EXIT.y-origin.y,CITY_EXIT.z-origin.z,"lodestone");
 }
 for(const p of [...roleIds.map(i=>CITY_ROLES[i].pos),...(core?[CITY_ARRIVAL]:[])]){
  const x=Math.floor(p.x)-origin.x,y=p.y-origin.y,z=Math.floor(p.z)-origin.z;
  put(x,y-1,z,corridor);
  fill(x,x,y,y+1,z,z,"air");
 }
 // Give the dock an inset nose and the outlying wings reinforced roof spines.
 for(const x of [0,1,w-2,w-1])for(const z of [0,1,d-2,d-1]){
  put(x,0,z,"air");
  put(x,h-1,z,"air");
 }
 for(let x=3;x<w-3;x++){
  put(x,h-1,middle,core?"iron_block":"polished_andesite");
  if(x%7===0)put(x,h-1,middle-1,"sea_lantern");
 }
 const palette=[...new Set(cells.values())], lookup=new Map(palette.map((v,i)=>[v,i]));
 const blocks=Array.from({length:w*h*d},(_,i)=>lookup.get(cells.get(i))??-1);
 const data=nbt.comp({format_version:nbt.int(1),size:nbt.list(nbt.int([w,h,d])),
  structure_world_origin:nbt.list(nbt.int([0,0,0])),structure:nbt.comp({
   block_indices:{type:"list",value:{type:"list",value:[nbt.int(blocks),nbt.int(blocks.map(()=>-1))]}},
   entities:nbt.list(nbt.comp([])),palette:nbt.comp({default:nbt.comp({
    block_position_data:nbt.comp({}),
    block_palette:nbt.list(nbt.comp(palette.map(name=>({name:nbt.string(name),states:nbt.comp({}),version:nbt.int(18168865)})))),
   })}),
  }),
 });
 writeFileSync(new URL(`../behavior_pack/structures/bearframe/${id}.mcstructure`,import.meta.url),nbt.writeUncompressed(data,"little"));
}
