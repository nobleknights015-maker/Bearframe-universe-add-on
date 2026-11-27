import json,zipfile,hashlib,sys,re,subprocess,tempfile
from pathlib import Path
base,out=sys.argv[1:3]; B='Bearframe_Behavior/'; R='Bearframe_Resources/'
with zipfile.ZipFile(base) as z: old={n:z.read(n) for n in z.namelist()}
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None; f={n:z.read(n) for n in z.namelist()}; assert len(f)==len(z.namelist())
assert set(n.split('/')[0] for n in f)=={B[:-1],R[:-1]}
assert all(f[n]==b for n,b in old.items() if n.endswith('.mcstructure'))
for p in [B,R]:
 m=json.loads(f[p+'manifest.json']); assert m['header']['version']==[0,11,21] and m['header']['uuid']==json.loads(old[p+'manifest.json'])['header']['uuid']; assert all(x['version']==[0,11,21] for x in m['modules'])
assert b'import "./rarity/main.js"' in f[B+'scripts/main.js'];assert b'import "./chest_loot/main.js"' in f[B+'scripts/main.js']
for n in f:
 if not n.endswith('.js'):continue
 if n not in old or f[n]!=old[n]:subprocess.run(['node','--input-type=module','--check'],input=f[n],check=True,capture_output=True)
 for m in re.finditer(rb'from\s*[\'\"](\.[^\'\"]+)[\'\"]|import\s*[\'\"](\.[^\'\"]+)[\'\"]',f[n]):
  import posixpath
  path=posixpath.normpath(posixpath.join(posixpath.dirname(n),(m[1] or m[2]).decode()));assert path in f,(n,path)
for n,b in f.items():
 if n.endswith('.json') and (n not in old or old[n]!=b):json.loads(b)
for n in f:
 if not n.startswith((B+'loot_tables/chests/',B+'loot_tables/structures/')) or not n.endswith('.json'):continue
 a=json.loads(old[n]); b=json.loads(f[n]); assert len(a['pools'])==len(b['pools'])
 for p,q in zip(a['pools'],b['pools']):
  assert p['rolls']==q['rolls'];assert [(e.get('name'),e.get('weight'),e['type']) for e in p['entries']]==[(e.get('name'),e.get('weight'),e['type']) for e in q['entries']]
# Run exact source functions in an isolated Node context, no Minecraft runtime claims.
rr=f[B+'scripts/rarity/main.js'].decode(); chest=f[B+'scripts/chest_loot/main.js'].decode(); lib=f[B+'scripts/rarity/mainLib.js'].decode()
def chunk(s,start,end):return s[s.index(start):s.index(end,s.index(start))]
script=chunk(rr,'const BF_GEAR =','function moddedMaterialParse')+'\n'+chunk(rr,'function randomRarity','function randomStats')+'\n'+chunk(chest,'const BF_RESTRICTED','const DB_KEY')+'\n'+chunk(chest,'const RARITY_CHANCES','const CHESTLOOT_RARITY_WEIGHTS')+'\n'+chunk(chest,'function getRandomInt','function splitLootIntoStacks')+'\n'+chunk(chest,'function clamp','/* =========================================================\n   STARTUP')
script=lib.replace('export const','const')+'\nconst RR_BASE=RARITY.COMMON;\n'+script+'''\nimport assert from 'node:assert/strict';
assert.equal(BF_GEAR.size,18);
for(const name of BF_GEAR){assert.equal(parseTags(name).data,'sword');assert.equal(parseMaterial(name).maxRarity,6);}
assert.equal(parseTags('bearframe:field_scanner').rarity,false);assert.equal(parseTags('minecraft:iron_sword').data,'sword');
for(let i=0;i<1000;i++)assert(randomRarity(RARITY.COMMON,{chance:0,maxRarity:6}).id<=6);
const table={minItemTypes:1,maxItemTypes:4,items:[{itemId:'bearframe:field_cutter',minAmount:1,maxAmount:1,rarity:'Very Common'},{itemId:'bearframe:veil_anchor',minAmount:1,maxAmount:1,rarity:'Very Common'},{itemId:'minecraft:bread',minAmount:2,maxAmount:4,rarity:'Common'}]};
for(let i=0;i<1000;i++){const items=generateLootItems(table);assert(items.length<=1);assert(items.every(x=>x.itemId==='minecraft:bread'&&x.amount>=2&&x.amount<=4));}
console.log('Targeted source tests: 18 gear IDs, excluded utility, vanilla equipment, 1000 rarity rolls, 1000 restricted chest rolls passed.');'''
subprocess.run(['node','--input-type=module'],input=script.encode(),check=True)
print('Archive verified: %d entries; %d structure files unchanged; original native loot weights and rolls unchanged; exact local imports resolve.'%(len(f),sum(n.endswith('.mcstructure') for n in f)))
