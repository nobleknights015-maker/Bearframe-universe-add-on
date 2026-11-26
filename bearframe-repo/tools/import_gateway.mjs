import fs from "node:fs";
import {gunzipSync} from "node:zlib";
import nbt from "prismarine-nbt";

const blocks=new Map();
const key=(x,y,z)=>[x,y,z].join(",");
const put=(x,y,z,name,states={})=>blocks.set(key(x,y,z),[x,y,z,name,states]);
const mc=name=>"minecraft:"+name;
const stairDirs={east:0,west:1,south:2,north:3};
const source=process.argv[2]??new URL("./gateway/gateway_ii_blocks.json.gz",import.meta.url);
const input=fs.readFileSync(source);
const json=input[0]===0x1f&&input[1]===0x8b?gunzipSync(input):input;
for(const [x,y,z,name,props] of JSON.parse(json.toString("utf8"))){
 const p=props??{};
 let states={};
 if(name.endsWith("_stairs"))states={weirdo_direction:nbt.int(stairDirs[p.facing]),upside_down_bit:nbt.byte(Number(p.half==="top"))};
 if(name.endsWith("_slab"))states={"minecraft:vertical_half":nbt.string(p.type==="top"?"top":"bottom")};
 if(name.endsWith("_trapdoor"))states={direction:nbt.int(stairDirs[p.facing]),upside_down_bit:nbt.byte(Number(p.half==="top")),open_bit:nbt.byte(Number(p.open==="true"))};
 put(x+13,y+70,z+16,name,states);
}

const colors=["cyan_terracotta","light_gray_terracotta","blue_terracotta","white_concrete"];
const bays=[
 {roleIds:[0,9,14],name:"Farfield Dispatch",x:8,z:-7,props:["cartography_table","lectern","bookshelf"]},
 {roleIds:[2,11],name:"Systems",x:19,z:-7,props:["observer","redstone_lamp","iron_block"]},
 {roleIds:[4,10,12],name:"Fabrication",x:29,z:-7,props:["blast_furnace","smithing_table","anvil"]},
 {roleIds:[3,5,15],name:"Watchtower",x:39,z:-7,props:["observer","barrel","redstone_lamp"]},
 {roleIds:[1,7,16],name:"Commons",x:8,z:7,props:["moss_block","smoker","bookshelf"]},
 {roleIds:[8,13,6],name:"Gallery",x:19,z:7,props:["amethyst_block","chiseled_quartz_block","light_blue_wool"]},
 {roleIds:[],name:"Medbay",x:29,z:7,props:["white_wool","brewing_stand","cauldron"]},
 {roleIds:[],name:"Crew Quarters",x:39,z:7,props:["white_wool","cyan_wool","barrel"]},
];
const positions=Array(17);
const box=(x0,x1,y0,y1,z0,z1,name)=>{
 for(let x=x0;x<=x1;x++)for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++)put(x,y,z,mc(name));
};
// Fit out the central cabin inside the source hull; the exterior stays at its original scale.
box(0,48,100,100,-11,11,"smooth_quartz");
box(0,48,101,104,-11,11,"air");
box(0,48,105,105,-11,11,"polished_deepslate");
for(const z of [-11,11]){
 box(0,48,101,104,z,z,"polished_deepslate");
 box(2,46,102,103,z,z,"tinted_glass");
}
for(const x of [0,48])box(x,x,101,104,-10,10,"polished_deepslate");
box(1,47,100,100,-1,1,"cyan_terracotta");
for(let x=2;x<48;x+=4)for(const z of [-2,2])put(x,104,z,mc("sea_lantern"));
for(const [i,{x,z,props,roleIds}] of bays.entries()){
 const lo=z<0?-10:3,hi=z<0?-3:10,back=z<0?-9:9;
 box(x,x+7,100,100,lo,hi,colors[i%colors.length]);
 for(const [j,prop] of props.entries()){
  put(x+1+2*j,101,back,mc(prop));
  if(prop==="moss_block")put(x+1+2*j,102,back,mc("flowering_azalea"));
 }
 for(const [j,index] of roleIds.entries())positions[index]={x:x+1.5+j*2,y:101,z:z+.5};
}
put(1,101,2,mc("lodestone"));

const root=new URL("../behavior_pack/structures/bearframe/",import.meta.url);
const slices=[];
for(let start=-76;start<=127;start+=32){
 const points=[...blocks.values()].filter(([x])=>x>=start&&x<start+32);
 const min=(axis)=>Math.min(...points.map(p=>p[axis]));
 const max=(axis)=>Math.max(...points.map(p=>p[axis]));
 const x0=min(0),y0=min(1),z0=min(2),w=max(0)-x0+1,h=max(1)-y0+1,d=max(2)-z0+1;
 const palette=[], keys=new Map(), data=Array(w*h*d).fill(-1);
 for(const [x,y,z,name,states] of points){
  const tile=JSON.stringify([name,states]);
  if(!keys.has(tile)){
   keys.set(tile,palette.length);
   palette.push({name:nbt.string(name),states:nbt.comp(states),version:nbt.int(18168865)});
  }
  data[((x-x0)*h+y-y0)*d+z-z0]=keys.get(tile);
 }
 const id="gateway_hull_"+slices.length;
 const tag=nbt.comp({
  format_version:nbt.int(1),size:nbt.list(nbt.int([w,h,d])),
  structure_world_origin:nbt.list(nbt.int([0,0,0])),
  structure:nbt.comp({
   block_indices:{type:"list",value:{type:"list",value:[nbt.int(data),nbt.int(data.map(()=>-1))]}},
   entities:nbt.list(nbt.comp([])),
   palette:nbt.comp({default:nbt.comp({block_position_data:nbt.comp({}),block_palette:nbt.list(nbt.comp(palette))})}),
  }),
 });
 fs.writeFileSync(new URL(id+".mcstructure",root),nbt.writeUncompressed(tag,"little"));
 slices.push({id,origin:{x:x0,y:y0,z:z0},size:[w,h,d]});
}
fs.writeFileSync(new URL("../behavior_pack/scripts/gateway_layout.js",import.meta.url),
 "export const GATEWAY_PARTS="+JSON.stringify(slices,null,2)+";\nexport const GATEWAY_CREW="+JSON.stringify(positions,null,2)+";\n");
