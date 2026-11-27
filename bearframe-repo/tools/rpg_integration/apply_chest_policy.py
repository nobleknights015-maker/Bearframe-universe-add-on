"""Rebuild the 0.11.22 chest-only equipment policy from the local 0.11.21 candidate."""
import argparse, copy, hashlib, json, re, subprocess, zipfile
from pathlib import Path
BP='Bearframe_Behavior/'
RP='Bearframe_Resources/'
MATERIALS={'bearframe:salvaged_alloy','bearframe:legacy_cell'}
RRS_SIGNATURES={'rrs:oreman_signature_weapon','rrs:razor_signature_weapon'}
REPLACEMENTS={'bearframe:phase_edge':'minecraft:iron_sword','bearframe:watchtower_lance':'minecraft:diamond_sword','bearframe:foundry_prototype':'minecraft:netherite_sword'}
def restricted(name):
    return isinstance(name,str) and ((name.startswith('bearframe:') and name not in MATERIALS) or name in RRS_SIGNATURES)
def json_bytes(obj):
    return (json.dumps(obj,indent=2)+'\n').encode()
def walk(obj):
    if isinstance(obj,dict):
        yield obj
        for v in obj.values():yield from walk(v)
    elif isinstance(obj,list):
        for v in obj:yield from walk(v)
def build(source,output):
    with zipfile.ZipFile(source) as z:
        assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))
        old={n:z.read(n) for n in z.namelist()}
    f=old.copy()
    tables={n for n in f if n.startswith((BP+'loot_tables/chests/',BP+'loot_tables/structures/')) and n.endswith('.json')}
    structures=[n for n in f if n.endswith('.mcstructure')]
    assert len(tables)==23 and len(structures)==724
    for n in structures+[n for n in f if n.startswith(BP+'worldgen/processors/') and n.endswith('.json')]:
        for ref in re.findall(rb'loot_tables/[a-zA-Z0-9_./-]+\.json',f[n]):
            path=BP+ref.decode();assert path in f;tables.add(path)
    pending=list(tables)
    while pending:
        n=pending.pop()
        for e in walk(json.loads(f[n])):
            if e.get('type')=='loot_table':
                path=BP+e['name'];assert path in f
                if path not in tables:tables.add(path);pending.append(path)
    assert not any('/entities/' in n for n in tables)
    count=0;changed=0
    for n in sorted(tables):
        data=json.loads(f[n]);before=copy.deepcopy(data)
        for e in walk(data):
            if e.get('type')=='item' and restricted(e.get('name')):
                e['name']=REPLACEMENTS[e['name']];count+=1
        if data!=before:f[n]=json_bytes(data);changed+=1
        assert not any(e.get('type')=='item' and restricted(e.get('name')) for e in walk(data))
    assert (changed,count)==(23,46)
    script=BP+'scripts/chest_loot/main.js'
    js=f[script].decode()
    policy='const BF_CHEST_MATERIALS = new Set('+json.dumps(sorted(MATERIALS))+');\nconst BF_RRS_SIGNATURES = new Set('+json.dumps(sorted(RRS_SIGNATURES))+');\nfunction isRestrictedChestItem(id) {\n    if (typeof id !== "string") return true;\n    const name = id.trim().toLowerCase();\n    return (name.startsWith("bearframe:") && !BF_CHEST_MATERIALS.has(name)) || BF_RRS_SIGNATURES.has(name);\n}'
    js,hits=re.subn(r'^const BF_RESTRICTED = new Set\([^\n]+\);$',lambda _:policy,js,flags=re.M);assert hits==1
    def replace(a,b):
        nonlocal js
        assert js.count(a)==1,a
        js=js.replace(a,b)
    a='    /*\n     * Verify that Minecraft actually recognizes'
    replace(a,'    if (isRestrictedChestItem(itemId)) {\n        return { valid: false, message: "§cReserved equipment cannot be placed in random chest loot." };\n    }\n\n'+a)
    replace('lootTable.items.filter(item=>!BF_RESTRICTED.has(item.itemId))','lootTable.items.filter(item=>item && !isRestrictedChestItem(item.itemId))')
    replace('        const loot =\n            stacks[i];\n\n        try {','        const loot =\n            stacks[i];\n        if (isRestrictedChestItem(loot.itemId)) continue;\n\n        try {')
    f[script]=js.encode()
    subprocess.run(['node','--input-type=module','--check'],input=f[script],check=True)
    ids=[json.loads(f[n])['minecraft:item']['description']['identifier'] for n in f if n.startswith(BP+'items/') and n.endswith('.json')]
    blocked=sorted(n for n in ids if restricted(n));assert len(blocked)==26
    for n in structures:
        assert all(i.encode() not in f[n] for i in blocked),n
    for p in (BP,RP):
        n=p+'manifest.json';m=json.loads(f[n]);assert m['header']['version']==[0,11,21]
        m['header']['version']=[0,11,22]
        for mod in m['modules']:mod['version']=[0,11,22]
        for dep in m.get('dependencies',[]):
            if dep.get('version')==[0,11,21]:dep['version']=[0,11,22]
        f[n]=json_bytes(m)
    for n in old:
        if n not in tables and n not in {script,BP+'manifest.json',RP+'manifest.json'}:assert f[n]==old[n],n
    def part(a,b):return js[js.index(a):js.index(b,js.index(a))]
    test='\n'.join([part('const BF_CHEST_MATERIALS','const DB_KEY'),part('const RARITY_CHANCES','const CHESTLOOT_RARITY_WEIGHTS'),part('function getRandomInt','function splitLootIntoStacks'),part('function clamp','/* =========================================================\n   STARTUP')])
    start=js.index('function parseSingleItem(');end=re.search(r'^function \w+\(',js[start+1:],re.M).start()+start+1
    test+='\n'+js[start:end]+'\nclass ItemStack {}\nimport assert from "node:assert/strict";\nconst blocked='+json.dumps(blocked)+';\n'
    test+="""
for (const id of blocked) {assert(isRestrictedChestItem(id));assert(!parseSingleItem(id).valid);}
assert(isRestrictedChestItem('bearframe:future_weapon'));assert(isRestrictedChestItem(' BEARFRAME:CYBER_KATANA_MK6 '));
for (const id of ['minecraft:iron_sword','minecraft:diamond_sword','minecraft:netherite_sword','bearframe:salvaged_alloy','bearframe:legacy_cell']) assert(!isRestrictedChestItem(id));
const items=[...blocked,'minecraft:iron_sword','minecraft:bread','bearframe:salvaged_alloy'].map(itemId=>({itemId,minAmount:1,maxAmount:1,rarity:'Very Common'}));
for(let i=0;i<2000;i++){const result=generateLootItems({items,minItemTypes:1,maxItemTypes:27});assert(result.length>0);assert(result.every(e=>!isRestrictedChestItem(e.itemId)));}
assert.deepEqual(generateLootItems({items:items.slice(0,blocked.length),minItemTypes:1,maxItemTypes:27}),[]);
"""
    subprocess.run(['node','--input-type=module'],input=test.encode(),check=True)
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(f.items()):z.writestr(n,b)
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None and len(z.namelist())==len(f)
        assert all(z.read(n)==b for n,b in f.items())
    print('23 chest tables, 46 replacements, 724 unchanged structures, 26 restricted IDs, 2000 loot rolls. SHA256',hashlib.sha256(output.read_bytes()).hexdigest())
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();build(a.source,a.output)
