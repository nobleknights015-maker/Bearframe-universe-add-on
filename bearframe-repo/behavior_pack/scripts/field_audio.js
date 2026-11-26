export function fieldSound(dim,cue,position){
  try{dim.playSound("bearframe."+cue,position,{volume:.65});}
  catch(error){console.warn("[Bearframe audio] "+error);}
}
