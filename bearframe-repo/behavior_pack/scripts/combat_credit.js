// Shared combat attribution for melee and projectile-based quest progress.
export function creditedPlayer(source){
  const player=e=>e?.typeId==="minecraft:player"&&e.isValid;
  if(player(source?.damagingEntity))return source.damagingEntity;
  try{
    const owner=source?.damagingProjectile?.getComponent("minecraft:projectile")?.owner;
    return player(owner)?owner:undefined;
  }catch{return undefined;}
}
