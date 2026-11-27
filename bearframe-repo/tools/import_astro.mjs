import fs from "node:fs";
import nbt from "prismarine-nbt";
import {readLitematic} from "./read_litematic.mjs";

const [source,paletteFile]=process.argv.slice(2);
if(!source||!paletteFile)throw Error("Usage: node tools/import_astro.mjs astro.litematic Bedrock-blockStates.json");
const [region,...others]=readLitematic(source);
if(others.length||region.name!=="astro"||region.occupied!==35961)throw Error("Expected the original Astro schematic");
const db=new Map();
for(const state of JSON.parse(fs.readFileSync(paletteFile))){
  const options=db.get(state.name)??[];
  options.push(state);db.set(state.name,options);
}
const cardinal=["south","west","north","east"],face=["down","up","north","south","west","east"];
const stair=["east","west","south","north"];
const aliases={dirt_path:"grass_path",magma_block:"magma",snow_block:"snow",snow:"snow_layer",
  stone_slab:"smooth_stone_slab",shulker_box:"undyed_shulker_box",tripwire:"trip_wire",
  weeping_vines_plant:"weeping_vines",twisting_vines_plant:"twisting_vines"};
function resolve(name,expected={}){
  const found=db.get(name)?.find(({states})=>Object.entries(expected).every(([key,value])=>states[key]?.value===value));
  if(!found)throw Error("No Bedrock state for "+name+" "+JSON.stringify(expected));
  return found;
}
function translate({Name,Properties:p={}}){
  const src=Name.slice(10);let name=aliases[src]??src;
  const states={};
  const set=(key,val)=>{if(val!==undefined)states[key]=val};
  if(p.axis)set("pillar_axis",p.axis);
  if(src.endsWith("_stairs")){
    set("weirdo_direction",stair.indexOf(p.facing));set("upside_down_bit",+(p.half==="top"));
    set("minecraft:corner",p.shape==="straight"?"none":p.shape);
  }else if(src.endsWith("_slab")){
    if(p.type==="double")name=name.replace(/_slab$/,"_double_slab");
    else set("minecraft:vertical_half",p.type);
  }else if(src.endsWith("_wall")){
    for(const d of cardinal)set("wall_connection_type_"+d,p[d]==="low"?"short":p[d]==="tall"?"tall":"none");
    set("wall_post_bit",+(p.up==="true"));
  }else if(["iron_bars","red_stained_glass_pane","oak_fence","tripwire"].includes(src)){
    for(const d of cardinal)set("minecraft:connection_"+d,+(p[d]==="true"));
    if(src==="tripwire")for(const tag of ["attached","disarmed","powered"])set(tag+"_bit",+(p[tag]==="true"));
  }else if(src==="iron_trapdoor"){
    set("direction",cardinal.indexOf(p.facing));set("open_bit",+(p.open==="true"));set("upside_down_bit",+(p.half==="top"));
  }else if(["anvil","carved_pumpkin","repeater"].includes(src)){
    if(src==="repeater"){name=p.powered==="true"?"powered_repeater":"unpowered_repeater";set("repeater_delay",+p.delay-1);}
    set("minecraft:cardinal_direction",p.facing);
  }else if(src==="redstone_wall_torch"){
    name=p.lit==="true"?"redstone_torch":"unlit_redstone_torch";set("torch_facing_direction",p.facing);
  }else if(src==="daylight_detector"){
    if(p.inverted==="true")name="daylight_detector_inverted";set("redstone_signal",+p.power);
  }else if(src==="grindstone"){
    set("attachment",p.face==="wall"?"side":p.face==="ceiling"?"hanging":"standing");set("direction",cardinal.indexOf(p.facing));
  }else if(src==="lever"){
    set("lever_direction",p.face==="wall"?p.facing:(p.face==="ceiling"?"down":"up")+
      (["east","west"].includes(p.facing)?"_east_west":"_north_south"));
    set("open_bit",+(p.powered==="true"));
  }else if(src==="tripwire_hook"){
    set("direction",cardinal.indexOf(p.facing));set("attached_bit",+(p.attached==="true"));set("powered_bit",+(p.powered==="true"));
  }else if(["ladder","end_rod","lightning_rod","hopper","stone_button"].includes(src)){
    set("facing_direction",face.indexOf(src==="stone_button"&&p.face!=="wall"?(p.face==="floor"?"up":"down"):p.facing));
    if(src==="hopper")set("toggle_bit",+(p.enabled==="false"));
    if(src==="lightning_rod")set("powered_bit",+(p.powered==="true"));
    if(src==="stone_button")set("button_pressed_bit",+(p.powered==="true"));
  }else if(src.includes("amethyst")&&p.facing)set("minecraft:block_face",p.facing);
  else if(src.endsWith("candle")){set("candles",+p.candles-1);set("lit",+(p.lit==="true"));}
  else if(src==="cactus")set("age",+p.age);
  else if(src==="farmland")set("moisturized_amount",+p.moisture);
  else if(src==="heavy_weighted_pressure_plate")set("redstone_signal",+p.power);
  else if(src==="lava")set("liquid_depth",+p.level);
  else if(src==="lilac")set("upper_block_bit",+(p.half==="upper"));
  else if(src==="snow")set("height",+p.layers-1);
  else if(name.endsWith("_vines"))set(name+"_age",+(p.age??25));
  return {block:resolve(name,states),waterlogged:p.waterlogged==="true"};
}

