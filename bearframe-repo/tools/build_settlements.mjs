import fs from "node:fs";
import path from "node:path";
import {fileURLToPath} from "node:url";
import nbt from "prismarine-nbt";

const root = fileURLToPath(new URL("../behavior_pack/", import.meta.url));
const poolDir = path.join(root, "worldgen/template_pools");
const templateDir = path.join(root, "structures/bearframe");
const air = "minecraft:air";
const lamp = "bearframe:field_lantern";

const palettes = {
  civic: ["stone_bricks", "white_terracotta", "weathered_cut_copper", "cyan_terracotta"],
  industrial: ["deepslate_bricks", "tuff_bricks", "oxidized_cut_copper", "orange_terracotta"],
  woodland: ["mossy_stone_bricks", "mud_bricks", "oxidized_cut_copper", "green_terracotta"],
  checkpoint: ["polished_blackstone_bricks", "light_gray_terracotta", "cracked_deepslate_tiles", "red_terracotta"],
};
const themeFor = id => /intrusion|shattered|transit/.test(id) ? "checkpoint"
  : /forge|works|foundry|spillway|pump|grid|skiff/.test(id) ? "industrial"
  : /frontier|overgrown|echo|rootbound|verdantis/.test(id) ? "woodland" : "civic";

const sourcePart = name => JSON.parse(fs.readFileSync(
  new URL(`./lost_cities/parts/${name}.json`,import.meta.url),
)).slices;
const plans = Object.fromEntries(Object.entries({
  housing: ["building1_1","building1_4","building1_1","top1x1_3"],
  offices: ["building2_1","building2_3","building2_1","top1x1_1"],
  warehouse: ["building3_1","building3_4","top1x1_1"],
  archive: ["library00_1","building4_1","top1x1_3"],
  residence: ["building5_1","building5_3","top1x1_3"],
  shopping: ["shopping00_0","shopping00_1","shopping00_r1"],
  fountain: ["park_fountain1"],
  garden: ["park_trees"],
}).map(([role,parts])=>[role,parts.flatMap(sourcePart)]));

const layouts = {
  civic: ["housing","archive","shopping","fountain","offices","residence","garden","warehouse"],
  industrial: ["warehouse","offices","housing","fountain","shopping","warehouse","archive","residence"],
  woodland: ["garden","residence","archive","housing","warehouse","fountain","residence","shopping"],
  checkpoint: ["offices","archive","warehouse","garden","housing","shopping","offices","residence"],
};
const bedrockPalette = {
  " ":air,"*":"flower_pot","1":"polished_deepslate","@":"tinted_glass","D":"rooted_dirt",
  F:"furnace",L:"bookshelf",T:"air",a:"light_blue_stained_glass",l:"air",
  "$":"smooth_stone",C:"chest","%":"web",":":"iron_bars",S:"smooth_stone",
  c:"stone_brick_stairs",d:"stone_brick_stairs","-":"smooth_stone",".":"oak_fence",
  "=":"smooth_stone",K:"poppy","_":"smooth_stone",")":"quartz_stairs",Q:"quartz_block",
  w:"cobblestone_wall",W:"light_blue_stained_glass",p:"poppy",P:"moss_block",
};

const bunkerDepth = 22;
const bunkerThemes = {
  collapsed_transit_bunker: "transit",
  flooded_pump_bunker: "pumps",
  rootbound_service_bunker: "maintenance",
  sealed_archive_bunker: "records",
  shelter_bunker: "shelter",
  spillway_bunker: "pumps",
};

