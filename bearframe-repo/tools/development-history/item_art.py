from zipfile import ZipFile,ZIP_DEFLATED
from pathlib import Path
from io import BytesIO
import json
from PIL import Image,ImageDraw,ImageFont

folder=Path('deliverables')
old=ZipFile(folder/'Bearframe_Bedrock_0.8.0_Star_Odyssey.mcaddon')
rp='Bearframe_Resources/'
bp='Bearframe_Behavior/'
prefix=rp+'textures/bearframe/'
palette={
 'deep':'#242a29','void':'#323a37','steel':'#4a5753','gunmetal':'#636d63',
 'alloy':'#888e77','edge':'#adb19a','pale':'#d1d5b6',
 'copper_dark':'#654b38','copper':'#8d6a47','brass':'#b18b52','gold':'#d4ad67',
 'navy':'#243c48','teal_dark':'#31585c','teal':'#407a7d',
 'cyan':'#65a9a6','light':'#a2d0bf','signal':'#d5e8c8','burn':'#6e443d',
}
def line(d,coords,color,width=1):d.line(coords,fill=palette[color],width=width)
def poly(d,coords,color):d.polygon(coords,fill=palette[color])
def rect(d,coords,color):d.rectangle(coords,fill=palette[color])
def dots(d,coords,color):d.point(coords,fill=palette[color])

def schematic(d):
    # Slanted, hinged circuit folio with a removable trace strip.
    poly(d,[(1,7),(8,2),(15,5),(15,7),(8,13),(1,11)],'deep')
    poly(d,[(2,7),(8,3),(14,5),(8,11),(2,10)],'edge')
    poly(d,[(3,7),(8,4),(13,5),(8,10),(3,9)],'teal_dark')
    poly(d,[(4,7),(8,5),(12,6),(8,9),(4,8)],'teal')
    line(d,[(4,7),(6,8),(8,6),(10,7),(11,6)],'light')
    dots(d,[(4,7),(8,6),(11,6)],'signal')
    line(d,[(2,10),(8,12),(13,8)],'alloy')
    line(d,[(2,8),(2,10),(4,11)],'brass')
    dots(d,[(8,4),(12,5),(8,10)],'pale')

def insignia(d):
    poly(d,[(5,2),(10,2),(13,5),(13,10),(10,13),(5,13),(2,10),(2,5)],'deep')
    poly(d,[(5,3),(10,3),(12,5),(12,10),(10,12),(5,12),(3,10),(3,5)],'brass')
    poly(d,[(6,4),(9,4),(11,6),(11,9),(9,11),(6,11),(4,9),(4,6)],'navy')
    poly(d,[(7,5),(8,7),(10,7),(8,8),(8,10),(7,9),(5,8),(7,7)],'cyan')
    line(d,[(6,8),(7,7),(8,6)],'light')
    dots(d,[(5,3),(7,3),(4,5),(3,7),(10,12)],'gold')
    dots(d,[(2,9),(12,9),(9,12)],'copper')

def salvage(d):
    # Two jagged pieces stacked with fractured ends and bolt holes.
    poly(d,[(1,9),(4,4),(9,3),(12,5),(15,6),(14,11),(11,13),(5,14),(2,12)],'deep')
    poly(d,[(2,9),(6,6),(12,5),(14,7),(12,11),(5,13),(2,11)],'gunmetal')
    poly(d,[(3,8),(6,6),(12,6),(11,9),(6,11),(3,11)],'alloy')
    poly(d,[(4,6),(6,4),(9,4),(10,5),(8,7),(4,8)],'edge')
    line(d,[(4,6),(6,5),(8,5)],'pale')
    line(d,[(7,8),(8,8),(8,9),(10,8)],'steel')
    line(d,[(4,12),(6,12),(8,11),(12,10)],'copper')
    dots(d,[(6,7),(11,7),(10,10)],'deep')
    dots(d,[(3,9),(9,6),(13,8)],'brass')
    dots(d,[(12,8),(9,10)],'teal')

def cell(d):
    poly(d,[(1,10),(4,6),(9,3),(12,2),(14,4),(15,7),(11,12),(6,14),(3,13)],'deep')
    poly(d,[(2,10),(5,6),(10,4),(13,4),(14,7),(10,11),(5,13),(3,12)],'steel')
    poly(d,[(4,9),(7,6),(10,5),(12,7),(10,10),(7,11),(5,11)],'teal_dark')
    line(d,[(5,9),(7,7),(10,6),(11,7),(9,9),(7,10)],'cyan')
    line(d,[(6,9),(8,7),(10,7)],'light')
    dots(d,[(7,9),(9,8)],'signal')
    line(d,[(3,10),(4,11),(5,12),(7,11)],'brass')
    line(d,[(10,4),(12,3),(13,4),(14,6)],'gold')
    dots(d,[(3,11),(12,8),(7,12),(13,6)],'copper_dark')

