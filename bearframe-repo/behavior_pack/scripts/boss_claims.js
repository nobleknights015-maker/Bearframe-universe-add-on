// Legacy boolean claims are retained; only explicitly defeated encounters can be retried.
export const RETRY_TICKS=12000;
export function siteClaimKey(id,p){return "bearframe:boss_site:"+[id,Math.floor(p.x),Math.floor(p.y),Math.floor(p.z)].join(":");}
export function canRetryClaim(claim,hunt,now){if(!claim)return true;if(!hunt||typeof claim!=="string"||!claim.startsWith("defeated:"))return false;const tick=Number(claim.slice(9));return Number.isFinite(tick)&&(now<tick||now-tick>=RETRY_TICKS);}
export function defeatedClaim(now){return "defeated:"+now;}
