import {BUNKER_ENTRY,BUNKER_TERMINAL,TOWN_DECK,TOWN_TERMINAL} from "../behavior_pack/scripts/ruins.js";
import {REGION_ANCHOR,PIN} from "../behavior_pack/scripts/regions.js";

const mc=(name)=>"minecraft:"+name;
const AIR=mc("air");
const brick=mc("stone_bricks");
const dark=mc("deepslate_tiles");
const oxidized=mc("oxidized_cut_copper");

export function stampBunker(mould,def,index,signalShelter){
 const {put,fill}=mould;
 const [start,surface,axis]=BUNKER_ENTRY;
 const [px,py,pz]=BUNKER_TERMINAL;
 const deck=py-1;
 const shell=signalShelter?mc("polished_deepslate"):mc("stone_bricks");
 const stripe=signalShelter?mc("yellow_terracotta"):oxidized;
 // Below ground: one structural collar around a complete network.
 fill(14,deck-1,3,34,deck+6,19,shell);
 fill(15,deck+1,4,33,deck+5,18,AIR);
 fill(15,deck,4,33,deck,18,dark);
 fill(15,deck,10,33,deck,12,brick);
 for(const x of [16,20,24,27,32])put(x,deck+4,12,mc("sea_lantern"));

 // Roofed headhouse and a broad pad at original ground level.
 fill(0,surface-9,6,6,surface,16,mc("stone"));
 fill(0,surface,6,6,surface,16,brick);
 fill(0,surface+1,6,6,surface+4,16,AIR);
 fill(1,surface+1,8,6,surface+4,14,shell);
 fill(2,surface+1,9,5,surface+3,13,AIR);
 fill(1,surface+1,10,1,surface+3,12,AIR);
 fill(1,surface,10,5,surface,12,stripe);
 put(4,surface+3,10,mc("sea_lantern"));

 // Descending corridor with headroom and a stair for each one-block rise.
 for(let x=start+2;x<=16;x++){
  const stairY=surface-(x-start-2);
  fill(x,stairY-1,axis-2,x,stairY+4,axis+2,shell);
  fill(x,stairY+1,axis-1,x,stairY+3,axis+1,AIR);
  for(let z=axis-1;z<=axis+1;z++)put(x,stairY,z,mc("stone_brick_stairs"),{
   weirdo_direction:1,upside_down_bit:false
  });
  if(x%3===0)put(x,stairY+3,axis,mc("sea_lantern"));
 }
 // Cut the stairwell into the lower vestibule after the collar and tunnel meet.
 fill(17,deck+1,axis-1,18,deck+3,axis+1,AIR);
 fill(17,deck,axis-1,18,deck,axis+1,brick);

 const local=([x,y,z],name,states)=>put(px+x,py+y,pz+z,name,states);
 for(const z of [8,14]){
  fill(19,deck+1,z,26,deck+5,z,shell);
  fill(20,deck+1,z,20,deck+3,z,AIR);
  fill(25,deck+1,z,25,deck+3,z,AIR);
 }
 fill(px+6,deck+1,4,px+6,deck+5,18,shell);
 if(signalShelter){
  for(const x of [21,23,25]) {
   put(x,deck+1,5,mc("smooth_quartz"));
   put(x,deck+1,6,mc("white_carpet"));
   put(x,deck+1,17,mc("iron_block"));
   put(x,deck+2,17,mc("tinted_glass"));
  }
  // A recessed cistern has a dry service rim and visibly retained water.
  fill(21,deck-1,16,25,deck,18,shell);
  fill(22,deck,17,24,deck,17,mc("water"));
  put(22,deck+3,17,mc("sea_lantern"));
  fill(29,deck+2,6,32,deck+2,7,mc("cut_copper"));
 }else{
  for(const x of [21,23,25]) {
   fill(x,deck+1,5,x,deck+2,5,oxidized);
   put(x,deck+1,16,mc("blast_furnace"));
  }
  fill(29,deck+1,16,32,deck+3,16,mc("weathered_copper"));
 }
 for(const [x,z] of [[17,7],[17,15],[26,6],[30,8],[32,13]])put(x,deck+1,z,mc("cobblestone"));
 // Preserve the threshold, power light, and two full blocks of standing space.
 for(const p of def.layout.seal)local(p,mc("iron_bars"));
 local(def.layout.cache,mc("barrel"));
 local(def.layout.signal,mc("coal_block"));
 const [ax,ay,az]=def.layout.actor;
 local([ax,ay,az],AIR);local([ax,ay+1,az],AIR);
 local([0,-2,0],REGION_ANCHOR,{"bearframe:region":index,"bearframe:status":0});
 local(PIN,mc("lodestone"));
 local([0,0,0],def.panel);
 put(0,surface-2,axis,"bearframe:approach_anchor",{"bearframe:graded":false});
 put(1,surface-2,axis,mc("polished_deepslate"));
}

