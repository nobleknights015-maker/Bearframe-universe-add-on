import {at,DIRECTION,ROTATIONS} from "./layout.js";
import {PIN,REGION_ANCHOR,TYPES} from "./regions.js";
import {SPILLWAY_BUILT,SPILLWAY_DATUM,SPILLWAY_MARKER,SPILLWAY_PANEL} from "./spillway_layout.js";
import {ARCHIVE_SITE_IDS} from "./campaign_data.js";

const archives={
  relay_nine:[-3,0,-2],frontier_ruin:[-3,0,-4],crashed_skiff:[2,0,-3],
  sealed_archive_bunker:[2,0,-2],collapsed_transit_bunker:[-3,0,-2],
  rootbound_service_bunker:[2,0,2],flooded_pump_bunker:[-3,0,-2],
  overgrown_colony:[-2,0,-2],lost_waystation:[-4,0,-2],
  nivalis_lab:[-3,0,-3],shattered_array:[-3,0,-2],
};

export function chartSiteAvailable(dim,id,pos){
  let unloaded=false;
  const block=point=>{
    if(!dim.isChunkLoaded(point)){unloaded=true;return;}
    return dim.getBlock(point);
  };
  const index=TYPES.findIndex(site=>site.id===id);
  const terminal=point=>{
    const relay=id==="maintenance_relay";
    const panel=relay?"minecraft:lectern":TYPES[index].panel;
    const anchor=block(at(point,[0,-2,0]));
    if(anchor?.typeId!==(relay?"bearframe:relay_anchor":REGION_ANCHOR))return false;
    if(!relay&&anchor.permutation.getState("bearframe:region")!==index)return false;
    return block(point)?.typeId===panel&&ROTATIONS.some((_,r)=>
      block(at(point,relay?DIRECTION:PIN,r))?.typeId==="minecraft:lodestone");
  };
  let found;
  if(archives[id]){
    const record=ARCHIVE_SITE_IDS.indexOf(id);
    found=[pos,at(pos,archives[id])].some(point=>{
      const reader=block(point);
      return reader?.typeId==="bearframe:field_archive"&&reader.permutation.getState("bearframe:record")===record;
    });
  }else if(id==="spillway_bunker"){
    const marker=block(pos);
    if(marker?.typeId===SPILLWAY_MARKER&&marker.permutation.getState(SPILLWAY_BUILT)){
      const panel=at(pos,SPILLWAY_PANEL.map((v,i)=>v-SPILLWAY_DATUM[i]));
      const entry=at(pos,[2,0,0]);
      found=terminal(panel)&&[entry,at(entry,[0,1,0])].every(p=>block(p)?.isAir);
    }else found=terminal(pos);
  }else if(id==="maintenance_relay"||index>=0){
    found=terminal(pos);
  }else return true;
  return found||unloaded;
}
