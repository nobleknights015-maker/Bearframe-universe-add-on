from zipfile import ZipFile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from bedrock_nbt import Site
from math import sin,cos,radians
import hashlib
folder=Path('deliverables')
z=ZipFile(folder/'Bearframe_Bedrock_0.5.1.mcaddon')
names={
 'sealed_archive_bunker_site':'Sealed Archive Bunker',
 'flooded_pump_bunker_site':'Flooded Pump Bunker',
 'collapsed_transit_bunker_site':'Collapsed Transit Bunker',
 'rootbound_service_bunker_site':'Rootbound Service Bunker',
 'overgrown_colony_site':'Overgrown Colony',
 'collapsed_rail_settlement_site':'Collapsed Rail Settlement',
 'lost_waystation_site':'Lost Waystation',
}
palette={
 'air':'#000000','smooth_quartz':'#d7dddd','calcite':'#d4dede','iron_block':'#b6cbd0','polished_andesite':'#899091','andesite':'#808987',
 'cyan_terracotta':'#438f91','stone_bricks':'#626c72','stone':'#535d61','tinted_glass':'#4a767f','glass':'#81b5aa',
 'weathered_cut_copper':'#578778','oxidized_cut_copper':'#42836f','oxidized_copper':'#44856f','cut_copper':'#bd7351',
 'waxed_cut_copper':'#ad6b4d','redstone_block':'#b53d3a','red_terracotta':'#ab4946','cyan_concrete':'#3c8186',
 'cracked_deepslate_tiles':'#343b49','deepslate_tiles':'#414858','polished_deepslate':'#4f5760','deepslate_bricks':'#46545c',
 'polished_blackstone':'#3d3946','polished_blackstone_bricks':'#484552','blackstone':'#41404a','basalt':'#57535d',
 'mossy_stone_bricks':'#576e53','moss_block':'#657d42','azalea_leaves':'#657d46','flowering_azalea_leaves':'#729b60',
 'flowering_azalea':'#779564','mangrove_roots':'#695343','mangrove_log':'#514439','mangrove_planks':'#895846','mud_bricks':'#8f7162',
 'smooth_sandstone':'#d4b480','cut_sandstone':'#bfa77b','orange_terracotta':'#b97549','sand':'#ccb78d',
 'packed_ice':'#76a5bd','light_blue_terracotta':'#658caa','sea_lantern':'#b4f3e2','spillway_lamp':'#b4f3e2',
 'amethyst_block':'#946bc4','white_wool':'#d7d7c7','barrel':'#886647','coarse_dirt':'#88705f','tuff':'#757d71',
 'yellow_terracotta':'#c39e50','end_stone':'#b7af86','iron_bars':'#879896','smooth_stone':'#8f9da2',
 'dark_oak_planks':'#6a5142','spruce_planks':'#94745d','chiseled_stone_bricks':'#768995','water':'#437f9f',
 'spillway_grate':'#53656b','spillway_casing':'#75838c','light_gray_concrete':'#a9b4b4','blast_furnace':'#606974',
}
def rgb(h):
    return tuple(bytes.fromhex(h[1:]))
def render(site,low,high,size):
    w,h=size
    im=Image.new('RGB',size,'#202930')
    d=ImageDraw.Draw(im)
    faces=[]
    def screen(x,y,z):
        return ((x-z)*.87,(x+z)*.44-y)
    occupied={}
    for i,b in enumerate(site.blocks):
        if b<0: continue
        x,y,z=site.xyz(i)
        n=site.label(b)
        if low<=y<=high and n!='air':
            occupied[x,y,z]=n
    bound=[screen(x,y,z) for x,y,z in occupied]
    spanx=max(x for x,y in bound)-min(x for x,y in bound)
    spany=max(y for x,y in bound)-min(y for x,y in bound)
    scale=min((w-34)/(spanx+2),(h-26)/(spany+2))
    midx=(max(x for x,y in bound)+min(x for x,y in bound))/2
    midy=(max(y for x,y in bound)+min(y for x,y in bound))/2
    def pt(x,y,z):
        px,py=screen(x,y,z)
        return ((px-midx)*scale+w/2,(py-midy)*scale+h/2)
    facesets=(
        ((1,0,0),[(1,0,0),(1,0,1),(1,1,1),(1,1,0)],.82),
        ((0,0,1),[(0,0,1),(1,0,1),(1,1,1),(0,1,1)],.72),
        ((0,1,0),[(0,1,0),(1,1,0),(1,1,1),(0,1,1)],1.03))
    for (x,y,z),name in sorted(occupied.items(),key=lambda a:sum(a[0])):
        color=rgb(palette.get(name,'#7f8581'))
        shade=((x*3+y*7+z*11)%7)-3
        for (dx,dy,dz),points,factor in facesets:
            if (x+dx,y+dy,z+dz) in occupied: continue
            tile=tuple(int(max(0,min(255,c*factor+shade))) for c in color)
            d.polygon([pt(x+a,y+b,z+c) for a,b,c in points],fill=tile)
    return im
W,H=1560,1050
sheet=Image.new('RGB',(W,H),'#141b20')
draw=ImageDraw.Draw(sheet)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans'
def text(x,y,s,sz,fill='#e5edee',bold=False):
    draw.text((x,y),s,font=ImageFont.truetype(font+('-Bold.ttf' if bold else '.ttf'),sz),fill=fill)
text(33,25,'Bearframe Bedrock 0.5.1',49,bold=True)
text(36,89,'SEVEN RUIN VARIANTS   /   RENDERS FROM THE RELEASE TEMPLATES',20,'#a7bfbf')
for i,(key,label) in enumerate(names.items()):
    group=1
    j=i
    x=29+(j%3)*504
    y=175+(j//3)*280
    if j==0:
        text(32,y-43,'Bunker and settlement ruins',29,'#7bd6cf',True)
    draw.rounded_rectangle((x,y,x+488,y+265),15,fill='#202930',outline='#3b5658',width=2)
    s=Site(z.read('Bearframe_Behavior/structures/bearframe/'+key+'.mcstructure'))
    high=s.h-1
    low=3 if group else {'orbital_city':1,'spillway_facility':4,'shelter_bunker':8}.get(key,13)
    underground=key in ('orbital_city','shelter_bunker','spillway_facility')
    if key.startswith(('flooded_','sealed_','collapsed_transit','rootbound_')):
        underground=True
        high=6
    elif underground:
        high={'orbital_city':5,'shelter_bunker':12,'spillway_facility':9}[key]
    pic=render(s,low,high,(469,218))
    sheet.paste(pic,(x+10,y+36))
    text(x+15,y+9,label,20,bold=True)
    if underground: text(x+350,y+12,'CUTAWAY',12,'#92b6b4')
sheet.save(folder/'Bearframe_0.5.1_Ruin_Preview.png')
sheet.thumbnail((780,1275))
sheet.save('ruin_contact.png')
