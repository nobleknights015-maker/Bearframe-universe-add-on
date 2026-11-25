import {registerChartSite,removeChartBeacon} from "./route_charts.js";
import {populateRuin,retainResident} from "./ecology.js";
import {BlockTypes,BlockVolume,world} from "@minecraft/server";
import {at} from "./layout.js";
import {SURFACE_DATUM,SURFACE_DONE,SURFACE_SITES,LEGACY_DATUM,LEGACY_SITES} from "./surface_layout.js";

const crews={
  "frontier_colony": [
    [
      "ward_resident",
      30,
      4,
      26
    ],
    [
      "echo_drifter",
      26,
      4,
      26
    ],
    [
      "grid_repair_crawler",
      28,
      4,
      24
    ]
  ],
  "colony_waystation": [
    [
      "echo_drifter",
      24,
      4,
      21
    ],
    [
      "grid_hauler",
      20,
      4,
      21
    ]
  ],
  "coalition_city": [
    [
      "ward_resident",
      32,
      4,
      28
    ],
    [
      "echo_drifter",
      28,
      4,
      28
    ],
    [
      "grid_repair_crawler",
      30,
      4,
      26
    ],
    [
      "grid_watcher",
      30,
      4,
      30
    ]
  ],
  "frontier_ruin": [
    [
      "echo_drifter",
      23,
      4,
      21
    ],
    [
      "echo_sentinel",
      24,
      4,
      18
    ]
  ],
  "relay_nine": [
    [
      "grid_protocol_keeper",
      22,
      4,
      19
    ],
    [
      "grid_repair_crawler",
      18,
      4,
      19
    ]
  ],
  "crashed_skiff": [
    [
      "echo_drifter",
      23,
      4,
      19
    ],
    [
      "grid_watcher",
      20,
      4,
      18
    ]
  ],
  "syndicate_forge": [
    [
      "grid_hauler",
      26,
      4,
      22
    ],
    [
      "grid_repair_crawler",
      22,
      4,
      22
    ]
  ],
  "cinder_works": [
    [
      "grid_hauler",
      25,
      4,
      21
    ],
    [
      "grid_watcher",
      21,
      4,
      21
    ]
  ],
  "nivalis_lab": [
    [
      "grid_protocol_keeper",
      24,
      4,
      21
    ],
    [
      "echo_drifter",
      20,
      4,
      21
    ]
  ],
  "verdantis_station": [
    [
      "echo_drifter",
      25,
      4,
      21
    ],
    [
      "grid_repair_crawler",
      21,
      4,
      21
    ]
  ],
  "shattered_array": [
    [
      "grid_walker",
      25,
      4,
      22
    ],
    [
      "grid_watcher",
      21,
      4,
      22
    ]
  ],
  "sealed_archive_bunker": [
    [
      "ward_resident",
      22,
      4,
      20
    ],
    [
      "grid_protocol_keeper",
      18,
      4,
      20
    ]
  ],
  "flooded_pump_bunker": [
    [
      "grid_watcher",
      23,
      4,
      20
    ],
    [
      "grid_repair_crawler",
      19,
      4,
      20
    ]
  ],
  "collapsed_transit_bunker": [
    [
      "echo_drifter",
      23,
      4,
      20
    ],
    [
      "echo_sentinel",
      19,
      4,
      20
    ]
  ],
  "rootbound_service_bunker": [
    [
      "echo_drifter",
      23,
      4,
      20
    ],
    [
      "grid_repair_crawler",
      19,
      4,
      20
    ]
  ],
  "overgrown_colony": [
    [
      "ward_resident",
      30,
      4,
      26
    ],
    [
      "echo_drifter",
      26,
      4,
      26
    ],
    [
      "grid_repair_crawler",
      28,
      4,
      24
    ]
  ],
  "collapsed_rail_settlement": [
    [
      "echo_drifter",
      32,
      4,
      28
    ],
    [
      "grid_hauler",
      28,
      4,
      28
    ],
    [
      "grid_watcher",
      30,
      4,
      26
    ]
  ],
  "lost_waystation": [
    [
      "ward_resident",
      24,
      4,
      21
    ],
    [
      "grid_protocol_keeper",
      20,
      4,
      21
    ],
    [
      "grid_repair_crawler",
      22,
      4,
      23
    ]
  ]
};
const isDatum=id=>id===SURFACE_DATUM||id===LEGACY_DATUM;

