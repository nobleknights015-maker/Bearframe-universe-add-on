// Dry survey checks are intentionally separate from native flooded habitats.
export function drySoil(block,soil){
 return Boolean(block&&!block.isWaterlogged&&!block.isLiquid&&soil.has(block.typeId));
}
export function dryClear(block,clear){
 return Boolean(block&&!block.isWaterlogged&&!block.isLiquid&&clear.has(block.typeId));
}
