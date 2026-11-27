"""Build a local Ranzie + Bearframe city test candidate from owner-supplied packs.
No third-party structure data is stored in this tool or required in GitHub.
"""
import argparse, hashlib, json, struct, zipfile
from pathlib import Path
from collections import Counter
SOURCE_SHA='291007a870c3b22d7c8e463af251f177dac83586feccec37d261bca9fd5bbed6'
MARKER='bearframe:overgrown_city_marker'
PREFIX='Bearframe_Overgrown_Cities/'
BP='Bearframe_Behavior/'
class NBT:
    def __init__(self,b): self.b=b; self.p=0; self.ranges={}; self.list_headers={}
    def take(self,n):
        if n<0 or self.p+n>len(self.b): raise ValueError('invalid NBT size')
        r=self.b[self.p:self.p+n]; self.p+=n; return r
    def num(self,f): return struct.unpack('<'+f,self.take(struct.calcsize('<'+f)))[0]
    def string(self): return self.take(self.num('H')).decode('utf8')
    def read(self,t,path=()):
        start=self.p
        if t==10:
            result={}
            while (k:=self.num('B')):
                n=self.string(); result[n]=self.read(k,path+(n,))
        elif t==9:
            k=self.num('B'); count=self.num('i'); self.list_headers[path]=(start+1,count,k)
            result=[self.read(k,path+(i,)) for i in range(count)]
        elif t==8: result=self.string()
        elif t in (7,11,12): result=self.take(self.num('i')*{7:1,11:4,12:8}[t])
        else: result=self.num({1:'b',2:'h',3:'i',4:'q',5:'f',6:'d'}[t])
        self.ranges[path]=(start,self.p)
        return result
    def root(self):
        if self.num('B')!=10: raise ValueError('expected compound')
        self.string(); r=self.read(10)
        if self.p!=len(self.b): raise ValueError('trailing NBT data')
        return r

def strtag(s):
    b=s.encode(); return struct.pack('<H',len(b))+b

def palette_entry(version):
    return b'\x08'+strtag('name')+strtag(MARKER)+b'\x0a'+strtag('states')+b'\x00'+b'\x03'+strtag('version')+struct.pack('<i',version)+b'\x00'

def add_marker(blob):
    n=NBT(blob); d=n.root(); w,h,l=d['size']; s=d['structure']; p=s['palette']['default']['block_palette']; idx,sec=s['block_indices']; be=s['palette']['default'].get('block_position_data',{})
    def at(x,y,z):
        i=idx[(x*h+y)*l+z]; return p[i]['name'] if i>=0 else None
    candidates=[]
    for x in range(2,w-2):
        for y in range(h-2):
            for z in range(2,l-2):
                i=(x*h+y)*l+z
                if at(x,y,z) in ('minecraft:stone_bricks','minecraft:cobbled_deepslate') and at(x,y+1,z)=='minecraft:air' and at(x,y+2,z)=='minecraft:air' and all(sec[j]==-1 for j in (i,i+l,i+2*l)) and str(i) not in be:
                    candidates.append((abs(x-(w-1)/2)+abs(z-(l-1)/2),i))
    if not candidates: raise ValueError('no dry open pavement for marker')
    _,i=min(candidates); pp=('structure','palette','default','block_palette'); ip=('structure','block_indices',0,i)
    pos,count,kind=n.list_headers[pp]; assert kind==10 and count==len(p)
    a,b=n.ranges[ip]; assert b-a==4
    end=n.ranges[pp][1]; edits=[(a,b,struct.pack('<i',count)),(pos,pos+4,struct.pack('<i',count+1)),(end,end,palette_entry(p[idx[i]]['version']))]
    out=blob
    for a,b,v in sorted(edits,reverse=True): out=out[:a]+v+out[b:]
    check=NBT(out).root(); cs=check['structure']; assert cs['block_indices'][0][i]==count and cs['palette']['default']['block_palette'][count]['name']==MARKER
    assert cs['block_indices'][1]==sec and cs['entities']==s['entities'] and cs['palette']['default'].get('block_position_data',{})==be
    return out

def item(name,weight,low=1,high=1):
    e={'type':'item','name':name,'weight':weight}
    if high>1:e['functions']=[{'function':'set_count','count':{'min':low,'max':high}}]
    return e

def loot(tier):
    base=[item('minecraft:bread',8,1,3),item('minecraft:torch',7,2,6),item('minecraft:paper',5,1,4),item('minecraft:iron_nugget',7,2,7),item('minecraft:copper_ingot',5,1,3),item('minecraft:coal',6,1,4),item('minecraft:string',4,1,3)]
    salvage=[item('bearframe:salvaged_alloy',8,1,min(4,tier+1)),item('minecraft:iron_ingot',6,1,3),item('minecraft:redstone',5,1,4),item('minecraft:amethyst_shard',4,1,3),item('bearframe:legacy_cell',max(1,tier-1))]
    odds=[(98,2,0,0),(94,6,0,0),(86,12,2,0),(76,18,5,1),(96,4,0,0)][tier]
    gear=[{'type':'empty','weight':odds[0]}]+[item(n,w) for n,w in zip(('bearframe:phase_edge','bearframe:watchtower_lance','bearframe:foundry_prototype'),odds[1:]) if w]
    return {'pools':[{'rolls':{'min':2,'max':4},'entries':base},{'rolls':{'min':0,'max':min(3,tier+1)},'entries':[{'type':'empty','weight':10}]+salvage},{'rolls':1,'entries':gear}]}