const mineral=["grass_block","dirt","coarse_dirt","rooted_dirt","podzol","stone","andesite","diorite","granite",
  "tuff","gravel","snow","calcite","packed_ice","sand","red_sand","sandstone","red_sandstone","clay","terracotta",
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
    if(!clear.has(block.typeId)&&!isDatum(block.typeId))return;
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

  const isBeacon=b=>isDatum(b?.typeId)&&b.x===beacon.x&&b.y===beacon.y&&b.z===beacon.z;
  const foundations=[];
  // The entire platform needs dry ground no more than two blocks below it.
  if(!rect(0,0,width-1,depth-1,(x,z)=>{
    for(let y=floor-1;y>=floor-(site.expanded?6:3);y--){
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

  const valid=[...soil,...clear,SURFACE_DATUM,LEGACY_DATUM].filter(id=>BlockTypes.get(id));
  const occupied=dim.getBlocks(new BlockVolume(p(0,floor-2,0),p(width-1,height-1,depth-1)),{excludeTypes:valid},false);
  if(occupied.getCapacity())return;
  // Reject waterlogged foliage and other survey sites in the grade envelope.
  if(!rect(0,0,width-1,depth-1,(x,z)=>{
    for(let y=floor-2;y<=height-1;y++){
      const b=block(x,y,z);
      if(b?.isWaterlogged||(isDatum(b?.typeId)&&!isBeacon(b)))return false;
    }
    return true;
  }))return;
  if(dim.getPlayers({location:p(midX,floor,midZ),maxDistance:65}).some(player=>{
    const {x,y,z}=player.location;
    return x>=base.x&&x<base.x+width&&z>=base.z&&z<base.z+depth&&y>=base.y+floor-(site.expanded?6:3)&&y<base.y+height;
  }))return;
  return foundations;
}

export function buildSurfaceSite(marker, search=true){
  if(marker.permutation.getState(SURFACE_DONE))return;
  const sites=marker.typeId===LEGACY_DATUM?LEGACY_SITES:SURFACE_SITES;
  const site=sites[marker.permutation.getState("bearframe:site")];
  if(!site)return;
  const {dimension:dim,location:loc}=marker;
  registerChartSite(site.id,dim.id,loc,"beacon");
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
      if(isDatum(marker.typeId))marker.setPermutation(marker.permutation.withState(SURFACE_DONE,true));
      // The placement and spawn run synchronously. Mark the successful build
      // before spawning so a failed mob cannot cause a duplicate structure.
      for(const [unit,x,y,z] of crews[site.id]??[]){
        const pos=at(base,[x,y,z]);
        const feet=dim.getBlock(pos);
        if(!feet?.isAir||!feet.above()?.isAir||feet.below()?.isLiquid||feet.below()?.isAir)continue;
        try{
          const frame=dim.spawnEntity("bearframe:"+unit,{x:pos.x+.5,y:pos.y,z:pos.z+.5});
          frame.setDynamicProperty("bearframe:region_role",site.id);
          retainResident(frame);
        }catch(error){
          console.warn("Bearframe resident spawn at "+site.id+": "+error);
        }
      }
      removeChartBeacon(site.id,dim.id,loc);
      registerChartSite(site.id,dim.id,at(base,[site.size.x>>1,site.deck+1,site.size.z>>1]));
      populateRuin(dim,site.id,base);
      return base;
    }
  }
}