function buildBunker({cross,deck,theme,put,fill,crate}) {
  const floor=deck-16, start=cross-27;
  const transit=theme==="transit";
  const skin=transit?"stone_bricks":"deepslate_bricks";
  const deckplate=transit?"stone_bricks":"polished_andesite";
  const trim=transit?"cracked_stone_bricks":"oxidized_cut_copper";
  const bunkerLamp=transit?"glowstone":lamp;
  const torchState={torch_facing_direction:nbt.string("top")};
  const stairs={weirdo_direction:nbt.int(3),upside_down_bit:nbt.byte(0)};
  // A battered street access with a handrail and a lit stair to the lower level.
  for(let i=0;i<16;i++){
    const z=start+i,y=deck-i;
    fill(21,25,y-1,y+3,z,z,skin);
    fill(22,24,y+1,y+3,z,z,air);
    for(let x=22;x<=24;x++) put(x,y,z,"stone_brick_stairs",stairs);
    if(i%4===1) put(22,y+2,z,bunkerLamp);
  }
  fill(21,25,deck+1,deck+1,start,start,trim);
  fill(22,24,deck+1,deck+3,start,start,air);
  for(const x of [21,25]){
    put(x,deck+2,start,skin);
    put(x,deck+3,start,bunkerLamp);
  }

  const hall=cross-10, secure=cross+10;
  function shell(z) {
    fill(10,27,floor,floor+6,z,z+16,skin);
    fill(11,26,floor+1,floor+5,z+1,z+15,air);
    for(const x of [11,26]) for(const dz of [3,8,13]) put(x,floor+4,z+dz,bunkerLamp);
  }
  shell(hall);
  shell(secure);
  if(transit){
    const railPalette={
      Q:"quartz_block",g:"redstone_torch",h:"glowstone","~":air,
      // Bearframe encounters and salvage tables supply the combat and rewards.
      "!":"iron_block","1":"stone_bricks","4":"stone_bricks",
    };
    for(const [part,z] of [["station_underground",hall+1],["rail_dungeon1",secure+1]]){
      for(const [y,layer] of sourcePart(part).entries()){
        for(const [dz,row] of layer.entries()) for(const [dx,symbol] of [...row].entries()){
          const x=11+dx, height=floor+y, depth=z+dz;
          if(symbol==="C") crate(x,height,depth,"industrial");
          else if(symbol==="e"){
            put(x,height,depth,"rail",{rail_direction:nbt.int(1)});
          }else if(symbol==="f"){
            put(x,height,depth,"golden_rail",{rail_direction:nbt.int(1),rail_data_bit:nbt.byte(1)});
          }else if(symbol==="y"){
            // Upstream's stonebrick variant uses a 9:8:1000 crack/moss/plain mix.
            const roll=((Math.imul(x+1,73856093)^Math.imul(height+1,19349663)^Math.imul(depth+1,83492791))>>>0)%1017;
            put(x,height,depth,roll<9?"cracked_stone_bricks":roll<17?"mossy_stone_bricks":skin);
          }else{
            const block=railPalette[symbol];
            if(!block)throw Error("Unmapped bunker tile "+symbol);
            put(x,height,depth,block,symbol==="g"?torchState:undefined);
          }
        }
      }
    }

  }else{
    const fittings={
      shelter:["white_wool","light_gray_wool","smoker","cauldron"],
      records:["bookshelf","bookshelf","cartography_table","tinted_glass"],
      maintenance:["smithing_table","anvil","cut_copper","moss_block"],
      pumps:["copper_block","cauldron","iron_bars","oxidized_copper"],
    }[theme];
    for(const z of [hall,secure]){
      for(const x of [13,17,24]) for(const dz of [3,6,12,14]){
        put(x,floor+1,z+dz,fittings[(x+dz)%fittings.length]);
        if(theme==="records"&&x<20)put(x,floor+2,z+dz,"bookshelf");
      }
      for(const x of [12,25]){
        fill(x,x,floor+4,floor+4,z+2,z+14,trim);
        put(x,floor+3,z+8,bunkerLamp);
      }
      fill(12,16,floor+1,floor+1,z+9,z+9,theme==="pumps"?"iron_bars":trim);
      if(theme==="pumps")fill(12,16,floor+1,floor+1,z+10,z+11,"water");
      if(theme==="maintenance")put(12,floor+1,z+10,"flowering_azalea");
      if(theme==="shelter"){
        for(const x of [13,16]) fill(x,x,floor+1,floor+1,z+10,z+12,"cyan_wool");
      }
    }
  }

  // Continuous passage with full-block floors and two blocks of headroom.
  for(const [x0,x1,z0,z1] of [[22,24,start+16,hall+3],[19,24,hall+2,hall+5],[19,22,hall+1,secure+15]]){
    fill(x0,x1,floor,floor,z0,z1,deckplate);
    fill(x0,x1,floor+1,floor+3,z0,z1,air);
  }
  for(const z of [hall+4,secure+5]) put(23,floor+1,z,bunkerLamp);
  crate(18,floor+1,hall+5,theme==="shelter"?"bunker":"industrial");
  crate(23,floor+1,secure+12,theme==="records"?"archive":"bunker");
}

