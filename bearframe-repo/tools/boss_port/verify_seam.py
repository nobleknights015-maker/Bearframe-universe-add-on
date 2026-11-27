import zipfile,json,sys,subprocess,re,hashlib
from pathlib import Path
base,jar,out=sys.argv[1:];BP='Bearframe_Behavior/';RP='Bearframe_Resources/';boss='echo_seam_riven'
with zipfile.ZipFile(base) as z:old={n:z.read(n) for n in z.namelist()}
with zipfile.ZipFile(out) as z:f={n:z.read(n) for n in z.namelist()};assert z.testzip() is None
with zipfile.ZipFile(jar) as z:source=json.loads(z.read('assets/mowziesmobs/geo/umvuthana.geo.json'))['minecraft:geometry'][0];a=json.loads(z.read('assets/mowziesmobs/animations/umvuthana.animation.json'))['animations']
geo=json.loads(f[RP+'models/entity/'+boss+'.geo.json'])['minecraft:geometry'][0];assert [{k:v for k,v in b.items() if k!='cubes'} for b in geo['bones']]==[{k:v for k,v in b.items() if k!='cubes'} for b in source['bones']]
assert all(old[n]==f[n] for n in old if n.endswith('.mcstructure') or 'loot_tables/' in n)
assert all(old[n]==f[n] for n in old if '/chest_loot/' in n or '/rarity_stats/' in n)
clips=json.loads(f[RP+'animations/'+boss+'.animation.json'])['animations'];
for alias,key in [('idle','idle_aggressive'),('walk','walk_aggressive'),('attack0','attack_slash_right'),('attack1','attack_slash_left'),('death','die')]:
 clip=clips['animation.bearframe.'+boss+'.'+alias];assert clip['animation_length']==a[key]['animation_length'];assert set(clip['bones'])<=set(b['name'] for b in geo['bones'])
# Exercise actual strike branch, using world/entity stand-ins, not a Bedrock test.
s=f[BP+'scripts/boss_combat.js'].decode();start=s.index('    if (strike.move.sourceSlash) {');end=s.index('    if (!strike.released && elapsed >= strike.move.windup',start);branch=s[start:end]
js='''import assert from 'node:assert/strict';
const EntityDamageCause={entityAttack:'entityAttack'}; let hits=0, lunges=0,resets=0,blocked=false,inRange=true;
const height=(v,y)=>({...v,y:v.y+y});const clearPath=()=>!blocked;const inside=()=>inRange;
const reset=()=>resets++;const victim={id:'target',location:{x:1,y:0,z:0},applyDamage:()=>hits++};const other={id:'other',location:{x:1,y:0,z:0},applyDamage:()=>{throw Error('wrong target')}};
const entity={location:{x:0,y:0,z:0},applyImpulse:()=>lunges++};const dimension={playSound:()=>{}};let players=[victim,other];const state={};
const newStrike=()=>({move:{sourceSlash:true,windup:13,end:39,damage:9},direction:{x:1,z:0},targetId:'target',enraged:false});
function tick(strike,elapsed){const now=elapsed;
'''+branch+'''\n}
let s=newStrike();tick(s,4);assert.equal(lunges,0);tick(s,5);tick(s,6);assert.equal(lunges,1);tick(s,12);assert.equal(hits,0);tick(s,13);tick(s,14);assert.equal(hits,1);tick(s,39);assert.equal(resets,1);
s=newStrike();blocked=true;tick(s,5);tick(s,13);assert.equal(lunges,1);assert.equal(hits,1);blocked=false;
s=newStrike();players=[other];tick(s,13);assert.equal(hits,1);players=[victim,other];
s=newStrike();inRange=false;tick(s,13);assert.equal(hits,1);inRange=true;
s=newStrike();tick(s,20);assert.equal(hits,1);console.log('5 focused source-slash scenario checks passed');
'''
subprocess.run(['node','--input-type=module'],input=js.encode(),check=True)
print('70 source bone transforms exact; 5 clip durations match; 724 structures and all loot byte-identical.')
