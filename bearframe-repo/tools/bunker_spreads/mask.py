import numpy as np,json,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parent
from scipy import ndimage as nd
w=np.load(ROOT/'central.npz')['world'];pal=json.load(open(ROOT/'palette.json')); X0,Z0,Y0=-128,-128,-56
natural=set('air cave_air void_air water lava stone deepslate dirt grass_block bedrock gravel sand sandstone tuff calcite andesite granite diorite clay snow snow_block ice packed_ice dripstone_block pointed_dripstone moss_block rooted_dirt mud terracotta smooth_basalt basalt budding_amethyst amethyst_block amethyst_cluster small_amethyst_bud medium_amethyst_bud large_amethyst_bud grass tall_grass short_grass glow_lichen cave_vines cave_vines_plant azalea_leaves spruce_leaves oak_leaves spruce_log oak_log lily_pad'.split())
auth=[i for i,p in enumerate(pal) if p['Name'].startswith('minecraft:') and p['Name'].split(':')[1] not in natural and not p['Name'].endswith('_ore')]
mask=np.isin(w,auth); mask[:,67-Y0:,:]=False
# select connected built complex, allow gaps between floors and hall segments
link=nd.binary_dilation(mask,iterations=2); lab,n=nd.label(link); seed=lab[8-X0,61-Y0,40-Z0];print('seed',seed); counts=np.bincount(lab[mask]);print(sorted(enumerate(counts),key=lambda a:-a[1])[:20]);
seed=int(np.argmax(counts[1:])+1);sel=mask&(lab==seed);print('selected',sel.sum()); xx,yy,zz=np.where(sel);print('bounds',xx.min()+X0,xx.max()+X0,yy.min()+Y0,yy.max()+Y0,zz.min()+Z0,zz.max()+Z0)
# close per-layer gaps and fill rooms.  use floors/ceilings to bound large open voids.
inside=sel.copy()
for y in range(w.shape[1]):
 layer=sel[:,y,:]; a=nd.binary_closing(layer,iterations=2); a=nd.binary_fill_holes(a|layer)
 # preserve all cells in enclosed layer, including natural rocks deliberately part of original walls
 inside[:,y,:]|=a
# vertical corridors, large room interiors bounded by authored floors and ceilings within 15 blocks
above=np.zeros_like(sel);below=np.zeros_like(sel)
for delta in range(1,16):
 above[:,:-delta,:]|=sel[:,delta:,:];below[:,delta:,:]|=sel[:,:-delta,:]
inside|=above&below
# include source air/water within 2 blocks of built shell in underground and entrance, no exterior terrain
near=nd.binary_dilation(sel,iterations=2); airids=[i for i,a in enumerate(pal) if a['Name'] in ('minecraft:air','minecraft:cave_air','minecraft:water','minecraft:bubble_column')];inside|=near&np.isin(w,airids)
# cut any isolated terrain beyond the selected source footprint, retain only known data
inside &= w>=0
xx,yy,zz=np.where(inside);print('total',inside.sum(),'bounds',xx.min()+X0,xx.max()+X0,yy.min()+Y0,yy.max()+Y0,zz.min()+Z0,zz.max()+Z0)
co=collections.Counter()
for i,n in enumerate(np.bincount(w[inside],minlength=len(pal))):co[pal[i]['Name']]+=int(n)
print(co.most_common(120));np.save(ROOT/'mask.npy',inside);np.save(ROOT/'auth.npy',sel)