function buildDistrict(tag, id, surfaceDeck) {
  const themeBelow=bunkerThemes[id];
  const lift=themeBelow?bunkerDepth:0;
  const deck=surfaceDeck+lift;
  const [oldWidth, oldHeight, oldDepth] = tag.value.size.value.value;
  const side = 32, end = 44;
  const width = oldWidth + 2*side, depth = oldDepth + 2*end;
  const height = Math.max(oldHeight+lift, deck + 25);
  const index = (x, y, z) => (x * height + y) * depth + z;
  const structure = tag.value.structure.value;
  const palette = structure.palette.value.default.value;
  const [primary, secondary] = structure.block_indices.value.value;
  const [main, extra] = [primary, secondary].map(() => Array(width * height * depth).fill(-1));
  const shift = oldIndex => {
    const x = Math.floor(oldIndex / (oldHeight * oldDepth));
    const y = Math.floor(oldIndex / oldDepth) % oldHeight;
    return index(x + side, y+lift, oldIndex % oldDepth + end);
  };
  if (structure.entities.value.value.length) throw Error(id + " has entities that need relocation");
  for (const [source, destination] of [[primary.value, main], [secondary.value, extra]]) {
    source.forEach((block, i) => { if (block >= 0) destination[shift(i)] = block; });
  }
  palette.block_position_data.value = Object.fromEntries(
    Object.entries(palette.block_position_data.value).map(([i, data]) => {
      const entity = data.value.block_entity_data?.value;
      if (entity?.x && entity?.z) {
        entity.x.value += side;
        if (entity.y) entity.y.value += lift;
        entity.z.value += end;
      }
      return [shift(Number(i)), data];
    }),
  );

  const types = palette.block_palette.value.value;
  const ids = new Map();
  function type(name, states = {}) {
    if (!name.includes(":")) name = "minecraft:" + name;
    const key = JSON.stringify([name,states]);
    if (!ids.has(key)) {
      ids.set(key, types.length);
      types.push({name:nbt.string(name), states:nbt.comp(states), version:nbt.int(18168865)});
    }
    return ids.get(key);
  }
  function put(x,y,z,name,states) {
    const i = index(x,y,z);
    delete palette.block_position_data.value[i];
    main[i] = type(name,states);
    extra[i] = type(air);
  }
  function fill(x0,x1,y0,y1,z0,z1,name) {
    for (let x=x0;x<=x1;x++) for (let z=z0;z<=z1;z++) for(let y=y0;y<=y1;y++) put(x,y,z,name);
  }

  const theme = themeFor(id);
  const [stone, wall, roof, trim] = palettes[theme];
  const boulevard = [23,width-24];
  function road(x0,x1,z0,z1) {
    fill(x0,x1,Math.max(0,deck-4),deck-1,z0,z1,stone);
    fill(x0,x1,deck,deck,z0,z1,"polished_andesite");
    fill(x0,x1,deck+1,deck+3,z0,z1,air);
  }
  for (const x of boulevard) road(x-3,x+3,0,depth-1);
  for (const z of [9,depth-10]) road(0,width-1,z-2,z+2);
  const cross = depth >> 1;
  road(24,side-1,cross-2,cross+2);
  road(width-side,width-25,cross-2,cross+2);
  const center = width >> 1;
  road(center-2,center+2,12,end-1);
  road(center-2,center+2,depth-end,depth-13);

  function crate(x,y,z,loot) {
    put(x,y,z,"chest",{"minecraft:cardinal_direction":nbt.string("north")});
    palette.block_position_data.value[index(x,y,z)] = nbt.comp({block_entity_data:nbt.comp({
      id:nbt.string("Chest"),x:nbt.int(x),y:nbt.int(y),z:nbt.int(z),
      isMovable:nbt.byte(1),LootTable:nbt.string(`loot_tables/chests/bearframe_${loot}.json`),
      LootTableSeed:nbt.long(0n),
    })});
  }

  function building(flip,z,role,damage) {
    const x = u => flip ? width-1-(3+u) : 3+u;
    const place = (u,y,v,name,states) => put(x(u),deck+y,z+v,name,states);
    const floors = plans[role];
    const park = role==="fountain" || role==="garden";
    fill(flip?width-19:3,flip?width-4:18,Math.max(deck-5,0),deck-1,z,z+15,stone);
    for(const [y,layer] of floors.entries()) {
      for(const [v,row] of layer.entries()) for(const [u,symbol] of [...row].entries()) {
        let name = bedrockPalette[symbol];
        if (symbol==="#") name = y%6===0 ? stone : wall;
        if (name===undefined) throw new Error(`Unmapped Lost Cities tile ${role}: ${symbol}`);
        if (name==="chest") {
          crate(x(u),deck+y,z+v,role==="warehouse"?"industrial":"settlement");
          continue;
        }
        if (damage && y>=8 && u<=3 && v<=3) name = air;
        const stair = name.endsWith("_stairs") ? {
          weirdo_direction:nbt.int(symbol==="d"?3:2),upside_down_bit:nbt.byte(Number(symbol==="d")),
        } : undefined;
        place(u,y,v,name,stair);
      }
    }
    const access = flip ? width-21 : 19;
    // The source entrances face different streets. Give each imported plot a
    // short recessed entry off our boulevard and keep its existing floor plan.
    for(const v of [7,8]) for(let u=12;u<=15;u++) {
      place(u,0,v,u===15?trim:park?"mossy_stone_bricks":"polished_andesite");
      for(let y=1;y<=2;y++) place(u,y,v,air);
    }
    for(const v of [6,9]) {
      place(15,0,v,stone);
      place(15,1,v,wall);
      place(15,2,v,wall);
    }
    if(!park) {
      for(const v of [7,8]) place(15,3,v,roof);
      place(14,3,7,lamp);
    }
    road(access,access+1,z+7,z+8);
    put(flip?width-20:19,deck+1,z+6,lamp);
    put(flip?width-20:19,deck,z+6,trim);
    if(park) {
      for(const [u,v] of [[3,3],[12,12]]) {
        place(u,0,v,"moss_block");
        place(u,1,v,"flowering_azalea");
      }
      return;
    }
    // Cut a continuous service ladder through the imported floors.
    for(let y=1;y<floors.length-1;y++) {
      place(3,y,5,stone);
      place(3,y,6,"ladder",{facing_direction:nbt.int(3)});
      if(y%6===0) place(3,y+1,7,air);
    }
    for(let y=1;y<=floors.length-6;y+=6) {
      place(8,y,3,lamp);
    }
    for(const [u,v] of [[1,1],[2,1],[1,2]]) {
      place(u,1,v,"moss_block");
    }
    if(role==="shopping" || role==="archive") crate(x(12),deck+1,z+12,role==="archive"?"archive":"settlement");
  }

  const lots = Array.from({length:4},(_,i)=>15+Math.floor(i*(depth-47)/3));
  for(const flip of [false,true]) for(const [i,z] of lots.entries()) {
    building(flip,z,layouts[theme][i+(flip?4:0)],i===(flip?1:2));
  }
  for(const x of boulevard) for(let z=4;z<depth;z+=8) put(x,deck,z,trim);

  if(themeBelow)buildBunker({cross,deck,theme:themeBelow,put,fill,crate});

  tag.value.size.value.value = [width,height,depth];
  primary.value = main;
  secondary.value = extra;
  return [width,height,depth];
}

