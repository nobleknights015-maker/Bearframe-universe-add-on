import {pathToFileURL} from "node:url";
import {readFileSync} from "node:fs";
import {gunzipSync} from "node:zlib";
import nbt from "prismarine-nbt";

export function readLitematic(path){
if(!path)throw new Error("Pass the extracted .litematic path");
const {Metadata,Regions,MinecraftDataVersion}=nbt.simplify(nbt.parseUncompressed(gunzipSync(readFileSync(path)),"big"));
return Object.entries(Regions).map(([name,region])=>{
  const axes=["x","y","z"];
  const dimensions=axes.map(axis=>Math.abs(region.Size[axis]));
  const origin=axes.map(axis=>region.Position[axis]+Math.min(0,region.Size[axis]+1));
  const volume=dimensions.reduce((a,b)=>a*b,1);
  const size=Math.max(2,Math.ceil(Math.log2(region.BlockStatePalette.length)));
  const mask=(1n<<BigInt(size))-1n;
  const words=region.BlockStates.map(([hi,lo])=>(BigInt(hi>>>0)<<32n)|BigInt(lo>>>0));
  if(words.length!==Math.ceil(volume*size/64))throw new Error("Packed volume does not match region size");
  const points=[];
  const counts=Array(region.BlockStatePalette.length).fill(0);
  const levels=Array(dimensions[1]).fill(0);
  for(let i=0;i<volume;i++){
    const word=Math.floor(i*size/64),shift=i*size%64;
    let value=words[word]>>BigInt(shift);
    if(shift+size>64)value|=words[word+1]<<BigInt(64-shift);
    const index=Number(value&mask);
    const state=region.BlockStatePalette[index];
    if(!state)throw new Error("Palette index outside range at "+i);
    counts[index]++;
    if(!/^minecraft:(air|cave_air|void_air)$/.test(state.Name)){
      const y=Math.floor(i/(dimensions[0]*dimensions[2]));
      levels[y]++;
      points.push([i%dimensions[0],y,Math.floor(i/dimensions[0])%dimensions[2],index]);
    }
  }
  return {
    points,name,author:Metadata.Author,MinecraftDataVersion,origin,dimensions,
    occupied:levels.reduce((a,b)=>a+b,0),levels,
    blockEntities:region.TileEntities??[],
    states:region.BlockStatePalette.map((state,i)=>({state,count:counts[i]}))
  };
});
}
if(process.argv[1] && import.meta.url===pathToFileURL(process.argv[1]).href)
  for(const {points,...region} of readLitematic(process.argv[2]))
    console.log(JSON.stringify(region,(_,value)=>typeof value==="bigint"?value.toString():value,2));
