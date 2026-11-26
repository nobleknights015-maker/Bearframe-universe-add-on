// Legacy boolean claims are retained; only explicitly defeated encounters can be retried.
export const RETRY_TICKS=12000;
export function siteClaimKey(id,p){return "bearframe:boss_site:"+[id,Math.floor(p.x),Math.floor(p.y),Math.floor(p.z)].join(":");}
export function canRetryClaim(claim,hunt,now){if(!claim)return true;if(!hunt||typeof claim!=="string"||!claim.startsWith("defeated:"))return false;const tick=Number(claim.slice(9));return Number.isFinite(tick)&&(now<tick||now-tick>=RETRY_TICKS);}
export function defeatedClaim(now){return "defeated:"+now;}

export const HABITAT_DIRECTORY="bearframe:boss_habitats:";
export function recordHabitat(entries,p){
 const point=[Math.floor(p.x),Math.floor(p.y),Math.floor(p.z)];
 if(entries.some(e=>e.every((v,i)=>v===point[i])))return entries;
 return [point,...entries].slice(0,24);
}
export function chooseHabitat(entries,origin,claimFor,valid,now){
 return entries.filter(p=>valid(p)).filter(p=>{const c=claimFor(p);return c==="active"||canRetryClaim(c,true,now);}).sort((a,b)=>Math.hypot(a[0]-origin[0],a[2]-origin[2])-Math.hypot(b[0]-origin[0],b[2]-origin[2]))[0];
}
