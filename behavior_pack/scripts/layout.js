export const SIZE = {x:21,y:19,z:17};
export const DECK = 13;
export const TERMINAL = [0,0,0];
export const DIRECTION = [1,-2,0];
export const BREAKER = [2,0,1];
export const GATE = [[4,0,0],[4,1,0]];
export const RECOVERY = [7,0,0];
export const BULKHEAD = [3,0,2];
export const POWER_LIGHTS = [[-2,2,0],[6,2,0]];
export const ACTORS = {
  engineer:[-3,0,-3], walker:[0,0,4], scout:[1,0,-3]
};
export const ROTATIONS = [
  (x,z)=>[x,z], (x,z)=>[-z,x], (x,z)=>[-x,-z], (x,z)=>[z,-x]
];
export function at(origin,[x,y,z],rotation=0){
  const [dx,dz]=ROTATIONS[rotation](x,z);
  return {x:origin.x+dx,y:origin.y+y,z:origin.z+dz};
}