const palette=region.states.map(({state,count})=>count?translate(state):null);
const cells=new Map();
const key=(x,y,z)=>[x,y,z].join(",");
const put=(x,y,z,name,states)=>cells.set(key(x,y,z),{x,y,z,block:resolve(name,states)});
for(const [x,y,z,i] of region.points)cells.set(key(x,y,z),{x,y,z,...palette[i]});
const sections=[
  {name:"Systems",x:36,y:42,z:135,roles:[2,11],fixtures:["iron_block","observer","redstone_lamp","barrel"]},
  {name:"Atlas Production",x:120,y:42,z:135,roles:[4,5,10,12],fixtures:["smithing_table","blast_furnace","anvil","barrel"]},
  {name:"Watchtower",x:78,y:42,z:93,roles:[3,15],fixtures:["cartography_table","observer","barrel","redstone_lamp"]},
  {name:"Visual Production",x:78,y:42,z:177,roles:[6,8,13],fixtures:["amethyst_block","bookshelf","chiseled_quartz_block","sea_lantern"]},
  {name:"Farfield Dispatch",x:86,y:54,z:124,roles:[0,9,14],fixtures:["cartography_table","lectern","bookshelf","barrel"]},
  {name:"Main Commons",x:68,y:54,z:138,roles:[1,7,16],fixtures:["bookshelf","smoker","barrel","flower_pot","smooth_quartz_stairs","smooth_quartz_stairs","cyan_carpet","sea_lantern"]},
];
const offset={x:256,y:96,z:-128};
const global=(x,y,z)=>({x:x+offset.x,y:y+offset.y,z:z+offset.z});
const landings=[];
function floor(x,y,z){return cells.get(key(x,y-1,z))?.block.name}
function open(x,y,z){
  const below=floor(x,y,z);
  return !!below&&!/glass|bars|wall|rod|lava|fence|trapdoor|candle|carpet/.test(below)&&
    !cells.has(key(x,y,z))&&!cells.has(key(x,y+1,z));
}
function choose(section,n){
  const {x,y,z}=section, candidates=[];
  for(let dx=-6;dx<=6;dx++)for(let dz=-6;dz<=6;dz++)
    if(open(x+dx,y,z+dz))candidates.push([x+dx,y,z+dz]);
  candidates.sort((a,b)=>Math.hypot(a[0]-x,a[2]-z)-Math.hypot(b[0]-x,b[2]-z));
  const picked=[];
  for(const p of candidates){
    if(landings.some(q=>q[1]===p[1]&&Math.hypot(p[0]-q[0],p[2]-q[2])<2))continue;
    picked.push(p);landings.push(p);
    if(picked.length===n)return picked;
  }
  throw Error("Not enough safe positions in "+section.name);
}
const staff=[], signs=[];
const [arrival,exit,upper,log]=choose(sections[5],4);
const [lower]=choose({x:74,y:42,z:132,name:"Lower deck lift"},1);
for(const [i,section] of sections.entries()){
  const visits=i===5?[[0,"Farfield off-shift surveyor"],[2,"Systems off-shift engineer"],[3,"Watchtower off-shift officer"],[4,"Atlas off-shift rigger"],[6,"Visual Production off-shift artisan"]]:[];
  const people=[...section.roles.map(id=>[id,null]),...visits];
  const spots=choose(section,people.length+section.fixtures.length+1);
  for(const [j,[role,name]] of people.entries()){
    const [x,y,z]=spots[j];
    // A full-height floor keeps the player and crew out of bottom-slab collision.
    put(x,y-1,z,"smooth_quartz");
    staff.push({role,name,section:section.name,pos:global(x+.5,y,z+.5)});
  }
  for(const [j,type] of section.fixtures.entries())put(...spots[people.length+j],type);
  const p=spots.at(-1);
  put(...p,"standing_sign",{ground_sign_direction:0});
  signs.push({pos:global(...p),text:section.name});
}
for(const p of [exit,upper,lower])put(...p,"lodestone");
put(arrival[0],arrival[1]-1,arrival[2],"smooth_quartz");
function labelNear(p,text){
  const [spot]=choose({x:p[0],y:p[1],z:p[2],name:text},1);
  put(...spot,"standing_sign",{ground_sign_direction:0});
  signs.push({pos:global(...spot),text});
}
labelNear(exit,"Return Desk\nSurface berth");
labelNear(upper,"Deck Lift\nSystems • Atlas\nWatchtower • Visual");
labelNear(lower,"Deck Lift\nCommons • Farfield\nReturn Desk");
const [lowerArrival]=choose({x:lower[0],y:lower[1],z:lower[2],name:"Lower deck landing"},1);
put(lowerArrival[0],lowerArrival[1]-1,lowerArrival[2],"smooth_quartz");
const group=new Map();
for(const block of cells.values()){
  const {x,y,z}=block;
  const bucket=[x,y,z].map(v=>Math.floor(v/32)).join(",");
  const points=group.get(bucket)??[];points.push(block);group.set(bucket,points);
}
const parts=[];
const out=new URL("../behavior_pack/structures/bearframe/",import.meta.url);
const water=resolve("water",{liquid_depth:0});
const actorIds={jukebox:"Jukebox",shulker_box:"ShulkerBox",hopper:"Hopper",daylight_detector:"DaylightDetector"};
const actors=new Map(region.blockEntities.map(e=>[key(e.x,e.y,e.z),e]));
for(const points of group.values()){
  const axes=["x","y","z"];
  const [x,y,z]=axes.map(k=>Math.min(...points.map(p=>p[k])));
  const [w,h,d]=axes.map((k,i)=>Math.max(...points.map(p=>p[k]))-[x,y,z][i]+1);
  const primary=Array(w*h*d).fill(-1), secondary=primary.slice();
  const tiles=[],tileKeys=new Map(),positionData={};
  function tile({name,states,version}){
    const k=JSON.stringify([name,states]);
    if(!tileKeys.has(k)){tileKeys.set(k,tiles.length);tiles.push({name:nbt.string("minecraft:"+name),states:nbt.comp(states),version:nbt.int(version)});}
    return tileKeys.get(k);
  }
  for(const p of points){
    const i=((p.x-x)*h+p.y-y)*d+p.z-z;
    primary[i]=tile(p.block);
    if(p.waterlogged)secondary[i]=tile(water);
    const original=actors.get(key(p.x,p.y,p.z));
    if(original){
      const id=actorIds[original.id.slice(10)];
      if(!id)throw Error("Unmapped block entity "+original.id);
      if(original.Items?.length)throw Error("Unexpected nonempty schematic container");
      const actor={id:nbt.string(id),x:nbt.int(p.x-x),y:nbt.int(p.y-y),z:nbt.int(p.z-z),isMovable:nbt.byte(1)};
      if(id==="Hopper"||id==="ShulkerBox")actor.Items=nbt.list(nbt.comp([]));
      if(id==="Hopper")actor.TransferCooldown=nbt.int(original.TransferCooldown);
      positionData[i]=nbt.comp({block_entity_data:nbt.comp(actor)});
    }
  }
  const id="astro_section_"+parts.length;
  const raw=nbt.comp({format_version:nbt.int(1),size:nbt.list(nbt.int([w,h,d])),
    structure_world_origin:nbt.list(nbt.int([0,0,0])),
    structure:nbt.comp({block_indices:{type:"list",value:{type:"list",value:[nbt.int(primary),nbt.int(secondary)]}},
      entities:nbt.list(nbt.comp([])),palette:nbt.comp({default:nbt.comp({
        block_position_data:nbt.comp(positionData),block_palette:nbt.list(nbt.comp(tiles))})})})});
  fs.writeFileSync(new URL(id+".mcstructure",out),nbt.writeUncompressed(raw,"little"));
  parts.push({id,origin:global(x,y,z),size:[w,h,d]});
}
const [ax,ay,az]=arrival,[lx,ly,lz]=lowerArrival;
const layout={parts,staff,signs,exit:global(...exit),arrival:global(ax+.5,ay,az+.5),log:global(...log),
  lifts:[{pos:global(...upper),target:global(lx+.5,ly,lz+.5),label:"Department deck"},
         {pos:global(...lower),target:global(ax+.5,ay,az+.5),label:"Main Commons"}]};
fs.writeFileSync(new URL("../behavior_pack/scripts/astro_layout.js",import.meta.url),
  "export const ASTRO="+JSON.stringify(layout,null,2)+";\n");
console.log("Astro:",region.occupied,"original blocks,",parts.length,"sparse sections,",staff.length,"staff");
