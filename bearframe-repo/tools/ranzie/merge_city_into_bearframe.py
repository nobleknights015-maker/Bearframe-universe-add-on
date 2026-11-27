"""Consolidate the owner-local 0.11.18 city candidate into Bearframe's two packs."""
import argparse, hashlib, json, zipfile
from pathlib import Path
BP='Bearframe_Behavior/'
RP='Bearframe_Resources/'
CITY='Bearframe_Overgrown_Cities/'
VERSION=[0,11,19]

def merge(source,output):
    with zipfile.ZipFile(source) as z:
        assert z.testzip() is None
        files={n:z.read(n) for n in z.namelist() if not n.endswith('/')}
        assert len(files)==len([n for n in z.namelist() if not n.endswith('/')])
    base={n:b for n,b in files.items() if not n.startswith(CITY)}
    city={n[len(CITY):]:b for n,b in files.items() if n.startswith(CITY)}
    assert sum(n.endswith('.mcstructure') for n in city)==536
    manifest=json.loads(base[BP+'manifest.json']); old=manifest['header']['version']; assert old==[0,11,18]
    # The ordinary Overgrown subpack becomes the default content. Custom preset
    # overrides are deliberately not installed. Preserve all source city IDs.
    for n,b in city.items():
        if n in ('manifest.json','pack_icon.png') or n.startswith('subpacks/'):continue
        dest=BP+n
        if dest in base:raise ValueError('city path collision: '+dest)
        base[dest]=b
    for n,b in city.items():
        if n.startswith('subpacks/overgrown/'):
            dest=BP+n[len('subpacks/overgrown/'):]
            if dest in base and dest[len(BP):] not in city:raise ValueError('Overgrown preset collision: '+dest)
            base[dest]=b
    # Source includes a malformed vanilla block identifier in processor predicates.
    corrections=0
    for n in base:
        if n.startswith(BP+'worldgen/processors/') and n[len(BP):] in city:
            b=base[n]; corrections+=b.count(b'minecraft:stone_ brick_slab');base[n]=b.replace(b'minecraft:stone_ brick_slab',b'minecraft:stone_brick_slab')
    # The unused fifth house processor incorrectly declares house1's ID.
    house=BP+'worldgen/processors/house5.json'
    assert base[house].count(b'"jigsaw:house1"')==1
    base[house]=base[house].replace(b'"jigsaw:house1"',b'"jigsaw:house5"')
    main=BP+'scripts/main.js'; line=b'import "./city_population.js";\n'
    assert line not in base[main]
    base[main]=line+base[main]
    for prefix in (BP,RP):
        path=prefix+'manifest.json'; m=json.loads(base[path]); assert m['header']['version']==old
        m['header']['version']=VERSION
        for mod in m['modules']: mod['version']=VERSION
        for dep in m.get('dependencies',[]):
            if dep.get('version')==old:dep['version']=VERSION
        base[path]=(json.dumps(m,indent=2)+'\n').encode()
    # No city module, extra UUID, dependency, or subpack selection required.
    assert set(n.split('/')[0] for n in base)=={BP[:-1],RP[:-1]}
    assert all(base[BP+n]==b for n,b in city.items() if n.endswith('.mcstructure'))
    assert all(base[n]==b for n,b in files.items() if n.startswith(BP+'structures/'))
    assert all(base[n]==b for n,b in files.items() if n.startswith(RP) and n!=RP+'manifest.json')
    assert base[BP+'scripts/city_population.js']==city['scripts/city_population.js']
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(base.items()):z.writestr(n,b)
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None and len(z.namelist())==len(base)
        assert all(z.read(n)==b for n,b in base.items())
    print(f'{len(base)} files; 536 city structures; {corrections} processor typo corrections; SHA256 {hashlib.sha256(output.read_bytes()).hexdigest()}')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('output',type=Path);a=p.parse_args();merge(a.source,a.output)