export function stampTown(mould,def,index,saltline){
 const {put,fill}=mould;
 const [px,py,pz]=TOWN_TERMINAL;
 const floor=TOWN_DECK;
 const wall=saltline?mc("smooth_sandstone"):mc("polished_andesite");
 const trim=saltline?mc("orange_terracotta"):mc("cyan_terracotta");
 const roof=saltline?mc("cut_sandstone"):mc("weathered_cut_copper");

 function foundation(x1,z1,x2,z2,cap){
  fill(x1,0,z1,x2,floor-1,z2,mc("stone"));
  fill(x1,floor,z1,x2,floor,z2,cap);
 }
 function road(x1,z1,x2,z2,cap=brick){
  foundation(x1,z1,x2,z2,cap);
  fill(x1,floor+1,z1,x2,floor+3,z2,AIR);
 }
 function house(x1,z1,x2,z2,doorX,doorZ){
  foundation(x1,z1,x2,z2,wall);
  fill(x1,floor+1,z1,x2,floor+4,z2,wall);
  fill(x1+1,floor+1,z1+1,x2-1,floor+3,z2-1,AIR);
  fill(x1,floor+4,z1,x2,floor+4,z2,roof);
  fill(doorX,floor+1,doorZ,doorX,floor+2,doorZ,AIR);
  put(x1+1,floor+3,z1+1,mc("lantern"));
 }
 road(0,13,36,17);
 road(16,0,20,30);
 road(12,11,26,20,mc("polished_andesite"));
 for(let x=2;x<=35;x+=3)put(x,floor,15,trim);

 if(saltline){
  // Long loading canopy across the lane, plus rooms where shift crews slept.
  house(4,3,13,9,8,9);
  house(4,21,13,27,8,21);
  house(24,3,33,10,27,10);
  house(28,20,34,26,29,20);
  road(7,9,9,13);road(7,17,9,21);
  road(26,10,28,13);road(28,17,30,20);
  for(const x of [5,10,26,32])for(const z of [12,18]){
   foundation(x,z,x,z,wall);
   fill(x,floor+1,z,x,floor+5,z,wall);
  }
  fill(4,floor+5,12,11,floor+5,18,roof);
  fill(25,floor+5,12,33,floor+5,18,roof);
  for(const [x,z] of [[5,5],[12,23],[31,5],[30,24]])put(x,floor+1,z,mc("barrel"));
  for(const [x,z] of [[5,8],[11,22],[25,9],[33,20]])put(x,floor+1,z,mc("sand"));
  for(const x of [9,10,11])put(x,floor+1,4,mc("smooth_sandstone"));
  put(11,floor+1,24,mc("cartography_table"));
  put(29,floor+1,23,mc("smoker"));
  put(28,floor+1,5,mc("chiseled_sandstone"));
 }else{
  house(3,4,10,10,6,10);
  house(3,20,10,27,6,20);
  house(24,4,32,10,27,10);
  house(26,21,32,27,29,21);
  road(5,10,7,13);road(5,17,7,20);
  road(26,10,28,13);road(28,17,30,21);
  for(const [x,z] of [[4,6],[8,8],[28,5]])put(x,floor+1,z,mc("crafting_table"));
  road(12,21,14,24);
  fill(12,floor,22,14,floor,23,oxidized);
  for(const [x,z] of [[4,22],[8,25],[30,23],[13,18]])put(x,floor+1,z,mc("moss_block"));
  for(const [x,z] of [[8,5],[4,25],[31,8],[27,23]])put(x,floor+1,z,mc("polished_andesite_stairs"),{weirdo_direction:2,upside_down_bit:false});
  put(5,floor+1,24,mc("smoker"));
  put(29,floor+1,6,mc("cauldron"));
  put(28,floor+1,23,mc("smithing_table"));
  for(const [x,z] of [[5,6],[6,7],[28,5]])put(x,floor+4,z,AIR);
 }

 // Municipal service building opens onto the mapped road and central square.
 house(21,12,24,18,21,15);
 const local=([x,y,z],name,states)=>put(px+x,py+y,pz+z,name,states);
 for(const p of def.layout.seal)local(p,mc("iron_bars"));
 local(def.layout.cache,mc("barrel"));
 local(def.layout.signal,mc("coal_block"));
 local([0,-2,0],REGION_ANCHOR,{"bearframe:region":index,"bearframe:status":0});
 local(PIN,mc("lodestone"));
 local([0,0,0],def.panel);
 for(const [x,z,dx,dz] of [[0,15,-1,0],[36,15,1,0],[18,0,0,-1],[18,30,0,1]]){
  put(x,floor-2,z,"bearframe:approach_anchor",{"bearframe:graded":false});
  put(x-dx,floor-2,z-dz,mc("polished_deepslate"));
 }
}