def encode(o): return (json.dumps(o,indent=2)+'\n').encode()

def build(source,base,out):
    assert hashlib.sha256(source.read_bytes()).hexdigest()==SOURCE_SHA,'wrong Ranzie input version'
    with zipfile.ZipFile(base) as z:
        assert z.testzip() is None
        files={n:z.read(n) for n in z.namelist() if not n.endswith('/')}
    manifest=json.loads(files[BP+'manifest.json']); old_version=manifest['header']['version']; bp_uuid=manifest['header']['uuid']
    assert old_version==[0,11,17], 'expected 0.11.17 base'
    version=[0,11,18]
    # Keep all historical structures and quest-critical sites; stop generating four redundant general settlements.
    general={'bearframe:coalition_city','bearframe:frontier_colony','bearframe:colony_waystation','bearframe:collapsed_rail_settlement'}
    key=BP+'worldgen/structure_sets/farfield_landmarks.json'; landmarks=json.loads(files[key]); entries=landmarks['minecraft:structure_set']['structures']
    assert general <= {e['structure'] for e in entries}
    landmarks['minecraft:structure_set']['structures']=[e for e in entries if e['structure'] not in general]; files[key]=encode(landmarks)
    for prefix in (BP,'Bearframe_Resources/'):
        key=prefix+'manifest.json'; m=json.loads(files[key]); m['header']['version']=version
        for module in m['modules']: module['version']=version
        for dep in m.get('dependencies',[]):
            if dep.get('version')==old_version:dep['version']=version
        files[key]=encode(m)
    with zipfile.ZipFile(source) as z:
        assert z.testzip() is None
        city={n:z.read(n) for n in z.namelist() if not n.endswith('/')}
    old_count=sum(n.endswith('.mcstructure') for n in city); assert old_count==536
    # The original archive contains a fragment, not a valid template-pool definition.
    city.pop('worldgen/template_pools/village/custom/test.json')
    city.pop('loot_tables/chests/names.json')
    for i,name in enumerate(('iron','gold','diamond','netherite','cstore')):
        table=loot(i)
        for pool in table['pools']:
            for e in pool['entries']:
                if e.get('name','').startswith('bearframe:'):
                    assert BP+'items/'+e['name'].split(':')[1]+'.json' in files
        city['loot_tables/chests/'+name+'.json']=encode(table)
    for n in list(city):
        if n.startswith('structures/village/custom/streets/') and Path(n).stem in {*(f'road{i}' for i in range(1,5)),*(f'cross{i}' for i in range(1,7))} and n.endswith('.mcstructure'):
            city[n]=add_marker(city[n])
    cm=json.loads(city['manifest.json']); cm['header']['name']='R&S Overgrown Cities — Bearframe local compatibility'; cm['header']['version']=[1,3,1]; cm['header']['min_engine_version']=manifest['header']['min_engine_version']
    for module in cm['modules']:module['version']=[1,3,1]
    cm['dependencies']=[{'uuid':bp_uuid,'version':version},{'module_name':'@minecraft/server','version':'2.10.0'}]
    cm['modules'].append({'type':'script','language':'javascript','entry':'scripts/city_population.js','uuid':'13a1cf45-96a7-4a91-b6ed-5bccb3476039','version':[1,3,1]})
    city['manifest.json']=encode(cm)
    city['scripts/city_population.js']=Path(__file__).with_name('city_population.js').read_bytes()
    city['blocks/overgrown_city_marker.json']=encode({'format_version':'1.26.50','minecraft:block':{'description':{'identifier':MARKER},'components':{'minecraft:geometry':'minecraft:geometry.full_block','minecraft:material_instances':{'*':{'texture':'bearframe_frontier_marking','render_method':'opaque'}},'minecraft:destructible_by_mining':{'seconds_to_destroy':1.5},'minecraft:destructible_by_explosion':{'explosion_resistance':6}}}})
    for n,b in city.items():files[PREFIX+n]=b
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(files.items()):z.writestr(n,b)
    with zipfile.ZipFile(out) as z:assert z.testzip() is None and len(z.namelist())==len(files)
    print(f'{out}: {len(files)} files, {old_count} city templates, SHA-256 {hashlib.sha256(out.read_bytes()).hexdigest()}')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('base',type=Path);p.add_argument('out',type=Path);a=p.parse_args();build(a.source,a.base,a.out)