def scanner(d):
    # Padded field enclosure, angled grip, and separate receiver.
    poly(d,[(2,5),(10,3),(11,1),(13,1),(13,4),(15,5),(14,12),(11,15),(3,14),(1,11)],'deep')
    poly(d,[(2,6),(10,4),(14,6),(13,11),(10,14),(3,13),(2,11)],'steel')
    poly(d,[(3,6),(10,5),(13,6),(12,10),(9,11),(3,10)],'alloy')
    poly(d,[(4,6),(10,6),(12,7),(11,9),(8,10),(4,9)],'navy')
    line(d,[(5,8),(6,8),(7,7),(8,8),(10,7)],'cyan')
    dots(d,[(5,8),(10,7)],'light')
    line(d,[(11,3),(12,3),(12,1)],'brass')
    dots(d,[(12,1),(4,11),(6,11),(9,12)],'gold')
    line(d,[(4,13),(8,13),(11,12)],'gunmetal')
    dots(d,[(2,8),(13,8),(3,5)],'edge')

def wrench(d):
    # Open jaw and thick diagonal handle remain readable at 16 pixels.
    poly(d,[(1,12),(6,7),(6,4),(8,1),(11,0),(11,2),(9,4),(10,5),(12,4),(14,2),(15,3),(15,6),(13,9),(10,10),(5,15),(2,15)],'deep')
    poly(d,[(2,12),(7,7),(7,4),(9,2),(10,1),(10,2),(8,4),(9,6),(11,6),(14,3),(14,6),(12,8),(9,9),(4,14),(2,14)],'gunmetal')
    line(d,[(7,5),(8,3),(10,1)],'edge')
    line(d,[(11,7),(13,6),(14,4)],'edge')
    line(d,[(4,13),(9,8)],'alloy',2)
    line(d,[(3,12),(5,11),(6,10)],'brass')
    line(d,[(3,13),(5,12)],'copper')
    dots(d,[(2,13),(9,8),(12,7)],'pale')
    dots(d,[(6,11),(10,8)],'steel')

designs={
 'relay_schematic':('Relay Schematic',schematic),
 'farfield_insignia':('Farfield Survey Insignia',insignia),
 'salvaged_alloy':('Salvaged Chassis Alloy',salvage),
 'legacy_cell':('Legacy Power Cell',cell),
 'field_scanner':('Farfield Diagnostic Scanner',scanner),
 'repair_wrench':('Atlas Maintenance Wrench',wrench),
}
updates={}
old_icons={}
new_icons={}
def encode(data):return (json.dumps(data,indent=2)+'\n').encode()
for name,(_,draw) in designs.items():
    path=prefix+name+'.png'
    old_icons[name]=Image.open(BytesIO(old.read(path))).convert('RGBA')
    im=Image.new('RGBA',(16,16))
    draw(ImageDraw.Draw(im))
    assert im.getbbox() is not None
    assert im.getchannel('A').getextrema()==(0,255)
    new_icons[name]=im
    buf=BytesIO();im.save(buf,'PNG')
    updates[path]=buf.getvalue()
for root in (bp,rp):
    path=root+'manifest.json'
    data=json.loads(old.read(path))
    for item in [data['header'],*data['modules'],*data.get('dependencies',[])]:
        if item.get('version')==[0,8,0]:item['version']=[0,8,1]
    updates[path]=encode(data)
release=folder/'Bearframe_Bedrock_0.8.1_Star_Odyssey.mcaddon'
with ZipFile(release,'w',ZIP_DEFLATED) as z:
    for path in old.namelist():z.writestr(path,updates[path] if path in updates else old.read(path))
with ZipFile(release) as z:
    assert z.testzip() is None
    assert set(z.namelist())==set(old.namelist())
    assert {path for path in z.namelist() if old.read(path)!=z.read(path)}==updates.keys()
    atlas=json.loads(z.read(rp+'textures/item_texture.json'))['texture_data']
    for path in {prefix+name+'.png' for name in designs}:
        assert any(rp+x['textures']+'.png'==path for x in atlas.values())
        assert Image.open(BytesIO(z.read(path))).size==(16,16)

sheet=Image.new('RGB',(1080,647),'#131d24')
d=ImageDraw.Draw(sheet)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans'
def text(x,y,value,size,color='#eaf0ef',bold=False,anchor=None):
    d.text((x,y),value,font=ImageFont.truetype(font+('-Bold.ttf' if bold else '.ttf'),size),fill=color,anchor=anchor)
text(29,22,'Bearframe inventory art',43,bold=True)
text(32,79,'STAR ODYSSEY EDITION  /  0.8.1  /  SIX REDRAWN ICONS',16,'#86b9ba',True)
for index,(name,(label,_)) in enumerate(designs.items()):
    left=26+(index%3)*345
    top=122+(index//3)*253
    d.rounded_rectangle((left,top,left+334,top+235),12,fill='#26373d',outline='#435f66')
    text(left+13,top+15,label,18,bold=True)
    for j,img in enumerate((old_icons[name],new_icons[name])):
        x=left+20+j*155
        d.rounded_rectangle((x,top+53,x+137,top+187),8,fill='#19262b')
        v=img.resize((112,112),Image.Resampling.NEAREST)
        sheet.paste(v,(x+13,top+64),v)
        text(x+69,top+200,'BEFORE' if j==0 else '0.8.1',13,'#9cb9bb',True,'mt')
sheet.save(folder/'Bearframe_0.8.1_Item_Preview.png')
print('Verified six new icons, native 16-pixel scale, original gameplay and Star Odyssey dependency.')