for (const file of fs.readdirSync(poolDir).filter(file=>file.endsWith(".json")).sort()) {
  const id = path.basename(file,".json");
  const poolPath = path.join(poolDir,file);
  const pool = JSON.parse(fs.readFileSync(poolPath));
  const [entry] = pool["minecraft:template_pool"].elements;
  const source = path.basename(entry.element.location).replace(/_district$/,"");
  const structure = JSON.parse(fs.readFileSync(path.join(root,"worldgen/structures",file)));
  const start=structure["minecraft:jigsaw"].start_height.value;
  const depth=bunkerThemes[id]?bunkerDepth:0;
  const oldHeight=-start.absolute;
  const deck=depth&&oldHeight>=depth?oldHeight-depth:oldHeight;
  if (!Number.isInteger(deck)||deck<3) throw Error("Invalid surface level for "+id);
  const fileData = fs.readFileSync(path.join(templateDir,source+".mcstructure"));
  const {parsed} = await nbt.parse(fileData,"little");
  const size = buildDistrict(parsed,id,deck);
  const district = source + "_district";
  fs.writeFileSync(path.join(templateDir,district+".mcstructure"),nbt.writeUncompressed(parsed,"little"));
  entry.element.location = "bearframe/" + district;
  fs.writeFileSync(poolPath,JSON.stringify(pool,null,2)+"\n");
  start.absolute=-(deck+depth);
  fs.writeFileSync(path.join(root,"worldgen/structures",file),JSON.stringify(structure,null,2)+"\n");
  console.log(id,size.join(" × "));
}
