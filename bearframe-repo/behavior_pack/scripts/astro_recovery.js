// Recovery never rewrites an occupied section; verify authored cells only.
export async function inspectPlacedSection({structure,origin,size,readBlock,yieldTick,batchSize=512}){
  let checked=0,scanned=0;
  for(let x=0;x<size[0];x++)for(let y=0;y<size[1];y++)for(let z=0;z<size[2];z++){
    if(++scanned%batchSize===0)await yieldTick();
    const offset={x,y,z};
    const expected=structure.getBlockPermutation(offset);
    if(!expected)continue;
    const p={x:origin.x+x,y:origin.y+y,z:origin.z+z};
    const block=readBlock(p);
    if(!block)return {ok:false,reason:"unloaded",position:p};
    if(!block.permutation.matches(expected.type.id,expected.getAllStates())||
       Boolean(block.isWaterlogged)!==structure.getIsWaterlogged(offset))
      return {ok:false,reason:"mismatch",position:p};
    checked++;
  }
  return {ok:checked>0,reason:checked?"matched":"empty-template",checked};
}

export function liftLanding({isCurrent,standing,teleport,notify,label}){
  if(!isCurrent())return "cancelled";
  if(!standing()||!teleport()){
    notify("Lift landing is blocked or unavailable. Clear the landing and try again.");
    return "blocked";
  }
  notify(label);
  return "arrived";
}
